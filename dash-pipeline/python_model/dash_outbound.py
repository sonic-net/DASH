from dash_headers import *
from dash_service_tunnel import *
from __table import *
from dash_vxlan import *
from dash_acl import *
from dash_flows import *
from __sai_keys import *

def set_route_meter_attrs(meter_policy_en : Annotated[int, 1],
                          meter_class     : Annotated[int, 16]):
    meta.meter_policy_en = meter_policy_en
    meta.route_meter_class = meter_class

def route_vnet(dst_vnet_id     : Annotated[int, 16],
               meter_policy_en : Annotated[int, 1],
               meter_class     : Annotated[int, 16]):
    meta.dst_vnet_id = dst_vnet_id
    set_route_meter_attrs(meter_policy_en, meter_class)

def route_vnet_direct(dst_vnet_id            : Annotated[int, 16],
                      is_overlay_ip_v4_or_v6 : Annotated[int, 1],
                      overlay_ip             : Annotated[int, 128],
                      meter_policy_en        : Annotated[int, 1],
                      meter_class            : Annotated[int, 16]):
    meta.dst_vnet_id = dst_vnet_id
    meta.lkup_dst_ip_addr = overlay_ip
    meta.is_lkup_dst_ip_v6 = is_overlay_ip_v4_or_v6
    set_route_meter_attrs(meter_policy_en, meter_class)

def route_direct(meter_policy_en : Annotated[int, 1],
                 meter_class     : Annotated[int, 16]):
    set_route_meter_attrs(meter_policy_en, meter_class)
    # send to underlay router without any encap

def drop():
    meta.dropped = True

def route_service_tunnel(is_overlay_dip_v4_or_v6      : Annotated[int, 1],
                         overlay_dip                  : Annotated[int, 128],
                         is_overlay_dip_mask_v4_or_v6 : Annotated[int, 1],
                         overlay_dip_mask             : Annotated[int, 128],
                         is_overlay_sip_v4_or_v6      : Annotated[int, 1],
                         overlay_sip                  : Annotated[int, 128],
                         is_overlay_sip_mask_v4_or_v6 : Annotated[int, 1],
                         overlay_sip_mask             : Annotated[int, 128],
                         is_underlay_dip_v4_or_v6     : Annotated[int, 1],
                         underlay_dip                 : Annotated[int, 128],
                         is_underlay_sip_v4_or_v6     : Annotated[int, 1],
                         underlay_sip                 : Annotated[int, 128],
                         dash_encapsulation           : Annotated[int, 16],
                         tunnel_key                   : Annotated[int, 24],
                         meter_policy_en              : Annotated[int, 1],
                         meter_class                  : Annotated[int, 16]):
    # Assume the overlay addresses provided are always IPv6 and the original are IPv4
    # assert(is_overlay_dip_v4_or_v6 == 1 && is_overlay_sip_v4_or_v6 == 1);
    # assert(is_overlay_dip_mask_v4_or_v6 == 1 && is_overlay_sip_mask_v4_or_v6 == 1);
    # assert(is_underlay_dip_v4_or_v6 != 1 && is_underlay_sip_v4_or_v6 != 1);
    meta.encap_data.original_overlay_dip = hdr.ipv4.src_addr
    meta.encap_data.original_overlay_sip = hdr.ipv4.dst_addr

    service_tunnel_encode(overlay_dip,
                          overlay_dip_mask,
                          overlay_sip,
                          overlay_sip_mask)

    # encapsulation will be done in apply block based on dash_encapsulation
    if underlay_dip == 0:
        meta.encap_data.underlay_dip = meta.encap_data.original_overlay_dip
    else:
        meta.encap_data.underlay_dip = underlay_dip
    
    if underlay_sip == 0:
        meta.encap_data.underlay_sip = meta.encap_data.original_overlay_sip
    else:
        meta.encap_data.underlay_sip = underlay_sip

    meta.encap_data.overlay_dmac = hdr.ethernet.dst_addr
    meta.encap_data.dash_encapsulation = dash_encapsulation
    meta.encap_data.service_tunnel_key = tunnel_key
    set_route_meter_attrs(meter_policy_en, meter_class)

