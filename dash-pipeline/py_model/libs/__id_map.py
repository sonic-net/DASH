
UNSPECIFIED = 0x00
ACTION = 0x01
TABLE = 0x02
COUNTER = 0x12
DIRECT_COUNTER = 0x13
# VALUE_SET = PyIds_Prefix_VALUE_SET
# CONTROLLER_HEADER = PyIds_Prefix_CONTROLLER_HEADER
# PSA_EXTERNS_START = PyIds_Prefix_PSA_EXTERNS_START
# ACTION_PROFILE = PyIds_Prefix_ACTION_PROFILE
# METER = PyIds_Prefix_METER
# DIRECT_METER = PyIds_Prefix_DIRECT_METER
# REGISTER = PyIds_Prefix_REGISTER
# DIGEST = PyIds_Prefix_DIGEST
# OTHER_EXTERNS_START = PyIds_Prefix_OTHER_EXTERNS_START
# MAX = PyIds_Prefix_MAX

# Global registries
table_ids = {}          # {tid: table_name}
table_objs = {}         # {table_name: Table}
action_ids = {}         # {aid: action_name}
action_objs = {}        # {action_name: callable}
counter_ids = {}        # {cid: counter_name}
direct_counter_ids = {} # {dcid: counter_name}

def compute_hash(key: str) -> int:
    key_bytes = key.encode('utf-8')
    hash_val = 0
    for b in key_bytes:
        hash_val = (hash_val + b) & 0xFFFFFFFF
        hash_val = (hash_val + (hash_val << 10)) & 0xFFFFFFFF
        hash_val = (hash_val ^ (hash_val >> 6)) & 0xFFFFFFFF
    hash_val = (hash_val + (hash_val << 3)) & 0xFFFFFFFF
    hash_val = (hash_val ^ (hash_val >> 11)) & 0xFFFFFFFF
    hash_val = (hash_val + (hash_val << 15)) & 0xFFFFFFFF
    return hash_val

def gen_symbol_id(name: str, prefix: int) -> int:
    """
    Generate a P4Runtime ID just like p4c:
      - prefix = 8-bit object type code (e.g., 0x01 action, 0x02 table).
      - suffix = 24-bit Jenkins hash of name.
      - ID = (prefix << 24) | suffix
    """
    x = compute_hash(name)
    suffix = x & 0xFFFFFF
    id = (prefix << 24) | suffix
    return id 
