from .sai_common import SaiCommon


class SaiAttribute(SaiCommon):
    """
    This class represents a single SAI attribute.
    """

    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        attr_value_field: str,
        default: str,
        isresourcetype: bool,
        flags: str,
        object_name: str,
    ):
        super().__init__(name, description)
        self.type: str = type
        self.attr_value_field: str = attr_value_field
        self.default: str = default
        self.isresourcetype: bool = isresourcetype
        self.flags: bool = flags
        self.object_name: str = object_name
