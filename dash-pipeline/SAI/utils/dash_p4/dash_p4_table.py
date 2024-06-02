from typing import List
from .common import *
from .dash_p4_enum import *
from .dash_p4_counter import *
from .dash_p4_table_action_param import *
from .dash_p4_table_key import *
from .dash_p4_table_action import *
from ..sai_spec import SaiApi, SaiStruct, SaiEnum, SaiEnumMember, SaiAttribute, SaiApiP4MetaAction, SaiApiP4MetaTable


@dash_p4rt_parser
class DashP4Table(DashP4Object):
    """
    This class represents a single SAI API set and provides parser from the P4Runtime table object
    """

    def __init__(self):
        super().__init__()
        self.ignored: bool = False
        self.ignored_in_header: bool = False
        self.api_name: str = ""
        self.ipaddr_family_attr: str = "false"
        self.keys: List[DashP4TableKey] = []
        self.actions: List[DashP4TableAction] = []
        self.action_params: List[DashP4TableActionParam] = []
        self.counters: List[DashP4Counter] = []
        self.with_counters: str = "false"
        self.sai_attributes: List[DashP4TableAttribute] = []
        self.sai_stats: List[DashP4TableAttribute] = []

        # Extra properties from annotations
        self.stage: Optional[str] = None
        self.is_object: Optional[str] = None
        self.api_type: Optional[str] = None

    def parse_p4rt(
        self,
        p4rt_table: Dict[str, Any],
        program: Dict[str, Any],
        all_actions: Dict[int, DashP4TableAction],
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
            table_key = DashP4TableKey.from_p4rt(p4rt_table_key)

            if self.is_object != "false":
                table_key.is_entry_key = False

            self.keys.append(table_key)

        self.keys = DashP4TableAttribute.link_ip_is_v6_vars(self.keys)

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
        self, p4rt_table: Dict[str, Any], all_actions: List[DashP4TableAction]
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

    def __merge_action_info_to_table(self, action: DashP4TableAction) -> None:
        """
        Merge objects used by an action into the table for SAI attributes generation.

        This is needed for deduplication. If the same counter is used by multiple actions, we only need to keep one
        copy of for a table, so we don't generate multiple SAI attributes.
        """
        self.__merge_action_params_to_table_params(action)
        self.__merge_action_counters_to_table_counters(action)

    def __merge_action_params_to_table_params(self, action: DashP4TableAction) -> None:
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
        self, action: DashP4TableAction
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

    def __update_table_param_object_name_reference(self, all_table_names: List[str]) -> None:
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

    #
    # Functions for generating SAI specs:
    #
    def to_sai(self) -> SaiApi:
        sai_api = SaiApi(self.name, self.name.replace('_', ' '), self.is_object != "false")
        sai_api.p4_meta.tables.append(SaiApiP4MetaTable(self.id))

        self.create_sai_action_enum(sai_api)
        self.create_sai_structs(sai_api)
        self.create_sai_attributes(sai_api)
        self.create_sai_stats(sai_api)

        return sai_api

    def create_sai_action_enum(self, sai_api: SaiApi) -> None:
        # If the table represents an SAI object, it should not have an action enum.
        # If the table has only 1 action, we don't need to create the action enum.
        if len(self.actions) <= 1 and self.is_object != "false":
            # We still need to create the p4 meta action here for generating default action code in libsai.
            if len(self.actions) == 1:
                sai_api.p4_meta.tables[0].actions["default"] = SaiApiP4MetaAction("default", self.actions[0].id)
            return

        action_enum_member_value = 0
        action_enum_members: List[SaiEnumMember] = []
        for action in self.actions:
            action_enum_member_name = f"SAI_{self.name.upper()}_ACTION_{action.name.upper()}"

            action_enum_members.append(
                SaiEnumMember(
                    name=action_enum_member_name,
                    description="",
                    value=str(action_enum_member_value),
                )
            )

            p4_meta_action = SaiApiP4MetaAction(
                name=action_enum_member_name,
                id=action.id,
            )

            for action_param in action.params:
                p4_meta_action.attr_param_id[action_param.get_sai_name(self.name)] = action_param.id

            sai_api.p4_meta.tables[0].actions[action_enum_member_name] = p4_meta_action

            action_enum_member_value += 1

        action_enum_type_name = f"sai_{self.name.lower()}_action_t"

        action_enum = SaiEnum(
            name=action_enum_type_name,
            description=f"Attribute data for #SAI_{ self.name.upper() }_ATTR_ACTION",
            members=action_enum_members,
        )
        sai_api.enums.append(action_enum)

        sai_attr_action = SaiAttribute(
            name=f"SAI_{self.name.upper()}_ATTR_ACTION",
            description="Action",
            type=action_enum_type_name,
            flags="CREATE_AND_SET",
            default=action_enum_members[0].name,
        )
        sai_api.attributes.append(sai_attr_action)


    def create_sai_structs(self, sai_api: SaiApi) -> None:
        # The entry struct is only needed for non-object tables.
        if self.is_object != "false":
            return

        sai_struct_members = [
            SaiStructEntry(
                name="switch_id",
                type=f"sai_object_id_t",
                description="Switch ID",
                objects="SAI_OBJECT_TYPE_SWITCH",
            )
        ]

        for attr in self.keys:
            if attr.skipattr != "true":
                sai_struct_members.extend(attr.to_sai_struct_entry(self.name))

        # If any match key in this table supports priority, we need to add a priority attribute.
        if any([key.match_type != "exact" for key in self.keys]) and all(
            [key.match_type != "lpm" for key in self.keys]
        ):
            priority_entry = SaiStructEntry(
                name="priority",
                description="Rule priority in table",
                type="sai_uint32_t",
            )

            sai_struct_members.append(priority_entry)

        print("Creating struct for table: " + self.name)
        sai_struct = SaiStruct(
            name=f"sai_{self.name.lower()}_t",
            description=f"Entry for {self.name.lower()}",
            members=sai_struct_members,
        )

        sai_api.structs.append(sai_struct)

    def create_sai_stats(self, sai_api: SaiApi) -> None:
        sai_api.stats = []
        for sai_stat in self.sai_stats:
            sai_api.stats.extend(sai_stat.to_sai_attribute(self.name))

    def create_sai_attributes(self, sai_api: SaiApi) -> None:
        # If the table is an object with more one key (table entry id), we need to add all the keys into the attributes.
        if self.is_object == "true" and len(self.keys) > 1:
            for key in self.keys:
                sai_api.attributes.extend(key.to_sai_attribute(self.name, create_only=True))

        # Add all the action parameters into the attributes.
        for attr in self.sai_attributes:
            if attr.skipattr != "true":
                sai_api.attributes.extend(attr.to_sai_attribute(self.name, add_action_valid_only_check=len(self.actions) > 1))

        # If the table has an counter attached, we need to create a counter attribute for it.
        # The counter attribute only counts that packets that hits any entry, but not the packet that misses all entries.
        if self.with_counters == "true":
            counter_attr = SaiAttribute(
                name=f"SAI_{self.name.upper()}_ATTR_COUNTER_ID",
                description="Attach a counter. When it is empty, then packet hits won't be counted.",
                type="sai_object_id_t",
                default="SAI_NULL_OBJECT_ID",
                object_name="SAI_OBJECT_TYPE_COUNTER",
                allow_null=True,
            )

            sai_api.attributes.append(counter_attr)

        if self.is_object == "true":
            # If any match key in this table supports priority, we need to add a priority attribute.
            if any([key.match_type != "exact" for key in self.keys]) and all(
                [key.match_type != "lpm" for key in self.keys]
            ):
                priority_attr = SaiAttribute(
                    name=f"SAI_{self.name.upper()}_ATTR_PRIORITY",
                    description="Rule priority in table",
                    type="sai_uint32_t",
                    flags="MANDATORY_ON_CREATE | CREATE_ONLY",
                )

                sai_api.attributes.append(priority_attr)

        # If any match key contains an IP address, we need to add an IP address family attribute
        # for IPv4 and IPv6 support.
        if self.ipaddr_family_attr == "true":
            ip_addr_family_attr = SaiAttribute(
                name=f"SAI_{self.name.upper()}_ATTR_IP_ADDR_FAMILY",
                description="IP address family for resource accounting",
                type="sai_ip_addr_family_t",
                flags="READ_ONLY",
                isresourcetype=True,
            )

            sai_api.attributes.append(ip_addr_family_attr)
