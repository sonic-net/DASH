import json
from typing import List
from .common import *
from .dash_p4_table_group import DashP4TableGroup
from .dash_p4_enum import DashP4Enum
from .dash_p4_counter import DashP4Counter
from .dash_p4_table import DashP4Table
from .dash_p4_table_action import DashP4TableAction
from ..p4ir import P4VarRefGraph
from ..sai_spec import *


@dash_p4rt_parser
class DashP4SAIExtensions(DashP4Object):
    """
    This class holds all parsed SAI APIs and provides parser for the generated p4 runtime json file
    """

    def __init__(self):
        super().__init__()
        self.enums: List[DashP4Enum] = []
        self.counters: List[DashP4Counter] = []
        self.table_groups: List[DashP4TableGroup] = []

    @staticmethod
    def from_p4rt_file(
        p4rt_json_file_path: str, ignore_tables: List[str], var_ref_graph: P4VarRefGraph
    ) -> "DashP4SAIExtensions":
        print("Parsing SAI APIs BMv2 P4Runtime Json file: " + p4rt_json_file_path)
        with open(p4rt_json_file_path) as p4rt_json_file:
            p4rt = json.load(p4rt_json_file)

        return DashP4SAIExtensions.from_p4rt(
            p4rt,
            name="dash_sai_apis",
            ignore_tables=ignore_tables,
            var_ref_graph=var_ref_graph,
        )

    def parse_p4rt(
        self, p4rt_value: Dict[str, Any], ignore_tables: List[str], var_ref_graph
    ) -> None:
        self.__parse_enums_from_p4rt(p4rt_value)
        self.__parse_counters_from_p4rt(p4rt_value, var_ref_graph)
        self.__parse_dash_apis_from_p4rt(p4rt_value, ignore_tables)

    def __parse_enums_from_p4rt(self, p4rt_value: Dict[str, Any]) -> None:
        all_p4rt_enums = p4rt_value[TYPE_INFO_TAG][SERIALIZABLE_ENUMS_TAG]
        self.enums = [
            DashP4Enum.from_p4rt(enum_value, name=enum_name)
            for enum_name, enum_value in all_p4rt_enums.items()
        ]

    def __parse_counters_from_p4rt(
        self, p4rt_value: Dict[str, Any], var_ref_graph: P4VarRefGraph
    ) -> None:
        all_p4rt_counters = p4rt_value[COUNTERS_TAG]
        for p4rt_counter in all_p4rt_counters:
            counter = DashP4Counter.from_p4rt(p4rt_counter, var_ref_graph)
            self.counters.extend(counter.generate_counter_sai_attributes())

    def __parse_dash_apis_from_p4rt(
        self, program: Dict[str, Any], ignore_tables: List[str]
    ) -> None:
        # Group all counters by action name.
        counters_by_action_name: Dict[str, List[DashP4Counter]] = {}
        for counter in self.counters:
            for action_name in counter.param_actions:
                counters_by_action_name.setdefault(action_name, []).append(counter)

        # Parse all actions.
        actions = self.__parse_sai_table_action(
            program[ACTIONS_TAG], self.enums, counters_by_action_name
        )

        # Parse all tables into SAI APIs
        tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
        for table in tables:
            sai_api_table_data = DashP4Table.from_p4rt(
                table, program, actions, ignore_tables
            )
            if sai_api_table_data.ignored:
                continue

            for table_group in self.table_groups:
                if table_group.app_name == sai_api_table_data.api_name:
                    table_group.add_table(sai_api_table_data)
                    break
            else:
                new_api = DashP4TableGroup(sai_api_table_data.api_name)
                new_api.add_table(sai_api_table_data)
                self.table_groups.append(new_api)

        # Sort all parsed tables by API order, so we can always generate the APIs in the same order for keeping ABI compatibility.
        for table_group in self.table_groups:
            table_group.tables.sort(key=lambda x: x.order)

    def __parse_sai_table_action(
        self,
        p4rt_actions: Dict[str, Any],
        sai_enums: List[DashP4Enum],
        counters_by_action_name: Dict[str, List[DashP4Counter]],
    ) -> Dict[int, DashP4TableAction]:
        action_data = {}
        for p4rt_action in p4rt_actions:
            action = DashP4TableAction.from_p4rt(
                p4rt_action, sai_enums, counters_by_action_name
            )
            action_data[action.id] = action
        return action_data

    def post_parsing_process(self) -> None:
        all_table_names = [table.name for api in self.table_groups for table in api.tables]
        for table_group in self.table_groups:
            table_group.post_parsing_process(all_table_names)

    #
    # Functions for generating SAI specs:
    #
    def to_sai(self) -> SaiSpec:
        sai_spec = SaiSpec()
        sai_spec.api_groups = [api_group.to_sai() for api_group in self.table_groups]

        self.create_sai_api_types(sai_spec)
        self.create_sai_object_types(sai_spec)
        self.create_sai_object_entries(sai_spec)
        self.create_sai_enums(sai_spec)
        self.create_sai_port_counters(sai_spec.port_extenstion)

        return sai_spec
    
    def create_sai_api_types(self, sai_spec: SaiSpec):
        for table_group in self.table_groups:
            sai_spec.api_types.append(f"SAI_API_{table_group.app_name.upper()}")

    def create_sai_object_types(self, sai_spec: SaiSpec):
        for table_group in self.table_groups:
            for table in table_group.tables:
                if table.ignored_in_header:
                    continue

                sai_spec.object_types.append(f"SAI_OBJECT_TYPE_{table.name.upper()}")
    
    def create_sai_object_entries(self, sai_spec: SaiSpec):
        for table_group in self.table_groups:
            for table in table_group.tables:
                if table.ignored_in_header:
                    continue

                if table.is_object != "false":
                    continue

                object_entry = SaiStructEntry(
                    name=table.name,
                    description=f"Object entry for DASH API {table.name}",
                    type=f"sai_{table.name}_t",
                    valid_only=f"object_type == SAI_OBJECT_TYPE_{table.name.upper()},"
                )

                sai_spec.object_entries.append(object_entry)
    
    def create_sai_enums(self, sai_spec: SaiSpec):
        for enum in self.enums:
            sai_spec.enums.append(enum.to_sai())

    def create_sai_port_counters(self, api_ext: SaiApiExtension) -> None:
        for counter in self.counters:
            # If the counter is associated to any table actions, the counter will be generated as part of that table.
            # Otherwise, the counters will be generated as part of the port level counter or stats.
            if len(counter.param_actions) > 0:
                continue

            sai_counters = counter.to_sai_attribute("port")

            if counter.attr_type != "stats":
                api_ext.attributes.extend(sai_counters)
            else:
                api_ext.stats.extend(sai_counters)