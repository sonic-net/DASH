from __packet_in import *
from dash_parser import *
from __vars import *
from dash_pipeline import *

def run_pipeline(pkt_bytes):
    pkt_in.reset()
    hdr.reset()
    pkt_in.set_data(pkt_bytes)
    state = dash_parser(pkt_in, hdr)
    if state == State.reject:
        raise ValueError("Parser rejected the packet")
    standard_metadata.ingress_port = 0
    meta.dropped = False
    meta.appliance_id = 0
    meta.encap_data.original_overlay_sip = 0
    meta.encap_data.original_overlay_dip = 0
    apply()
    if is_dropped(standard_metadata):
        raise ValueError("Pipeline dropped the packet")
    pkt_out = packet_out()
    dash_deparser(pkt_out, hdr)
    final_pkt = pkt_out.data + pkt_in.get_unparsed_slice()
    return final_pkt.tobytes()