outbound_routing = Table(
    key = {
        "meta.eni_id"          : (EXACT,  {SAI_KEY_NAME: "eni_id"}),
        "meta.is_overlay_ip_v6": (EXACT,  {SAI_KEY_NAME: "is_destination_v4_or_v6"}),
        "meta.dst_ip_addr"     : (LPM,    {SAI_KEY_NAME: "destination"})
    },
    actions = [
       route_vnet,
       route_vnet_direct,
       route_direct,
       route_service_tunnel,
       drop
    ],
    default_action = drop,
    per_entry_stats = True
)

def set_tunnel_mapping(underlay_dip         : Annotated[int, 32],
                       overlay_dmac         : Annotated[int, 48],
                       use_dst_vnet_vni     : Annotated[int, 1],
                       meter_class          : Annotated[int, 16],
                       meter_class_override : Annotated[int, 1]):
    if use_dst_vnet_vni == 1:
        meta.vnet_id = meta.dst_vnet_id
    meta.encap_data.overlay_dmac = overlay_dmac
    meta.encap_data.underlay_dip = underlay_dip
    meta.mapping_meter_class = meter_class
    meta.mapping_meter_class_override = meter_class_override

outbound_ca_to_pa = Table(
    key = {
        "meta.dst_vnet_id"      : (EXACT, {SAI_KEY_NAME: "dst_vnet_id"}),
        "meta.is_lkup_dst_ip_v6": (EXACT, {SAI_KEY_NAME: "is_dip_v4_or_v6"}),
        "meta.lkup_dst_ip_addr" : (EXACT, {SAI_KEY_NAME: "dip"})
    },
    actions = [
       set_tunnel_mapping,
       (drop, {DEFAULT_ONLY : True})
    ],
    default_action = drop,
    per_entry_stats = True
)

def set_vnet_attrs(vni: Annotated[int, 24]):
    meta.encap_data.vni = vni

vnet = Table(
    key = {
        "meta.vnet_id": EXACT
    },
    actions = [
       set_vnet_attrs
    ]
)

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
    forward_flow["action"] = flow_action_outbound
    forward_flow["params"] = [timer]

    reverse_flow["meta.eni_id"] = meta.eni_id
    reverse_flow["meta.src_ip_addr"] = meta.dst_ip_addr
    reverse_flow["meta.dst_ip_addr"] = meta.src_ip_addr
    reverse_flow["meta.ip_protocol"] = meta.ip_protocol
    reverse_flow["meta.src_l4_port"] = meta.dst_l4_port
    reverse_flow["meta.dst_l4_port"] = meta.src_l4_port
    reverse_flow["action"] = flow_action_inbound
    reverse_flow["params"] = [
        timer,
        meta.encap_data.original_overlay_sip,
        meta.encap_data.original_overlay_dip
    ]
    flows.insert(forward_flow)
    flows.insert(reverse_flow)

    timer.start()

def outbound_apply():
    flow_hit = flows.apply()["hit"]

    if not flow_hit:
        acl_apply()
        if not meta.dropped:
            _create_flows()

    meta.lkup_dst_ip_addr = meta.dst_ip_addr
    meta.is_lkup_dst_ip_v6 = meta.is_overlay_ip_v6

    action_run = outbound_routing.apply()["action_run"]

    if action_run == route_vnet_direct or action_run == route_vnet:
        outbound_ca_to_pa.apply()
        vnet.apply()
        vxlan_encap(meta.encap_data.underlay_dmac,
                    meta.encap_data.underlay_smac,
                    meta.encap_data.underlay_dip,
                    meta.encap_data.underlay_sip,
                    meta.encap_data.overlay_dmac,
                    meta.encap_data.vni)
    elif action_run == route_service_tunnel:
        if meta.encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN:
            vxlan_encap(meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.overlay_dmac,
                        meta.encap_data.service_tunnel_key)
        elif meta.encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE:
            nvgre_encap(meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.overlay_dmac,
                        meta.encap_data.service_tunnel_key)
        else:
            drop()
