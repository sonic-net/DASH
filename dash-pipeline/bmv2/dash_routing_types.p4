#ifndef _DASH_ROUTING_TYPES_P4_
#define _DASH_ROUTING_TYPES_P4_

#include "dash_headers.p4"
#include "routing_actions/routing_actions.p4"

action set_meter_attrs(
    inout metadata_t meta,
    bit<32> meter_class_or,
    bit<32> meter_class_and)
{
    meta.meter_context.meter_class_or = meta.meter_context.meter_class_or | meter_class_or;
    meta.meter_context.meter_class_and = meta.meter_context.meter_class_and & meter_class_and;
}

// Routing Type - drop:
action drop(inout metadata_t meta) {
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY;
    meta.dropped = true;
}

// Routing Type - vnet:
// - Continue to look up in VNET mapping stage with the destination VNET ID.
// - No routing action will be populated in this routing type.
action route_vnet(
    inout headers_t hdr,
    inout metadata_t meta,
    @SaiVal[type="sai_object_id_t"] bit<16> dst_vnet_id,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<32> meter_class_or,
    @SaiVal[default_value="4294967295"] bit<32> meter_class_and,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.dash_tunnel_id = dash_tunnel_id;

    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_MAPPING;
    meta.dst_vnet_id = dst_vnet_id;
    set_meter_attrs(meta, meter_class_or, meter_class_and);
}

// Routing Type - vnet_direct:
// - Forward with overrided destination overlay IP.
// - No routing action will be populated in this routing type.
action route_vnet_direct(
    inout headers_t hdr,
    inout metadata_t meta,
    bit<16> dst_vnet_id,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<1> overlay_ip_is_v6,
    @SaiVal[type="sai_ip_address_t"]
    IPv4ORv6Address overlay_ip,
    bit<32> meter_class_or,
    @SaiVal[default_value="4294967295"] bit<32> meter_class_and,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.dash_tunnel_id = dash_tunnel_id;

    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_MAPPING;
    meta.dst_vnet_id = dst_vnet_id;
    meta.lkup_dst_ip_addr = overlay_ip;
    meta.is_lkup_dst_ip_v6 = overlay_ip_is_v6;
    set_meter_attrs(meta, meter_class_or, meter_class_and);
}

// Routing Type - direct:
// - Send to underlay router without any encap
// - No routing action will be populated in this routing type.
action route_direct(
    inout headers_t hdr,
    inout metadata_t meta,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<32> meter_class_or,
    @SaiVal[default_value="4294967295"] bit<32> meter_class_and,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY;
    set_meter_attrs(meta, meter_class_or, meter_class_and);
    meta.dash_tunnel_id = dash_tunnel_id;
}

// Routing Type - servicetunnel
// - Encap the packet with the given overlay and underlay addresses.
// - Perform 4-to-6 translation on the overlay addresses.
action route_service_tunnel(
    inout headers_t hdr,
    inout metadata_t meta,
    bit<1> overlay_dip_is_v6,
    IPv4ORv6Address overlay_dip,
    bit<1> overlay_dip_mask_is_v6,
    IPv4ORv6Address overlay_dip_mask,
    bit<1> overlay_sip_is_v6,
    IPv4ORv6Address overlay_sip,
    bit<1> overlay_sip_mask_is_v6,
    IPv4ORv6Address overlay_sip_mask,
    bit<1> underlay_dip_is_v6,
    IPv4ORv6Address underlay_dip,
    bit<1> underlay_sip_is_v6,
    IPv4ORv6Address underlay_sip,
    @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
    dash_encapsulation_t dash_encapsulation,
    bit<24> tunnel_key,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<32> meter_class_or,
    @SaiVal[default_value="4294967295"] bit<32> meter_class_and,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.dash_tunnel_id = dash_tunnel_id;

    /* Assume the overlay addresses provided are always IPv6 and the original are IPv4 */
    /* assert(overlay_dip_is_v6 == 1 && overlay_sip_is_v6 == 1);
    assert(overlay_dip_mask_is_v6 == 1 && overlay_sip_mask_is_v6 == 1);
    assert(underlay_dip_is_v6 != 1 && underlay_sip_is_v6 != 1); */

    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY;

    push_action_nat46(hdr = hdr,
                    meta = meta,
                    sip = overlay_sip,
                    sip_mask = overlay_sip_mask,
                    dip = overlay_dip,
                    dip_mask = overlay_dip_mask);

#ifndef DISABLE_128BIT_ARITHMETIC
    // As of 2024-Feb-09, p4c-dpdk does not yet support arithmetic on 128-bit operands.
    // This lack of support extends to cast operations.
    push_action_static_encap(hdr = hdr,
                            meta = meta,
                            encap = dash_encapsulation,
                            vni = tunnel_key,
                            underlay_sip = underlay_sip == 0 ? hdr.u0_ipv4.src_addr : (IPv4Address)underlay_sip,
                            underlay_dip = underlay_dip == 0 ? hdr.u0_ipv4.dst_addr : (IPv4Address)underlay_dip,
                            overlay_dmac = hdr.u0_ethernet.dst_addr);

#endif

    set_meter_attrs(meta, meter_class_or, meter_class_and);
}

