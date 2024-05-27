from typing import List
from .sai_common import SaiCommon
from .sai_attribute import SaiAttribute
from .sai_enum import SaiEnum
from .sai_struct import SaiStruct


class SaiApi(SaiCommon):
    """
    Defines a SAI API, such as an object or table.
    """

    def __init__(self, name: str, description: str, is_object: bool = False):
        super().__init__(name, description)
        self.is_object: bool = is_object
        self.enums: List[SaiEnum] = []
        self.structs: List[SaiStruct] = []
        self.attributes: List[SaiAttribute] = []
        self.stats: List[SaiAttribute] = []
