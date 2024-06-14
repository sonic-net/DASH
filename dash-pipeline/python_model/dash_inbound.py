from dash_headers import *
from dash_service_tunnel import *
from dash_vxlan import *
from dash_flows import *
from dash_acl import *

def inbound_apply():
    flow_hit = flows.apply()["hit"]

    if meta.encap_data.original_overlay_sip != 0:
        service_tunnel_decode(meta.encap_data.original_overlay_sip,
                              meta.encap_data.original_overlay_dip)

    if not flow_hit:
        acl_apply()
        if not meta.dropped:
            _create_flows()

    vxlan_encap(meta.encap_data.underlay_dmac,
                meta.encap_data.underlay_smac,
                meta.encap_data.underlay_dip,
                meta.encap_data.underlay_sip,
                hdr.ethernet.dst_addr,
                meta.encap_data.vni)

def _create_flows():
    forward_flow = {}
    reverse_flow = {}
    timer = flow_timer(5, forward_flow, reverse_flow)

    forward_flow["meta.eni_id"] = meta.eni_id
    forward_flow["meta.src_ip_addr"] = meta.src_ip_addr
    forward_flow["meta.dst_ip_addr"] = meta.dst_ip_addr
    forward_flow["meta.ip_protocol"] = meta.ip_protocol
    forward_flow["meta.src_l4_port"] = meta.src_l4_port
    forward_flow["meta.dst_l4_port"] = meta.dst_l4_port
    forward_flow["action"] = flow_action_inbound
    forward_flow["params"] = [timer, 0, 0]

    reverse_flow["meta.eni_id"] = meta.eni_id
    reverse_flow["meta.src_ip_addr"] = meta.dst_ip_addr
    reverse_flow["meta.dst_ip_addr"] = meta.src_ip_addr
    reverse_flow["meta.ip_protocol"] = meta.ip_protocol
    reverse_flow["meta.src_l4_port"] = meta.dst_l4_port
    reverse_flow["meta.dst_l4_port"] = meta.src_l4_port
    reverse_flow["action"] = flow_action_outbound
    reverse_flow["params"] = [timer]

    flows.insert(forward_flow)
    flows.insert(reverse_flow)

    timer.start()
