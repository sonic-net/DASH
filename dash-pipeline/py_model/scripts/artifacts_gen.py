#!/usr/bin/env python3
"""
Optimized generator for py_p4rt.json from dash_py_model in-memory model.
- Caches expensive reflection (enum/member lookups, annotation width reads)
- Uses comprehensions where appropriate
- Simplifies/clarifies structured-annotation extraction
- Keeps behavior compatible with your original code
"""

import os
import re
import sys
import enum
import json
import base64
import inspect
from functools import lru_cache
from collections import OrderedDict
from typing import Annotated, Optional, get_origin, get_args, get_type_hints as get_annotations

from py_model.scripts.gen_ir import gen_ir
from py_model.scripts.gen_table_chain import generate_table_chain
from py_model.scripts.gen_action_chain import generate_action_chain
from py_model.scripts.gen_counter_chain import generate_counter_chain
from py_model.scripts.gen_global_actions_chain import generate_global_actions_chain

from py_model.libs.__table import *
from py_model.libs.__id_map import *
from py_model.libs.__jsonize import *
from py_model.libs.__counters import *
from py_model.dash_py_v1model import *

_isclass = inspect.isclass
_isfunction = inspect.isfunction
_getmembers = inspect.getmembers
_enum_types = (enum.IntEnum, enum.IntFlag)
_RE_CAMEL1 = re.compile(r'(.)([A-Z][a-z]+)')
_RE_CAMEL2 = re.compile(r'([a-z0-9])([A-Z])')

project_dir = "py_model/data_plane"
func_set = []
func_chain = []
act_alias_names = []
table_chain = []
tab_alias_names = []
counter_chain = []
direct_counter_chain = []
GLOBAL_NAMES = globals()

class SafeEncoder(json.JSONEncoder):
    def default(self, o):
        # enum members -> their value
        if isinstance(o, enum.Enum):
            return o.value
        # enum types -> mapping name->value
        if inspect.isclass(o) and issubclass(o, enum.Enum):
            return {e.name: e.value for e in o}
        # callables -> name
        if callable(o):
            return getattr(o, "__name__", str(o))
        return super().default(o)

def is_int_str(val: str) -> bool:
    if not isinstance(val, str):
        return False
    return val.lstrip("-").isdigit()

def format_scalar(val):
    if isinstance(val, str):
        return json.dumps(val)
    elif isinstance(val, bool):
        return "true" if val else "false"
    return str(val)

def to_snake_case(name):
    # camelCase or PascalCase → snake_case
    s1 = _RE_CAMEL1.sub(r'\1_\2', name)
    return _RE_CAMEL2.sub(r'\1_\2', s1).lower()

def base64_to_escaped(b64_str):
    # Decode base64 to bytes
    decoded_bytes = base64.b64decode(b64_str)
    # Convert each byte to \ooo (octal) escaped format
    escaped = ''.join(f'\\{byte:03o}' for byte in decoded_bytes)
    return escaped

def dict_to_textproto(d: dict, indent: int = 0, parent_key: str = "") -> str:
    """Recursively dumps a dict/list into Protobuf text format style."""
    lines = []
    pad = " " * indent

    if isinstance(d, dict):
        for key, value in d.items():
            key = to_snake_case(key)

            # Special-case for serializable_enums (map field)
            if key == "serializable_enums" and isinstance(value, dict):
                for map_key, map_val in value.items():
                    lines.append(f"{pad}{key} {{")
                    lines.append(f"{pad}  key: \"{map_key}\"")
                    lines.append(f"{pad}  value {{")
                    lines.append(dict_to_textproto(map_val, indent + 4))
                    lines.append(f"{pad}  }}")
                    lines.append(f"{pad}}}")
            elif isinstance(value, dict):
                lines.append(f"{pad}{key} {{")
                lines.append(dict_to_textproto(value, indent + 2))
                lines.append(f"{pad}}}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{pad}{key} {{")
                        lines.append(dict_to_textproto(item, indent + 2))
                        lines.append(f"{pad}}}")
                    else:
                        lines.append(f"{pad}{key}: {format_scalar(item)}")
            else:
                if key != "unit" and key != "size" and key != "int64_value" and key != "match_type" and value != "DEFAULT_ONLY":
                    value = format_scalar(value)
                if value == "LIST" or value == "RANGE_LIST":
                    value = "OPTIONAL"
                if key == 'value':
                    value = base64_to_escaped(value)
                    value = f"\"{value}\""
                append = lines.append
                append(f"{pad}{key}: {value}")


    elif isinstance(d, list):
        for item in d:
            if isinstance(item, dict):
                lines.append(f"{pad}{{")
                lines.append(dict_to_textproto(item, indent + 2))
                lines.append(f"{pad}}}")
            else:
                lines.append(f"{pad}{format_scalar(item)}")

    return "\n".join(lines)

