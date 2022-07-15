#!/usr/bin/env python3

try:
    import os
    import json
    import argparse
    import shutil
    from jinja2 import Template, Environment, FileSystemLoader
except ImportError as ie:
    print("Import failed for " + ie.name)
    exit(1)

NAME_TAG = 'name'
TABLES_TAG = 'tables'
BITWIDTH_TAG = 'bitwidth'
ACTIONS_TAG = 'actions'
ACTION_PARAMS_TAG = 'actionParams'
PREAMBLE_TAG = 'preamble'
OTHER_MATCH_TYPE_TAG = 'otherMatchType'
MATCH_TYPE_TAG = 'matchType'
PARAMS_TAG = 'params'
ACTION_REFS_TAG = 'actionRefs'
MATCH_FIELDS_TAG = 'matchFields'
NOACTION = 'NoAction'
STAGES_TAG = 'stages'
PARAM_ACTIONS = 'paramActions'
OBJECT_NAME_TAG = 'objectName'

def get_sai_key_type(key_size, key_header, key_field):
    if key_size == 1:
        return 'bool', "booldata"
    elif key_size <= 8:
        return 'sai_uint8_t', "u8"
    elif key_size == 16 and ('_id' in key_field):
        return 'sai_object_id_t', "u16"
    elif key_size <= 16:
        return 'sai_uint16_t', "u16"
    elif key_size == 32 and ('ip_addr_family' in key_field):
        return 'sai_ip_addr_family_t', "u32"
    elif key_size == 32 and ('addr' in key_field or 'ip' in key_header):
        return 'sai_ip_address_t', "ipaddr"
    elif key_size == 32 and ('_id' in key_field):
        return 'sai_object_id_t', "u32"
    elif key_size <= 32:
        return 'sai_uint32_t', "u32"
    elif key_size == 48 and ('addr' in key_field or 'mac' in key_header):
        return 'sai_mac_t', "mac"
    elif key_size <= 64:
        return 'sai_uint64_t', "u64"
    elif key_size == 128:
        return 'sai_ip_address_t', "ipaddr"
    else:
        raise ValueError(f'key_size={key_size} is not supported')


def get_sai_lpm_type(key_size, key_header, key_field):
    if key_size == 32 and ('addr' in key_field or 'ip' in key_header):
        return 'sai_ip_prefix_t', 'ipPrefix'
    elif key_size == 128 and ('addr' in key_field or 'ip' in key_header):
        return 'sai_ip_prefix_t', 'ipPrefix'
    raise ValueError(f'key_size={key_size}, key_header={key_header}, and key_field={key_field} is not supported')


def get_sai_list_type(key_size, key_header, key_field):
    if key_size <= 8:
        return 'sai_u8_list_t', "u8list"
    elif key_size <= 16:
        return 'sai_u16_list_t', "u16list"
    elif key_size == 32 and ('addr' in key_field or 'ip' in key_header):
        return 'sai_ip_address_list_t', "ipaddrlist"
    elif key_size <= 32:
        return 'sai_u32_list_t', "u32list"
    elif key_size <= 64:
        ValueError(f'sai_u64_list_t is not supported')
        return 'sai_u64_list_t', "no mapping"
    raise ValueError(f'key_size={key_size} is not supported')

def get_sai_range_list_type(key_size, key_header, key_field):
    if key_size <= 8:
        return 'sai_u8_range_list_t', 'u8rangelist'
    elif key_size <= 16:
        return 'sai_u16_range_list_t', 'u16rangelist'
    elif key_size == 32 and ('addr' in key_field or 'ip' in key_header):
        return 'sai_ipaddr_range_list_t', 'ipaddrrangelist'
    elif key_size <= 32:
        return 'sai_u32_range_list_t',  'u32rangelist'
    elif key_size <= 64:
        return 'sai_u64_range_list_t',  'u64rangelist'
    raise ValueError(f'key_size={key_size} is not supported')


