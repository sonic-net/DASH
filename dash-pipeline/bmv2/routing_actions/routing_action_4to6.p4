#ifndef _DASH_ROUTING_ACTION_4TO6_P4_
#define _DASH_ROUTING_ACTION_4TO6_P4_

action set_action_4to6(
    in headers_t hdr,
    inout metadata_t meta,
    in IPv6Address sip,
    in IPv6Address sip_mask,
    in IPv6Address dip,
    in IPv6Address dip_mask)
{
    meta.overlay_sip_4to6_value = sip;
    meta.overlay_sip_4to6_mask = sip_mask;
    meta.overlay_dip_4to6_value = dip;
    meta.overlay_dip_4to6_mask = dip_mask;
}

action do_action_4to6(
    inout headers_t hdr,
    in metadata_t meta)
{
    hdr.u0_ipv6.setValid();
    hdr.u0_ipv6.version = 6;
    hdr.u0_ipv6.traffic_class = 0;
    hdr.u0_ipv6.flow_label = 0;
    hdr.u0_ipv6.payload_length = hdr.u0_ipv4.total_len - IPV4_HDR_SIZE;
    hdr.u0_ipv6.next_header = hdr.u0_ipv4.protocol;
    hdr.u0_ipv6.hop_limit = hdr.u0_ipv4.ttl;
#ifndef DISABLE_128BIT_ARITHMETIC
    // As of 2024-Feb-09, p4c-dpdk does not yet support arithmetic on
    // 128-bit operands.
    hdr.u0_ipv6.dst_addr = ((IPv6Address)hdr.u0_ipv4.dst_addr & ~meta.overlay_dip_4to6_mask) | (meta.overlay_dip_4to6_value & meta.overlay_dip_4to6_mask);
    hdr.u0_ipv6.src_addr = ((IPv6Address)hdr.u0_ipv4.src_addr & ~meta.overlay_sip_4to6_mask) | (meta.overlay_sip_4to6_value & meta.overlay_sip_4to6_mask);
#endif
    
    hdr.u0_ipv4.setInvalid();
    hdr.u0_ethernet.ether_type = IPV6_ETHTYPE;
}

#endif /* _DASH_ROUTING_ACTION_4TO6_P4_ */