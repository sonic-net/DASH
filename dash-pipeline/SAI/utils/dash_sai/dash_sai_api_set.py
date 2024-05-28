from typing import List, Optional
from .common import *
from .sai_api_table import SAIAPITable


class DASHAPISet(SAIObject):
    """
    This class holds all parsed SAI API info for a specific API set, such as routing or CA-PA mapping.
    """

    def __init__(self, api_name: str):
        self.app_name: str = api_name
        self.api_type: Optional[str] = None
        self.tables: List[SAIAPITable] = []

    def add_table(self, table: SAIAPITable) -> None:
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
