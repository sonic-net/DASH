from typing import List
from .sai_api_group import SaiApiGroup
from .sai_api_extension import SaiApiExtension


class SaiSpec:
    """
    Top class of the SAI API, which holds all the SAI API groups and any top level objects.
    """

    def __init__(self):
        self.api_groups: List[SaiApiGroup] = []
        self.port_extenstion: SaiApiExtension = SaiApiExtension()