def get_sai_key_data(key):
    sai_key_data = dict()
    sai_key_data['id'] =  key['id']
    full_key_name, sai_key_name = key[NAME_TAG].split(':')
    key_tuple = full_key_name.split('.')
    if len(key_tuple) == 3:
        key_struct, key_header, key_field = key_tuple
    else:
        key_header, key_field = key_tuple
    sai_key_data['sai_key_name'] = sai_key_name

    key_size = key[BITWIDTH_TAG]

    if OTHER_MATCH_TYPE_TAG in key:
        sai_key_data['match_type'] =  key[OTHER_MATCH_TYPE_TAG].lower()
    elif MATCH_TYPE_TAG in key:
        sai_key_data['match_type'] =  key[MATCH_TYPE_TAG].lower()
    else:
        raise ValueError(f'No valid match tag found')

    if sai_key_data['match_type'] == 'exact' or  sai_key_data['match_type'] == 'optional':
        sai_key_data['sai_key_type'], sai_key_data['sai_key_field'] = get_sai_key_type(key_size, key_header, key_field)
    elif sai_key_data['match_type'] == 'lpm':
        sai_key_data['sai_lpm_type'], sai_key_data['sai_lpm_field'] = get_sai_lpm_type(key_size, key_header, key_field)
    elif sai_key_data['match_type'] == 'list':
        sai_key_data['sai_list_type'], sai_key_data['sai_list_field']  = get_sai_list_type(key_size, key_header, key_field)
    elif sai_key_data['match_type'] == 'range_list':
        sai_key_data['sai_range_list_type'], sai_key_data['sai_range_list_field'] = get_sai_range_list_type(key_size, key_header, key_field)
    else:
        raise ValueError(f"match_type={sai_key_data['match_type']} is not supported")

    sai_key_data['bitwidth'] = key_size
    return sai_key_data


def extract_action_data(program):
    action_data = {}
    for action in program[ACTIONS_TAG]:
        preable = action[PREAMBLE_TAG]
        id = preable['id']
        name = preable[NAME_TAG].split('.')[-1]
        params = []
        if PARAMS_TAG in action:
            for p in action[PARAMS_TAG]:
                param = dict()
                param['id'] = p['id']
                param[NAME_TAG] = p[NAME_TAG]
                param['type'], param['field'] = get_sai_key_type(int(p[BITWIDTH_TAG]), p[NAME_TAG], p[NAME_TAG])
                param['bitwidth'] = p[BITWIDTH_TAG]
                params.append(param)
        action_data[id] = {'id': id, NAME_TAG: name, PARAMS_TAG: params}
    return action_data


def table_with_counters(program, table_id):
    for counter in program['directCounters']:
        if counter['directTableId'] == table_id:
            return 'true'
    return 'false'

def fill_action_params(table_params, param_names, action):
    for param in action[PARAMS_TAG]:
        # skip v4/v6 selector
        if 'v4_or_v6' in param[NAME_TAG]:
           continue
        if param[NAME_TAG] not in param_names:
            param_names.append(param[NAME_TAG])
            param[PARAM_ACTIONS] = [action[NAME_TAG]]
            table_params.append(param)
        else:
            # ensure that same param passed to multiple actions of the
            # same P4 table does not generate more than 1 SAI attribute
            for tbl_param in table_params:
                if tbl_param[NAME_TAG] == param[NAME_TAG]:
                    tbl_param[PARAM_ACTIONS].append(action[NAME_TAG])

