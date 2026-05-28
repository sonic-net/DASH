from py_model.libs.__utils import *
from py_model.data_plane.dash_tunnel import *

def push_action_set_smac(overlay_smac: Annotated[int, EthernetAddress_size]):
    # not used by now
    pass

def push_action_set_dmac(overlay_dmac: Annotated[int, EthernetAddress_size]):
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.SET_DMAC
    meta.overlay_data.dmac = overlay_dmac

class do_action_set_smac:
    @classmethod
    def apply(cls):
        # not used by now
        pass

class do_action_set_dmac:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.SET_DMAC == 0):
            return
        
        hdr.customer_ethernet.dst_addr = meta.overlay_data.dmac
