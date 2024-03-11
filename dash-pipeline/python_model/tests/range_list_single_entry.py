from __table import *

def default_action():
    print("default_action executed!")

outbound_routing = Table(
    key = {
        "meta.ip_protocol" : EXACT,
        "hdr.ipv4.ihl"     : RANGE_LIST
    },
    actions = [],
    default_action = default_action
)


def action0(a, b):
    print("action0 executed! parameters are:")
    print(a)
    print(b)


# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
#     ---   -----     -----------

outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : [
        {
            "first" : 5,
            "last"  : 7
        },
        {
            "first" : 2,
            "last"  : 3
        },
        {
            "first" : 10,
            "last"  : 13
        }
    ],
    "priority" : 4,
    "action"   : action0,
    "params"   : [44, 55]
})


meta.ip_protocol = 246
hdr.ipv4 = ipv4_t()
hdr.ipv4.ihl = 11

outbound_routing.apply()
