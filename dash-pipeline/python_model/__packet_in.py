from inspect import *
from bitarray import *
from bitarray.util import *

class packet_in:
    def __init__(self):
        self.reset()

    def reset(self):
        self.data  = bitarray(endian="big")
        self.index = 0

    def set_data(self, data: bytes):
        self.data.frombytes(data)

    def extract(self, hdr_type):
        hdr = hdr_type()
        annotations = get_annotations(hdr_type)
        for k in annotations:
            width = annotations[k].__metadata__[0]
            if self.index + width > len(self.data):
                return None
            value = ba2int(self.data[self.index : self.index + width])
            setattr(hdr, k, value)
            self.index += width
        return hdr

    def get_pkt_size(self):
        return int(len(self.data) / 8)

    def get_unparsed_slice(self):
        return self.data[self.index:]
