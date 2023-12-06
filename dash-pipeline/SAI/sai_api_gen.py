#!/usr/bin/env python3

try:
    import os
    import json
    import argparse
    import shutil
    import copy
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
STAGE_TAG = 'stage'
PARAM_ACTIONS = 'paramActions'
OBJECT_NAME_TAG = 'objectName'
SCOPE_TAG = 'scope'
TYPE_INFO_TAG = 'typeInfo'
SERIALIZABLE_ENUMS_TAG = 'serializableEnums'
MEMBERS_TAG = 'members'
STRUCTURED_ANNOTATIONS_TAG = 'structuredAnnotations'
KV_PAIRS_TAG = 'kvPairs'
KV_PAIR_LIST_TAG = 'kvPairList'
SAI_TAG = 'Sai'

sai_type_to_field = {
    'bool': 'booldata',
    'sai_uint8_t': 'u8',
    'sai_object_id_t': 'u16',
    'sai_uint16_t': 'u16',
    'sai_ip_address_t': 'ipaddr',
    'sai_ip_addr_family_t': 'u32',
    'sai_uint32_t': 'u32',
    'sai_uint64_t': 'u64',
    'sai_mac_t': 'mac',
    'sai_ip_prefix_list_t': 'ipprefixlist'
}

#
# SAI parser decorators
#
def sai_parser_from_p4rt(cls):
    @staticmethod
    def create(p4rt_value, *args, **kwargs):
        sai_object = cls()
        sai_object.parse(p4rt_value, *args, **kwargs)
        return sai_object

    def parse(self, p4rt_value, *args, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
            kwargs.pop('name')

        self.parse_preamble_if_exists(p4rt_value)
        self.parse_p4rt(p4rt_value, *args, **kwargs)

        return

    setattr(cls, "from_p4rt", create)
    setattr(cls, "parse", parse)

    return cls

#
# Parsed SAI objects and parsers
#
class SAIType:
    @staticmethod
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

    @staticmethod
    def get_sai_lpm_type(key_size, key_header, key_field):
        if key_size == 32 and ('addr' in key_field or 'ip' in key_header):
            return 'sai_ip_prefix_t', 'ipPrefix'
        elif key_size == 128 and ('addr' in key_field or 'ip' in key_header):
            return 'sai_ip_prefix_t', 'ipPrefix'
        raise ValueError(f'key_size={key_size}, key_header={key_header}, and key_field={key_field} is not supported')

    @staticmethod
    def get_sai_list_type(key_size, key_header, key_field):
        if key_size <= 8:
            return 'sai_u8_list_t', "u8list"
        elif key_size <= 16:
            return 'sai_u16_list_t', "u16list"
        elif key_size == 32 and ('addr' in key_field or 'ip' in key_header):
            return 'sai_ip_prefix_list_t', "ipprefixlist"
        elif key_size <= 32:
            return 'sai_u32_list_t', "u32list"
        elif key_size == 128 and ('addr' in key_field or 'ip' in key_header):
            return 'sai_ip_prefix_list_t', "ipprefixlist"
        else:
            raise ValueError(f'key_size={key_size} is not supported')

    @staticmethod
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
        else:
            raise ValueError(f'key_size={key_size} is not supported')

class SAIObject:
    def __init__(self):
        # Properties from P4Runtime preamble
        self.name = ''
        self.id = 0
        self.alias = ''

        # Properties from SAI annotations
        self.type = None
        self.isresourcetype = None
        self.isreadonly = None
        self.objectName = None
        self.skipattr = None
        self.field = None

    def parse_preamble_if_exists(self, p4rt_object):
        '''
        This method parses the P4Runtime preamble object and populates the SAI object.

        Example P4Runtime preamble object:

            "preamble": {
                "id": 33810473,
                "name": "dash_ingress.outbound.acl.stage1:dash_acl_rule|dash_acl",
                "alias": "outbound.acl.stage1:dash_acl_rule|dash_acl"
            },
        '''
        if PREAMBLE_TAG in p4rt_object:
            preamble = p4rt_object[PREAMBLE_TAG]
            self.id = preamble['id']
            self.name = preamble['name']
            self.alias = preamble['alias']

    def _parse_sai_object_annotation(self, p4rt_anno_list):
        '''
        This method parses the SAI annotations and populates the SAI object.
        
        Example SAI annotations:

            {
                "name": "Sai",
                "kvPairList": {
                    "kvPairs": [
                        { "key": "type", "value": { "stringValue": "sai_ip_addr_family_t" } },
                        { "key": "isresourcetype", "value": { "stringValue": "true" } }
                    ]
                }
            }
        '''
        for anno in p4rt_anno_list[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if kv['key'] == 'type':
                        self.type = kv['value']['stringValue']
                    elif kv['key'] == 'isresourcetype':
                        self.isresourcetype = kv['value']['stringValue']
                    elif kv['key'] == 'isreadonly':
                        self.isreadonly = kv['value']['stringValue']
                    elif kv['key'] == 'objects':
                        self.objectName = kv['value']['stringValue']
                    elif kv['key'] == 'skipattr':
                        self.skipattr = kv['value']['stringValue']
                    else:
                        raise ValueError("Unknown attr annotation " + kv['key'])

        self.field = sai_type_to_field[self.type]

@sai_parser_from_p4rt
class SAIEnumMember(SAIObject):
    '''
    This class represents a single SAI enum member and provides parser from the P4Runtime enum member object
    '''
    def __init__(self):
        super().__init__()
        self.sai_name = ""
        self.p4rt_value = ""

    def parse_p4rt(self, p4rt_member):
        '''
        This method parses the P4Runtime enum member object and populates the SAI enum member object.

        Example P4Runtime enum member object:

            { "name": "INVALID", "value": "AAA=" }
        '''
        self.sai_name = self.name
        self.p4rt_value = p4rt_member

@sai_parser_from_p4rt
class SAIEnum(SAIObject):
    '''
    This class represents a single SAI enum and provides parser from the P4Runtime enum object
    '''
    def __init__(self):
        super().__init__()
        self.members = []
        
    def parse_p4rt(self, p4rt_enum):
        '''
        This method parses the P4Runtime enum object and populates the SAI enum object.
        
        Example P4Runtime enum object:

            "dash_encapsulation_t": {
                "underlyingType": { "bitwidth": 16 },
                "members": [
                    { "name": "INVALID", "value": "AAA=" },
                    { "name": "VXLAN", "value": "AAE=" },
                    { "name": "NVGRE", "value": "AAI=" }
                ]
            }
        '''
        print("Parsing enum: " + self.name)
        self.name = self.name[:-2]
        self.members = [SAIEnumMember.from_p4rt(enum_member['value'], name = enum_member['name']) for enum_member in p4rt_enum[MEMBERS_TAG]]

@sai_parser_from_p4rt
class SAIAPITableKey(SAIObject):
    '''
    This class represents a single SAI API table key and provides parser from the P4Runtime table key object.
    '''
    def __init__(self):
        super().__init__()
        self.sai_key_name = ""
        self.match_type = ""
        self.type = ""
        self.field = ""
        self.bitwidth = 0
        self.v4_or_v6_id = 0

    def parse_p4rt(self, p4rt_table_key, v4_or_v6_key_ids):
        '''
        This method parses the P4Runtime table key object and populates the SAI API table key object.

        Example P4Runtime table key object:

            {
                "id": 1,
                "name": "meta.vnet_id:vnet_id",
                "bitwidth": 16,
                "matchType": "EXACT"
            },
            {
                "id": 2,
                "name": "hdr.ipv4.src_addr:sip",
                "bitwidth": 32,
                "matchType": "EXACT"
            }
        '''

        print("Parsing table p4rt_table_key: " + self.name)

        self.id =  p4rt_table_key['id']
        full_key_name, self.sai_key_name = p4rt_table_key[NAME_TAG].split(':')

        key_tuple = full_key_name.split('.')
        if len(key_tuple) == 3:
            key_struct, key_header, key_field = key_tuple
        else:
            key_header, key_field = key_tuple

        self.bitwidth = p4rt_table_key[BITWIDTH_TAG]

        if OTHER_MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type =  p4rt_table_key[OTHER_MATCH_TYPE_TAG].lower()
        elif MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type =  p4rt_table_key[MATCH_TYPE_TAG].lower()
        else:
            raise ValueError(f'No valid match tag found')

        if STRUCTURED_ANNOTATIONS_TAG in p4rt_table_key:
            self._parse_sai_object_annotation(p4rt_table_key)
        else:
            if self.match_type == 'exact' or  self.match_type == 'optional' or self.match_type == 'ternary':
                self.type, self.field = SAIType.get_sai_key_type(self.bitwidth, key_header, key_field)
            elif self.match_type == 'lpm':
                self.type, self.field = SAIType.get_sai_lpm_type(self.bitwidth, key_header, key_field)
            elif self.match_type == 'list':
                self.type, self.field  = SAIType.get_sai_list_type(self.bitwidth, key_header, key_field)
            elif self.match_type == 'range_list':
                self.type, self.field = SAIType.get_sai_range_list_type(self.bitwidth, key_header, key_field)
            else:
                raise ValueError(f"match_type={self.match_type} is not supported")

        # If v4_or_v6 key is present, save its id.
        if "is_" + self.sai_key_name + "_v4_or_v6" in v4_or_v6_key_ids:
            self.v4_or_v6_id = p4rt_table_key['id']

        return

@sai_parser_from_p4rt
class SAIAPITableData(SAIObject):
    '''
    This class represents a single SAI API set and provides parser from the P4Runtime table object
    '''
    def __init__(self):
        super().__init__()
        self.ignored = False
        self.api_name = ""
        self.ipaddr_family_attr = 'false'
        self.keys = []
        self.actions = []
        self.action_params = []
        self.with_counters = 'false'
        self.stage = None
        self.is_object = None

    def parse_p4rt(self, p4rt_table, program, all_actions, ignore_tables):
        table_control, self.name = p4rt_table[PREAMBLE_TAG][NAME_TAG].split('.', 1)

        self.__parse_sai_table_annotations(p4rt_table[PREAMBLE_TAG])
        if self.ignored:
            ignore_tables.append(self.name)
        if self.name in ignore_tables:
            return

        print("Found table: " + self.name)

        self.name, self.api_name = self.name.split('|')
        if '.' in self.name:
            self.name = self.name.split('.')[-1]

        if ':' in self.name:
            stage, group_name = self.name.split(':')
            self.name = group_name
            self.stage = stage.replace('.' , '_')

        self.with_counters = self.__table_with_counters(program)

        self.__parse_table_keys(p4rt_table)

        param_names = []
        for action in p4rt_table[ACTION_REFS_TAG]:
            action_id = action["id"]
            if all_actions[action_id][NAME_TAG] != NOACTION and not (SCOPE_TAG in action and action[SCOPE_TAG] == 'DEFAULT_ONLY'):
                fill_action_params(self.action_params, param_names, all_actions[action_id])
                self.actions.append(all_actions[action_id])

        if self.is_object == None:
            if len(self.keys) == 1 and self.keys[0].sai_key_name.endswith(self.name.split('.')[-1] + '_id'):
                self.is_object = 'true'
            elif len(self.keys) > 5:
                self.is_object = 'true'
            else:
                self.is_object = 'false'
                self.name = self.name + '_entry'

        return

    def __parse_sai_table_annotations(self, p4rt_table_preamble):
        if STRUCTURED_ANNOTATIONS_TAG not in p4rt_table_preamble:
            return

        for anno in p4rt_table_preamble[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if kv['key'] == 'isobject':
                        self.is_object = kv['value']['stringValue']
                    if kv['key'] == 'ignoretable':
                        self.ignored = True

        return

    def __table_with_counters(self, program):
        for counter in program['directCounters']:
            if counter['directTableId'] == self.id:
                return 'true'
        return 'false'

    def __parse_table_keys(self, p4rt_table):
        v4_or_v6_key_ids = dict()
        for p4rt_table_key in p4rt_table[MATCH_FIELDS_TAG]:
            if 'v4_or_v6' in p4rt_table_key[NAME_TAG]:
                _, v4_or_v6_key_name = p4rt_table_key[NAME_TAG].split(':')
                v4_or_v6_key_ids[v4_or_v6_key_name] = p4rt_table_key['id']

        for p4rt_table_key in p4rt_table[MATCH_FIELDS_TAG]:
            table_key = SAIAPITableKey.from_p4rt(p4rt_table_key, v4_or_v6_key_ids)
            self.keys.append(table_key)

        for p4rt_table_key in self.keys:
            if (p4rt_table_key.match_type == 'exact' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'ternary' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'lpm' and p4rt_table_key.type == 'sai_ip_prefix_t') or \
                (p4rt_table_key.match_type == 'list' and p4rt_table_key.type == 'sai_ip_prefix_list_t'):
                    self.ipaddr_family_attr = 'true'

        return

class DASHAPISet:
    '''
    This class holds all parsed SAI API info for a specific API set, such as routing or CA-PA mapping.
    '''
    def __init__(self, api_name):
        self.app_name = api_name
        self.tables = []
    
    def add_table(self, table):
        self.tables.append(table)

@sai_parser_from_p4rt
class DASHSAIExtensions(SAIObject):
    '''
    This class holds all parsed SAI APIs and provides parser for the generated p4 runtime json file
    '''
    def __init__(self):
        super().__init__()
        self.sai_enums = []
        self.sai_apis = []

    @staticmethod
    def from_p4rt_file(p4rt_json_file_path, ignore_tables):
        print("Parsing SAI APIs BMv2 P4Runtime Json file: " + p4rt_json_file_path)
        with open(p4rt_json_file_path) as p4rt_json_file:
            p4rt = json.load(p4rt_json_file)

        return DASHSAIExtensions.from_p4rt(p4rt, name = 'dash_sai_apis', ignore_tables = ignore_tables)

    def get_all_table_names(self):
        return [table.name for api in self.sai_apis for table in api.tables]
    
    def parse_p4rt(self, p4rt_value, ignore_tables):
        self.__parse_sai_enums_from_p4rt(p4rt_value)
        self.__parse_sai_apis_from_p4rt(p4rt_value, ignore_tables)

    def __parse_sai_enums_from_p4rt(self, p4rt_value):
        all_p4rt_enums = p4rt_value[TYPE_INFO_TAG][SERIALIZABLE_ENUMS_TAG]
        self.sai_enums = [SAIEnum.from_p4rt(enum_value, name = enum_name) for enum_name, enum_value in all_p4rt_enums.items()]

    def __parse_sai_apis_from_p4rt(self, program, ignore_tables):
        all_actions = extract_action_data(program, self.sai_enums)
        tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
        for table in tables:
            sai_api_table_data = SAIAPITableData.from_p4rt(table, program, all_actions, ignore_tables)

            for sai_api in self.sai_apis:
                if sai_api.app_name == sai_api_table_data.api_name:
                    sai_api.add_table(sai_api_table_data)
                    break
            else:
                new_api = DASHAPISet(sai_api_table_data.api_name)
                new_api.add_table(sai_api_table_data)
                self.sai_apis.append(new_api)

        return


def extract_action_data(program, sai_enums):
    action_data = {}
    for action in program[ACTIONS_TAG]:
        print("Found action: " + action[PREAMBLE_TAG][NAME_TAG])

        preable = action[PREAMBLE_TAG]
        id = preable['id']
        name = preable[NAME_TAG].split('.')[-1]
        params = []
        if PARAMS_TAG in action:
            for p in action[PARAMS_TAG]:
                param = dict()
                param['id'] = p['id']
                param[NAME_TAG] = p[NAME_TAG]
                if STRUCTURED_ANNOTATIONS_TAG in p:
                    p4_annotation_to_sai_attr(p, param)
                else:
                    param['type'], param['field'] = SAIType.get_sai_key_type(int(p[BITWIDTH_TAG]), p[NAME_TAG], p[NAME_TAG])
                    for sai_enum in sai_enums:
                        if param[NAME_TAG] == sai_enum.name:
                            param['type'] = 'sai_' + param[NAME_TAG] + '_t'
                            param['field'] = 's32'
                            param['default'] = 'SAI_' + param[NAME_TAG].upper() + '_INVALID'
                param['bitwidth'] = p[BITWIDTH_TAG]
                params.append(param)
        action_data[id] = {'id': id, NAME_TAG: name, PARAMS_TAG: params}
    return action_data


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

    for param in action[PARAMS_TAG]:
        # mark presence of v4/v6 selector in the parent param
        if 'v4_or_v6' in param[NAME_TAG]:
            v4_or_v6_param_name = param[NAME_TAG]
            for param2 in  action[PARAMS_TAG]:
                if "is_" + param2[NAME_TAG] + "_v4_or_v6" == param[NAME_TAG]:
                    param2["v4_or_v6_id"] = param['id']
                    break


def get_uniq_sai_api(sai_api):
    """ Only keep one table per group(with same table name) """
    groups = set()
    sai_api = copy.deepcopy(sai_api)
    tables = []
    for table in sai_api.tables:
        if table.name in groups:
            continue
        tables.append(table)
        groups.add(table.name)
    sai_api.tables = tables
    return sai_api

# don't write content to file if file already exists
# and the content is the same, this will not touch
# the file and let make utilize this
def write_if_different(file,content):
    if os.path.isfile(file) == True:
        o = open(file, "r")
        data = o.read()
        o.close()
        if data == content:
            return # nothing to change, file is up to date
    with open(file, 'w') as o:
        o.write(content)

def write_sai_impl_files(sai_api):
    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    env.add_extension('jinja2.ext.loopcontrols')
    env.add_extension('jinja2.ext.do')
    sai_impl_tm = env.get_template('/templates/saiapi.cpp.j2')
    if "dash" in sai_api.app_name:
        header_prefix = "experimental"
    else:
        header_prefix = ""
    sai_impl_str = sai_impl_tm.render(tables = sai_api.tables, app_name = sai_api.app_name, header_prefix = header_prefix)
    write_if_different('./lib/sai' + sai_api.app_name.replace('_', '') + '.cpp',sai_impl_str)

def write_sai_fixed_api_files(sai_api_full_name_list):
    env = Environment(loader=FileSystemLoader('.'))

    for filename in ['saifixedapis.cpp', 'saiimpl.h']:
        env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
        sai_impl_tm = env.get_template('/templates/%s.j2' % filename)
        sai_impl_str = sai_impl_tm.render(tables = sai_api.tables, app_name = sai_api.app_name, api_names = sai_api_full_name_list)

        write_if_different('./lib/%s' % filename,sai_impl_str)


def write_sai_files(sai_api):
    # The main file
    with open('templates/saiapi.h.j2', 'r') as sai_header_tm_file:
        sai_header_tm_str = sai_header_tm_file.read()

    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    env.add_extension('jinja2.ext.loopcontrols')
    env.add_extension('jinja2.ext.do')
    sai_header_tm = env.get_template('templates/saiapi.h.j2')
    sai_header_str = sai_header_tm.render(sai_api = sai_api)

    write_if_different('./SAI/experimental/saiexperimental' + sai_api.app_name.replace('_', '') + '.h',sai_header_str)

    # The SAI Extensions
    with open('./SAI/experimental/saiextensions.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental APIs above this line' in line:
            new_line = '    SAI_API_' + sai_api.app_name.upper() + ',\n'
            if new_line not in lines:
                new_lines.append(new_line + '\n')
        if 'new experimental object type includes' in line:
            new_lines.append(line)
            new_line = '#include "saiexperimental' + sai_api.app_name.replace('_', '') + '.h"\n'
            if new_line not in lines:
                new_lines.append(new_line)
            continue

        new_lines.append(line)

    write_if_different('./SAI/experimental/saiextensions.h',''.join(new_lines))

    # The SAI Type Extensions
    with open('./SAI/experimental/saitypesextensions.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental object types above this line' in line:
            
            for table in sai_api.tables:
                new_line = '    SAI_OBJECT_TYPE_' + table.name.upper() + ',\n'
                if new_line not in lines:
                    new_lines.append(new_line + '\n')

        new_lines.append(line)

    write_if_different('./SAI/experimental/saitypesextensions.h',''.join(new_lines))

    # The SAI object struct for entries
    with open('./SAI/inc/saiobject.h', 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if 'Add new experimental entries above this line' in line:
            for table in sai_api.tables:
                if table.is_object == 'false':
                    new_line = '    sai_' + table.name + '_t ' + table.name + ';\n'
                    if new_line not in lines:
                        new_lines.append('    /** @validonly object_type == SAI_OBJECT_TYPE_' + table[NAME_TAG].upper() + ' */\n')
                        new_lines.append(new_line + '\n')
        if 'new experimental object type includes' in line:
            new_lines.append(line)
            new_line = '#include <saiexperimental' + sai_api.app_name.replace('_', '') + '.h>\n'
            if new_line not in lines:
                new_lines.append(new_line)
            continue

        new_lines.append(line)

    write_if_different('./SAI/inc/saiobject.h',''.join(new_lines))


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
dash_sai_exts = DASHSAIExtensions.from_p4rt_file(args.filepath, args.ignore_tables.split(','))
sai_apis = dash_sai_exts.sai_apis
all_table_names = dash_sai_exts.get_all_table_names()
sai_enums = dash_sai_exts.sai_enums

sai_api_name_list = []
sai_api_full_name_list = []
for sai_api in sai_apis:
    # Update object name reference for action params
    for table in sai_api.tables:
        for param in table.action_params:
            if param['type'] == 'sai_object_id_t':
                table_ref = param[NAME_TAG][:-len("_id")]
                for table_name in all_table_names:
                    if table_ref.endswith(table_name):
                        param[OBJECT_NAME_TAG] = table_name
    # Update object name reference for keys
    for table in sai_api.tables:
        for key in table.keys:
            if 'type' in key:
                if key['type'] == 'sai_object_id_t':
                    table_ref = key['sai_key_name'][:-len("_id")]
                    for table_name in all_table_names:
                        if table_ref.endswith(table_name):
                            key[OBJECT_NAME_TAG] = table_name
    # Write SAI dictionary into SAI API headers
    if "dash" in sai_api.app_name:
        write_sai_files(get_uniq_sai_api(sai_api))

    # Write SAI implementation    
    write_sai_impl_files(sai_api)
    sai_api_name_list.append(sai_api.app_name.replace('_', ''))
    sai_api_full_name_list.append(sai_api.app_name)

env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
env.add_extension('jinja2.ext.loopcontrols')
env.add_extension('jinja2.ext.do')

final_sai_enums = []
with open('./SAI/experimental/saitypesextensions.h', 'r') as f:
    content = f.read()
    for enum in sai_enums:
        if enum.name not in content:
            final_sai_enums.append(enum)

sai_enums_tm = env.get_template('templates/saienums.j2')
sai_enums_str = sai_enums_tm.render(sai_enums = final_sai_enums)
sai_enums_lines = sai_enums_str.split('\n')

# The SAI object struct for entries
with open('./SAI/experimental/saitypesextensions.h', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '/* __SAITYPESEXTENSIONS_H_ */' in line:
        for enum_line in sai_enums_lines:
            new_lines.append(enum_line + '\n')
        new_lines = new_lines[:-1]
    new_lines.append(line)

write_if_different('./SAI/experimental/saitypesextensions.h',''.join(new_lines))


write_sai_fixed_api_files(sai_api_full_name_list)

if args.print_sai_lib:
    print(json.dumps(sai_api, indent=2))