def generate_sai_apis(program, ignore_tables):
    sai_apis = []
    table_names = []
    all_actions = extract_action_data(program)
    tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
    for table in tables:
        sai_table_data = dict()
        sai_table_data['keys'] = []
        sai_table_data[ACTIONS_TAG] = []
        sai_table_data[STAGES_TAG] = []
        sai_table_data[ACTION_PARAMS_TAG] = []

        table_control, table_name = table[PREAMBLE_TAG][NAME_TAG].split('.', 1)
        if table_name in ignore_tables:
            continue

        table_name, api_name = table_name.split('|')
        if '.' in table_name:
            sai_table_data[NAME_TAG] = table_name.split('.')[-1]
        else:
            sai_table_data[NAME_TAG] = table_name
        sai_table_data['id'] =  table[PREAMBLE_TAG]['id']
        sai_table_data['with_counters'] = table_with_counters(program, sai_table_data['id'])

        # chechk if table belongs to a group
        is_new_group = True
        if ':' in table_name:
            stage, group_name = table_name.split(':')
            table_name = group_name
            stage = stage.replace('.' , '_')
            for sai_api in sai_apis:
                for sai_table in sai_api[TABLES_TAG]:
                    if sai_table['name'] == table_name:
                        sai_table[STAGES_TAG].append(stage)
                        is_new_group = False
                        break
            if is_new_group:
                sai_table_data[NAME_TAG] = table_name
                sai_table_data[STAGES_TAG].append(stage)
            else:
                continue

        for key in table[MATCH_FIELDS_TAG]:
            # skip v4/v6 selector
            if 'v4_or_v6' in key[NAME_TAG]:
                continue
            sai_table_data['keys'].append(get_sai_key_data(key))

        param_names = []
        for action in table[ACTION_REFS_TAG]:
            action_id = action["id"]
            if all_actions[action_id][NAME_TAG] != NOACTION:
                fill_action_params(sai_table_data[ACTION_PARAMS_TAG], param_names, all_actions[action_id])
                sai_table_data[ACTIONS_TAG].append(all_actions[action_id])

        if len(sai_table_data['keys']) == 1 and sai_table_data['keys'][0]['sai_key_name'].endswith(table_name.split('.')[-1] + '_id'):
            sai_table_data['is_object'] = 'true'
        elif len(sai_table_data['keys']) > 5:
            sai_table_data['is_object'] = 'true'
        else:
            sai_table_data['is_object'] = 'false'
            sai_table_data['name'] = sai_table_data['name'] + '_entry'

        table_names.append(sai_table_data[NAME_TAG])
        is_new_api = True
        for sai_api in sai_apis:
            if sai_api['app_name'] == api_name:
                sai_api[TABLES_TAG].append(sai_table_data)
                is_new_api = False
                break

        if is_new_api:
            new_api = dict()
            new_api['app_name'] = api_name
            new_api[TABLES_TAG] = [sai_table_data]
            sai_apis.append(new_api)

    return sai_apis, table_names

def write_sai_impl_files(sai_api):
    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    sai_impl_tm = env.get_template('/templates/saiapi.cpp.j2')
    sai_impl_str = sai_impl_tm.render(tables = sai_api[TABLES_TAG], app_name = sai_api['app_name'])

    with open('./lib/sai' + sai_api['app_name'].replace('_', '') + '.cpp', 'w') as o:
        o.write(sai_impl_str)

def write_sai_makefile(sai_api_name_list):
    env = Environment(loader=FileSystemLoader('.'))
    makefile_tm = env.get_template('/templates/Makefile.j2')
    makefile_str = makefile_tm.render(api_names = sai_api_name_list)

    with open('./lib/Makefile', 'w') as o:
        o.write(makefile_str)

    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    sai_impl_tm = env.get_template('/templates/utils.cpp.j2')
    sai_impl_str = sai_impl_tm.render(tables = sai_api[TABLES_TAG], app_name = sai_api['app_name'])

    with open('./lib/utils.cpp', 'w') as o:
        o.write(sai_impl_str)

    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    sai_impl_tm = env.get_template('/templates/utils.h.j2')
    sai_impl_str = sai_impl_tm.render(tables = sai_api[TABLES_TAG], app_name = sai_api['app_name'])

    with open('./lib/utils.h', 'w') as o:
        o.write(sai_impl_str)


