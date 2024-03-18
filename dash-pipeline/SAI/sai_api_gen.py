#!/usr/bin/env python3

try:
    import os
    import json
    import argparse
    import copy
    import re
    from jinja2 import Template, Environment, FileSystemLoader
    from typing import (Type, Any, Dict, List, Optional, Callable, Iterator)
    import jsonpath_ng.ext as jsonpath_ext
    import jsonpath_ng as jsonpath
except ImportError as ie:
    print("Import failed for " + ie.name)
    exit(1)

NAME_TAG: str = 'name'
TABLES_TAG: str = 'tables'
BITWIDTH_TAG: str = 'bitwidth'
ACTIONS_TAG: str = 'actions'
ACTION_PARAMS_TAG: str = 'actionParams'
PREAMBLE_TAG: str = 'preamble'
OTHER_MATCH_TYPE_TAG: str = 'otherMatchType'
MATCH_TYPE_TAG: str = 'matchType'
PARAMS_TAG: str = 'params'
ACTION_REFS_TAG: str = 'actionRefs'
MATCH_FIELDS_TAG: str = 'matchFields'
NOACTION: str = 'NoAction'
STAGE_TAG: str = 'stage'
PARAM_ACTIONS: str = 'paramActions'
OBJECT_NAME_TAG: str = 'objectName'
SCOPE_TAG: str = 'scope'
TYPE_INFO_TAG: str = 'typeInfo'
COUNTERS_TAG: str = 'counters'
SERIALIZABLE_ENUMS_TAG: str = 'serializableEnums'
MEMBERS_TAG: str = 'members'
STRUCTURED_ANNOTATIONS_TAG: str = 'structuredAnnotations'
KV_PAIRS_TAG: str = 'kvPairs'
KV_PAIR_LIST_TAG: str = 'kvPairList'
SAI_VAL_TAG: str = 'SaiVal'
SAI_COUNTER_TAG: str = 'SaiCounter'
SAI_TABLE_TAG: str = 'SaiTable'

#
# P4 IR parser and analyzer:
#
class P4IRTree:
    @staticmethod
    def from_file(path: str) -> 'P4IRTree':
        with open(path, 'r') as f:
            return P4IRTree(json.load(f))

    def __init__(self, program: Dict[str, Any]) -> None:
        self.program = program

    def walk(self, path: str, on_match: Callable[[Any, Any], None]) -> None:
        jsonpath_exp = jsonpath_ext.parse(path)
        for match in jsonpath_exp.find(self.program):
            on_match(match)


class P4IRVarInfo:
    @staticmethod
    def from_ir(ir_def_node: Any) -> 'P4IRVarInfo':
        return P4IRVarInfo(
            ir_def_node["Node_ID"],
            ir_def_node["name"],
            ir_def_node["Source_Info"]["source_fragment"],
            ir_def_node["type"]["path"]["name"])

    def __init__(self, ir_id: int, ir_name: str, code_name: str, type_name: str) -> None:
        self.ir_id = ir_id
        self.ir_name = ir_name
        self.code_name = code_name
        self.type_name = type_name

    def __str__(self) -> str:
        return f"ID = {self.ir_id}, Name = {self.ir_name}, VarName = {self.code_name}, Type = {self.type_name}"


class P4IRVarRefInfo:
    @staticmethod
    def from_ir(ir_ref_node: Any, ir_var_info: P4IRVarInfo) -> 'P4IRVarRefInfo':
        return P4IRVarRefInfo(
            ir_var_info,
            ir_ref_node["Node_ID"],
            ir_ref_node["Node_Type"],
            ir_ref_node["name"])

    def __init__(self, var: P4IRVarInfo, caller_id: int, caller_type: str, caller: str) -> None:
        self.var = var
        self.caller_id = caller_id 
        self.caller_type = caller_type
        self.caller = caller

    def __str__(self) -> str:
        return f"VarName = {self.var.code_name}, CallerID = {self.caller_id}, CallerType = {self.caller_type}, Caller = {self.caller}"


class P4VarRefGraph:
    def __init__(self, ir: P4IRTree) -> None:
        self.ir = ir
        self.counters: Dict[str, P4IRVarInfo] = {}
        self.var_refs: Dict[str, List[P4IRVarRefInfo]] = {}
        self.__build_graph()

    def __build_graph(self) -> None:
        self.__build_counter_list()
        self.__build_counter_caller_mapping()
        pass

    def __build_counter_list(self) -> None:
        def on_counter_definition(match: jsonpath.DatumInContext) -> None:
            ir_value = P4IRVarInfo.from_ir(match.value)
            self.counters[ir_value.ir_name] = ir_value
            print(f"Counter definition found: {ir_value}")

        self.ir.walk('$..*[?Node_Type = "Declaration_Instance" & type.Node_Type = "Type_Name" & type.path.name = "counter"]', on_counter_definition)

    def __build_counter_caller_mapping(self) -> None:
        # Build the mapping from counter name to its caller.
        def on_counter_invocation(match: jsonpath.DatumInContext) -> None:
            var_ir_name: str = match.value["expr"]["path"]["name"]
            if var_ir_name not in self.counters:
                return

            # Walk through the parent nodes to find the closest action or control block.
            cur_node = match
            while cur_node.context is not None:
                cur_node = cur_node.context
                if "Node_Type" not in cur_node.value:
                    continue

                if cur_node.value["Node_Type"] in ["P4Action", "P4Control"]:
                    var = self.counters[var_ir_name]
                    var_ref = P4IRVarRefInfo.from_ir(cur_node.value, var)
                    self.var_refs.setdefault(var.code_name, []).append(var_ref)
                    print(f"Counter reference found: {var_ref}")
                    break

        # Get all nodes with Node_Type =  and name = "counter". This will be the nodes that represent the counter calls.
        self.ir.walk('$..*[?Node_Type = "Member" & member = "count"]', on_counter_invocation)