def find_best_match(name: str, chain: Iterable[str]) -> Optional[str]:
    """
    Find the best match in `chain` for the given `name`, by matching
    from the end (dot-separated segments).
    """
    input_parts = name.split(".")
    best_match = None
    best_len = 0

    for full_name in chain:
        full_parts = full_name.split(".")
        min_len = min(len(input_parts), len(full_parts))
        match_len = 0
        # compare backwards
        for i in range(1, min_len + 1):
            if input_parts[-i] == full_parts[-i]:
                match_len += 1
            else:
                break
        if match_len > best_len:
            best_len = match_len
            best_match = full_name

    return best_match

@lru_cache(maxsize=512)
def find_by_function_name(func_name: str) -> Optional[str]:
    return find_best_match(func_name, func_chain)

@lru_cache(maxsize=512)
def find_by_table_name(table_name: str) -> Optional[str]:
    return find_best_match(table_name, table_chain)

@lru_cache(maxsize=512)
def find_by_counter_name(counter_name: str) -> Optional[str]:
    return find_best_match(counter_name, counter_chain)

@lru_cache(maxsize=512)
def find_by_direct_counter_name(counter_name: str) -> Optional[str]:
    return find_best_match(counter_name, direct_counter_chain)

@lru_cache(maxsize=1024)
def _read_width(k: str) -> Optional[int]:
    """
    Read bitwidth for a dotted key like "Container.field.subfield".
    Caches results because this uses runtime type introspection.
    """
    try:
        tokens = k.split(".")
        if not tokens:
            return None
        # First token is a global name
        root_name, *rest = tokens
        container = GLOBAL_NAMES.get(root_name)
        if container is None:
            return None

        # iterate through annotation types
        container_type = type(container)
        var_name = rest[0] if rest else None
        for token in rest[1:]:
            anns = get_annotations(container_type) or {}
            container_type = anns.get(var_name)
            var_name = token
            if container_type is None:
                return None

        anns = get_annotations(container_type) or {}
        ann = anns.get(var_name)
        if ann is None:
            return None

        if get_origin(ann) is Annotated:
            args = get_args(ann)
            # metadata usually at args[2] in your pattern
            if len(args) >= 3 and isinstance(args[2], dict):
                # assume 'bitwidth' or direct width is in metadata
                return args[2].get("bitwidth") or args[2].get("width") or None

            # numeric second arg for Annotated[int, <width>]
            if len(args) > 1 and isinstance(args[1], int):
                return args[1]

        # If annotation is an enum class, try its __bitwidth__
        if _isclass(ann) and issubclass(ann, _enum_types):
            return getattr(ann, "__bitwidth__", None)

        # fallback: if it's a raw int annotation assume 32
        if ann is int:
            return 32

    except Exception:
        # Do not crash on unexpected types; caller should handle None.
        return None

def _extract_attrs(obj, exclude_keys=None):
    if obj is None:
        return None
    d = getattr(obj, "__dict__", None)
    if not d:
        return None
    out = {k: v for k, v in d.items()
           if v is not None and not _isfunction(v) and not isinstance(v, staticmethod)}
    if exclude_keys:
        for k in exclude_keys:
            out.pop(k, None)
    return out or None

_get_str_annos_for_table = lambda t: _extract_attrs(t, getattr(t, "key", {}))
_get_str_annos_for_key = lambda hints, k: _extract_attrs(hints.get(k))

