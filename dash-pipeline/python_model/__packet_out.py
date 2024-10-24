from inspect import *
from bitarray import *
from bitarray.util import *

class packet_out:
    def __init__(self):
        self.data = bitarray(endian="big")

    def emit(self, hdr):
        if hdr:
            annotations = get_annotations(type(hdr))
            for k in annotations:
                width = annotations[k].__metadata__[0]
                value = getattr(hdr, k)
                self.data.extend(int2ba(value, width))
