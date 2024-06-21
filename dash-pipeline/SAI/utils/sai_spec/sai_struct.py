from typing import List
from .sai_common import SaiCommon
from .sai_struct_entry import SaiStructEntry
from . import sai_spec_utils

class SaiStruct(SaiCommon):
    """
    This class represents a single SAI struct.
    """

    def __init__(self, name: str, description: str, members: List[SaiStructEntry] = []):
        super().__init__(name, description)
        self.members: List[SaiStructEntry] = members
    
    def finalize(self):
        super().finalize()
        _ = [member.finalize() for member in self.members]

    def merge(self, other: "SaiCommon"):
        super().merge(other)
        sai_spec_utils.merge_sai_common_lists(self.members, other.members)