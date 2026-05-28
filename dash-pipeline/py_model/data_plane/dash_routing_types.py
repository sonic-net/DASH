from py_model.libs.__utils import *
from py_model.data_plane.dash_tunnel import *
from py_model.data_plane.routing_actions.routing_actions import *

def set_meter_attrs(meter_class_or:  Annotated[int, 32],
                    meter_class_and: Annotated[int, 32]):
    
    meta.meter_context.meter_class_or = meta.meter_context.meter_class_or | meter_class_or
    meta.meter_context.meter_class_and = meta.meter_context.meter_class_and & meter_class_and

# Routing Type - drop:
def drop():
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY
    meta.dropped = True

# Routing Type - vnet:
# - Continue to look up in VNET mapping stage with the destination VNET ID.
# - No routing action will be populated in this routing type.
def route_vnet(dst_vnet_id                                   : Annotated[int, 16, {"type" : "sai_object_id_t"}],
               dash_tunnel_id                                : Annotated[int, 16, {"type" : "sai_object_id_t"}],
               meter_class_or                                : Annotated[int, 32],
               meter_class_and                               : Annotated[int, 32, {"default_value" : "4294967295"}],
               routing_actions_disabled_in_flow_resimulation : dash_flow_action_t):
    
    meta.dash_tunnel_id = dash_tunnel_id
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_MAPPING
    meta.dst_vnet_id = dst_vnet_id
    set_meter_attrs(meter_class_or, meter_class_and)
    
# Routing Type - vnet_direct:
# - Forward with overrided destination overlay IP.
# - No routing action will be populated in this routing type.
def route_vnet_direct(dst_vnet_id                                   : Annotated[int, 16],
                      dash_tunnel_id                                : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      overlay_ip_is_v6                              : Annotated[int, 1],
                      overlay_ip                                    : Annotated[int, IPv6Address_size, {"type" :"sai_ip_address_t"}],
                      meter_class_or                                : Annotated[int, 32],
                      meter_class_and                               : Annotated[int, 32, {"default_value" : "4294967295"}],
                      routing_actions_disabled_in_flow_resimulation : dash_flow_action_t):
    
    meta.dash_tunnel_id = dash_tunnel_id
    
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_MAPPING
    meta.dst_vnet_id = dst_vnet_id
    meta.lkup_dst_ip_addr = overlay_ip
    meta.is_lkup_dst_ip_v6 = overlay_ip_is_v6
    set_meter_attrs(meter_class_or, meter_class_and)

# Routing Type - direct:
# - Send to underlay router without any encap
# - No routing action will be populated in this routing type.
def route_direct(dash_tunnel_id                                : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                 meter_class_or                                : Annotated[int, 32],
                 meter_class_and                               : Annotated[int, 32 , {"default_value" : "4294967295"}],
                 routing_actions_disabled_in_flow_resimulation : dash_flow_action_t):
    
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY
    set_meter_attrs(meter_class_or, meter_class_and)
    meta.dash_tunnel_id = dash_tunnel_id

