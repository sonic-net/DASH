from __table import *

def set_acl_outcome(allow: Annotated[int, 1], terminate: Annotated[int, 1]):
    meta.acl_outcome_allow = allow
    meta.acl_outcome_terminate = terminate

def default_action():
    print("default_action executed!")

acl = Table(
    key = {
        "meta.dash_acl_group_id" : EXACT,
        "meta.src_ip_addr"  : LIST,
        "meta.dst_ip_addr"  : LIST,
        "meta.src_l4_port"  : RANGE_LIST,
        "meta.dst_l4_port"  : RANGE_LIST,
        "meta.ip_protocol"  : LIST
    },
    actions = [],
    default_action=default_action
)

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0x0A000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x14000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x0A00000A,
            "mask"  : 0xFFFFFFFF
        },
        {
            "value" : 0x0A00000B,
            "mask"  : 0xFFFFFFFF
        },
        {
            "value" : 0x0A00000C,
            "mask"  : 0xFFFFFFFF
        },
        {
            "value" : 0x0A00000D,
            "mask"  : 0xFFFFFFFF
        },
        {
            "value" : 0x0A00000E,
            "mask"  : 0xFFFFFFFF
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0x06,
            "mask"  : 0xFF
        }
    ],
    "priority" : 0,
    "action"   : set_acl_outcome,
    "params"   : [1, 0]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0x0A000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x14000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x0A0000C8,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0x06,
            "mask"  : 0xFF
        }
    ],
    "priority" : 1,
    "action"   : set_acl_outcome,
    "params"   : [1, 0]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0x0A000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x14000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x0A0000C9,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0x06,
            "mask"  : 0xFF
        }
    ],
    "priority" : 2,
    "action"   : set_acl_outcome,
    "params"   : [0, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0x0A000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x14000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x0A0000CA,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0x06,
            "mask"  : 0xFF
        }
    ],
    "priority" : 3,
    "action"   : set_acl_outcome,
    "params"   : [1, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0x0A000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x14000000,
            "mask"  : 0xFFFFFF00
        },
        {
            "value" : 0x1E000000,
            "mask"  : 0xFFFFFF00
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x0A0000CB,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0x06,
            "mask"  : 0xFF
        }
    ],
    "priority" : 4,
    "action"   : set_acl_outcome,
    "params"   : [1, 0]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x08080808,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 5,
    "action"   : set_acl_outcome,
    "params"   : [0, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x08080808,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 6,
    "action"   : set_acl_outcome,
    "params"   : [1, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0x09090909,
            "mask"  : 0xFFFFFFFF
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 7,
    "action"   : set_acl_outcome,
    "params"   : [1, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 8,
    "action"   : set_acl_outcome,
    "params"   : [0, 0]
})



meta.dash_acl_group_id = 1
meta.src_ip_addr = 0x0A000064
meta.dst_ip_addr = 0x01010102
meta.src_l4_port = 56
meta.dst_l4_port = 99
meta.ip_protocol = 0x06



acl.apply()
