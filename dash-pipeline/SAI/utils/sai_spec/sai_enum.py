from typing import List
from .sai_common import SaiCommon
from .sai_enum_member import SaiEnumMember


class SaiEnum(SaiCommon):
    """
    This class represents a single SAI enum and holds all enum values.
    """

    def __init__(self, name: str, description: str, members: List[SaiEnumMember] = []):
        super().__init__(name, description)
        self.members: List[SaiEnumMember] = members
