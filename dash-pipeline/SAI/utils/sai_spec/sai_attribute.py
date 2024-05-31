from typing import Optional
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
        attr_value_field: Optional[str] = None,
        default: Optional[str] = None,
        isresourcetype: bool = False,
        flags: str = "CREATE_AND_SET",
        object_name: Optional[str] = None,
        allow_null: bool = False,
        valid_only: Optional[str] = None,
        deprecated: Optional[bool] = None,
    ):
        super().__init__(name, description)
        self.type = type
        self.attr_value_field = attr_value_field
        self.default = default
        self.isresourcetype = isresourcetype
        self.flags = flags
        self.object_name = object_name
        self.allow_null = allow_null
        self.valid_only = valid_only
        self.deprecated = deprecated