def write_sai_files(sai_api):
    # The main file
    with open('templates/saiapi.h.j2', 'r') as sai_header_tm_file:
        sai_header_tm_str = sai_header_tm_file.read()

    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    sai_header_tm = env.get_template('templates/saiapi.h.j2')
    sai_header_str = sai_header_tm.render(sai_api = sai_api)

    with open('./SAI/experimental/saiexperimental' + sai_api['app_name'].replace('_', '') + '.h', 'w') as o:
        o.write(sai_header_str)

    # The SAI Extensions
    with open('./SAI/experimental/saiextensions.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental APIs above this line' in line:
            new_line = '    SAI_API_' + sai_api['app_name'].upper() + ',\n'
            if new_line not in lines:
                new_lines.append(new_line + '\n')
        if 'new experimental object type includes' in line:
            new_lines.append(line)
            new_line = '#include "saiexperimental' + sai_api['app_name'].replace('_', '') + '.h"\n'
            if new_line not in lines:
                new_lines.append(new_line)
            continue

        new_lines.append(line)

    with open('./SAI/experimental/saiextensions.h', 'w') as f:
        f.write(''.join(new_lines))

    # The SAI Type Extensions
    with open('./SAI/experimental/saitypesextensions.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental object types above this line' in line:
            for table in sai_api[TABLES_TAG]:
                new_line = '    SAI_OBJECT_TYPE_' + table[NAME_TAG].upper() + ',\n'
                if new_line not in lines:
                    new_lines.append(new_line + '\n')

        new_lines.append(line)

    with open('./SAI/experimental/saitypesextensions.h', 'w') as f:
        f.write(''.join(new_lines))

    # The SAI object struct for entries
    with open('./SAI/inc/saiobject.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental entries above this line' in line:
            for table in sai_api[TABLES_TAG]:
                if table['is_object'] == 'false':
                    new_line = '    sai_' + table[NAME_TAG] + '_t ' + table[NAME_TAG] + ';\n'
                    if new_line not in lines:
                        new_lines.append('    /** @validonly object_type == SAI_OBJECT_TYPE_' + table[NAME_TAG].upper() + ' */\n')
                        new_lines.append(new_line + '\n')
        if 'new experimental object type includes' in line:
            new_lines.append(line)
            new_line = '#include "../experimental/saiexperimental' + sai_api['app_name'].replace('_', '') + '.h"\n'
            if new_line not in lines:
                new_lines.append(new_line)
            continue

        new_lines.append(line)

    with open('./SAI/inc/saiobject.h', 'w') as f:
        f.write(''.join(new_lines))



# CLI
parser = argparse.ArgumentParser(description='P4 SAI API generator')
parser.add_argument('filepath', type=str, help='Path to P4 program RUNTIME JSON file')
parser.add_argument('apiname', type=str, help='Name of the new SAI API')
parser.add_argument('--print-sai-lib', type=bool)
parser.add_argument('--ignore-tables', type=str, default='', help='Comma separated list of tables to ignore')
args = parser.parse_args()

if not os.path.isfile(args.filepath):
    print('File ' + args.filepath + ' does not exist')
    exit(1)

# 
# Get SAI dictionary from P4 dictionary
print("Generating SAI API...")
with open(args.filepath) as json_program_file:
    json_program = json.load(json_program_file)

sai_apis, all_table_names = generate_sai_apis(json_program, args.ignore_tables.split(','))

sai_api_name_list = []
for sai_api in sai_apis:
    # Update object name reference for action params
    for table in sai_api[TABLES_TAG]:
        for param in table[ACTION_PARAMS_TAG]:
            if param['type'] == 'sai_object_id_t':
                table_ref = param[NAME_TAG][:-len("_id")]
                for table_name in all_table_names:
                    if table_ref.endswith(table_name):
                        param[OBJECT_NAME_TAG] = table_name
    # Update object name reference for keys
    for table in sai_api[TABLES_TAG]:
        for key in table['keys']:
            if 'sai_key_type' in key:
                if key['sai_key_type'] == 'sai_object_id_t':
                    table_ref = key['sai_key_name'][:-len("_id")]
                    for table_name in all_table_names:
                        if table_ref.endswith(table_name):
                            key[OBJECT_NAME_TAG] = table_name
    # Write SAI dictionary into SAI API headers
    write_sai_files(sai_api)
    write_sai_impl_files(sai_api)
    sai_api_name_list.append(sai_api['app_name'].replace('_', ''))

write_sai_makefile(sai_api_name_list)

if args.print_sai_lib:
    print(json.dumps(sai_api, indent=2))
