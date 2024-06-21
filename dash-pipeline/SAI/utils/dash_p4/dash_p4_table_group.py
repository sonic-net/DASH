from typing import List, Optional
from .common import *
from .dash_p4_table import DashP4Table
from ..sai_spec import SaiApiGroup, SaiApi


class DashP4TableGroup(DashP4Object):
    """
    This class holds all parsed DASH p4 API info for a specific API group, such as routing or CA-PA mapping.
    """

    def __init__(self, api_name: str):
        self.app_name: str = api_name
        self.api_type: Optional[str] = None
        self.tables: List[DashP4Table] = []

    def add_table(self, table: DashP4Table) -> None:
        if self.api_type == None:
            self.api_type = table.api_type
        elif self.api_type != table.api_type:
            raise ValueError(
                f"API type mismatch: CurrentType = {self.api_type}, NewTableAPIType = {table.api_type}"
            )

        self.tables.append(table)

    def post_parsing_process(self, all_table_names: List[str]) -> None:
        for table in self.tables:
            table.post_parsing_process(all_table_names)

    def to_sai(self) -> SaiApiGroup:
        sai_api_list: List[SaiApi] = []
        sai_api_map: Dict[str, SaiApi] = {}

        for table in self.tables:
            sai_api = table.to_sai()

            if table.name in sai_api_map:
                table.ignored_in_header = True
                sai_api_map[table.name].p4_meta.tables.extend(sai_api.p4_meta.tables)
            else:
                sai_api_map[table.name] = sai_api
                sai_api_list.append(sai_api)

        sai_api_group = SaiApiGroup(self.app_name, self.app_name.replace("_", " "))
        sai_api_group.api_type = "overlay" if self.api_type == None else self.api_type
        sai_api_group.sai_apis = sai_api_list

        return sai_api_group
