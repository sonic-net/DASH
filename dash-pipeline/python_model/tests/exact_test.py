from __table import *

def default_action():
    print("default_action executed!")

outbound_routing = Table(
    key = {
        "meta.ip_protocol" : EXACT
    },
    actions = [],
    default_action = default_action
)

def action0():
    print("action0 executed!")
outbound_routing.insert({
    "meta.ip_protocol"  :  0b01111111,
    "action"            :  action0,
    "params"            :  []
})

def action1():
    print("action1 executed!")
outbound_routing.insert({
    "meta.ip_protocol"  :  0b10111111,
    "action"            :  action1,
    "params"            :  []
})

def action2():
    print("action2 executed!")
outbound_routing.insert({
    "meta.ip_protocol"  :  0b11011111,
    "action"            :  action2,
    "params"            :  []
})

def action3():
    print("action3 executed!")
outbound_routing.insert({
    "meta.ip_protocol"  :  0b11101111,
    "action"            :  action3,
    "params"            :  []
})

def action4():
    print("action4 executed!")
outbound_routing.insert({
    "meta.ip_protocol"  :  0b11110111,
    "action"            :  action4,
    "params"            :  []
})

meta.ip_protocol = 0b11110111

outbound_routing.apply()
