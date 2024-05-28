import json
from typing import List
from .common import *
from .dash_sai_api_set import DASHAPISet
from .sai_enum import SAIEnum
from .sai_api_counter import SAIAPICounter
from .sai_api_table import SAIAPITable
from .sai_api_table_action import SAIAPITableAction
from ..p4ir import P4VarRefGraph


@sai_parser_from_p4rt
class DASHSAIExtensions(SAIObject):
    """
    This class holds all parsed SAI APIs and provides parser for the generated p4 runtime json file
    """

    def __init__(self):
        super().__init__()
        self.sai_enums: List[SAIEnum] = []
        self.sai_counters: List[SAIAPICounter] = []
        self.sai_apis: List[DASHAPISet] = []

    @staticmethod
    def from_p4rt_file(
        p4rt_json_file_path: str, ignore_tables: List[str], var_ref_graph: P4VarRefGraph
    ) -> "DASHSAIExtensions":
        print("Parsing SAI APIs BMv2 P4Runtime Json file: " + p4rt_json_file_path)
        with open(p4rt_json_file_path) as p4rt_json_file:
            p4rt = json.load(p4rt_json_file)

        return DASHSAIExtensions.from_p4rt(
            p4rt,
            name="dash_sai_apis",
            ignore_tables=ignore_tables,
            var_ref_graph=var_ref_graph,
        )

    def parse_p4rt(
        self, p4rt_value: Dict[str, Any], ignore_tables: List[str], var_ref_graph
    ) -> None:
        self.__parse_sai_enums_from_p4rt(p4rt_value)
        self.__parse_sai_counters_from_p4rt(p4rt_value, var_ref_graph)
        self.__parse_sai_apis_from_p4rt(p4rt_value, ignore_tables)

    def __parse_sai_enums_from_p4rt(self, p4rt_value: Dict[str, Any]) -> None:
        all_p4rt_enums = p4rt_value[TYPE_INFO_TAG][SERIALIZABLE_ENUMS_TAG]
        self.sai_enums = [
            SAIEnum.from_p4rt(enum_value, name=enum_name)
            for enum_name, enum_value in all_p4rt_enums.items()
        ]

    def __parse_sai_counters_from_p4rt(
        self, p4rt_value: Dict[str, Any], var_ref_graph: P4VarRefGraph
    ) -> None:
        all_p4rt_counters = p4rt_value[COUNTERS_TAG]
        for p4rt_counter in all_p4rt_counters:
            counter = SAIAPICounter.from_p4rt(p4rt_counter, var_ref_graph)
            self.sai_counters.extend(counter.generate_counter_sai_attributes())

    def __parse_sai_apis_from_p4rt(
        self, program: Dict[str, Any], ignore_tables: List[str]
    ) -> None:
        # Group all counters by action name.
        counters_by_action_name = {}
        for counter in self.sai_counters:
            for action_name in counter.param_actions:
                counters_by_action_name.setdefault(action_name, []).append(counter)

        # Parse all actions.
        actions = self.__parse_sai_table_action(
            program[ACTIONS_TAG], self.sai_enums, counters_by_action_name
        )

        # Parse all tables into SAI API sets.
        tables = sorted(program[TABLES_TAG], key=lambda k: k[PREAMBLE_TAG][NAME_TAG])
        for table in tables:
            sai_api_table_data = SAIAPITable.from_p4rt(
                table, program, actions, ignore_tables
            )
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

    def __parse_sai_table_action(
        self,
        p4rt_actions: Dict[str, Any],
        sai_enums: List[SAIEnum],
        counters_by_action_name: Dict[str, List[SAIAPICounter]],
    ) -> Dict[int, SAIAPITableAction]:
        action_data = {}
        for p4rt_action in p4rt_actions:
            action = SAIAPITableAction.from_p4rt(
                p4rt_action, sai_enums, counters_by_action_name
            )
            action_data[action.id] = action
        return action_data

    def post_parsing_process(self) -> None:
        all_table_names = [table.name for api in self.sai_apis for table in api.tables]
        for sai_api in self.sai_apis:
            sai_api.post_parsing_process(all_table_names)
