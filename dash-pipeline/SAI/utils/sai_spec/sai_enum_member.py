from typing import Any, Dict
from .sai_common import SaiCommon


class SaiEnumMember(SaiCommon):
    """
    This class represents a single SAI enum member.
    """

    def __init__(self, name: str, description: str, value: str):
        super().__init__(name, description)
        self.value: str = value

    def merge(self, other: "SaiCommon"):
        super().merge(other)
        self.value = other.value