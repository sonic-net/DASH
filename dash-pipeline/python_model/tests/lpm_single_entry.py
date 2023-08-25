from __table import *

def default_action():
    print("default_action executed!")

outbound_routing = Table(
    key = {
        "meta.ip_protocol" : LPM,
        "hdr.ipv4.ihl"     : EXACT
    },
    actions = [],
    default_action = default_action
)


def action0(a, b):
    print("action0 executed! parameters are:")
    print(a)
    print(b)

outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b10101010,
        "prefix_len" : 4
    },
    "hdr.ipv4.ihl" : 12,
    "action"   : action0,
    "params"   : [44, 55]
})


meta.ip_protocol = 0b10101010
hdr.ipv4.ihl = 12

outbound_routing.apply()
