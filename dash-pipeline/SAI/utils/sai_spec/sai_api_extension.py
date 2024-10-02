from typing import List
from .sai_attribute import SaiAttribute
from . import sai_spec_utils


class SaiApiExtension:
    """
    The SAI APIs can be extended with additional attributes and stats.

    This class holds all the attributes and stats that is used to extend a single SAI API.
    """

    def __init__(self):
        self.attributes: List[SaiAttribute] = []
        self.stats: List[SaiAttribute] = []

    def finalize(self):
        _ = [attribute.finalize() for attribute in self.attributes]
        _ = [stat.finalize() for stat in self.stats]

    def merge(self, other: "SaiApiExtension"):
        sai_spec_utils.merge_sai_common_lists(self.attributes, other.attributes)
        sai_spec_utils.merge_sai_common_lists(self.stats, other.stats)
