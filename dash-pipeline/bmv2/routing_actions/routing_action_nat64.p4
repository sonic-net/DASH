#ifndef _DASH_ROUTING_ACTION_NAT64_P4_
#define _DASH_ROUTING_ACTION_NAT64_P4_

action push_action_nat64(
    in headers_t hdr,
    inout metadata_t meta,
    in IPv4Address src,
    in IPv4Address dst)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.NAT64;
    
    meta.overlay_data.is_ipv6 = false;
    meta.overlay_data.sip = (IPv4ORv6Address)src;
    meta.overlay_data.dip = (IPv4ORv6Address)dst;
}

control do_action_nat64(
    inout headers_t hdr,
    in metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.NAT64 == 0) {
            return;
        }

        REQUIRES(meta.overlay_data.is_ipv6 == false);

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
        hdr.u0_ipv4.dst_addr = (IPv4Address)meta.overlay_data.dip;
        hdr.u0_ipv4.src_addr = (IPv4Address)meta.overlay_data.sip;

        hdr.u0_ipv6.setInvalid();
        hdr.u0_ethernet.ether_type = IPV4_ETHTYPE;
    }
}

#endif /* _DASH_ROUTING_ACTION_NAT64_P4_ */