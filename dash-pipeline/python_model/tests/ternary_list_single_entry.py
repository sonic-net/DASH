from __table import *

def default_action():
    print("default_action executed!")

outbound_routing = Table(
    key = {
        "meta.ip_protocol" : EXACT,
        "hdr.ipv4.ihl"     : LIST
    },
    actions = [],
    default_action = default_action
)


def action0(a, b):
    print("action0 executed! parameters are:")
    print(a)
    print(b)


# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
#                 ---------       -----
#                           -----------
# 11XX  12-15
# 10XX   8-11
# 111X  14-15


outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : [
        {
            "value": 0b1100,
            "mask" : 0b1100
        },
        {
            "value": 0b1000,
            "mask" : 0b1100
        },
        {
            "value": 0b1110,
            "mask" : 0b1110
        }
    ],
    "priority" : 4,
    "action"   : action0,
    "params"   : [44, 55]
})


meta.ip_protocol = 246
hdr.ipv4 = ipv4_t()
hdr.ipv4.ihl = 15

outbound_routing.apply()
