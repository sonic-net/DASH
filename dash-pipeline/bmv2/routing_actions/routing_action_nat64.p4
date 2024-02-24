#ifndef _DASH_ROUTING_ACTION_NAT64_P4_
#define _DASH_ROUTING_ACTION_NAT64_P4_

#include "../dash_headers.p4"

action set_action_nat64(
    in headers_t hdr,
    inout metadata_t meta,
    in IPv4Address src,
    in IPv4Address dst)
{
    meta.pending_actions = meta.pending_actions | dash_routing_actions_t.NAT64;
    
    meta.nat64_sip = src;
    meta.nat64_dip = dst;
}

action do_action_nat64(
    inout headers_t hdr,
    in metadata_t meta)
{
    hdr.u0_ipv4.setValid();
    hdr.u0_ipv4.version = 4;
    hdr.u0_ipv4.ihl = 5;
    hdr.u0_ipv4.diffserv = 0;
    hdr.u0_ipv4.total_len = hdr.u0_ipv6.payload_length + IPV4_HDR_SIZE;
    hdr.u0_ipv4.identification = 1;
    hdr.u0_ipv4.flags = 0;
    hdr.u0_ipv4.frag_offset = 0;
    hdr.u0_ipv4.protocol = hdr.u0_ipv6.next_header;
    hdr.u0_ipv4.ttl = hdr.u0_ipv6.hop_limit;
    hdr.u0_ipv4.hdr_checksum = 0;
    hdr.u0_ipv4.dst_addr = meta.nat64_dip;
    hdr.u0_ipv4.src_addr = meta.nat64_sip;

    hdr.u0_ipv6.setInvalid();
    hdr.u0_ethernet.ether_type = IPV4_ETHTYPE;
}

#endif /* _DASH_ROUTING_ACTION_NAT64_P4_ */