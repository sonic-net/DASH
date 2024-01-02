from inspect import *
from __vars import *
from __sai_keys import *

class Entry:
    class Ternary:
        value : int
        mask  : int

    class LPM:
        value : int
        prefix_len : int

    class Range:
        first : int
        last  : int

    values   : list
    action   : function
    params   : list[int]
    priority : int

def EXACT(entry_value: int, match_value: int, width: int):
    return entry_value == match_value

def TERNARY(entry_value: Entry.Ternary, match_value: int, width: int):
    value = entry_value.value
    mask = entry_value.mask
    return (value & mask) == (match_value & mask)

def LIST(entry_value: list[Entry.Ternary], match_value: int, width: int):
    for ev in entry_value:
        if TERNARY(ev, match_value, width):
            return True
    return False

def RANGE(entry_value: Entry.Range, match_value: int, width: int):
    first = entry_value.first
    last = entry_value.last
    return match_value >= first and match_value <= last

def RANGE_LIST(entry_value: list[Entry.Range], match_value, width):
    for ev in entry_value:
        if RANGE(ev, match_value, width):
            return True
    return False

def LPM(entry_value: Entry.LPM, match_value: int, width: int):
    value = entry_value.value
    prefix_len = entry_value.prefix_len
    mask = ((1 << prefix_len) - 1) << (width - prefix_len)
    return (value & mask) == (match_value & mask)

def _winning_criteria_PRIORITY(a: Entry, b: Entry, key):
    return a.priority < b.priority

def _winning_criteria_PREFIX_LEN(a: Entry, b: Entry, key):
    idx = 0
    for k in key:
        if key[k] == LPM:
            break
        idx = idx + 1
    return a.values[idx].prefix_len > b.values[idx].prefix_len

class Table:
    def __init__(self, key, actions, default_action=NoAction, default_params=[], per_entry_stats = False, api_name=None, is_object=None):
        self.entries = []
        self.key = key
        self.actions = actions
        self.default_action = default_action
        self.default_params = default_params
        self.per_entry_stats = per_entry_stats
        if (default_action is NoAction) and (NoAction not in self.actions):
            self.actions.append((NoAction, {DEFAULT_ONLY : True}))
        self.api_hints = self.__extract_api_hints(api_name, is_object)

    def insert(self, entry):
        self.entries.append(entry)

    def apply(self):
        entry = self.__lookup()
        res = {}
        if entry is None:
            action = self.default_action
            params = self.default_params
            action(*params)
            res["hit"] = False
            res["action_run"] = action
        else:
            action = entry.action
            params = entry.params
            action(*params)
            res["hit"] = True
            res["action_run"] = action
        return res

    def delete(self, entry):
        self.entries.remove(entry)

    def __match_entry(self, entry: Entry):
        idx = 0
        for k in self.key:
            _read_value_res = _read_value(k)
            match_value = _read_value_res[0]
            width = _read_value_res[1]
            match_routine = self.key[k]
            entry_value = entry.values[idx]
            if not match_routine(entry_value, match_value, width):
                return False
            idx = idx + 1
        return True

    def __get_all_matching_entries(self):
        matching_entries = []
        for e in self.entries:
            if self.__match_entry(e):
                matching_entries.append(e)
        return matching_entries

    def __get_winning_criteria(self):
        for k in self.key:
            if self.key[k]==TERNARY or self.key[k]==LIST or self.key[k]==RANGE or self.key[k]==RANGE_LIST:
                return _winning_criteria_PRIORITY
        for k in self.key:
            if self.key[k]==LPM:
                return _winning_criteria_PREFIX_LEN
        return None

    def __select_winning_entry(self, matching_entries):
        winning_criteria = self.__get_winning_criteria()
        curr_winner = matching_entries[0]
        for e in matching_entries[1:]:
            if winning_criteria(e, curr_winner, self.key):
                curr_winner = e
        return curr_winner

    def __lookup(self):
        matching_entries = self.__get_all_matching_entries()
        if not matching_entries:
            return None
        else:
            return self.__select_winning_entry(matching_entries)

    def __extract_api_hints(self, api_name, is_object):
        api_hints = {}
        for k in self.key:
            if type(self.key[k]) == tuple:
                api_hints[k] = self.key[k][1]
                self.key[k] = self.key[k][0]
        for idx, action in enumerate(self.actions):
            if type(action) == tuple:
                api_hints[action[0]] = action[1]
                self.actions[idx] = action[0]
        if api_name:
            api_hints[API_NAME] = api_name
        if is_object:
            api_hints[ISOBJECT] = is_object
        return api_hints

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
