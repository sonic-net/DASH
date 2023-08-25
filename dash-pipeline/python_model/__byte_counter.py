from __vars import *

class byte_counter:
    def __init__(self, size):
        self.counters = [0] * size

    def count(self, index):
        self.counters[index] += pkt_in.get_pkt_size()
