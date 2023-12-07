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
# The SAI objects are parsed from the P4Runtime JSON file, generated by p4 compiler, which contains the information
# of all tables and entry information.
# 
# The classes below are used to parse the P4Runtime JSON file to get the key information, so we can generate the SAI
# API headers and implementation files afterwards.
#
# At high level, the hiredarchy of the SAI objects is as follows:
#
# DASHSAIExtensions: All DASH SAI extensions.
# - SAIEnum: A single enum type.
#   - SAIEnumMember: A single enum member within the enum.
# - SAIAPISet: All information for a single SAI API set, such as routing or CA-PA mapping.
#   - SAIAPITableData: All information for a single SAI API table used in the API set.
#     - SAIAPITableKey: Information of a single P4 table key defined in the table.
#     - SAIAPITableAction: Information of a single P4 table action defined used by the table.
#       - SAIAPITableActionParam: Information of a single P4 table action parameter used by the action.
#
class SAIType:
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

    @staticmethod
    def get_sai_default_field_from_type(sai_type):
        return SAIType.sai_type_to_field[sai_type]

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

        self.field = SAIType.get_sai_default_field_from_type(self.type)


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

        self.id = p4rt_table_key['id']
        self.name = p4rt_table_key[NAME_TAG]
        #print("Parsing table key: " + self.name)

        full_key_name, self.sai_key_name = self.name.split(':')
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
        v4_or_v6_key_name = "is_" + self.sai_key_name + "_v4_or_v6"
        if v4_or_v6_key_name in v4_or_v6_key_ids:
            self.v4_or_v6_id = v4_or_v6_key_ids[v4_or_v6_key_name]

        return


@sai_parser_from_p4rt
class SAIAPITableAction(SAIObject):
    def __init__(self):
        super().__init__()
        self.params = []

    def parse_p4rt(self, p4rt_table_action, sai_enums):
        '''
        This method parses the P4Runtime table action object and populates the SAI API table action object.

        Example P4Runtime table action object:

            {
                "preamble": {
                    "id": 25364446,
                    "name": "dash_ingress.outbound.route_vnet",
                    "alias": "route_vnet"
                },
                "params": [
                    { "id": 1, "name": "dst_vnet_id", "bitwidth": 16 },
                    { "id": 2, "name": "meter_policy_en", "bitwidth": 1 },
                    { "id": 3, "name": "meter_class", "bitwidth": 16 }
                ]
            }
        '''
        #print("Parsing table action: " + self.name)
        self.name = self.name.split('.')[-1]
        self.parse_action_params(p4rt_table_action, sai_enums)

    def parse_action_params(self, p4rt_table_action, sai_enums):
        if PARAMS_TAG not in p4rt_table_action:
            return

        # Save all *_v4_or_v6 param ids.
        v4_or_v6_param_ids = dict()
        for p4rt_table_action_param in p4rt_table_action[PARAMS_TAG]:
            if 'v4_or_v6' in p4rt_table_action_param[NAME_TAG]:
                v4_or_v6_param_name = p4rt_table_action_param[NAME_TAG]
                v4_or_v6_param_ids[v4_or_v6_param_name] = p4rt_table_action_param['id']

        # Parse all params.
        for p in p4rt_table_action[PARAMS_TAG]:
            param_name = p[NAME_TAG]
            param = SAIAPITableActionParam.from_p4rt(p, sai_enums = sai_enums, v4_or_v6_param_ids = v4_or_v6_param_ids)
            self.params.append(param)

        return


