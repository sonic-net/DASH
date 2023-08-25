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

def action0():
    print("action0 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b11010101,
        "prefix_len" : 8
    },
    "hdr.ipv4.ihl" : 246,
    "action"   : action0,
    "params"   : []
})

def action1():
    print("action1 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b01010101,
        "prefix_len" : 4
    },
    "hdr.ipv4.ihl" : 246,
    "action"   : action1,
    "params"   : []
})

def action2():
    print("action2 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b01010101,
        "prefix_len" : 5
    },
    "hdr.ipv4.ihl" : 246,
    "action"   : action2,
    "params"   : []
})

def action3():
    print("action3 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b01010101,
        "prefix_len" : 8
    },
    "hdr.ipv4.ihl" : 230,
    "action"   : action3,
    "params"   : []
})

def action4():
    print("action4 executed!")
outbound_routing.insert({
    "meta.ip_protocol" : {
        "value"      : 0b01010101,
        "prefix_len" : 1
    },
    "hdr.ipv4.ihl" : 246,
    "action"   : action4,
    "params"   : []
})

meta.ip_protocol = 0b01010101
hdr.ipv4.ihl = 246

outbound_routing.apply()