# Routing Type - servicetunnel
# - Encap the packet with the given overlay and underlay addresses.
# - Perform 4-to-6 translation on the overlay addresses.
def route_service_tunnel(overlay_dip_is_v6                             : Annotated[int, 1],
                         overlay_dip                                   : Annotated[int, IPv4ORv6Address_size],
                         overlay_dip_mask_is_v6                        : Annotated[int, 1],
                         overlay_dip_mask                              : Annotated[int, IPv4ORv6Address_size],
                         overlay_sip_is_v6                             : Annotated[int, 1],
                         overlay_sip                                   : Annotated[int, IPv4ORv6Address_size],
                         overlay_sip_mask_is_v6                        : Annotated[int, 1],
                         overlay_sip_mask                              : Annotated[int, IPv4ORv6Address_size],
                         underlay_dip_is_v6                            : Annotated[int, 1],
                         underlay_dip                                  : Annotated[int, IPv4ORv6Address_size],
                         underlay_sip_is_v6                            : Annotated[int, 1],
                         underlay_sip                                  : Annotated[int, IPv4ORv6Address_size],
                         dash_encapsulation                            : Annotated[dash_encapsulation_t,
                                                                                   {"type" : "sai_dash_encapsulation_t",
                                                                                    "default_value" : "SAI_DASH_ENCAPSULATION_VXLAN"}],
                         tunnel_key                                    : Annotated[int, 24],
                         dash_tunnel_id                                : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                         meter_class_or                                : Annotated[int, 32],
                         meter_class_and                               : Annotated[int, 32, {"default_value" : "4294967295"}],
                         routing_actions_disabled_in_flow_resimulation : dash_flow_action_t):

    meta.dash_tunnel_id = dash_tunnel_id
    
    # Assume the overlay addresses provided are always IPv6 and the original are IPv4
    # Required(overlay_dip_is_v6 == 1 and overlay_sip_is_v6 == 1)
    # Required(overlay_dip_mask_is_v6 == 1 and overlay_sip_mask_is_v6 == 1)
    # Required(underlay_dip_is_v6 != 1 and underlay_sip_is_v6 != 1)

    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY
    
    push_action_nat46(overlay_sip, overlay_sip_mask,
                      overlay_dip, overlay_dip_mask)
    
    # Python support arithmetic on 128-bit operands 
    push_action_set_dmac(hdr.u0_ethernet.dst_addr)

    push_action_encap_u0(encap = dash_encapsulation,
                        vni = tunnel_key,
                        underlay_sip = underlay_sip if underlay_sip != 0 else hdr.u0_ipv4.src_addr,
                        underlay_dip = underlay_dip if underlay_dip != 0 else hdr.u0_ipv4.dst_addr)

    set_meter_attrs(meter_class_or, meter_class_and)
    
def set_tunnel_mapping(underlay_dip                                   : Annotated[int, IPv4Address_size , {"type" : "sai_ip_address_t"}],
                       overlay_dmac                                   : Annotated[int, EthernetAddress_size],
                       use_dst_vnet_vni                               : Annotated[int, 1],
                       meter_class_or                                 : Annotated[int, 32],
                       dash_tunnel_id                                 : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                       flow_resimulation_requested                    : Annotated[int, 1],
                       routing_actions_disabled_in_flow_resimulation  : dash_flow_action_t):
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY
    meta.dash_tunnel_id = dash_tunnel_id
    
    if use_dst_vnet_vni == 1:
        meta.vnet_id = meta.dst_vnet_id

    push_action_set_dmac(overlay_dmac)
    
    push_action_encap_u0(underlay_dip=underlay_dip)
    
    set_meter_attrs(meter_class_or, 0xffffffff)
                            
def set_private_link_mapping(underlay_dip                                   : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                             overlay_sip                                    : Annotated[int, IPv6Address_size],
                             overlay_sip_mask                               : Annotated[int, IPv6Address_size],
                             overlay_dip                                    : Annotated[int, IPv6Address_size],
                             overlay_dip_mask                               : Annotated[int, IPv6Address_size],
                             dash_encapsulation                             : Annotated[dash_encapsulation_t, {"type" : "sai_dash_encapsulation_t"}],
                             tunnel_key                                     : Annotated[int, 24],
                             meter_class_or                                 : Annotated[int, 32],
                             dash_tunnel_id                                 : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                             flow_resimulation_requested                    : Annotated[int, 1],
                             routing_actions_disabled_in_flow_resimulation  : dash_flow_action_t,
                             outbound_port_map_id                           : Annotated[int, 16, {"type" : "sai_object_id_t"}]):
    
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY
    meta.dash_tunnel_id = dash_tunnel_id

    push_action_set_dmac(hdr.u0_ethernet.dst_addr)
 
    ##TODO Pass required arguments
    push_action_encap_u0(dash_encapsulation,
                         vni = tunnel_key,
                         # PL has its own underlay SIP, so override
                         underlay_sip = meta.eni_data.pl_underlay_sip,
                         underlay_dip = underlay_dip)

    # Python support arithmetic on 128-bit operands
    push_action_nat46(overlay_dip, overlay_dip_mask,
                    (((meta.src_ip_addr & ~overlay_sip_mask) | overlay_sip) & ~meta.eni_data.pl_sip_mask) | meta.eni_data.pl_sip,
                    0xffffffffffffffffffffffff)

    meta.port_map_ctx.map_id = outbound_port_map_id

    set_meter_attrs(meter_class_or, 0xffffffff)