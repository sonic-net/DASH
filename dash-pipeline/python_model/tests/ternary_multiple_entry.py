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

def action0():
    print("action0 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : {
        "value": 0b1101,
        "mask" : 0b1111
    },
    "priority" : 4,
    "action"   : action0,
    "params"   : []
})

def action1():
    print("action1 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : {
        "value": 0b0101,
        "mask" : 0b1111
    },
    "priority" : 4,
    "action"   : action1,
    "params"   : []
})

def action2():
    print("action2 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : {
        "value": 0b0101,
        "mask" : 0b1111
    },
    "priority" : 0,
    "action"   : action2,
    "params"   : []
})

def action3():
    print("action3 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : 230,
    "hdr.ipv4.ihl"     : {
        "value": 0b0101,
        "mask" : 0b1111
    },
    "priority" : 0,
    "action"   : action3,
    "params"   : []
})

def action4():
    print("action4 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : 246,
    "hdr.ipv4.ihl"     : {
        "value": 0b0101,
        "mask" : 0b1111
    },
    "priority" : 5,
    "action"   : action4,
    "params"   : []
})



meta.ip_protocol = 246
hdr.ipv4.ihl = 0b0101

outbound_routing.apply()
