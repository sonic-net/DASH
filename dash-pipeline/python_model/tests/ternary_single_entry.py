from __table import *

def default_action():
    print("default_action executed!")

outbound_routing = Table(
    key = {
        "meta.ip_protocol" : EXACT,
        "hdr.ipv4.ihl"     : TERNARY
    },
    actions = [],
    default_action = default_action
)


def action0(a, b):
    print("action0 executed! parameters are:")
    print(a)
    print(b)

outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : {
        "value": 0b0101,
        "mask" : 0b1111
    },
    "priority" : 4,
    "action"   : action0,
    "params"   : [44, 55]
})


meta.ip_protocol = 246
hdr.ipv4.ihl = 0b0101

outbound_routing.apply()
