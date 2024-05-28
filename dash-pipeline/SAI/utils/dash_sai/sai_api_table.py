from typing import List
from .common import *
from .sai_api_table_action_param import *
from .sai_api_counter import *
from .sai_enum import *
from .sai_api_table_key import *
from .sai_api_table_action import *


@sai_parser_from_p4rt
class SAIAPITable(SAIObject):
    """
    This class represents a single SAI API set and provides parser from the P4Runtime table object
    """

    def __init__(self):
        super().__init__()
        self.ignored: bool = False
        self.api_name: str = ""
        self.ipaddr_family_attr: str = "false"
        self.keys: List[SAIAPITableKey] = []
        self.actions: List[SAIAPITableAction] = []
        self.action_params: List[SAIAPITableActionParam] = []
        self.counters: List[SAIAPICounter] = []
        self.with_counters: str = "false"
        self.sai_attributes: List[SAIAPIAttribute] = []
        self.sai_stats: List[SAIAPIAttribute] = []

        # Extra properties from annotations
        self.stage: Optional[str] = None
        self.is_object: Optional[str] = None
        self.api_type: Optional[str] = None

    def parse_p4rt(
        self,
        p4rt_table: Dict[str, Any],
        program: Dict[str, Any],
        all_actions: Dict[int, SAIAPITableAction],
        ignore_tables: List[str],
    ) -> None:
        """
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
        """
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
            self.name = self.name + "_entry"

        return

    def __parse_sai_table_annotations(
        self, p4rt_table_preamble: Dict[str, Any]
    ) -> None:
        if STRUCTURED_ANNOTATIONS_TAG not in p4rt_table_preamble:
            return

        for anno in p4rt_table_preamble[STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_TABLE_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv["key"] == "isobject":
                        self.is_object = str(kv["value"]["stringValue"])
                    elif kv["key"] == "ignored":
                        self.ignored = True
                    elif kv["key"] == "stage":
                        self.stage = str(kv["value"]["stringValue"])
                    elif kv["key"] == "api":
                        self.api_name = str(kv["value"]["stringValue"])
                    elif kv["key"] == "api_type":
                        self.api_type = str(kv["value"]["stringValue"])

        if self.is_object == None:
            self.is_object = "false"

        return

    def __table_with_counters(self, program: Dict[str, Any]) -> None:
        for counter in program["directCounters"]:
            if counter["directTableId"] == self.id:
                return "true"
        return "false"

    def __parse_table_keys(self, p4rt_table: Dict[str, Any]) -> None:
        for p4rt_table_key in p4rt_table[MATCH_FIELDS_TAG]:
            table_key = SAIAPITableKey.from_p4rt(p4rt_table_key)
            self.keys.append(table_key)

        self.keys = SAIAPIAttribute.link_ip_is_v6_vars(self.keys)

        for p4rt_table_key in self.keys:
            if (
                (
                    p4rt_table_key.match_type == "exact"
                    and p4rt_table_key.type == "sai_ip_address_t"
                )
                or (
                    p4rt_table_key.match_type == "ternary"
                    and p4rt_table_key.type == "sai_ip_address_t"
                )
                or (
                    p4rt_table_key.match_type == "lpm"
                    and p4rt_table_key.type == "sai_ip_prefix_t"
                )
                or (
                    p4rt_table_key.match_type == "list"
                    and p4rt_table_key.type == "sai_ip_prefix_list_t"
                )
            ):
                self.ipaddr_family_attr = "true"

        return

    def __parse_table_actions(
        self, p4rt_table: Dict[str, Any], all_actions: List[SAIAPITableAction]
    ) -> None:
        for p4rt_table_action in p4rt_table[ACTION_REFS_TAG]:
            action_id = p4rt_table_action["id"]
            if all_actions[action_id].name != NOACTION and not (
                SCOPE_TAG in p4rt_table_action
                and p4rt_table_action[SCOPE_TAG] == "DEFAULT_ONLY"
            ):
                action = all_actions[action_id]
                self.actions.append(action)
                self.__merge_action_info_to_table(action)

    def __merge_action_info_to_table(self, action: SAIAPITableAction) -> None:
        """
        Merge objects used by an action into the table for SAI attributes generation.

        This is needed for deduplication. If the same counter is used by multiple actions, we only need to keep one
        copy of for a table, so we don't generate multiple SAI attributes.
        """
        self.__merge_action_params_to_table_params(action)
        self.__merge_action_counters_to_table_counters(action)

    def __merge_action_params_to_table_params(self, action: SAIAPITableAction) -> None:
        for action_param in action.params:
            # skip v4/v6 selector, as they are linked via parameter property.
            if "_is_v6" in action_param.name:
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

    def __merge_action_counters_to_table_counters(
        self, action: SAIAPITableAction
    ) -> None:
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
            if param.type == "sai_object_id_t":
                table_ref = param.name[: -len("_id")]
                for table_name in all_table_names:
                    if table_ref.endswith(table_name):
                        param.object_name = table_name

        # Update object name reference for keys
        for key in self.keys:
            if key.type != None:
                if key.type == "sai_object_id_t":
                    table_ref = key.name[: -len("_id")]
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
                sai_attributes_by_order.setdefault(action_param.order, []).append(
                    action_param
                )

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