@sai_parser_from_p4rt
class SAIAPITableActionParam(SAIObject):
    def __init__(self):
        super().__init__()
        self.bitwidth = 0
        self.default = None
        self.v4_or_v6_id = 0
        self.paramActions = []

    def parse_p4rt(self, p4rt_table_action_param, sai_enums, v4_or_v6_param_ids):
        '''
        This method parses the P4Runtime table action object and populates the SAI API table action object.

        Example P4Runtime table action object:

            { "id": 1, "name": "dst_vnet_id", "bitwidth": 16 }
        '''
        self.id = p4rt_table_action_param['id']
        self.name = p4rt_table_action_param[NAME_TAG]
        #print("Parsing table action param: " + self.name)

        if STRUCTURED_ANNOTATIONS_TAG in p4rt_table_action_param:
            self._parse_sai_object_annotation(p4rt_table_action_param)
        else:
            self.type, self.field = SAIType.get_sai_key_type(int(p4rt_table_action_param[BITWIDTH_TAG]), p4rt_table_action_param[NAME_TAG], p4rt_table_action_param[NAME_TAG])
            for sai_enum in sai_enums:
                if self.name == sai_enum.name:
                    self.type = 'sai_' + self.name + '_t'
                    self.field = 's32'
                    self.default = 'SAI_' + self.name.upper() + '_INVALID'

        self.bitwidth = p4rt_table_action_param[BITWIDTH_TAG]

        # If v4_or_v6 key is present, save its id.
        v4_or_v6_param_name = "is_" + self.name + "_v4_or_v6"
        if v4_or_v6_param_name in v4_or_v6_param_ids:
            self.v4_or_v6_id = v4_or_v6_param_ids[v4_or_v6_param_name]

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

        # Extra properties from annotations
        self.stage = None
        self.is_object = None

    def parse_p4rt(self, p4rt_table, program, all_actions, ignore_tables):
        table_control, table_name = p4rt_table[PREAMBLE_TAG][NAME_TAG].split('.', 1)

        self.__parse_sai_table_annotations(p4rt_table[PREAMBLE_TAG])
        if self.ignored:
            ignore_tables.append(table_name)
        if table_name in ignore_tables:
            return

        print("Parsing table: " + table_name)

        table_name, self.api_name = table_name.split('|')
        self.name = table_name.split('.')[-1] if '.' in table_name else table_name

        if ':' in table_name:
            stage, group_name = table_name.split(':')
            self.name = group_name
            self.stage = stage.replace('.' , '_')

        self.with_counters = self.__table_with_counters(program)

        self.__parse_table_keys(p4rt_table)

        for p4rt_table_action in p4rt_table[ACTION_REFS_TAG]:
            action_id = p4rt_table_action["id"]
            if all_actions[action_id].name != NOACTION and not (SCOPE_TAG in p4rt_table_action and p4rt_table_action[SCOPE_TAG] == 'DEFAULT_ONLY'):
                self.__merge_action_params_to_table_params(all_actions[action_id])
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
            if 'v4_or_v6' in p4rt_table_key[NAME_TAG]:
                continue

            table_key = SAIAPITableKey.from_p4rt(p4rt_table_key, v4_or_v6_key_ids)
            self.keys.append(table_key)

        for p4rt_table_key in self.keys:
            if (p4rt_table_key.match_type == 'exact' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'ternary' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'lpm' and p4rt_table_key.type == 'sai_ip_prefix_t') or \
                (p4rt_table_key.match_type == 'list' and p4rt_table_key.type == 'sai_ip_prefix_list_t'):
                    self.ipaddr_family_attr = 'true'

        return

    def __merge_action_params_to_table_params(self, action):
        '''
        Merge all parameters of an action into a single list of parameters for the table.

        When merge the parameters, we need to handle duplications. If the same param passed to multiple actions,
        we only need to keep one copy of the param in the table, so we don't generate multiple SAI attributes.
        '''
        for action_param in action.params:
            # skip v4/v6 selector, as they are linked via parameter property already.
            if 'v4_or_v6' in action_param.name:
                continue

            for table_action_param in self.action_params:
                # Already have this param in the table.
                if table_action_param.name == action_param.name:
                    table_action_param.paramActions.append(action.name)
                    break
            else:
                # New param is found, add it to the table.
                action_param.paramActions = [action.name]
                self.action_params.append(action_param)


class DASHAPISet(SAIObject):
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

    def parse_p4rt(self, p4rt_value, ignore_tables):
        self.__parse_sai_enums_from_p4rt(p4rt_value)
        self.__parse_sai_apis_from_p4rt(p4rt_value, ignore_tables)
        self.__update_table_param_object_name_reference()

    def __parse_sai_enums_from_p4rt(self, p4rt_value):
        all_p4rt_enums = p4rt_value[TYPE_INFO_TAG][SERIALIZABLE_ENUMS_TAG]
        self.sai_enums = [SAIEnum.from_p4rt(enum_value, name = enum_name) for enum_name, enum_value in all_p4rt_enums.items()]

    def __parse_sai_apis_from_p4rt(self, program, ignore_tables):
        # Parse all actions.
        actions = self.__parse_sai_table_action(program[ACTIONS_TAG], self.sai_enums)

        # Parse all tables into SAI API sets.
        tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
        for table in tables:
            sai_api_table_data = SAIAPITableData.from_p4rt(table, program, actions, ignore_tables)

            for sai_api in self.sai_apis:
                if sai_api.app_name == sai_api_table_data.api_name:
                    sai_api.add_table(sai_api_table_data)
                    break
            else:
                new_api = DASHAPISet(sai_api_table_data.api_name)
                new_api.add_table(sai_api_table_data)
                self.sai_apis.append(new_api)

    def __update_table_param_object_name_reference(self):
        all_table_names = [table.name for api in self.sai_apis for table in api.tables]
    
        for sai_api in self.sai_apis:
            # Update object name reference for action params
            for table in sai_api.tables:
                for param in table.action_params:
                    if param.type == 'sai_object_id_t':
                        table_ref = param.name[:-len("_id")]
                        for table_name in all_table_names:
                            if table_ref.endswith(table_name):
                                param.objectName = table_name

            # Update object name reference for keys
            for table in sai_api.tables:
                for key in table.keys:
                    if key.type != None:
                        if key.type == 'sai_object_id_t':
                            table_ref = key.sai_key_name[:-len("_id")]
                            for table_name in all_table_names:
                                if table_ref.endswith(table_name):
                                    key.objectName = table_name


    def __parse_sai_table_action(self, p4rt_actions, sai_enums):
        action_data = {}
        for p4rt_action in p4rt_actions:
            action = SAIAPITableAction.from_p4rt(p4rt_action, sai_enums)
            action_data[action.id] = action
        return action_data

