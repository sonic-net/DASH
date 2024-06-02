from typing import List, Optional
from .common import *
from .sai_type_solver import SAITypeInfo
from ..sai_spec import SaiAttribute, SaiStructEntry


class DashP4TableAttribute(DashP4Object):
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
        self.validonly: Optional[str] = None

    def _parse_sai_table_attribute_annotation(
        self, p4rt_anno_list: Dict[str, Any]
    ) -> None:
        """
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
        """
        if not (STRUCTURED_ANNOTATIONS_TAG in p4rt_anno_list):
            return

        for anno in p4rt_anno_list[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_VAL_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv["key"] == "type":
                        self.type = str(kv["value"]["stringValue"])
                    elif (
                        kv["key"] == "default_value"
                    ):  # "default" is a reserved keyword and cannot be used.
                        self.default = str(kv["value"]["stringValue"])
                    elif kv["key"] == "isresourcetype":
                        self.isresourcetype = str(kv["value"]["stringValue"])
                    elif kv["key"] == "isreadonly":
                        self.isreadonly = str(kv["value"]["stringValue"])
                    elif kv["key"] == "objects":
                        self.object_name = str(kv["value"]["stringValue"])
                    elif kv["key"] == "skipattr":
                        self.skipattr = str(kv["value"]["stringValue"])
                    elif kv["key"] == "match_type":
                        self.match_type = str(kv["value"]["stringValue"])
                    elif kv["key"] == "validonly":
                        self.validonly = str(kv["value"]["stringValue"])
                    else:
                        raise ValueError("Unknown attr annotation " + kv["key"])

    @staticmethod
    def link_ip_is_v6_vars(
        vars: List["DashP4TableAttribute"],
    ) -> List["DashP4TableAttribute"]:
        # Link *_is_v6 var to its corresponding var.
        ip_is_v6_key_ids = {
            v.name.replace("_is_v6", ""): v.id for v in vars if "_is_v6" in v.name
        }

        for v in vars:
            if v.name in ip_is_v6_key_ids:
                v.ip_is_v6_field_id = ip_is_v6_key_ids[v.name]

        # Delete all vars with *_is_v6 in their names.
        return [v for v in vars if "_is_v6" not in v.name]

    def set_sai_type(self, sai_type_info: SAITypeInfo) -> None:
        self.type = sai_type_info.name
        self.field = sai_type_info.sai_attribute_value_field
        if self.default == None:
            self.default = sai_type_info.default

    #
    # Functions for generating SAI specs.
    #
    def to_sai_struct_entry(self, table_name: str) -> List[SaiStructEntry]:
        name = self.name.lower()
        description = self.get_sai_description(table_name)
        object_name = f"SAI_OBJECT_TYPE_{self.object_name.upper()}" if self.object_name else None

        entries = [
            SaiStructEntry(
                name = name,
                description = description,
                type = self.type,
                objects = object_name,
                valid_only = self.validonly,
            )
        ]

        if self.match_type == "ternary":
            entries.append(
                SaiStructEntry(
                    name = f"{name}_mask",
                    description = f"{description} mask",
                    type = self.type,
                    objects = object_name,
                    valid_only = self.validonly,
                )
            )

        return entries

    def to_sai_attribute(self, table_name: str, create_only: bool = False, add_action_valid_only_check: bool = False) -> List[SaiAttribute]:
        name = self.get_sai_name(table_name)
        description = self.get_sai_description(table_name)

        object_name = f"SAI_OBJECT_TYPE_{self.object_name.upper()}" if self.object_name else None
        allow_null = True if self.type == "sai_object_id_t" else False
        is_vlan = True if self.type == "sai_uint16_t" else False

        if self.isreadonly == "true":
            sai_flags = "READ_ONLY"
            default_value = None
        elif create_only:
            sai_flags = "MANDATORY_ON_CREATE | CREATE_ONLY"
            default_value = None
            allow_null = False
        else:
            sai_flags = "CREATE_AND_SET"
            default_value = self.default

        valid_only_checks = []
        if add_action_valid_only_check:
            for param_action in self.param_actions:
                valid_only_checks.append(f"SAI_{table_name.upper()}_ATTR_ACTION == SAI_{table_name.upper()}_ACTION_{param_action.upper()}")
        
        if self.validonly:
            valid_only_checks.append(self.validonly)
        
        valid_only = " or ".join(valid_only_checks) if len(valid_only_checks) > 0 else None
        
        attributes = [
            SaiAttribute(
                name = name,
                description = description,
                type = self.type,
                attr_value_field = self.field,
                default = default_value,
                isresourcetype = self.isresourcetype == "true",
                flags = sai_flags,
                object_name = object_name,
                allow_null = allow_null,
                valid_only = valid_only,
                is_vlan = is_vlan,
            )
        ]

        if self.match_type == "ternary":
            attributes.append(SaiAttribute(
                name = f"{name}_MASK",
                description = f"{description} mask",
                type = self.type,
                attr_value_field = self.field,
                default = None,
                isresourcetype = self.isresourcetype == "true",
                flags = sai_flags,
                object_name = object_name,
                allow_null = allow_null,
                valid_only = valid_only,
            ))

        return attributes

    def get_sai_name(self, table_name: str) -> str:
        return f"SAI_{table_name.upper()}_ATTR_{self.name.upper()}"
    
    def get_sai_description(self, table_name: str):
        return f"Action parameter {self.name.replace('_', ' ')}"