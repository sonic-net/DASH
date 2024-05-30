class SAITypeInfo:
    def __init__(
        self,
        name: str,
        sai_attribute_value_field: str,
        default: str = None,
        is_enum: bool = False,
    ):
        self.name: str = name
        self.sai_attribute_value_field: str = sai_attribute_value_field
        self.default: str = default
        self.is_enum: bool = is_enum
