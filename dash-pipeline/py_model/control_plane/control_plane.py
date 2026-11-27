import base64
import hashlib
import builtins
from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.libs.__id_map import *
from py_model.libs.__obj_classes import *
from py_model.data_plane.dash_pipeline import *

class InsertRequest:
    class Value:
        class Ternary:
            def __init__(self):
                self.value = ""
                self.mask = ""

        class LPM:
            def __init__(self):
                self.value = ""
                self.prefix_len = 0

        class Range:
            def __init__(self):
                self.low = ""
                self.high = ""

        def __init__(self):
            self.exact = ""
            self.ternary = InsertRequest.Value.Ternary()
            self.prefix = InsertRequest.Value.LPM()
            self.range = InsertRequest.Value.Range()
            self.ternary_list = []
            self.range_list = []

    def __init__(self):
        self.table = 0
        self.values = []
        self.action = 0
        self.params = []
        self.priority = 0

def get_hex_value(value: str):
    decoded = base64.b64decode(value)
    return decoded.hex()

def get_table_name(table_id: int):
    return table_ids.get(table_id, "unknown")

def get_action_name(action_id: int) -> str:
    return action_ids.get(action_id, "unknown")

def _resolve_name(name: str, ctx=None, fallback_dict=None):
    if ctx is None:
        ctx = globals()
    obj = ctx
    for part in name.split(".")[1:] if len(name.split(".")) > 2 else name.split("."):
        try:
            obj = obj[part] if isinstance(obj, dict) else getattr(obj, part)
        except (KeyError, AttributeError):
            if fallback_dict and part in fallback_dict:
                obj = fallback_dict[part]
            else:
                py_log("info", f"ERROR: cannot resolve '{part}'")
                return None
    return obj

def resolve_action_name(name: str, ctx=None):
    return _resolve_name(name, ctx)

def resolve_table_name(name: str, ctx=None):
    if name in table_objs:
        return table_objs[name]
    return _resolve_name(name, ctx, globals())

def safe_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value.startswith(("0x", "0X")):
            return int(value, 16)
        try:
            return int(value, 16)
        except ValueError:
            try:
                return int(value)
            except Exception:
                raise ValueError(f"Invalid numeric value: {value}")
    raise ValueError(f"Unsupported type for conversion: {type(value)}")

def normalize_table_entry(entry: dict) -> dict:
    normalized = dict(entry)

    if "match" in normalized:
        normalized["match"].sort(key=lambda m: m.get("fieldId", 0))

    action_data = normalized.get("action", {}).get("action")
    if action_data and "params" in action_data:
        action_data["params"].sort(key=lambda p: p.get("paramId", 0))
        normalized["action"]["action"] = action_data

    return normalized

def populate_table_entry(insertRequest: InsertRequest, key_format: list):
    entry = Entry()
    entry.values = []

    for idx, val in builtins.enumerate(insertRequest.values):
        if idx >= len(key_format):
            py_log("info", f"Skipping index {idx}, no matching key format.")
            continue

        match_type = key_format[idx]

        try:
            if match_type is EXACT:
                entry.values.append(val.exact)

            elif match_type is TERNARY:
                ternary = Entry.Ternary()
                ternary.value = safe_int(val.ternary.value)
                ternary.mask = safe_int(val.ternary.mask)
                entry.values.append(ternary)

            elif match_type is LIST:
                entry.values.append([
                    Entry.Ternary(value=safe_int(t.value), mask=safe_int(t.mask))
                    for t in val.ternary_list
                ])

            elif match_type is RANGE:
                rng = Entry.Range()
                rng.low = safe_int(val.range.low)
                rng.high = safe_int(val.range.high)
                entry.values.append(rng)

            elif match_type is RANGE_LIST:
                entry.values.append([
                    Entry.Range(low=safe_int(r.low), high=safe_int(r.high))
                    for r in val.range_list
                ])

            elif match_type is LPM:
                lpm = Entry.LPM()
                lpm.value = val.prefix.value
                lpm.prefix_len = val.prefix.prefix_len
                entry.values.append(lpm)

        except Exception as e:
            py_log("error", f"{match_type} conversion error: {e}")
            continue

    # Handle action resolution
    action_id = insertRequest.action
    if action_id is not None:
        action_name = get_action_name(action_id)
        py_log(f"Action: {action_name}")
        action_obj = resolve_action_name(action_name)
        if not action_obj:
            py_log("info", f"Could not resolve action name: {action_name}")
            return None
        entry.action = action_obj
        entry.params = insertRequest.params
    entry.priority = insertRequest.priority

    return entry

