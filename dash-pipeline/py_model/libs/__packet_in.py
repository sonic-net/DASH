from enum import Enum
from bitarray import bitarray
from bitarray.util import ba2int
from inspect import get_annotations
from typing import get_origin, get_args, Annotated

class packet_in:
    def __init__(self):
        self.reset()

    def reset(self):
        self.data = bitarray(endian="big")
        self.index = 0

    def set_data(self, data: bytes):
        self.data.frombytes(data)

    def extract(self, hdr_type):
        hdr = hdr_type()
        annotations = get_annotations(hdr_type)
        for field_name, field_type in annotations.items():
            width = self._extract_bit_width(field_type, field_name)

            if self.index + width > len(self.data):
                return None  # Not enough bits left

            raw_value = ba2int(self.data[self.index : self.index + width])
            value = self._convert_from_int(raw_value, field_type, field_name)

            setattr(hdr, field_name, value)
            self.index += width

        return hdr

    def get_pkt_size(self) -> int:
        return len(self.data) // 8

    def get_unparsed_slice(self) -> bitarray:
        return self.data[self.index:]

    # ------------------- Internal helpers -------------------

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

    def _convert_from_int(self, value: int, field_type, field_name):
        try:
            # Handle Annotated fields
            if get_origin(field_type) is Annotated:
                base_type, *_ = get_args(field_type)
                if base_type is int:
                    return value
                if issubclass(base_type, Enum):
                    return base_type(value)

            # Handle Enums directly
            if isinstance(field_type, type) and issubclass(field_type, Enum):
                return field_type(value)

            # Plain int
            if field_type is int:
                return value

        except Exception as e:
            raise ValueError(f"Cannot map int '{value}' to field '{field_name}' of type '{field_type}'") from e

        raise TypeError(f"Unsupported field type '{field_type}' for field '{field_name}'")
