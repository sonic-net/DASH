from inspect import get_annotations
from py_model.libs.__utils import *
from py_model.libs.__id_map import *

class SaiTable:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.api = kwargs.get("api")
        self.api_type = kwargs.get("api_type")
        self.order = kwargs.get("order")
        self.stage = kwargs.get("stage")
        self.isobject = kwargs.get("isobject")
        self.ignored = kwargs.get("ignored")
        self.match_type = kwargs.get("match_type")
        self.single_match_priority = kwargs.get("single_match_priority")
        self.enable_bulk_get_api = kwargs.get("enable_bulk_get_api")
        self.enable_bulk_get_server = kwargs.get("enable_bulk_get_server")

class SaiVal:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")
        self.default_value = kwargs.get("default_value")
        self.isresourcetype = kwargs.get("isresourcetype")
        self.is_object_key = kwargs.get("is_object_key")
        self.objects = kwargs.get("objects")
        self.isreadonly = kwargs.get("isreadonly")
        self.iscreateonly = kwargs.get("iscreateonly")
        self.match_type = kwargs.get("match_type")
        self.ismandatory = kwargs.get("ismandatory")
        self.skipattr = kwargs.get("skipattr")

class Entry:
    class Ternary:
        def __init__(self, value: int = 0, mask: int = 0):
            self.value = value
            self.mask = mask

        def __eq__(self, other):
            return (isinstance(other, type(self)) and
                    self.value == other.value and
                    self.mask == other.mask)

    class LPM:
        def __init__(self, value: int = 0, prefix_len: int = 0):
            self.value = value
            self.prefix_len = prefix_len
        
        def __eq__(self, other):
            return (isinstance(other, type(self)) and
                    self.value == other.value and
                    self.prefix_len == other.prefix_len)

    class Range:
        def __init__(self, low: int = 0, high: int = 0):
            self.low = low
            self.high = high

        def __eq__(self, other):
            return (isinstance(other, type(self)) and
                    self.low == other.low and
                    self.high == other.high)

    def __init__(self,
                    values: list = None,
                    action: Callable = None,
                    params: list[int] = None,
                    priority: int = 0):
        self.values = values or []
        self.action = action
        self.params = params or []
        self.priority = priority

def _read_value(input):
    tokens = input.split(".")
    container = globals()[tokens[0]]
    var_name = tokens[1]
    var = getattr(container, var_name)
    for token in tokens[2:]:
        container = var
        var_name = token
        var = getattr(container, var_name)
    width = (get_annotations(type(container))[var_name].__metadata__)[0]
    return (var, width)

def EXACT(key: str, entry_value: int, match_value: int, width: int):
    curr_entry[key] = hex(entry_value)
    return entry_value == match_value

def TERNARY(key: str, entry_value: Entry.Ternary, match_value: int, width: int):
    val, mask = entry_value.value, entry_value.mask
    curr_entry[key] = hex(val)
    return (val & mask) == (match_value & mask)

def LIST(key: str, entry_value: list[Entry.Ternary], match_value: int, width: int):
    for ev in entry_value:
        if TERNARY(key, ev, match_value, width):
            return True
    return False

def RANGE(key: str, entry_value: Entry.Range, match_value: int, width: int):
    curr_entry[key] = hex(entry_value.low)
    return entry_value.low <= match_value <= entry_value.high

def RANGE_LIST(key: str, entry_value: list[Entry.Range], match_value: int, width: int):
    for ev in entry_value:
        if RANGE(key, ev, match_value, width):
            return True
    return False

def LPM(key: str, entry_value: Entry.LPM, match_value: int, width: int):
    value = entry_value.value
    prefix_len = entry_value.prefix_len
    prefix_len = max(0, min(prefix_len, width))

    if isinstance(value, str):
        value = int(value, 16)
    if isinstance(prefix_len, str):
        prefix_len = int(prefix_len)

    mask = ((1 << prefix_len) - 1) << (width - prefix_len)
    curr_entry[key] = hex(value)
    return (value & mask) == (match_value & mask)

def _winning_criteria_PRIORITY(a: Entry, b: Entry, key):
    return a.priority < b.priority

