from inspect import *
from enum import Enum
from bitarray import bitarray
from bitarray.util import int2ba
from typing import get_origin, get_args, Annotated


class packet_out:
    def __init__(self):
        self.reset()

    def reset(self):
        self.data = bitarray(endian="big")
        self.index = 0

    def emit(self, hdr):
        if hdr:
            annotations = get_annotations(type(hdr))
            for field_name, field_type in annotations.items():
                width = self._extract_bit_width(field_type, field_name) #width 48/32/16/8
                value = getattr(hdr, field_name) #Field value
                value = self._convert_to_int(value, field_name)
                if width <= 0:
                    raise ValueError(f"Field '{field_name}': bit width must be > 0")
                self.data.extend(int2ba(value, width))

    def _extract_bit_width(self, field_type, field_name) -> int:
        if get_origin(field_type) is Annotated:
            base_type, *metadata = get_args(field_type)
            return metadata[0]

        if isinstance(field_type, type) and issubclass(field_type, Enum):
            if hasattr(field_type, "__bitwidth__"):
                return field_type.__bitwidth__

        if field_type is int:
            raise ValueError(f"Field '{field_name}' is int but missing Annotated metadata")

        raise TypeError(f"Cannot determine width for field '{field_name}' of type '{field_type}'")

    def _convert_to_int(self, value, field_name) -> int:
        try:
            return value.value if isinstance(value, Enum) else int(value)
        except Exception as e:
            raise ValueError(f"Cannot convert '{value}' to int for field '{field_name}'") from e
