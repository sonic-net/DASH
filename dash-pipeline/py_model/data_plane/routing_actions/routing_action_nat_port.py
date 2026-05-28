from py_model.libs.__utils import *

def push_action_snat_port(sport: Annotated[int, 16]):
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.SNAT_PORT
    meta.overlay_data.sport = sport
    
def push_action_dnat_port(dport: Annotated[int, 16]):
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.DNAT_PORT
    meta.overlay_data.dport = dport

class do_action_snat_port:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.SNAT_PORT == 0):
            return
        
        if hdr.customer_tcp:
            hdr.customer_tcp.src_port = meta.overlay_data.sport
        elif hdr.customer_udp:
            hdr.customer_udp.src_port = meta.overlay_data.sport

class do_action_dnat_port:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.DNAT_PORT == 0):
            return
        
        if hdr.customer_tcp:
            hdr.customer_tcp.dst_port = meta.overlay_data.dport
        elif hdr.customer_udp:
            hdr.customer_udp.dst_port = meta.overlay_data.dport
