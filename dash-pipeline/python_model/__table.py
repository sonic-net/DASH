from inspect import *
from __vars import *
from threading import Lock
from dash_api_hints import *

def EXACT(entry_value, match_value, width):
    return entry_value == match_value

def TERNARY(entry_value, match_value, width):
    value = entry_value["value"]
    mask = entry_value["mask"]
    return (value & mask) == (match_value & mask)

def TERNARY_LIST(entry_value, match_value, width):
    for ev in entry_value:
        if TERNARY(ev, match_value, width):
            return True
    return False

def RANGE(entry_value, match_value, width):
    first = entry_value["first"]
    last = entry_value["last"]
    return match_value >= first and match_value <= last

def RANGE_LIST(entry_value, match_value, width):
    for ev in entry_value:
        if RANGE(ev, match_value, width):
            return True
    return False

def LPM(entry_value, match_value, width):
    value = entry_value["value"]
    prefix_len = entry_value["prefix_len"]
    mask = ((1 << prefix_len) - 1) << (width - prefix_len)
    return (value & mask) == (match_value & mask)

def _winning_criteria_PRIORITY(a, b, key):
    return a["priority"] < b["priority"]

def _winning_criteria_PREFIX_LEN(a, b, key):
    lpm_key = None
    for k in key:
        if key[k] == LPM:
            lpm_key = k
            break
    return a[lpm_key]["prefix_len"] > b[lpm_key]["prefix_len"]

class Table:
    def __init__(self, key, actions, default_action=NoAction, default_params=[], api_hints={}):
        self.entries = []
        self.key = key
        self.actions = actions
        self.default_action = default_action
        self.default_params = default_params
        self.api_hints = api_hints
        if (default_action is NoAction) and (NoAction not in self.actions):
            self.actions.append(NoAction)
            self.api_hints[NoAction] = {DEFAULT_ONLY : True}
        self.lock = Lock()

    def insert(self, entry):
        self.lock.acquire()
        self.__insert(entry)
        self.lock.release()

    def apply(self):
        self.lock.acquire()
        res = self.__apply()
        self.lock.release()
        return res

    def delete(self, entry):
        self.lock.acquire()
        self.__delete(entry)
        self.lock.release()

    def __insert(self, entry):
        self.entries.append(entry)

    def __apply(self):
        entry = self.__lookup()
        res = {}
        if entry is None:
            action = self.default_action
            params = self.default_params
            action(*params)
            res["hit"] = False
            res["action_run"] = action
        else:
            action = entry["action"]
            params = entry["params"]
            action(*params)
            res["hit"] = True
            res["action_run"] = action
        return res

    def __delete(self, entry):
        self.entries.remove(entry)

    def __match_entry(self, entry):
        for k in self.key:
            _read_value_res = _read_value(k)
            match_value = _read_value_res[0]
            width = _read_value_res[1]
            match_routine = self.key[k]
            entry_value = entry[k]
            if not match_routine(entry_value, match_value, width):
                return False
        return True

    def __get_all_matching_entries(self):
        matching_entries = []
        for e in self.entries:
            if self.__match_entry(e):
                matching_entries.append(e)
        return matching_entries

    def __get_winning_criteria(self):
        for k in self.key:
            if self.key[k]==TERNARY or self.key[k]==TERNARY_LIST or self.key[k]==RANGE or self.key[k]==RANGE_LIST:
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