def _apply_action_scope(node, aid, const_def_act_id, def_hint, def_act_name, act_name, hints):
    annotations = []
    if const_def_act_id and aid == const_def_act_id and def_hint:
        annotations.append("@defaultonly")
    elif def_act_name and act_name == "NoAction":
        annotations.append("@defaultonly")
    elif hints.get("annotations"):
        annotations.append(hints["annotations"])
    if annotations:
        node["annotations"] = annotations
        node["scope"] = "DEFAULT_ONLY"

def _make_str_annos_node(str_annos: dict, kind: int):
    """
    Turn a dict of structured annotations into the JSON node shape expected by P4RT.
    kind: 0=table, 1=saival/action param, 2=counter
    """
    if not str_annos:
        return None

    kv_pairs = []
    if kind == 0:  # SaiTable
        # "ignored" is special-cased in original code
        if "ignored" in str_annos:
            kv_pairs.append({"key": "ignored", "value": {"stringValue": str(str_annos["ignored"])}})
        else:
            for key, value in str_annos.items():
                val_type = "int64Value" if key == "order" else "stringValue"
                kv_pairs.append({"key": key, "value": {val_type: str(value)}})
        name = "SaiTable"
    elif kind == 2:  # SaiCounter
        name = "SaiCounter"
        for key, value in str_annos.items():
            # booleans should be expressed as strings for compatibility with original output
            kv_pairs.append({"key": key, "value": {"stringValue": str(value)}})
    else:  # SaiVal or action param
        name = "SaiVal"
        for key, value in str_annos.items():
            kv_pairs.append({"key": key, "value": {"stringValue": str(value)}})

    return [{"name": name, "kvPairList": {"kvPairs": kv_pairs}}]

def _extract_annotation_info(k: str, anno):
    """
    Returns (bitwidth:int or None, str_annos:dict or None).
    Handles Annotated[...] patterns, enums, and plain int.
    """
    origin = get_origin(anno)
    if origin is Annotated:
        args = get_args(anno)
        base, *meta = args
        width = next((m for m in meta if isinstance(m, int)), None)
        meta_dict = next((m for m in meta if isinstance(m, dict)), None)
        if _isclass(base) and issubclass(base, _enum_types):
            return width or getattr(base, "__bitwidth__", 16), meta_dict
        if base is int:
            return width or 32, meta_dict
        raise TypeError(f"Unsupported base type for param '{k}': {base}")
    if _isclass(anno) and issubclass(anno, _enum_types):
        return getattr(anno, "__bitwidth__", 16), None
    if anno is int:
        return 32, None
    raise TypeError(f"Unsupported annotation type for param '{k}': {anno}")

def unique_alias(full_name: str, used_aliases: List[str]) -> str:
    """Generate a unique alias for full_name, avoiding collisions in used_aliases."""
    alias = full_name.rsplit(".", 1)[-1]
    if alias not in used_aliases:
        used_aliases.append(alias)
        return alias

    parts = full_name.split(".")
    # progressively include more path components (2-part, 3-part, ...)
    for i in range(2, len(parts) + 1):
        candidate = ".".join(parts[-i:])
        if candidate not in used_aliases:
            used_aliases.append(candidate)
            return candidate

    # fallback to full name (last resort)
    used_aliases.append(full_name)
    return full_name

def resolve_func_name(raw: Any, func_name_to_classflag: Dict[str, bool]) -> str:
    """Centralized resolution for functions (handles class-method flags & find_by_function_name)."""
    name = getattr(raw, "__qualname__", getattr(raw, "__name__", str(raw)))
    is_class_method = func_name_to_classflag.get(name, False)
    if name not in func_name_to_classflag or is_class_method:
        # attempt to translate via project-level name lookup once
        found = find_by_function_name(name)
        return found or name
    return name

def _resolve_default_action(def_action, func_name_to_classflag):
    """Unify default-action handling (returns resolved name and its generated id)"""
    if def_action is None:
        return None, None
    func, hints = def_action if isinstance(def_action, tuple) else (def_action, {})
    name = getattr(func, "__qualname__", getattr(func, "__name__", str(func)))
    name = resolve_func_name(func, func_name_to_classflag)
    return name, gen_symbol_id(name, ACTION)