#
# SAI Generators
#
class SAIFileUpdater:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        with open(self.file_path, 'r') as f:
            self.lines = f.readlines()
        return self
 
    def __exit__(self, *args):
        print("Updating file: " + self.file_path + " ...")
        SAIFileUpdater.write_if_different(self.file_path, ''.join(self.lines))

    def insert_before(self, target_line, insert_lines, new_line_only=False):
        new_lines = []

        existing_lines = set([l.strip() for l in self.lines])
        for line in self.lines:
            if target_line in line:
                if new_line_only:
                    for insert_line in insert_lines:
                        if insert_line.strip() not in existing_lines:
                            new_lines.append(insert_line + '\n')
                else:
                    new_lines.extend([insert_line + '\n' for insert_line in insert_lines])

            new_lines.append(line)

        self.lines = new_lines

    def insert_after(self, target_line, insert_lines, new_line_only = False):
        new_lines = []

        existing_lines = set([l.strip() for l in self.lines])
        for line in self.lines:
            new_lines.append(line)
            if target_line in line:
                if new_line_only == True:
                    for insert_line in insert_lines:
                        if insert_line.strip() not in existing_lines:
                            new_lines.append(insert_line + '\n')
                else:
                    new_lines.extend([insert_line + '\n' for insert_line in insert_lines])

        self.lines = new_lines

    # don't write content to file if file already exists
    # and the content is the same, this will not touch
    # the file and let make utilize this
    @staticmethod
    def write_if_different(file, content):
        if os.path.isfile(file) == True:
            o = open(file, "r")
            data = o.read()
            o.close()
            if data == content:
                return # nothing to change, file is up to date
        with open(file, 'w') as o:
            o.write(content)

class SAITemplateRender:
    jinja2_env = None

    @classmethod
    def new_tm(cls, template_file_path):
        if cls.jinja2_env == None:
            cls.env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
            cls.env.add_extension('jinja2.ext.loopcontrols')
            cls.env.add_extension('jinja2.ext.do')
        
        return cls.env.get_template(template_file_path)

    def __init__(self, template_file_path):
        self.template_file_path = template_file_path
        self.tm = SAITemplateRender.new_tm(template_file_path)

    def render(self, **kwargs):
        return self.tm.render(**kwargs)

    def render_to_file(self, target_file_path, **kwargs):
        print("Updating file: " + target_file_path + " (template = " + self.template_file_path + ") ...")
        rendered_str = self.tm.render(**kwargs)
        SAIFileUpdater.write_if_different(target_file_path, rendered_str)

