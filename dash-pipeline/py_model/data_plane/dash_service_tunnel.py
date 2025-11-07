from py_model.libs.__utils import *

# Encodes V4 in V6
def service_tunnel_encode(st_dst      : Annotated[int, IPv6Address_size],
                          st_dst_mask : Annotated[int, IPv6Address_size],
                          st_src      : Annotated[int, IPv6Address_size],
                          st_src_mask : Annotated[int, IPv6Address_size]):
    hdr.u0_ipv6 = ipv6_t()
    hdr.u0_ipv6.version = 6
    hdr.u0_ipv6.traffic_class = 0
    hdr.u0_ipv6.flow_label = 0
    hdr.u0_ipv6.payload_length = hdr.u0_ipv4.total_len - IPV4_HDR_SIZE
    hdr.u0_ipv6.next_header = hdr.u0_ipv4.protocol
    hdr.u0_ipv6.hop_limit = hdr.u0_ipv4.ttl

    # Python support arithmetic on 128-bit operands
    hdr.u0_ipv6.dst_addr = (hdr.u0_ipv4.dst_addr & ~st_dst_mask) | (st_dst & st_dst_mask)
    hdr.u0_ipv6.src_addr = (hdr.u0_ipv4.src_addr & ~st_src_mask) | (st_src & st_src_mask)

    hdr.u0_ipv4 = None
    hdr.ethernet.ether_type = IPV6_ETHTYPE

# Decodes V4 from V6
def service_tunnel_decode(src : Annotated[int, IPv4Address_size],
                          dst : Annotated[int, IPv4Address_size]):
    hdr.u0_ipv4 = ipv4_t()
    hdr.u0_ipv4.version = 4
    hdr.u0_ipv4.ihl = 5
    hdr.u0_ipv4.diffserv = 0
    hdr.u0_ipv4.total_len = hdr.u0_ipv6.payload_length + IPV4_HDR_SIZE
    hdr.u0_ipv4.identification = 1
    hdr.u0_ipv4.flags = 0
    hdr.u0_ipv4.frag_offset = 0
    hdr.u0_ipv4.protocol = hdr.u0_ipv6.next_header
    hdr.u0_ipv4.ttl = hdr.u0_ipv6.hop_limit
    hdr.u0_ipv4.hdr_checksum = 0
    hdr.u0_ipv4.dst_addr = dst
    hdr.u0_ipv4.src_addr = src

    hdr.u0_ipv6 = None
    hdr.ethernet.ether_type = IPV4_ETHTYPE
