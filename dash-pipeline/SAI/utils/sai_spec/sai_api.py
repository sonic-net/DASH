from typing import List
from .sai_common import SaiCommon
from .sai_attribute import SaiAttribute
from .sai_enum import SaiEnum
from .sai_struct import SaiStruct
from .sai_api_p4_meta import SaiApiP4Meta
from . import sai_spec_utils


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
        self.p4_meta: SaiApiP4Meta = SaiApiP4Meta()
    
    def finalize(self):
        super().finalize()
        _ = [enum.finalize() for enum in self.enums]
        _ = [struct.finalize() for struct in self.structs]
        _ = [attribute.finalize() for attribute in self.attributes]
        _ = [stat.finalize() for stat in self.stats]

    def merge(self, other: "SaiCommon"):
        super().merge(other)

        self.is_object = other.is_object
        sai_spec_utils.merge_sai_common_lists(self.enums, other.enums)
        sai_spec_utils.merge_sai_common_lists(self.structs, other.structs)
        sai_spec_utils.merge_sai_common_lists(self.attributes, other.attributes)
        sai_spec_utils.merge_sai_common_lists(self.stats, other.stats)
        
        # The P4 meta can be merged by replacing the old one, since it doesn't affect the ABI,
        # and the new one is always more up-to-date.
        self.p4_meta = other.p4_meta
