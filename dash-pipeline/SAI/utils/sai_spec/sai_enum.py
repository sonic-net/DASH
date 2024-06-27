from typing import List
from .sai_common import SaiCommon
from .sai_enum_member import SaiEnumMember
from . import sai_spec_utils


class SaiEnum(SaiCommon):
    """
    This class represents a single SAI enum and holds all enum values.
    """

    def __init__(self, name: str, description: str, members: List[SaiEnumMember] = []):
        super().__init__(name, description)
        self.members: List[SaiEnumMember] = members

    def finalize(self):
        super().finalize()
        _ = [member.finalize() for member in self.members]

    def merge(self, other: "SaiCommon"):
        super().merge(other)
        sai_spec_utils.merge_sai_common_lists(self.members, other.members)
