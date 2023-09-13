from __main import *
from __id_map import *
from __sai_keys import *
import sys
from __jsonize import *

def _get_sai_key_name(api_hints, k, default):
    sai_key_name: str
    try:
        sai_key_name = api_hints[k][SAI_KEY_NAME]
    except:
        sai_key_name = default
    return sai_key_name

def _read_width(k):
    tokens = k.split(".")
    container_type = type(globals()[tokens[0]])
    var_name = tokens[1]
    for token in tokens[2:]:
        container_type = get_annotations(container_type)[var_name]
        var_name = token
    return (get_annotations(container_type)[var_name].__metadata__)[0]

def _get_str_annos_for_key(api_hints, k):
    key_hints = api_hints.get(k, None)
    if key_hints is None:
        return None
    str_annos = {}

    for k in key_hints:
        if k != SAI_KEY_NAME:
            str_annos[k] = key_hints[k]

    if len(str_annos) > 0:
        return str_annos
    else:
        return None

def _get_str_annos_for_table(table):
    str_annos = {}
    for k in table.api_hints:
        if (k != API_NAME) and (not isfunction(k)) and (not(k in table.key)):
            str_annos[k] = table.api_hints[k]
    if len(str_annos) > 0:
        return str_annos
    else:
        return None

def _make_str_annos_node(str_annos):
    kvPairs_node = []
    for s_a in str_annos:
        s_a_node = {}
        s_a_node["key"] = s_a
        s_a_node["value"] = {"stringValue" : str_annos[s_a]}
        kvPairs_node.append(s_a_node)
    str_annos_node = [{
        "name"       : "Sai",
        "kvPairList" : {"kvPairs" : kvPairs_node}
    }]
    return str_annos_node

def make_table_node(table: Table, table_name):
    table_node = {}

    preamble_node = {}
    preamble_node["id"] = generate_id(table)
    preamble_node["name"] = "." + table_name + "|" + table.api_hints.get(API_NAME, "dash_" + table_name)
    str_annos = _get_str_annos_for_table(table)
    if str_annos is not None:
        preamble_node["structuredAnnotations"] = _make_str_annos_node(str_annos)
    table_node["preamble"] = preamble_node

    matchFields_node = []
    match_field_id = 1
    for k in table.key:
        match_field_node = {}
        match_field_node["id"] = match_field_id
        match_field_id += 1
        match_field_node["name"] = k + ":" + _get_sai_key_name(table.api_hints, k, k.split(".")[-1])
        match_field_node["bitwidth"] = _read_width(k)
        match_field_node["matchType"] = table.key[k].__name__
        mf_str_annos = _get_str_annos_for_key(table.api_hints, k)
        if mf_str_annos is not None:
            match_field_node["structuredAnnotations"] = _make_str_annos_node(mf_str_annos)
        matchFields_node.append(match_field_node)
    table_node["matchFields"] = matchFields_node

    actionRefs_node = []
    for action in table.actions:
        actionRef_node = {}
        actionRef_node["id"] = generate_id(action)
        if action in table.api_hints:
            actionRef_node["annotations"] = ["@defaultonly"]
            actionRef_node["scope"] = "DEFAULT_ONLY"
        actionRefs_node.append(actionRef_node)
    table_node["actionRefs"] = actionRefs_node
    return table_node

def make_action_node(action, id):
    action_node = {}

    preamble_node = {}
    preamble_node["id"] = id
    preamble_node["name"] = action.__name__
    action_node["preamble"] = preamble_node

    params_node = []
    param_id = 1
    annotations = get_annotations(action)
    for k in annotations:
        param_node = {}
        param_node["id"] = param_id
        param_id += 1
        param_node["name"] = k
        param_node["bitwidth"] = annotations[k].__metadata__[0]
        if len(annotations[k].__metadata__) > 1:
            str_annos = annotations[k].__metadata__[1]
            str_annos_node = _make_str_annos_node(str_annos)
            param_node["structuredAnnotations"] = str_annos_node
        params_node.append(param_node)
    if len(params_node) > 0:
        action_node["params"] = params_node
    return action_node

def get_dash_enum_members(e):
    members = []
    for i in getmembers(e):
        if not i[0].startswith('_'):
            members.append(i)
    members.sort(key=lambda e : e[1])
    return members

def make_enum_node(enum):
    enum_node = {}
    enum_node["underlyingType"] = {"bitwidth": 16}

    members_node = []
    members = get_dash_enum_members(enum)
    for m in members:
        members_node.append({
            "name"  : m[0],
            "value" : m[1]
        })
    enum_node["members"] = members_node
    return enum_node

def get_dash_enum_list():
    class_list = getmembers(sys.modules[__name__], isclass)
    dash_enum_list = []
    for item in class_list:
        if issubclass(item[1], dash_enum) and item[1] != dash_enum:
            dash_enum_list.append(item[1])
    return dash_enum_list

def make_p4info(ignore_tables):
    p4info = {}

    tables_node = []
    global_vars = globals()
    for k in global_vars:
        if type(global_vars[k]) == Table:
            table = global_vars[k]
            table_name = k
            if not (table in ignore_tables):
                tables_node.append(make_table_node(table, table_name))
    p4info["tables"] = tables_node

    actions_node = []
    for k in id_map:
        if isfunction(id_map[k]):
            action = id_map[k]
            action_id = k
            actions_node.append(make_action_node(action, action_id))
    p4info["actions"] = actions_node

    serializableEnums_node = {}
    dash_enum_list = get_dash_enum_list()
    for e in dash_enum_list:
        serializableEnums_node[e.__name__] = make_enum_node(e)
    p4info["typeInfo"] = {"serializableEnums" : serializableEnums_node}

    directCounters_node = []
    for table_node in p4info["tables"]:
        table_id = table_node["preamble"]["id"]
        if id_map[table_id].per_entry_stats:
            directCounters_node.append({"directTableId": table_id})
    p4info["directCounters"] = directCounters_node

    return p4info


p4info = make_p4info([flows, appliance])


jsonize("my_p4info.json", p4info)


