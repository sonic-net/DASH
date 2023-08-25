from dash_headers import *
from __table import *

# Send packet on different/same port it arrived based on routing
def set_nhop(next_hop_id : Annotated[int, 9]):
    standard_metadata.egress_spec = next_hop_id

# Send packet on same port it arrived (echo) by default
def def_act():
    standard_metadata.egress_spec = standard_metadata.ingress_port

# TODO: To add structural annotations (example: @Sai[skipHeaderGen=true])
underlay_routing = Table(
    key = {
        "meta.dst_ip_addr" : LPM
    },
    actions = [
        set_nhop,
        def_act
    ],
    default_action=def_act
)

def underlay_apply():
    underlay_routing.apply()
