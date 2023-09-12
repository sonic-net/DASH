from dash_headers import *
from __table import *
from __sai_keys import *

# The values in this context have been sourced from the 'saiswitch.h' file and 
# have been manually designated to maintain alignment with enum values specified in the SAI commit <d8d40b4>.
SAI_PACKET_ACTION_DROP = 0
SAI_PACKET_ACTION_FORWARD = 1

# Send packet on different/same port it arrived based on routing
def set_nhop(next_hop_id : Annotated[int, 9]):
    standard_metadata.egress_spec = next_hop_id

def pkt_act(packet_action: Annotated[int, 9], next_hop_id: Annotated[int, 9]):
    if packet_action == SAI_PACKET_ACTION_DROP:
        # Drops the packet
        meta.dropped = True
    elif packet_action == SAI_PACKET_ACTION_FORWARD:
        # Forwards the packet on different/same port it arrived based on routing
        set_nhop(next_hop_id)

# Send packet on same port it arrived (echo) by default
def def_act():
    standard_metadata.egress_spec = standard_metadata.ingress_port

# TODO: To add structural annotations (example: @Sai[skipHeaderGen=true])
route = Table(
    key = {
        "meta.dst_ip_addr": (LPM, {SAI_KEY_NAME : "destination"})
    },
    actions = [
        pkt_act,
        (def_act, {DEFAULT_ONLY : True})
    ],
    api_name = "route"
)

def underlay_apply():
    route.apply()
