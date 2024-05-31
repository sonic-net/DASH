from typing import List
from .sai_attribute import SaiAttribute


class SaiApiExtension:
    """
    The SAI APIs can be extended with additional attributes and stats.

    This class holds all the attributes and stats that is used to extend a single SAI API.
    """

    def __init__(self):
        self.attributes: List[SaiAttribute] = []
        self.stats: List[SaiAttribute] = []
