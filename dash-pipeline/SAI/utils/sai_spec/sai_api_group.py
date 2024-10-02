from typing import List
from .sai_common import SaiCommon
from .sai_api import SaiApi
from . import sai_spec_utils


class SaiApiGroup(SaiCommon):
    """
    Defines a SAI API group, which holds multiple SAI APIs.
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.api_type: str = ""
        self.sai_apis: List[SaiApi] = []

    def finalize(self):
        super().finalize()
        _ = [sai_api.finalize() for sai_api in self.sai_apis]

    def merge(self, other: "SaiCommon"):
        super().merge(other)
        self.api_type = other.api_type
        sai_spec_utils.merge_sai_common_lists(self.sai_apis, other.sai_apis)

    def deprecate(self) -> bool:
        """
        Deprecate API group.

        When deprecating the API group, we can safely remove it from the list as the
        net effect is the same as keeping it:
        - The old API type, object type and object entries will not be changed.
        - The SAI headers will not be changed, because their API groups are present.
        - The DASH libsai will not be generated anymore, but it is ok, since we will not
          use them in the BMv2 anyway.
        """
        return True
