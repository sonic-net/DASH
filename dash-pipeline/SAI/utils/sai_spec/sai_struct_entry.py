from typing import Optional
from .sai_common import SaiCommon


class SaiStructEntry(SaiCommon):
    """
    This class represents a single SAI struct entry.
    """

    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        objects: Optional[str] = None,
        valid_only: Optional[str] = None,
    ):
        super().__init__(name, description)
        self.type = type
        self.objects = objects
        self.valid_only = valid_only

    def merge(self, other: "SaiCommon"):
        super().merge(other)
        self.__dict__.update(other.__dict__)