@lru_cache(maxsize=256)
def get_dash_enum_members(e):
    """Return a list of (name, enum-member) sorted by numeric value."""
    members = [(name, val) for name, val in _getmembers(e) if not name.startswith("_") and isinstance(val, e)]
    members.sort(key=lambda item: int(item[1]))
    return members

def make_enum_node(enum_cls):
    """Build the enum representation node used in typeInfo.serializableEnums."""
    enum_node = OrderedDict()
    bitwidth = getattr(enum_cls, "__bitwidth__", 16)
    enum_node["underlyingType"] = {"bitwidth": bitwidth}

    members_node = []
    members = get_dash_enum_members(enum_cls)

    # If IntFlag and has NONE member, ensure it's first (preserves original behavior)
    if issubclass(enum_cls, enum.IntFlag) and hasattr(enum_cls, "NONE"):
        members = [m for m in members if m[0] != "NONE"]
        members.insert(0, ("NONE", getattr(enum_cls, "NONE")))

    bytes_needed = (bitwidth + 7) // 8
    for name, member in members:
        int_value = int(member)
        # encode to big-endian with sufficient bytes
        b64_value = base64.b64encode(int_value.to_bytes(bytes_needed, "big", signed=False)).decode("ascii")
        members_node.append(OrderedDict([("name", name), ("value", b64_value)]))

    enum_node["members"] = members_node
    return enum_node

@lru_cache(maxsize=1)
def get_dash_enum_list():
    """Return list of enum classes in current module that are IntEnum/IntFlag subclasses."""
    class_list = _getmembers(sys.modules[__name__], inspect.isclass)
    return [
        cls
        for name, cls in class_list
        if not name.startswith("_")
        and inspect.isclass(cls)
        and issubclass(cls, _enum_types)
        and cls not in _enum_types
        and name not in ("BufferFlags",)
    ]

def make_table_node(table: "Table", table_name: str, tid: int):
    """Construct table JSON node from Table instance (optimized)."""
    global tab_alias_names, func_set, action_ids

    table_node = OrderedDict()

    # alias
    alias_name = unique_alias(table_name, tab_alias_names)
    preamble_node = OrderedDict(id=tid, name=table_name, alias=alias_name)

    # structured annotations for table preamble
    str_annos = _get_str_annos_for_table(table.sai_table)
    if str_annos:
        preamble_node["structuredAnnotations"] = _make_str_annos_node(str_annos, 0)
    table_node["preamble"] = preamble_node

    # matchFields
    match_fields = []
    for mf_id, k in enumerate(table.key, start=1):
        mf = OrderedDict(
            id=mf_id,
            name=str(k),
            bitwidth=_read_width(k),
            matchType=table.key[k].__name__,
        )
        mf_str_annos = _get_str_annos_for_key(table.sai_val, k)
        if mf_str_annos:
            mf["structuredAnnotations"] = _make_str_annos_node(mf_str_annos, 1)
        match_fields.append(mf)
    table_node["matchFields"] = match_fields

    # Build a small cache of func name -> is_class_method to avoid repeated searches
    func_name_to_classflag = {name: flag for name, flag in func_set}

    # default actions (resolved once)
    def_act_name, def_act_id = _resolve_default_action(table.default_action, func_name_to_classflag)
    const_def_act_name, const_def_act_id = _resolve_default_action(table.const_default_action, func_name_to_classflag)

    # compute def_hint only once
    def_hint = any(isinstance(a, tuple) and a[1] for a in table.actions)

    # actions -> actionRefs
    action_refs = []
    for action in table.actions:
        func, hints = action if isinstance(action, tuple) else (action, {})
        act_name = getattr(func, "__qualname__", getattr(func, "__name__", str(func)))

        # resolve using cache/lookup
        is_class_method = func_name_to_classflag.get(act_name, False)
        if act_name not in func_name_to_classflag or is_class_method:
            resolved = find_by_function_name(act_name) or act_name
            act_name = resolved

        aid = gen_symbol_id(act_name, ACTION)
        action_ids[aid] = act_name

        node: Dict[str, Any] = {"id": aid}
        annotations = []

        # set DEFAULT_ONLY for some conditions
        _apply_action_scope(node, aid, const_def_act_id, def_hint, def_act_name, act_name, hints)

        action_refs.append(node)

    table_node["actionRefs"] = action_refs

    # prefer const default action id if provided (match original logic)
    if table.const_default_action:
        table_node["constDefaultActionId"] = const_def_act_id

    # attach direct counter if present
    parts = table_name.split(".")
    attempts = [".".join(parts[-3:]), ".".join(parts[-2:]), parts[-1]]

    for idx, tname in enumerate(attempts, start=1):
        if tname in DashTableCounters._attachments:
            ctr_name = DashTableCounters._attachments[tname]
            ctr = DashTableCounters._counters.get(ctr_name)
            full_ctr_name = f"{table_name.rsplit('.', 1)[0]}.{ctr_name}"
            cid = gen_symbol_id(full_ctr_name, DIRECT_COUNTER) if ctr else None
            if ctr:
                table_node["directResourceIds"] = [cid]
            break  # stop after first successful match

    # size handling (prefer structured annotation size if present)
    size = (str_annos or {}).get("size") if str_annos else None
    table_node["size"] = size if size is not None else "1024"

    return table_node