class SAIGenerator:
    def __init__(self, dash_sai_ext):
        self.dash_sai_ext = dash_sai_ext
        self.sai_api_names = []
        self.generated_sai_api_extension_names = []
        self.generated_sai_type_extension_names = []
        self.generated_sai_object_entry_extension_names = []
        self.generated_header_file_names = []
        self.generated_impl_file_names = []

    def generate(self):
        print("\nGenerating all SAI APIs ...")

        for sai_api in self.dash_sai_ext.sai_apis:
            self.generate_sai_api(sai_api)

        self.generate_dash_sai_global_definitions()
        self.generate_sai_enum()
        self.generate_sai_fixed_api_files()

    def generate_sai_api(self, sai_api):
        print("\nGenerating DASH SAI API definitions and implementation for API: " + sai_api.app_name + " ...")

        self.sai_api_names.append(sai_api.app_name)
    
        # For new DASH APIs, we need to generate SAI API headers.
        unique_sai_api = self.__get_uniq_sai_api(sai_api)
        if "dash" in sai_api.app_name:
            self.generate_dash_sai_definitions_for_api(unique_sai_api)

        # Generate SAI API implementation for all APIs.
        self.generate_sai_impl_file_for_api(sai_api)

    def generate_dash_sai_definitions_for_api(self, sai_api):
        # SAI header file
        sai_header_file_name = 'saiexperimental' + sai_api.app_name.replace('_', '') + '.h'
        SAITemplateRender('templates/saiapi.h.j2').render_to_file('SAI/experimental/' + sai_header_file_name, sai_api = sai_api)
        self.generated_header_file_names.append(sai_header_file_name)

        # Gather SAI API extension name and object types
        self.generated_sai_api_extension_names.append('    SAI_API_' + sai_api.app_name.upper() + ',')

        for table in sai_api.tables:
            self.generated_sai_type_extension_names.append('    SAI_OBJECT_TYPE_' + table.name.upper() + ',')

            if table.is_object == 'false':
                self.generated_sai_object_entry_extension_names.append('    /** @validonly object_type == SAI_OBJECT_TYPE_' + table.name.upper() + ' */')
                self.generated_sai_object_entry_extension_names.append('    sai_' + table.name + '_t ' + table.name + ';')

        return

    def generate_sai_impl_file_for_api(self, sai_api):
        sai_impl_file_name = 'sai' + sai_api.app_name.replace('_', '') + '.cpp'
        header_prefix = "experimental" if "dash" in sai_api.app_name else ""
        SAITemplateRender('templates/saiapi.cpp.j2').render_to_file('lib/' + sai_impl_file_name, tables = sai_api.tables, app_name = sai_api.app_name, header_prefix = header_prefix)
        self.generated_impl_file_names.append(sai_impl_file_name)

    def generate_dash_sai_global_definitions(self):
        print("\nGenerating DASH SAI API global definitions ...")

        # Update SAI extensions with API names and includes
        with SAIFileUpdater('SAI/experimental/saiextensions.h') as f:
            f.insert_before('Add new experimental APIs above this line', self.generated_sai_api_extension_names, new_line_only=True)
            f.insert_after('new experimental object type includes', ['#include "{}"'.format(f) for f in self.generated_header_file_names], new_line_only=True)

        # Update SAI type extensions with object types
        with SAIFileUpdater('SAI/experimental/saitypesextensions.h') as f:
            f.insert_before('Add new experimental object types above this line', self.generated_sai_type_extension_names, new_line_only=True)

        # Update SAI object struct for entries
        with SAIFileUpdater('SAI/inc/saiobject.h') as f:
            f.insert_before('Add new experimental entries above this line', self.generated_sai_object_entry_extension_names, new_line_only=True)
            f.insert_after('new experimental object type includes', ["#include <{}>".format(f) for f in self.generated_header_file_names], new_line_only=True)

        return

    def generate_sai_enum(self):
        new_sai_enums = []
        with open('SAI/experimental/saitypesextensions.h', 'r') as f:
            content = f.read()
            for enum in self.dash_sai_ext.sai_enums:
                if enum.name not in content:
                    new_sai_enums.append(enum)

        sai_enums_str = SAITemplateRender('templates/saienums.j2').render(sai_enums = new_sai_enums)
        sai_enums_lines = [s.rstrip(" \n") for s in sai_enums_str.split('\n')]
        sai_enums_lines = sai_enums_lines[:-1] # Remove the last empty line, so we won't add extra empty line to the file.

        with SAIFileUpdater('SAI/experimental/saitypesextensions.h') as f:
            f.insert_before('/* __SAITYPESEXTENSIONS_H_ */', sai_enums_lines)

    def generate_sai_fixed_api_files(self):
        print("\nGenerating SAI fixed APIs ...")
        for filename in ['saifixedapis.cpp', 'saiimpl.h']:
            SAITemplateRender('templates/%s.j2' % filename).render_to_file('lib/%s' % filename, api_names = self.sai_api_names)

    def __get_uniq_sai_api(self, sai_api):
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


if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description='P4 SAI API generator')
    parser.add_argument('filepath', type=str, help='Path to P4 program RUNTIME JSON file')
    parser.add_argument('apiname', type=str, help='Name of the new SAI API')
    parser.add_argument('--print-sai-lib', type=bool)
    parser.add_argument('--ignore-tables', type=str, default='', help='Comma separated list of tables to ignore')
    args = parser.parse_args()

    p4rt_file_path = os.path.realpath(args.filepath)
    if not os.path.isfile(p4rt_file_path):
        print('File ' + p4rt_file_path + ' does not exist')
        exit(1)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Parse SAI data from P4 runtime json file
    dash_sai_exts = DASHSAIExtensions.from_p4rt_file(p4rt_file_path, args.ignore_tables.split(','))

    if args.print_sai_lib:
        print("Dumping parsed SAI data:")
        print(json.dumps(dash_sai_exts, indent=2))

    # Generate and update all SAI files
    SAIGenerator(dash_sai_exts).generate()