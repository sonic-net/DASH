from . import sai_spec_utils

class SaiCommon:
    """
    Base class for all SAI objects.
    """

    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description

    def finalize(self):
        """
        Finalize the object after all the attributes are set.
        """
        self.description = sai_spec_utils.normalize_sai_comment(self.description)

    def merge(self, other: "SaiCommon"):
        """
        Merge the other SaiCommon object into this object.
        """
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot merge {type(self)} with {type(other)}")

        self.description = other.description

    def deprecate(self) -> bool:
        """
        Deprecate this object.
        
        If the value doesn't support deprecation marking, we don't do anything
        but return False to keep it in the list.
        """
        return False