#
# SAI parser decorators:
#
def sai_parser_from_p4rt(cls: Type['SAIObject']):
    @staticmethod
    def create(p4rt_value, *args, **kwargs):
        sai_object = cls()
        sai_object.parse(p4rt_value, *args, **kwargs)
        return sai_object

    def parse(self, p4rt_value, *args, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
            kwargs.pop('name')

        self.parse_basic_info_if_exists(p4rt_value)
        self.parse_p4rt(p4rt_value, *args, **kwargs)

        return

    setattr(cls, "from_p4rt", create)
    setattr(cls, "parse", parse)

    return cls

#
# Parsed SAI objects and parsers:
#
# The SAI objects are parsed from the P4Runtime JSON file, generated by p4 compiler, which contains the information
# of all tables and entry information.
# 
# The classes below are used to parse the P4Runtime JSON file to get the key information, so we can generate the SAI
# API headers and implementation files afterwards.
#
# At high level, the hiredarchy of the SAI objects is as follows:
#
# DASHSAIExtensions                     : All DASH SAI extensions.
# |- SAIEnum                            : A single enum type.
# |  |- SAIEnumMember                   : A single enum member within the enum.
# |- SAIAPISet                          : All information for a single SAI API set, such as routing or CA-PA mapping.
#    |- SAIAPITableData                 : All information for a single SAI API table used in the API set.
#       |- SAIAPITableKey               : Information of a single P4 table key defined in the table.
#       |- SAIAPITableAction  <-------| : Information of a single P4 table action defined used by the table.
#          |- SAIAPITableActionParam -| : Information of a single P4 table action parameter used by the action.
#
class SAITypeInfo:
    def __init__(self, name: str, sai_attribute_value_field: str, default: str = None, is_enum: bool = False):
        self.name: str = name
        self.sai_attribute_value_field: str = sai_attribute_value_field
        self.default: str = default
        self.is_enum: bool = is_enum

class SAITypeSolver:
    sai_type_info_registry: Dict[str, SAITypeInfo] = {
        "bool": SAITypeInfo("bool", "booldata", default="false"),
        "sai_uint8_t": SAITypeInfo("sai_uint8_t", "u8", default="0"),
        "sai_object_id_t": SAITypeInfo("sai_object_id_t", "u16", default="SAI_NULL_OBJECT_ID"),
        "sai_uint16_t": SAITypeInfo("sai_uint16_t", "u16", default="0"),
        "sai_ip_address_t": SAITypeInfo("sai_ip_address_t", "ipaddr", default="0.0.0.0"),
        "sai_ip_addr_family_t": SAITypeInfo("sai_ip_addr_family_t", "u32", default="SAI_IP_ADDR_FAMILY_IPV4"),
        "sai_uint32_t": SAITypeInfo("sai_uint32_t", "u32", default="0"),
        "sai_uint64_t": SAITypeInfo("sai_uint64_t", "u64", default="0"),
        "sai_mac_t": SAITypeInfo("sai_mac_t", "mac", default="0:0:0:0:0:0"),
        "sai_ip_prefix_t": SAITypeInfo("sai_ip_prefix_t", "ipPrefix", default="0"),
        "sai_u8_list_t": SAITypeInfo("sai_u8_list_t", "u8list", default="empty"),
        "sai_u16_list_t": SAITypeInfo("sai_u16_list_t", "u16list", default="empty"),
        "sai_u32_list_t": SAITypeInfo("sai_u32_list_t", "u32list", default="empty"),
        "sai_ip_prefix_list_t": SAITypeInfo("sai_ip_prefix_list_t", "ipprefixlist", default="empty"),
        "sai_u32_range_t": SAITypeInfo("sai_u32_range_t", "u32range", default="empty"),
        "sai_u8_range_list_t": SAITypeInfo("sai_u8_range_list_t", "u8rangelist", default="empty"),
        "sai_u16_range_list_t": SAITypeInfo("sai_u16_range_list_t", "u16rangelist", default="empty"),
        "sai_u32_range_list_t": SAITypeInfo("sai_u32_range_list_t", "u32rangelist", default="empty"),
        "sai_u64_range_list_t": SAITypeInfo("sai_u64_range_list_t", "u64rangelist", default="empty"),
        "sai_ipaddr_range_list_t": SAITypeInfo("sai_ipaddr_range_list_t", "ipaddrrangelist", default="empty"),
    }

    @staticmethod
    def register_sai_type(name: str, sai_attribute_value_field: str, default: bool = None, is_enum: bool = False) -> None:
        SAITypeSolver.sai_type_info_registry[name] = SAITypeInfo(name, sai_attribute_value_field=sai_attribute_value_field, default=default, is_enum=is_enum)

    @staticmethod
    def get_sai_type(sai_type: str) -> SAITypeInfo:
        if sai_type not in SAITypeSolver.sai_type_info_registry:
            raise ValueError(f'sai_type={sai_type} is not supported')

        return SAITypeSolver.sai_type_info_registry[sai_type]

    @staticmethod
    def get_object_sai_type(object_size: int) -> SAITypeInfo:
        sai_type_name: str = ""

        if object_size == 1:
            sai_type_name = 'bool'
        elif object_size <= 8:
            sai_type_name = 'sai_uint8_t'
        elif object_size <= 16:
            sai_type_name = 'sai_uint16_t'
        elif object_size <= 32:
            sai_type_name = 'sai_uint32_t'
        elif object_size == 48:
            sai_type_name = 'sai_mac_t'
        elif object_size <= 64:
            sai_type_name = 'sai_uint64_t'
        elif object_size == 128:
            sai_type_name = 'sai_ip_address_t'
        else:
            raise ValueError(f'key_size={object_size} is not supported')

        return SAITypeSolver.get_sai_type(sai_type_name)

    @staticmethod
    def get_match_key_sai_type(match_type: str, key_size: int) -> SAITypeInfo:
        if match_type == 'exact' or match_type == 'optional' or match_type == 'ternary':
            return SAITypeSolver.get_object_sai_type(key_size)

        sai_type_name: str = ""
        if match_type == 'lpm':
            sai_type_name = SAITypeSolver.__get_lpm_match_key_sai_type(key_size)
        elif match_type == 'list':
            sai_type_name = SAITypeSolver.__get_list_match_key_sai_type(key_size)
        elif match_type == 'range':
            sai_type_name = SAITypeSolver.__get_range_match_key_sai_type(key_size)
        elif match_type == 'range_list':
            sai_type_name = SAITypeSolver.__get_range_list_match_key_sai_type(key_size)
        else:
            raise ValueError(f"match_type={match_type} is not supported")

        return SAITypeSolver.get_sai_type(sai_type_name)

    @staticmethod
    def __get_lpm_match_key_sai_type(key_size: int) -> str:
        # LPM match key should always be converted into IP prefix.
        if key_size == 32:
            return 'sai_ip_prefix_t'
        elif key_size == 128:
            return 'sai_ip_prefix_t'
        else:
            raise ValueError(f'key_size={key_size} is not supported')

    @staticmethod
    def __get_list_match_key_sai_type(key_size: int) -> str:
        if key_size <= 8:
            return 'sai_u8_list_t'
        elif key_size <= 16:
            return 'sai_u16_list_t'
        elif key_size <= 32:
            return 'sai_u32_list_t'
        else:
            raise ValueError(f'key_size={key_size} is not supported')

    @staticmethod
    def __get_range_match_key_sai_type(key_size: int) -> str:
        # In SAI, all ranges that having smaller size than 32-bits are passed as 32-bits, such as port ranges and etc.
        # So, we convert all ranges that is smaller than 32-bits to sai_u32_range_t by default.
        if key_size <= 32:
            return 'sai_u32_range_t'
        else:
            raise ValueError(f'key_size={key_size} is not supported')

    @staticmethod
    def __get_range_list_match_key_sai_type(key_size: int) -> str:
        if key_size <= 8:
            return 'sai_u8_range_list_t'
        elif key_size <= 16:
            return 'sai_u16_range_list_t'
        elif key_size <= 32:
            return 'sai_u32_range_list_t'
        elif key_size <= 64:
            return 'sai_u64_range_list_t'
        else:
            raise ValueError(f'key_size={key_size} is not supported')


class SAIObject:
    def __init__(self):
        # Properties from P4Runtime preamble
        self.raw_name: str = ''
        self.name: str = ''
        self.id: int = 0
        self.alias: str = ''
        self.order: int = 0

    def parse_basic_info_if_exists(self, p4rt_object: Dict[str, Any]) -> None:
        '''
        This method parses basic info, such as id and name, from either the object itself or the P4Runtime preamble object and populates the SAI object.

        Example P4Runtime preamble object:

            "preamble": {
                "id": 33810473,
                "name": "dash_ingress.outbound.acl.stage1:dash_acl_rule|dash_acl",
                "alias": "outbound.acl.stage1:dash_acl_rule|dash_acl"
            },
        '''
        if PREAMBLE_TAG in p4rt_object:
            preamble = p4rt_object[PREAMBLE_TAG]
            self.id = int(preamble['id'])
            self.name = str(preamble['name'])
            self.alias = str(preamble['alias'])
        else:
            self.id = int(p4rt_object['id']) if 'id' in p4rt_object else self.id
            self.name = str(p4rt_object['name']) if 'name' in p4rt_object else self.name

        # We only care about the last piece of the name, which is the actual object name.
        if '.' in self.name:
            name_parts = self.name.split('.')
            self.name = name_parts[-1]
        
        # We save the raw name here, because "name" can be override by annotation for API generation purpose, and the raw name will help us
        # to find the correlated P4 infomation from either Runtime or IR.
        self.raw_name = self.name

        return

    def _parse_sai_common_annotation(self, p4rt_anno: Dict[str, Any]) -> None:
        '''
        This method parses a single SAI annotation key value pair and populates the SAI object.

        Example SAI annotation key value pair:

            { "key": "type", "value": { "stringValue": "sai_ip_addr_family_t" } }
        '''
        if p4rt_anno['key'] == 'name':
            self.name = str(p4rt_anno['value']['stringValue'])
            return True
        elif p4rt_anno['key'] == 'order':
            self.order = str(p4rt_anno['value']['int64Value'])
            return True

        return False


@sai_parser_from_p4rt
class SAIEnumMember(SAIObject):
    '''
    This class represents a single SAI enum member and provides parser from the P4Runtime enum member object
    '''
    def __init__(self):
        super().__init__()
        self.p4rt_value: str = ""

    def parse_p4rt(self, p4rt_member: Dict[str, Any]) -> None:
        '''
        This method parses the P4Runtime enum member object and populates the SAI enum member object.

        Example P4Runtime enum member object:

            { "name": "INVALID", "value": "AAA=" }
        '''
        self.p4rt_value = str(p4rt_member["value"])


@sai_parser_from_p4rt
class SAIEnum(SAIObject):
    '''
    This class represents a single SAI enum and provides parser from the P4Runtime enum object
    '''
    def __init__(self):
        super().__init__()
        self.bitwidth: int = 0
        self.members: List[SAIEnumMember] = []
        
    def parse_p4rt(self, p4rt_enum: Dict[str, Any]) -> None:
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
        self.bitwidth = int(p4rt_enum['underlyingType'][BITWIDTH_TAG])
        self.members = [SAIEnumMember.from_p4rt(enum_member) for enum_member in p4rt_enum[MEMBERS_TAG]]

        # Register enum type info.
        SAITypeSolver.register_sai_type(
            'sai_' + self.name + '_t',
            "s32",
            default = 'SAI_' + self.name.upper() + "_" + self.members[0].name.upper(),
            is_enum = True)

class SAIAPITableAttribute(SAIObject):
    def __init__(self):
        super().__init__()

        # Properties from SAI annotations
        self.type: Optional[str] = None
        self.field: Optional[str] = None
        self.default: Optional[str] = None
        self.bitwidth: int = 0
        self.isresourcetype: Optional[str] = None
        self.isreadonly: Optional[str] = None
        self.object_name: Optional[str] = None
        self.skipattr: Optional[str] = None
        self.match_type: str = ""

    def _parse_sai_table_attribute_annotation(self, p4rt_anno_list: Dict[str, Any]) -> None:
        '''
        This method parses the SAI annotations and populates the SAI object.
        
        Example SAI annotations:

            {
                "name": "SaiVal",
                "kvPairList": {
                    "kvPairs": [
                        { "key": "type", "value": { "stringValue": "sai_ip_addr_family_t" } },
                        { "key": "isresourcetype", "value": { "stringValue": "true" } }
                    ]
                }
            }

        Whenever a new attribute is introduced, please update the doc here to get it captured: dash-pipeline/bmv2/README.md.
        '''
        for anno in p4rt_anno_list[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_VAL_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv['key'] == 'type':
                        self.type = str(kv['value']['stringValue'])
                    elif kv['key'] == 'default_value':  # "default" is a reserved keyword and cannot be used.
                        self.default = str(kv['value']['stringValue'])
                    elif kv['key'] == 'isresourcetype':
                        self.isresourcetype = str(kv['value']['stringValue'])
                    elif kv['key'] == 'isreadonly':
                        self.isreadonly = str(kv['value']['stringValue'])
                    elif kv['key'] == 'objects':
                        self.object_name = str(kv['value']['stringValue'])
                    elif kv['key'] == 'skipattr':
                        self.skipattr = str(kv['value']['stringValue'])
                    elif kv['key'] == 'match_type':
                        self.match_type = str(kv['value']['stringValue'])
                    elif kv['key'] == 'validonly':
                        self.validonly = str(kv['value']['stringValue'])
                    else:
                        raise ValueError("Unknown attr annotation " + kv['key'])

    @staticmethod
    def link_ip_is_v6_vars(vars: List['SAIAPITableAttribute']) -> List['SAIAPITableAttribute']:
        # Link *_is_v6 var to its corresponding var.
        ip_is_v6_key_ids = {v.name.replace("_is_v6", ""): v.id for v in vars if '_is_v6' in v.name}

        for v in vars:
            if v.name in ip_is_v6_key_ids:
                v.ip_is_v6_field_id = ip_is_v6_key_ids[v.name]

        # Delete all vars with *_is_v6 in their names.
        return [v for v in vars if '_is_v6' not in v.name]

    def set_sai_type(self, sai_type_info: SAITypeInfo) -> None:
        self.type = sai_type_info.name
        self.field = sai_type_info.sai_attribute_value_field
        if self.default == None:
            self.default = sai_type_info.default

@sai_parser_from_p4rt
class SAICounter(SAIAPITableAttribute):
    '''
    This class represents a single counter in SAI and provides parser from the P4Runtime counter object
    '''
    def __init__(self):
        super().__init__()
        self.bitwidth: int = 64
        self.isreadonly: str = "true"
        self.counter_type: str = "bytes"
        self.attr_type: str = "stats"
        self.no_suffix: bool = ""
        self.param_actions: List[str] = []

    def parse_p4rt(self, p4rt_counter: Dict[str, Any], var_ref_graph: P4VarRefGraph) -> None:
        '''
        This method parses the P4Runtime counter object and populates the SAI counter object.

        Example P4Runtime counter object:

            {
                "preamble": {
                    "id": 318423147,
                    "name": "dash_ingress.meter_bucket_inbound",
                    "alias": "meter_bucket_inbound"
                },
                "spec": {
                    "unit": "BYTES"
                },
                "size": "262144"
            }
        '''
        print("Parsing counter: " + self.name)
        self.__parse_sai_counter_annotation(p4rt_counter)

        # If this counter needs to be generated as SAI attributes, we need to figure out the data type for the counter value.
        if self.attr_type != "counter_id":
            counter_storage_type = SAITypeSolver.get_object_sai_type(self.bitwidth)

        # Otherwise, this counter should be linked to a SAI counter using an object ID.
        # In this case, the type needs to be sai_object_id_t.
        else:
            counter_storage_type = SAITypeSolver.get_sai_type("sai_object_id_t")
            self.name = f"{self.name}_counter_id"
            self.isreadonly = "false"
            self.object_name = "counter"
        
        self.set_sai_type(counter_storage_type)

        counter_unit = str(p4rt_counter['spec']['unit']).lower()
        if counter_unit in ['bytes', 'packets', 'both']:
            self.counter_type = counter_unit.lower()
        else:
            raise ValueError(f'Unknown counter unit: {counter_unit}')

        # If actions are specified by annotation, then we skip finding the referenced actions from the IR.
        if len(self.param_actions) == 0 and self.raw_name in var_ref_graph.var_refs:
            for ref in var_ref_graph.var_refs[self.raw_name]:
                if ref.caller_type == 'P4Action':
                    self.param_actions.append(ref.caller)

            print(f"Counter {self.name} is referenced by {self.param_actions}")

        return

    def __parse_sai_counter_annotation(self, p4rt_counter: Dict[str, Any]) -> None:
        '''
        This method parses the SAI annotations and populates the SAI counter object.
        
        Example SAI annotations:

            {
                "name": "SaiCounter",
                "kvPairList": {
                    "kvPairs": [
                        { "key": "name", "value": { "stringValue": "counter_name" } }
                    ]
                }
            }

        Whenever a new attribute is introduced, please update the doc here to get it captured: dash-pipeline/bmv2/README.md.
        '''
        for anno in p4rt_counter[PREAMBLE_TAG][STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_COUNTER_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv['key'] == 'action_names':
                        self.param_actions = str(kv['value']['stringValue']).split(",")
                    elif kv['key'] == 'attr_type':
                        self.attr_type = str(kv['value']['stringValue'])
                        if self.attr_type not in ["counter_attr", "counter_id", "stats"]:
                            raise ValueError(f'Unknown counter attribute type: attr_type={self.attr_type}')
                    elif kv['key'] == 'no_suffix':
                        self.no_suffix = str(kv['value']['stringValue']) == "true"
                    else:
                        raise ValueError("Unknown attr annotation " + kv['key'])

    def generate_counter_sai_attributes(self) -> 'Iterator[SAICounter]':
        # If the SAI attribute type is counter id, we generate as standard SAI counter ID attributes, hence return as it is.
        if self.attr_type == "counter_id":
            yield self

        counter_types = ['bytes', 'packets'] if self.counter_type == 'both' else [self.counter_type]

        for index, counter_type in enumerate(counter_types):
            counter = self
            if index != len(counter_types) - 1:
                counter = copy.deepcopy(self)
            
            counter.counter_type = counter_type

            if counter.attr_type == "counter_attr":
                counter.name = f"{counter.name}_{counter.counter_type}_counter" if not self.no_suffix else f"{counter.name}_counter"
            else:
                counter.name = f"{counter.name}_{counter.counter_type}" if not self.no_suffix else counter.name

            yield counter


@sai_parser_from_p4rt
class SAIAPITableKey(SAIAPITableAttribute):
    '''
    This class represents a single SAI API table key and provides parser from the P4Runtime table key object.
    '''
    def __init__(self):
        super().__init__()
        self.ip_is_v6_field_id: int = 0

    def parse_p4rt(self, p4rt_table_key: Dict[str, Any]) -> None:
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

        self.bitwidth = int(p4rt_table_key[BITWIDTH_TAG])
        # print("Parsing table key: " + self.name)

        if OTHER_MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type =  str(p4rt_table_key[OTHER_MATCH_TYPE_TAG].lower())
        elif MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type =  str(p4rt_table_key[MATCH_TYPE_TAG].lower())
        else:
            raise ValueError(f'No valid match tag found')

        if STRUCTURED_ANNOTATIONS_TAG in p4rt_table_key:
            self._parse_sai_table_attribute_annotation(p4rt_table_key)

        # If type is specified, use it. Otherwise, try to find the proper type using default heuristics.
        if self.type != None:
            sai_type_info = SAITypeSolver.get_sai_type(self.type)
        else:
            sai_type_info = SAITypeSolver.get_match_key_sai_type(self.match_type, self.bitwidth)

        self.set_sai_type(sai_type_info)

        return


@sai_parser_from_p4rt
class SAIAPITableAction(SAIObject):
    def __init__(self):
        super().__init__()
        self.params: List[SAIAPITableActionParam] = []
        self.counters: List[SAICounter] = []

    def parse_p4rt(self, p4rt_table_action: Dict[str, Any], sai_enums: List[SAIEnum], counters_by_action_name: Dict[str, List[SAICounter]]) -> None:
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
        # print("Parsing table action: " + self.name)
        self.parse_action_params(p4rt_table_action, sai_enums)
        self.counters = counters_by_action_name[self.name] if self.name in counters_by_action_name else []

    def parse_action_params(self, p4rt_table_action: Dict[str, Any], sai_enums: List[SAIEnum]) -> None:
        if PARAMS_TAG not in p4rt_table_action:
            return

        # Parse all params.
        for p in p4rt_table_action[PARAMS_TAG]:
            param = SAIAPITableActionParam.from_p4rt(p)
            self.params.append(param)

        self.params = SAIAPITableAttribute.link_ip_is_v6_vars(self.params)

        return


@sai_parser_from_p4rt
class SAIAPITableActionParam(SAIAPITableAttribute):
    def __init__(self):
        super().__init__()
        self.bitwidth: int = 0
        self.ip_is_v6_field_id: int = 0
        self.param_actions: List[SAIAPITableAction] = []

    def parse_p4rt(self, p4rt_table_action_param: Dict[str, Any]) -> None:
        '''
        This method parses the P4Runtime table action object and populates the SAI API table action object.

        Example P4Runtime table action object:

            { "id": 1, "name": "dst_vnet_id", "bitwidth": 16 }
        '''
        self.bitwidth = int(p4rt_table_action_param[BITWIDTH_TAG])
        # print("Parsing table action param: " + self.name)

        if STRUCTURED_ANNOTATIONS_TAG in p4rt_table_action_param:
            self._parse_sai_table_attribute_annotation(p4rt_table_action_param)

        # If type is specified, use it. Otherwise, try to find the proper type using default heuristics.
        if self.type != None:
            sai_type_info = SAITypeSolver.get_sai_type(self.type)
        else:
            sai_type_info = SAITypeSolver.get_object_sai_type(self.bitwidth)

        self.set_sai_type(sai_type_info)

        return


@sai_parser_from_p4rt
class SAIAPITableData(SAIObject):
    '''
    This class represents a single SAI API set and provides parser from the P4Runtime table object
    '''
    def __init__(self):
        super().__init__()
        self.ignored: bool = False
        self.api_name: str = ""
        self.ipaddr_family_attr: str = 'false'
        self.keys: List[SAIAPITableKey] = []
        self.actions: List[SAIAPITableAction] = []
        self.action_params: List[SAIAPITableActionParam] = []
        self.counters: List[SAICounter] = []
        self.with_counters: str = 'false'
        self.sai_attributes: List[SAIAPITableAttribute] = []
        self.sai_stats: List[SAIAPITableAttribute] = []

        # Extra properties from annotations
        self.stage: Optional[str] = None
        self.is_object: Optional[str] = None
        self.api_type: Optional[str] = None

    def parse_p4rt(self,
                   p4rt_table: Dict[str, Any],
                   program: Dict[str, Any],
                   all_actions: Dict[int, SAIAPITableAction],
                   ignore_tables: List[str]) -> None:
        '''
        This method parses the P4Runtime table object and populates the SAI API table object.

        Example P4Runtime table object:

            {
                "preamble": {
                    "id": 49812549,
                    "name": "dash_ingress.outbound.acl.stage2:dash_acl_rule|dash_acl",
                    "alias": "outbound.acl.stage2:dash_acl_rule|dash_acl"
                },
                "matchFields": [
                    {
                        "id": 1,
                        "name": "meta.dash_acl_group_id:dash_acl_group_id",
                        "bitwidth": 16,
                        "matchType": "EXACT",
                        "structuredAnnotations": [...]
                    },
                    ...
                ],
                "actionRefs": [
                    { "id": 18858683 },
                    ...
                ],
                "directResourceIds": [ 334749261 ],
                "size": "1024"
            }
        '''
        self.__parse_sai_table_annotations(p4rt_table[PREAMBLE_TAG])

        # If tables are specified as ignored via CLI or annotations, skip them.
        if self.name in ignore_tables:
            self.ignored = True
        elif self.ignored:
            ignore_tables.append(self.name)

        if self.ignored:
            print("Ignoring table: " + self.name)
            return

        print("Parsing table: " + self.name)
        self.with_counters = self.__table_with_counters(program)
        self.__parse_table_keys(p4rt_table)
        self.__parse_table_actions(p4rt_table, all_actions)

        if self.is_object == "false":
            self.name = self.name + '_entry'

        return

    def __parse_sai_table_annotations(self, p4rt_table_preamble: Dict[str, Any]) -> None:
        if STRUCTURED_ANNOTATIONS_TAG not in p4rt_table_preamble:
            return

        for anno in p4rt_table_preamble[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_TABLE_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv['key'] == 'isobject':
                        self.is_object = str(kv['value']['stringValue'])
                    elif kv['key'] == 'ignored':
                        self.ignored = True
                    elif kv['key'] == 'stage':
                        self.stage = str(kv['value']['stringValue'])
                    elif kv['key'] == 'api':
                        self.api_name = str(kv['value']['stringValue'])
                    elif kv['key'] == 'api_type':
                        self.api_type = str(kv['value']['stringValue'])

        if self.is_object == None:
            self.is_object = 'false'

        return

    def __table_with_counters(self, program: Dict[str, Any]) -> None:
        for counter in program['directCounters']:
            if counter['directTableId'] == self.id:
                return 'true'
        return 'false'

    def __parse_table_keys(self, p4rt_table: Dict[str, Any]) -> None:
        for p4rt_table_key in p4rt_table[MATCH_FIELDS_TAG]:
            table_key = SAIAPITableKey.from_p4rt(p4rt_table_key)
            self.keys.append(table_key)

        self.keys = SAIAPITableAttribute.link_ip_is_v6_vars(self.keys)

        for p4rt_table_key in self.keys:
            if (p4rt_table_key.match_type == 'exact' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'ternary' and p4rt_table_key.type == 'sai_ip_address_t') or \
                (p4rt_table_key.match_type == 'lpm' and p4rt_table_key.type == 'sai_ip_prefix_t') or \
                (p4rt_table_key.match_type == 'list' and p4rt_table_key.type == 'sai_ip_prefix_list_t'):
                    self.ipaddr_family_attr = 'true'

        return

    def __parse_table_actions(self, p4rt_table: Dict[str, Any], all_actions: List[SAIAPITableAction]) -> None:
        for p4rt_table_action in p4rt_table[ACTION_REFS_TAG]:
            action_id = p4rt_table_action["id"]
            if all_actions[action_id].name != NOACTION and not (SCOPE_TAG in p4rt_table_action and p4rt_table_action[SCOPE_TAG] == 'DEFAULT_ONLY'):
                action = all_actions[action_id]
                self.actions.append(action)
                self.__merge_action_info_to_table(action)

    def __merge_action_info_to_table(self, action: SAIAPITableAction) -> None:
        '''
        Merge objects used by an action into the table for SAI attributes generation.

        This is needed for deduplication. If the same counter is used by multiple actions, we only need to keep one
        copy of for a table, so we don't generate multiple SAI attributes.
        '''
        self.__merge_action_params_to_table_params(action)
        self.__merge_action_counters_to_table_counters(action)

    def __merge_action_params_to_table_params(self, action: SAIAPITableAction) -> None:
        for action_param in action.params:
            # skip v4/v6 selector, as they are linked via parameter property.
            if '_is_v6' in action_param.name:
                continue

            for table_action_param in self.action_params:
                # Already have this param in the table.
                if table_action_param.name == action_param.name:
                    table_action_param.param_actions.append(action.name)
                    break
            else:
                # New param is found, add it to the table.
                action_param.param_actions = [action.name]
                self.action_params.append(action_param)

    def __merge_action_counters_to_table_counters(self, action: SAIAPITableAction) -> None:
        for counter in action.counters:
            for table_counter in self.counters:
                # Already have this counter in the table.
                if table_counter.name == counter.name:
                    break
            else:
                # New counter is found, add it to the table.
                self.counters.append(counter)

    def post_parsing_process(self, all_table_names: List[str]) -> None:
        self.__update_table_param_object_name_reference(all_table_names)
        self.__build_sai_attributes_after_parsing()

    def __update_table_param_object_name_reference(self, all_table_names) -> None:
        # Update object name reference for action params
        for param in self.action_params:
            if param.type == 'sai_object_id_t':
                table_ref = param.name[:-len("_id")]
                for table_name in all_table_names:
                    if table_ref.endswith(table_name):
                        param.object_name = table_name

        # Update object name reference for keys
        for key in self.keys:
            if key.type != None:
                if key.type == 'sai_object_id_t':
                    table_ref = key.name[:-len("_id")]
                    for table_name in all_table_names:
                        if table_ref.endswith(table_name):
                            key.object_name = table_name

    def __build_sai_attributes_after_parsing(self):
        # Group all actions parameters and counters set by order with sequence kept the same.
        # Then merge them into a single list.
        sai_attributes_by_order = {}
        sai_stats_by_order = {}

        for action_param in self.action_params:
            if action_param.skipattr != "true":
                sai_attributes_by_order.setdefault(action_param.order, []).append(action_param)

        for counter in self.counters:
            if counter.attr_type != "stats":
                sai_attributes_by_order.setdefault(counter.order, []).append(counter)
            else:
                sai_stats_by_order.setdefault(counter.order, []).append(counter)
        
        # Merge all attributes into a single list by their order.
        self.sai_attributes = []
        for order in sorted(sai_attributes_by_order.keys()):
            self.sai_attributes.extend(sai_attributes_by_order[order])

        # Merge all stat counters into a single list by their order.
        self.sai_stats = []
        for order in sorted(sai_stats_by_order.keys()):
            self.sai_stats.extend(sai_stats_by_order[order])


class DASHAPISet(SAIObject):
    '''
    This class holds all parsed SAI API info for a specific API set, such as routing or CA-PA mapping.
    '''
    def __init__(self, api_name: str):
        self.app_name: str = api_name
        self.api_type: Optional[str] = None
        self.tables: List[SAIAPITableData] = []
    
    def add_table(self, table: SAIAPITableData) -> None:
        if self.api_type == None:
            self.api_type = table.api_type
        elif self.api_type != table.api_type:
            raise ValueError(f'API type mismatch: CurrentType = {self.api_type}, NewTableAPIType = {table.api_type}')

        self.tables.append(table)

    def post_parsing_process(self, all_table_names: List[str]) -> None:
        for table in self.tables:
            table.post_parsing_process(all_table_names)


@sai_parser_from_p4rt
class DASHSAIExtensions(SAIObject):
    '''
    This class holds all parsed SAI APIs and provides parser for the generated p4 runtime json file
    '''
    def __init__(self):
        super().__init__()
        self.sai_enums: List[SAIEnum] = []
        self.sai_counters: List[SAICounter] = []
        self.sai_apis: List[DASHAPISet] = []

    @staticmethod
    def from_p4rt_file(p4rt_json_file_path: str, ignore_tables: List[str], var_ref_graph: P4VarRefGraph) -> 'DASHSAIExtensions':
        print("Parsing SAI APIs BMv2 P4Runtime Json file: " + p4rt_json_file_path)
        with open(p4rt_json_file_path) as p4rt_json_file:
            p4rt = json.load(p4rt_json_file)

        return DASHSAIExtensions.from_p4rt(p4rt, name = 'dash_sai_apis', ignore_tables = ignore_tables, var_ref_graph = var_ref_graph)

    def parse_p4rt(self, p4rt_value: Dict[str, Any], ignore_tables: List[str], var_ref_graph) -> None:
        self.__parse_sai_enums_from_p4rt(p4rt_value)
        self.__parse_sai_counters_from_p4rt(p4rt_value, var_ref_graph)
        self.__parse_sai_apis_from_p4rt(p4rt_value, ignore_tables)

    def __parse_sai_enums_from_p4rt(self, p4rt_value: Dict[str, Any]) -> None:
        all_p4rt_enums = p4rt_value[TYPE_INFO_TAG][SERIALIZABLE_ENUMS_TAG]
        self.sai_enums = [SAIEnum.from_p4rt(enum_value, name = enum_name) for enum_name, enum_value in all_p4rt_enums.items()]

    def __parse_sai_counters_from_p4rt(self, p4rt_value: Dict[str, Any], var_ref_graph: P4VarRefGraph) -> None:
        all_p4rt_counters = p4rt_value[COUNTERS_TAG]
        for p4rt_counter in all_p4rt_counters:
            counter = SAICounter.from_p4rt(p4rt_counter, var_ref_graph)
            self.sai_counters.extend(counter.generate_counter_sai_attributes())

    def __parse_sai_apis_from_p4rt(self, program: Dict[str, Any], ignore_tables: List[str]) -> None:
        # Group all counters by action name.
        counters_by_action_name = {}
        for counter in self.sai_counters:
            for action_name in counter.param_actions:
                counters_by_action_name.setdefault(action_name, []).append(counter)

        # Parse all actions.
        actions = self.__parse_sai_table_action(program[ACTIONS_TAG], self.sai_enums, counters_by_action_name)

        # Parse all tables into SAI API sets.
        tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
        for table in tables:
            sai_api_table_data = SAIAPITableData.from_p4rt(table, program, actions, ignore_tables)
            if sai_api_table_data.ignored:
                continue

            for sai_api in self.sai_apis:
                if sai_api.app_name == sai_api_table_data.api_name:
                    sai_api.add_table(sai_api_table_data)
                    break
            else:
                new_api = DASHAPISet(sai_api_table_data.api_name)
                new_api.add_table(sai_api_table_data)
                self.sai_apis.append(new_api)

        # Sort all parsed tables by API order, so we can always generate the APIs in the same order for keeping ABI compatibility.
        for sai_api in self.sai_apis:
            sai_api.tables.sort(key=lambda x: x.order)

    def __parse_sai_table_action(self, p4rt_actions: Dict[str, Any], sai_enums: List[SAIEnum], counters_by_action_name: Dict[str, List[SAICounter]]) -> Dict[int, SAIAPITableAction]:
        action_data = {}
        for p4rt_action in p4rt_actions:
            action = SAIAPITableAction.from_p4rt(p4rt_action, sai_enums, counters_by_action_name)
            action_data[action.id] = action
        return action_data

    def post_parsing_process(self) -> None:
        all_table_names = [table.name for api in self.sai_apis for table in api.tables]
        for sai_api in self.sai_apis:
            sai_api.post_parsing_process(all_table_names)


#
# SAI Generators:
#
class SAIFileUpdater:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def __enter__(self):
        with open(self.file_path, 'r') as f:
            self.lines = f.readlines()
        return self
 
    def __exit__(self, *args):
        print("Updating file: " + self.file_path + " ...")
        SAIFileUpdater.write_if_different(self.file_path, ''.join(self.lines))

    def insert_before(self, target_line: str, insert_lines: List[str], new_line_only: bool = False) -> None:
        new_lines: List[str] = []

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

    def insert_after(self, target_line: str, insert_lines: List[str], new_line_only: bool = False) -> None:
        new_lines: List[str] = []

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
    def write_if_different(file: str, content: str) -> None:
        if os.path.isfile(file) == True:
            o = open(file, "r")
            data = o.read()
            o.close()
            if data == content:
                return # nothing to change, file is up to date
        with open(file, 'w') as o:
            o.write(content)

class SAITemplateRender:
    jinja2_env: Environment = None

    @classmethod
    def new_tm(cls, template_file_path: str):
        if cls.jinja2_env == None:
            cls.jinja2_env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
            cls.jinja2_env.add_extension('jinja2.ext.loopcontrols')
            cls.jinja2_env.add_extension('jinja2.ext.do')
        
        return cls.jinja2_env.get_template(template_file_path)

    def __init__(self, template_file_path: str):
        self.template_file_path = template_file_path
        self.tm = SAITemplateRender.new_tm(template_file_path)

    def render(self, **kwargs: Any) -> str:
        return self.tm.render(**kwargs)

    def render_to_file(self, target_file_path: str, **kwargs: Any) -> None:
        print("Updating file: " + target_file_path + " (template = " + self.template_file_path + ") ...")
        rendered_str = self.tm.render(**kwargs)
        SAIFileUpdater.write_if_different(target_file_path, rendered_str)

class SAIGenerator:
    def __init__(self, dash_sai_ext: DASHSAIExtensions):
        self.dash_sai_ext: DASHSAIExtensions = dash_sai_ext
        self.sai_api_names: List[str] = []
        self.generated_sai_api_extension_lines: List[str] = []
        self.generated_sai_type_extension_lines: List[str] = []
        self.generated_sai_port_attibute_extension_lines: List[str] = []
        self.generated_sai_object_entry_extension_lines: List[str] = []
        self.generated_header_file_names: List[str] = []
        self.generated_impl_file_names: List[str] = []

    def generate(self) -> None:
        print("\nGenerating all SAI APIs ...")

        for sai_api in self.dash_sai_ext.sai_apis:
            self.generate_sai_api_extensions(sai_api)

        self.generate_sai_global_extensions()
        self.generate_sai_type_extensions()
        self.generate_sai_port_extensions()
        self.generate_sai_object_extensions()
        self.generate_sai_enum_extensions()
        self.generate_sai_fixed_api_files()

    def generate_sai_api_extensions(self, sai_api: DASHAPISet) -> None:
        print("\nGenerating DASH SAI API definitions and implementation for API: " + sai_api.app_name + " ...")

        self.sai_api_names.append(sai_api.app_name)
    
        # For new DASH APIs, we need to generate SAI API headers.
        unique_sai_api = self.__get_uniq_sai_api(sai_api)
        if sai_api.api_type != 'underlay':
            self.generate_dash_sai_definitions_for_api(unique_sai_api)

        # Generate SAI API implementation for all APIs.
        self.generate_sai_impl_file_for_api(sai_api)

    def generate_dash_sai_definitions_for_api(self, sai_api: DASHAPISet) -> None:
        # SAI header file
        sai_header_file_name = 'saiexperimental' + sai_api.app_name.replace('_', '') + '.h'
        SAITemplateRender('templates/saiapi.h.j2').render_to_file('SAI/experimental/' + sai_header_file_name, sai_api = sai_api)
        self.generated_header_file_names.append(sai_header_file_name)

        # Gather SAI API extension name and object types
        self.generated_sai_api_extension_lines.append('    SAI_API_' + sai_api.app_name.upper() + ',\n')

        for table in sai_api.tables:
            self.generated_sai_type_extension_lines.append('    SAI_OBJECT_TYPE_' + table.name.upper() + ',\n')

            if table.is_object == 'false':
                self.generated_sai_object_entry_extension_lines.append('    /** @validonly object_type == SAI_OBJECT_TYPE_' + table.name.upper() + ' */')
                self.generated_sai_object_entry_extension_lines.append('    sai_' + table.name + '_t ' + table.name + ';\n')

        return

    def generate_sai_impl_file_for_api(self, sai_api: DASHAPISet) -> None:
        sai_impl_file_name = 'sai' + sai_api.app_name.replace('_', '') + '.cpp'
        header_prefix = "experimental" if sai_api.api_type != "underlay" else ""
        SAITemplateRender('templates/saiapi.cpp.j2').render_to_file('lib/' + sai_impl_file_name, tables = sai_api.tables, app_name = sai_api.app_name, header_prefix = header_prefix)
        self.generated_impl_file_names.append(sai_impl_file_name)

    def generate_sai_global_extensions(self) -> None:
        print("\nGenerating SAI global extensions with API names and includes ...")
        with SAIFileUpdater('SAI/experimental/saiextensions.h') as f:
            f.insert_before('Add new experimental APIs above this line', self.generated_sai_api_extension_lines, new_line_only=True)
            f.insert_after('new experimental object type includes', ['#include "{}"'.format(f) for f in self.generated_header_file_names], new_line_only=True)

    def generate_sai_type_extensions(self) -> None:
        print("\nGenerating SAI type extensions with object types ...")
        with SAIFileUpdater('SAI/experimental/saitypesextensions.h') as f:
            f.insert_before('Add new experimental object types above this line', self.generated_sai_type_extension_lines, new_line_only=True)

    def generate_sai_port_extensions(self) -> None:
        print("\nGenerating SAI port extensions with port attributes ...")

        # If any counter doesn't have any table assigned, they should be added as port attributes and track globally.
        new_port_counters: List[SAICounter] = []
        new_port_stats: List[SAICounter] = []
        is_first_attr = False
        is_first_stat = False
        with open('SAI/experimental/saiportextensions.h', 'r') as f:
            content = f.read()

            all_port_attrs = re.findall(r'SAI_PORT_ATTR_\w+', content)
            is_first_attr = len(all_port_attrs) == 3

            all_port_stats = re.findall(r'SAI_PORT_STAT_\w+', content)
            is_first_stat = len(all_port_stats) == 3

            for sai_counter in self.dash_sai_ext.sai_counters:
                if len(sai_counter.param_actions) == 0:
                    if sai_counter.attr_type != "stats":
                        sai_counter_port_attr_name = f"SAI_PORT_ATTR_{sai_counter.name.upper()}"
                        if sai_counter_port_attr_name not in all_port_attrs:
                            new_port_counters.append(sai_counter)
                    else:
                        sai_counter_port_stat_name = f"SAI_PORT_STAT_{sai_counter.name.upper()}"
                        if sai_counter_port_stat_name not in all_port_stats:
                            new_port_stats.append(sai_counter)

        sai_counters_str = SAITemplateRender('templates/saicounter.j2').render(table_name = "port", sai_counters = new_port_counters, is_first_attr = is_first_attr)
        sai_counters_lines = [s.rstrip(" \n") for s in sai_counters_str.split('\n')]
        sai_counters_lines = sai_counters_lines[:-1] # Remove the last empty line, so we won't add extra empty line to the file.

        sai_stats_str = SAITemplateRender('templates/headers/sai_stats_extensions.j2').render(table_name = "port", sai_stats = new_port_stats, is_first_attr = is_first_stat)
        sai_stats_lines = [s.rstrip(" \n") for s in sai_stats_str.split('\n')]
        sai_stats_lines = sai_stats_lines[:-1] # Remove the last empty line, so we won't add extra empty line to the file.

        with SAIFileUpdater('SAI/experimental/saiportextensions.h') as f:
            f.insert_before('Add new experimental port attributes above this line', sai_counters_lines)
            f.insert_before('Add new experimental port stats above this line', sai_stats_lines)

    def generate_sai_object_extensions(self) -> None:
        print("\nGenerating SAI object entry extensions ...")
        with SAIFileUpdater('SAI/inc/saiobject.h') as f:
            f.insert_before('Add new experimental entries above this line', self.generated_sai_object_entry_extension_lines, new_line_only=True)
            f.insert_after('new experimental object type includes', ["#include <{}>".format(f) for f in self.generated_header_file_names], new_line_only=True)

        return

    def generate_sai_enum_extensions(self) -> None:
        print("\nGenerating SAI enum extensions ...")
        new_sai_enums: List[SAIEnum] = []
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

    def generate_sai_fixed_api_files(self) -> None:
        print("\nGenerating SAI fixed APIs ...")
        for filename in ['saifixedapis.cpp', 'saiimpl.h']:
            SAITemplateRender('templates/%s.j2' % filename).render_to_file('lib/%s' % filename, api_names = self.sai_api_names)

    def __get_uniq_sai_api(self, sai_api: DASHAPISet) -> None:
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
    parser.add_argument('--ir', type=str, help="Path to P4 program IR JSON file")
    parser.add_argument('--print-sai-lib', type=bool)
    parser.add_argument('--ignore-tables', type=str, default='', help='Comma separated list of tables to ignore')
    args = parser.parse_args()

    p4rt_file_path = os.path.realpath(args.filepath)
    if not os.path.isfile(p4rt_file_path):
        print('File ' + p4rt_file_path + ' does not exist')
        exit(1)

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    p4ir = P4IRTree.from_file(args.ir)
    var_ref_graph = P4VarRefGraph(p4ir)

    # Parse SAI data from P4 runtime json file
    dash_sai_exts = DASHSAIExtensions.from_p4rt_file(p4rt_file_path, args.ignore_tables.split(','), var_ref_graph)
    dash_sai_exts.post_parsing_process()

    if args.print_sai_lib:
        print("Dumping parsed SAI data:")
        print(json.dumps(dash_sai_exts, indent=2))

    # Generate and update all SAI files
    SAIGenerator(dash_sai_exts).generate()