def make_action_node(act_name: str, annotations: dict, aid: int, flag: bool):
    """Create action node from action name and its annotations mapping."""
    global act_alias_names

    action_node = OrderedDict()

    alias_name = unique_alias(act_name, act_alias_names)
    preamble_node = OrderedDict(id=aid, name=act_name, alias=alias_name)

    # special-case NoAction
    if act_name == "NoAction":
        preamble_node["annotations"] = ['@noWarn("unused")']
        action_node["preamble"] = preamble_node
        return action_node

    action_node["preamble"] = preamble_node

    # params from annotations
    params = []
    for param_id, (k, anno) in enumerate((annotations or {}).items(), start=1):
        param_node = OrderedDict(id=param_id, name=k)
        bitwidth, str_annos = _extract_annotation_info(k, anno)
        if bitwidth is not None:
            param_node["bitwidth"] = bitwidth
        if str_annos:
            param_node["structuredAnnotations"] = _make_str_annos_node(str_annos, 1)
        params.append(param_node)

    if params:
        action_node["params"] = params
    return action_node

def make_counter_node(counter: "Counter"):
    """Create a general counter node."""
    cfg = counter.config
    node = OrderedDict()

    ctr_name = find_by_counter_name(cfg.ctr_name) or cfg.ctr_name
    cid = gen_symbol_id(ctr_name, COUNTER)

    node["preamble"] = OrderedDict(id=cid, name=ctr_name, alias=cfg.ctr_name)

    str_annos = {}
    if getattr(cfg, "name", None):
        str_annos["name"] = cfg.name
    if getattr(cfg, "attr_type", None):
        str_annos["attr_type"] = cfg.attr_type
    if getattr(cfg, "action_names", None):
        str_annos["action_names"] = cfg.action_names
    if getattr(cfg, "no_suffix", None):
        str_annos["no_suffix"] = "true"
    if str_annos:
        node["preamble"]["structuredAnnotations"] = _make_str_annos_node(str_annos, 2)

    node["spec"] = OrderedDict(unit=cfg.counter_type.value)
    node["size"] = str(cfg.size)
    return node

def make_direct_counter_node(counter: "DirectCounter", table_name: str, table_id: Optional[int] = None):
    node = OrderedDict()

    ctr_name = f"{table_name.rsplit('.', 1)[0]}.{counter.name}"
    ctr_name = find_by_direct_counter_name(ctr_name) or ctr_name

    d_cid = gen_symbol_id(ctr_name, DIRECT_COUNTER)
    node["preamble"] = OrderedDict(id=d_cid, name=ctr_name, alias=counter.name)
    node["spec"] = OrderedDict(unit=counter.counter_type.value)
    if table_id is not None:
        node["directTableId"] = table_id
    return node

