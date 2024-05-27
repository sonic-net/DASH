from typing import List
from .sai_enum import SaiEnum
from .sai_api_group import SaiApiGroup
from .sai_api_extension import SaiApiExtension


class SaiSpec:
    """
    Top class of the SAI API, which holds all the SAI API groups and any top level objects.
    """

    def __init__(self):
        self.api_types: List[str] = []
        self.object_types: List[str] = []
        self.enums: List[SaiEnum] = []
        self.port_extenstion: SaiApiExtension = SaiApiExtension()
        self.api_groups: List[SaiApiGroup] = []
