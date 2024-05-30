from typing import List, Optional
from .common import *
from .dash_p4_table import DashP4Table
from ..sai_spec import SaiApiGroup


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
        self.__ignore_duplicated_tables_in_headers()

        for table in self.tables:
            table.post_parsing_process(all_table_names)
    
    def __ignore_duplicated_tables_in_headers(self) -> None:
        table_names = set()

        for table in self.tables:
            if table.name in table_names:
                table.ignored_in_header = True
            table_names.add(table.name)

    def to_sai(self) -> SaiApiGroup:
        sai_api_group = SaiApiGroup(self.app_name, "")
        sai_api_group.sai_apis = [table.to_sai() for table in self.tables if not table.ignored_in_header]
        return sai_api_group