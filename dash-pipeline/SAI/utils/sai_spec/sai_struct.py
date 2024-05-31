from typing import List
from .sai_common import SaiCommon
from .sai_struct_entry import SaiStructEntry


class SaiStruct(SaiCommon):
    """
    This class represents a single SAI struct.
    """

    def __init__(self, name: str, description: str, members: List[SaiStructEntry] = []):
        super().__init__(name, description)
        self.members: List[SaiStructEntry] = members
