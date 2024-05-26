from typing import Any, Dict, Type


#
# Common tags in P4 runtime JSON file:
#
NAME_TAG: str = "name"
TABLES_TAG: str = "tables"
BITWIDTH_TAG: str = "bitwidth"
ACTIONS_TAG: str = "actions"
ACTION_PARAMS_TAG: str = "actionParams"
PREAMBLE_TAG: str = "preamble"
OTHER_MATCH_TYPE_TAG: str = "otherMatchType"
MATCH_TYPE_TAG: str = "matchType"
PARAMS_TAG: str = "params"
ACTION_REFS_TAG: str = "actionRefs"
MATCH_FIELDS_TAG: str = "matchFields"
NOACTION: str = "NoAction"
STAGE_TAG: str = "stage"
PARAM_ACTIONS: str = "paramActions"
OBJECT_NAME_TAG: str = "objectName"
SCOPE_TAG: str = "scope"
TYPE_INFO_TAG: str = "typeInfo"
COUNTERS_TAG: str = "counters"
SERIALIZABLE_ENUMS_TAG: str = "serializableEnums"
MEMBERS_TAG: str = "members"
STRUCTURED_ANNOTATIONS_TAG: str = "structuredAnnotations"
KV_PAIRS_TAG: str = "kvPairs"
KV_PAIR_LIST_TAG: str = "kvPairList"
SAI_VAL_TAG: str = "SaiVal"
SAI_COUNTER_TAG: str = "SaiCounter"
SAI_TABLE_TAG: str = "SaiTable"


#
# SAI parser decorators:
#
def sai_parser_from_p4rt(cls: Type["SAIObject"]):
    @staticmethod
    def create(p4rt_value, *args, **kwargs):
        sai_object = cls()
        sai_object.parse(p4rt_value, *args, **kwargs)
        return sai_object

    def parse(self, p4rt_value, *args, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"]
            kwargs.pop("name")

        self.parse_basic_info_if_exists(p4rt_value)
        self.parse_p4rt(p4rt_value, *args, **kwargs)

        return

    setattr(cls, "from_p4rt", create)
    setattr(cls, "parse", parse)

    return cls


class SAIObject:
    def __init__(self):
        # Properties from P4Runtime preamble
        self.raw_name: str = ""
        self.name: str = ""
        self.id: int = 0
        self.alias: str = ""
        self.order: int = 0

    def parse_basic_info_if_exists(self, p4rt_object: Dict[str, Any]) -> None:
        """
        This method parses basic info, such as id and name, from either the object itself or the P4Runtime preamble object and populates the SAI object.

        Example P4Runtime preamble object:

            "preamble": {
                "id": 33810473,
                "name": "dash_ingress.outbound.acl.stage1:dash_acl_rule|dash_acl",
                "alias": "outbound.acl.stage1:dash_acl_rule|dash_acl"
            },
        """
        if PREAMBLE_TAG in p4rt_object:
            preamble = p4rt_object[PREAMBLE_TAG]
            self.id = int(preamble["id"])
            self.name = str(preamble["name"])
            self.alias = str(preamble["alias"])
        else:
            self.id = int(p4rt_object["id"]) if "id" in p4rt_object else self.id
            self.name = str(p4rt_object["name"]) if "name" in p4rt_object else self.name

        # We only care about the last piece of the name, which is the actual object name.
        if "." in self.name:
            name_parts = self.name.split(".")
            self.name = name_parts[-1]

        # We save the raw name here, because "name" can be override by annotation for API generation purpose, and the raw name will help us
        # to find the correlated P4 infomation from either Runtime or IR.
        self.raw_name = self.name

        return

    def _parse_sai_common_annotation(self, p4rt_anno: Dict[str, Any]) -> None:
        """
        This method parses a single SAI annotation key value pair and populates the SAI object.

        Example SAI annotation key value pair:

            { "key": "type", "value": { "stringValue": "sai_ip_addr_family_t" } }
        """
        if p4rt_anno["key"] == "name":
            self.name = str(p4rt_anno["value"]["stringValue"])
            return True
        elif p4rt_anno["key"] == "order":
            self.order = int(p4rt_anno["value"]["int64Value"])
            return True

        return False
