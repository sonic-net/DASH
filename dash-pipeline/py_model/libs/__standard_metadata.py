from typing import *
from inspect import *

class standard_metadata_t:
    egress_spec : int
        
    def __init__(self):
        self.ingress_port = 0
        self.egress_spec = 0
        self.reset()

    def reset(self):
        annotations = get_annotations(type(self))
        for k in annotations:
            setattr(self, k, None)

_DROP_PORT = 511

def mark_to_drop(standard_metadata: standard_metadata_t):
    standard_metadata.egress_spec = _DROP_PORT

def is_dropped(standard_metadata: standard_metadata_t):
    return standard_metadata.egress_spec == _DROP_PORT

def NoAction():
    pass

    def __init__(self):
        self.reset()