def make_pyinfo(ignore_tables):
    """Assemble top-level pyinfo structure (optimized)."""
    global func_chain, func_set, table_chain, counter_chain, direct_counter_chain
    global table_objs, action_objs, action_ids, table_ids

    pyinfo = OrderedDict(pkgInfo={"arch": "python-model"})

    # build call graphs and sets once
    func_set = generate_global_actions_chain(project_dir)
    func_chain = generate_action_chain(project_dir)
    table_chain = generate_table_chain(project_dir)
    results = generate_counter_chain(project_dir)
    counter_chain = results[0]
    direct_counter_chain = results[1]

    # prepare a fast lookup for func-name -> is_class_method
    func_name_to_classflag = {name: flag for name, flag in func_set}

    # tables
    tables_node = []
    for tname, table in table_objs.items():
        if isinstance(table, Table) and table not in ignore_tables:
            table_name = find_by_table_name(tname) or tname
            tid = gen_symbol_id(table_name, TABLE)
            tables_node.append(make_table_node(table, table_name, tid))
            table_ids[tid] = table_name
        else:
            # keep original behavior: log warning
            print(f"Warning: No Table object found for {tname}")
    pyinfo["tables"] = tables_node

    # actions
    actions_node = []
    # first pass: functions from func_set
    for func, tag in func_set:
        if tag is True:
            func = find_by_function_name(func) or func
        aid = gen_symbol_id(func, ACTION)
        action_ids[aid] = func
        actions_node.append(make_action_node(func, {}, aid, False))

    # second pass: explicit action_objs (may include annotations)
    for act_name, func in action_objs.items():
        is_class_method = func_name_to_classflag.get(act_name, False)
        if act_name not in [n for n, _ in func_set] or is_class_method:
            newfunc, hints = func if isinstance(func, tuple) else (func, {})
            annotations = get_annotations(newfunc) or {}
            resolved_name = find_by_function_name(act_name) or act_name
            aid = gen_symbol_id(resolved_name, ACTION)
            # ensure we record id -> name mapping
            action_ids[aid] = resolved_name
            actions_node.append(make_action_node(resolved_name, annotations, aid, True))

    pyinfo["actions"] = actions_node

    # counters
    pyinfo["counters"] = [make_counter_node(c) for c in DashCounters._counters.values()]

    # direct counters (attached mapping)
    direct_counters = []
    for ctr_name, counter_name in DashTableCounters._attachments.items():
        attached_table = find_by_table_name(ctr_name) or ctr_name
        ctr_obj = DashTableCounters._counters.get(counter_name)
        table_id = gen_symbol_id(attached_table, TABLE)
        direct_counters.append(make_direct_counter_node(ctr_obj, attached_table, table_id))
    pyinfo["directCounters"] = direct_counters

    # enums -> typeInfo
    serializableEnums = OrderedDict()
    for e in get_dash_enum_list():
        serializableEnums[e.__name__] = make_enum_node(e)
    pyinfo["typeInfo"] = OrderedDict(serializableEnums=serializableEnums)

    return pyinfo

if __name__ == "__main__":
    output_dir = "py_model/dash_pipeline.py_model"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ignore_tables = set()

    # Generate and serialize
    pyinfo = make_pyinfo(ignore_tables=[])

    # Create an empty dash_pipeline.json file with valid JSON
    with open(os.path.join(output_dir, "dash_pipeline.json"), "w") as f:
        json.dump({}, f)

    # Dump to Protobuf text-format string
    textproto_output = dict_to_textproto(pyinfo)
    with open(os.path.join(output_dir, "dash_pipeline_p4rt.txt"), "w") as f:
        f.write(textproto_output + "\n")

    # Dump to Protobuf json-format string
    with open(os.path.join(output_dir, "dash_pipeline_p4rt.json"), "w") as f:
        json.dump(pyinfo, f, indent=2, sort_keys=False, cls=SafeEncoder)

    # Generate IR and save as JSON
    ir = gen_ir()
    with open(os.path.join(output_dir, "dash_pipeline_ir.json"), "w") as f:
        json.dump(ir, f, indent=2, sort_keys=False)

    print("Finished generating artifacts at 'dash_pipeline.py_model/'")
