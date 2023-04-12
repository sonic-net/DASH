#ifndef _SIRIUS_SERVICE_TUNNEL_P4_
#define _SIRIUS_SERVICE_TUNNEL_P4_

#include "dash_headers.p4"

/* Encodes V4 in V6 */
action service_tunnel_encode(inout headers_t hdr,
                             in IPv6Address st_dst,
                             in IPv6Address st_dst_mask,
                             in IPv6Address st_src,
                             in IPv6Address st_src_mask) {
    hdr.ipv6.setValid();
    hdr.ipv6.version = 6;
    hdr.ipv6.traffic_class = 0;
    hdr.ipv6.flow_label = 0;
    hdr.ipv6.payload_length = hdr.ipv4.total_len - IPV4_HDR_SIZE;
    hdr.ipv6.next_header = hdr.ipv4.protocol;
    hdr.ipv6.hop_limit = hdr.ipv4.ttl;
    hdr.ipv6.dst_addr = ((IPv6Address)hdr.ipv4.dst_addr & ~st_dst_mask) | (st_dst & st_dst_mask);
    hdr.ipv6.src_addr = ((IPv6Address)hdr.ipv4.src_addr & ~st_src_mask) | (st_src & st_src_mask);
    
    hdr.ipv4.setInvalid();
    hdr.ethernet.ether_type = IPV6_ETHTYPE;
}

/* Decodes V4 from V6 */
action service_tunnel_decode(inout headers_t hdr,
                             in IPv4Address src,
                             in IPv4Address dst) {
    hdr.ipv4.setValid();
    hdr.ipv4.version = 4;
    hdr.ipv4.ihl = 5;
    hdr.ipv4.diffserv = 0;
    hdr.ipv4.total_len = hdr.ipv6.payload_length + IPV4_HDR_SIZE;
    hdr.ipv4.identification = 1;
    hdr.ipv4.flags = 0;
    hdr.ipv4.frag_offset = 0;
    hdr.ipv4.protocol = hdr.ipv6.next_header;
    hdr.ipv4.ttl = hdr.ipv6.hop_limit;
    hdr.ipv4.hdr_checksum = 0;
    hdr.ipv4.dst_addr = dst;
    hdr.ipv4.src_addr = src;

    hdr.ipv6.setInvalid();
    hdr.ethernet.ether_type = IPV4_ETHTYPE;
}

#endif /* _SIRIUS_SERVICE_TUNNEL_P4_ */
