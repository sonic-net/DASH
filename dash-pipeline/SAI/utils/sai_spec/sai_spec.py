from typing import List
from .sai_api_group import SaiApiGroup


class SaiSpec:
    """
    Top class of the SAI API, which holds all the SAI API groups and any top level objects.
    """

    def __init__(self):
        self.api_groups: List[SaiApiGroup] = []

    def add_api_group(self, api_group: SaiApiGroup):
        self.api_groups.append(api_group)