// Routing type - vnet_encap:
action set_tunnel_mapping(
    inout headers_t hdr,
    inout metadata_t meta,
    @SaiVal[type="sai_ip_address_t"] IPv4Address underlay_dip,
    EthernetAddress overlay_dmac,
    bit<1> use_dst_vnet_vni,
    bit<32> meter_class_or,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<1> flow_resimulation_requested,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY;
    meta.dash_tunnel_id = dash_tunnel_id;

    if (use_dst_vnet_vni == 1)
        meta.vnet_id = meta.dst_vnet_id;

    push_action_static_encap(hdr = hdr,
                            meta = meta,
                            underlay_dip = underlay_dip,
                            overlay_dmac = overlay_dmac);

    set_meter_attrs(meta, meter_class_or, 0xffffffff);
}

// Routing type - privatelink:
action set_private_link_mapping(
    inout headers_t hdr,
    inout metadata_t meta, 
    @SaiVal[type="sai_ip_address_t"] IPv4Address underlay_dip,
    IPv6Address overlay_sip,
    IPv6Address overlay_sip_mask,
    IPv6Address overlay_dip,
    IPv6Address overlay_dip_mask,
    @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t dash_encapsulation,
    bit<24> tunnel_key,
    bit<32> meter_class_or,
    @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
    bit<1> flow_resimulation_requested,
    dash_routing_actions_t routing_actions_disabled_in_flow_resimulation)
{
    meta.target_stage = dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY;
    meta.dash_tunnel_id = dash_tunnel_id;
    
    push_action_static_encap(hdr = hdr,
                            meta = meta,
                            encap = dash_encapsulation,
                            vni = tunnel_key,
                            // PL has its own underlay SIP, so override
                            underlay_sip = meta.eni_data.pl_underlay_sip,
                            underlay_dip = underlay_dip,
                            overlay_dmac = hdr.u0_ethernet.dst_addr);

#ifndef DISABLE_128BIT_ARITHMETIC
    // As of 2024-Feb-09, p4c-dpdk does not yet support arithmetic on
    // 128-bit operands.
    //
    // Hence passing IPv6 addresses as arguments is not supported due to error below:
    // error: DPDK target supports up-to 64-bit immediate values, 128w0xffffffffffffffffffffffff exceeds the limit.
    push_action_nat46(hdr = hdr,
                    meta = meta,
                    dip = overlay_dip,
                    dip_mask = overlay_dip_mask,
                    sip = ((( (IPv6Address)hdr.u0_ipv4.src_addr & ~overlay_sip_mask) | overlay_sip) & ~meta.eni_data.pl_sip_mask) | meta.eni_data.pl_sip,
                    sip_mask = 0xffffffffffffffffffffffff);
#endif /* DISABLE_128BIT_ARITHMETIC */

    set_meter_attrs(meta, meter_class_or, 0xffffffff);
}

#endif /* _DASH_ROUTING_TYPES_P4_ */