def _winning_criteria_PREFIX_LEN(a: Entry, b: Entry, key):
    for idx, k in enumerate(key):
        if key[k] == LPM:
            return a.values[idx].prefix_len > b.values[idx].prefix_len
    return False

class Table:
    def __init__(self, key, actions, default_action=NoAction,
                 const_default_action=None, default_params=None,
                 tname=None, sai_table=None):

        if not tname:
            raise ValueError("Each table must have a unique 'tname'")

        self.entries = {}
        self.entry_cnt = 0
        self.default_params = default_params or []
        self.sai_table = sai_table or SaiTable(name=tname)
        self.const_default_action = self.const_default_action_id = None
        self.default_action = self.default_action_id = None
        self.actions = []
        table_objs[tname] = self

        self.key, self.sai_val = {}, {}
        for k, v in key.items():
            if isinstance(v, tuple):
                match_type, meta = v
                self.key[k] = match_type
                self.sai_val[k] = SaiVal(**meta)
            else:
                self.key[k] = v

        has_no_action = False
        for act in actions or []:
            func, hints = act if isinstance(act, tuple) else (act, {})
            self._register_action(func, hints)
            self.actions.append((func, hints))

            # handle @defaultonly or NoAction flags
            if hints.get("annotations") == "@defaultonly" or func is NoAction:
                self.default_action = default_action
                has_no_action = True

        if const_default_action is not None:
            # constant default overrides everything else
            self._register_action(const_default_action)
            self.const_default_action = const_default_action
            self.default_action = self.default_action_id = None
        elif not has_no_action and not any(f is default_action for f, _ in self.actions):
            # ensure NoAction is always registered if not present
            self._register_action(default_action)
            self.actions.append((NoAction, {}))
            self.default_action = default_action
            self.const_default_action = self.const_default_action_id = None

    def _register_action(self, func, hints=None):
        real_func = func.__func__ if isinstance(func, staticmethod) else func
        name = getattr(real_func, "__qualname__", getattr(real_func, "__name__", str(real_func)))
        action_objs.setdefault(name, (func, hints or {}))

    def insert(self, hash, entry):
        if hash in self.entries:
            py_log("warn", f"Entry already exists for hash {hash}")
        else:
            self.entry_cnt += 1
            self.entries[hash] = entry

    def update(self, hash, entry):
        if hash in self.entries:
            self.entries[hash] = entry
        else:
            py_log("warn", f"No entry found to update for hash {hash}")

    def delete(self, hash):
        if hash in self.entries:
            self.entry_cnt -= 1
            del self.entries[hash]
            return RETURN_SUCCESS
        # py_log("warn", f"No entry found to delete for hash {hash}")
        return RETURN_FAILURE

    def apply(self):
        entry = self.__lookup()
        if entry:
            show_matched_entry(curr_entry)

        action = (entry.action if entry else self.default_action or self.const_default_action)
        params = (entry.params if entry else self.default_params)

        py_log("info", f"Table {'HIT' if entry else 'MISS'}")
        py_log("info", f"Action entry: {action.__name__}\n")

        action(*params)
        return {"hit": bool(entry), "action_run": action}

    def __match_entry(self, entry: Entry):
        for idx, (k, match_routine) in enumerate(self.key.items()):
            if idx >= len(entry.values):
                break

            match_value, width = _read_value(k)
            entry_value = entry.values[idx]

            if isinstance(entry_value, str):
                entry_value = int(entry_value, 16)
            if isinstance(match_value, str):
                match_value = int(match_value, 16)

            result = match_routine(k, entry_value, match_value, width)

            if not result:
                # py_log("error", f"Match failed for key[{idx}], returning False.")
                return False

        return True

    def __get_all_matching_entries(self):
        return [e for e in self.entries.values() if self.__match_entry(e)]

    def __get_winning_criteria(self):
        if any(v == LPM for v in self.key.values()):
            return _winning_criteria_PREFIX_LEN
        return _winning_criteria_PRIORITY

    def __select_winning_entry(self, matches):
        crit = self.__get_winning_criteria()
        winner = matches[0]
        for e in matches[1:]:
            if crit(e, winner, self.key):
                winner = e
        return winner

    def __lookup(self):
        py_log("info", "Looking up key:")
        matches = self.__get_all_matching_entries()
        return self.__select_winning_entry(matches) if matches else None
