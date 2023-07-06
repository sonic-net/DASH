#ifndef _SIRIUS_HEADERS_P4_
#define _SIRIUS_HEADERS_P4_

typedef bit<48>  EthernetAddress;
typedef bit<32>  IPv4Address;
typedef bit<128> IPv6Address;
typedef bit<128> IPv4ORv6Address;

header ethernet_t {
    EthernetAddress dst_addr;
    EthernetAddress src_addr;
    bit<16>         ether_type;
}

const bit<16> ETHER_HDR_SIZE=112/8;

header ipv4_t {
    bit<4>      version;
    bit<4>      ihl;
    bit<8>      diffserv;
    bit<16>     total_len;
    bit<16>     identification;
    bit<3>      flags;
    bit<13>     frag_offset;
    bit<8>      ttl;
    bit<8>      protocol;
    bit<16>     hdr_checksum;
    IPv4Address src_addr;
    IPv4Address dst_addr;
}

const bit<16> IPV4_HDR_SIZE=160/8;

header ipv4options_t {
    varbit<320> options;
}

header udp_t {
    bit<16>  src_port;
    bit<16>  dst_port;
    bit<16>  length;
    bit<16>  checksum;
}

const bit<16> UDP_HDR_SIZE=64/8;

header vxlan_t {
    bit<8>  flags;
    bit<24> reserved;
    bit<24> vni;
    bit<8>  reserved_2;
}

const bit<16> VXLAN_HDR_SIZE=64/8;

header nvgre_t {
    bit<4>  flags;
    bit<9>  reserved;
    bit<3>  version;
    bit<16> protocol_type;
    bit<24> vsid;
    bit<8>  flow_id;
}

const bit<16> NVGRE_HDR_SIZE=64/8;

header tcp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

const bit<16> TCP_HDR_SIZE=160/8;

header ipv6_t {
    bit<4>      version;
    bit<8>      traffic_class;
    bit<20>     flow_label;
    bit<16>     payload_length;
    bit<8>      next_header;
    bit<8>      hop_limit;
    IPv6Address src_addr;
    IPv6Address dst_addr;
}

const bit<16> IPV6_HDR_SIZE=320/8;

struct headers_t {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    ipv4options_t ipv4options;
    ipv6_t     ipv6;
    udp_t      udp;
    tcp_t      tcp;
    vxlan_t    vxlan;
    nvgre_t    nvgre;
    ethernet_t inner_ethernet;
    ipv4_t     inner_ipv4;
    ipv6_t     inner_ipv6;
    udp_t      inner_udp;
    tcp_t      inner_tcp;
}

enum bit<16> dash_encapsulation_t {
    INVALID = 0,
    VXLAN = 1,
    NVGRE = 2
}

#endif /* _SIRIUS_HEADERS_P4_ */
