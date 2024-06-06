from typing import List
from .sai_common import SaiCommon
from .sai_api import SaiApi


class SaiApiGroup(SaiCommon):
    """
    Defines a SAI API group, which holds multiple SAI APIs.
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.sai_apis: List[SaiApi] = []