def table_insert_api(insertRequest: InsertRequest, obj_type, hash):
    table_name = get_table_name(insertRequest.table)
    if table_name == "unknown":
        return RETURN_FAILURE

    table = resolve_table_name(table_name)
    if not table or not table.key:
        return RETURN_FAILURE

    entry = populate_table_entry(insertRequest, list(table.key.values()))
    if not entry:
        return RETURN_FAILURE

    if obj_type == 'INSERT':
        if hash in table.entries:
            py_log("info", "Matching entry exists, use MODIFY if you wish to change action")
            return RETURN_FAILURE
        table.insert(hash, entry)
        # py_log("info", f"Entry {table.entry_cnt - 1} added to table '{table_name}'")
    elif obj_type == 'MODIFY':
        ret = table.update(hash, entry)
    else:
        py_log("info", f"Unknown operation type: {obj_type}")
        return RETURN_FAILURE

    return RETURN_SUCCESS

def parse_insert_request(json_obj, obj_type):
    insertRequest = InsertRequest()

    table_entry = normalize_table_entry(
        json_obj.get("entity", {}).get("tableEntry", {})
    )
    match = table_entry.get("match", {})
    hash_val = hashlib.sha256(str(match).encode()).hexdigest()

    insertRequest.table = table_entry.get("tableId", [])
    table_name = get_table_name(insertRequest.table)
    table = resolve_table_name(table_name)

    if obj_type == 'DELETE':
        if table.delete(hash_val) == RETURN_SUCCESS:
            py_log("info", f"Removed entry {table.entry_cnt + 1} from table '{table_name}'")
        return None, hash_val
    elif obj_type == 'INSERT':
        py_log("info", f"Entry {table.entry_cnt} being added to table '{table_name}'")
        py_log("info", f"Dumpling entry {table.entry_cnt}")
    elif obj_type == 'MODIFY':
        py_log("info", f"Modifying entry in table '{table_name}'")
        py_log("info", f"Dumpling entry")

    keys = list(table.key.keys())
    insertRequest.values = []

    py_log(None, "Match key:")
    for match_field in table_entry.get("match", []):
        field_idx = match_field["fieldId"] - 1
        field_key = keys[field_idx]
        val = InsertRequest.Value()

        def _get_val(field):
            return get_hex_value(field.get("value", "0"))

        if "exact" in match_field:
            val.exact = _get_val(match_field["exact"])
            py_log(None, f"* {field_key}: Exact : {val.exact}")

        if "ternary" in match_field:
            t = val.ternary
            t.value = _get_val(match_field["ternary"])
            t.mask = get_hex_value(match_field["ternary"]["mask"])
            val.ternary_list.append(t)
            py_log(None, f"* {field_key}: TERNARY : {t.value} && {t.mask}")

        if "optional" in match_field:
            opt_val = _get_val(match_field["optional"])
            if field_key in {'meta.dst_ip_addr', 'meta.src_ip_addr', 'meta.ip_protocol'}:
                t = val.ternary
                t.value = opt_val
                mask_bits = ((1 << ((int(opt_val, 16).bit_length() + 7) // 8 * 8)) - 1)
                t.mask = mask_bits
                val.ternary_list.append(t)
                py_log(None, f"* {field_key}: TERNARY-LIST : {t.value} && {hex(t.mask)}")
            elif field_key in {'meta.src_l4_port', 'meta.dst_l4_port'}:
                r = val.range
                r.low = r.high = opt_val
                val.range_list.append(r)
                py_log(None, f"* {field_key}: RANGE-LIST: {r.low} -> {r.high}")

        if "lpm" in match_field:
            val.prefix.value = _get_val(match_field["lpm"])
            val.prefix.prefix_len = match_field["lpm"]["prefixLen"]
            py_log(None, f"* {field_key}: LPM : {val.prefix.value} : {hex(val.prefix.prefix_len)}")

        if "range" in match_field:
            val.range.low = get_hex_value(match_field["range"]["low"])
            val.range.high = get_hex_value(match_field["range"]["high"])
            py_log(None, f"* {field_key}: Range: {val.range.low} -> {val.range.high}")

        insertRequest.values.append(val)

    insertRequest.priority = table_entry.get("priority", 0)
    py_log(None, f"Priority: {insertRequest.priority}")

    action_data = table_entry.get("action", {}).get("action", {})
    insertRequest.action = action_data.get("actionId", None)

    if insertRequest.action is not None:
        insertRequest.params = [
            int(get_hex_value(p["value"]), 16) if p.get("value") else 0
            for p in action_data.get("params", [])
        ]

    py_log(None, f"Action entry: {table_name} - {insertRequest.params}")

    return insertRequest, hash_val
