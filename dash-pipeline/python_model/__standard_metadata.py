class standard_metadata_t:
    egress_spec : int

_DROP_PORT = 511

def mark_to_drop(standard_metadata: standard_metadata_t):
    standard_metadata.egress_spec = _DROP_PORT

def is_dropped(standard_metadata: standard_metadata_t):
    return standard_metadata.egress_spec == _DROP_PORT

def NoAction():
    pass
