from dash_headers import *
from __vars import *

# Encodes V4 in V6
def service_tunnel_encode(st_dst      : Annotated[int, 128],
                          st_dst_mask : Annotated[int, 128],
                          st_src      : Annotated[int, 128],
                          st_src_mask : Annotated[int, 128]):
    hdr.ipv6 = ipv6_t()
    hdr.ipv6.version = 6
    hdr.ipv6.traffic_class = 0
    hdr.ipv6.flow_label = 0
    hdr.ipv6.payload_length = hdr.ipv4.total_len - IPV4_HDR_SIZE
    hdr.ipv6.next_header = hdr.ipv4.protocol
    hdr.ipv6.hop_limit = hdr.ipv4.ttl
    hdr.ipv6.dst_addr = (hdr.ipv4.dst_addr & ~st_dst_mask) | (st_dst & st_dst_mask)
    hdr.ipv6.src_addr = (hdr.ipv4.src_addr & ~st_src_mask) | (st_src & st_src_mask)

    hdr.ipv4 = None
    hdr.ethernet.ether_type = IPV6_ETHTYPE

# Decodes V4 from V6
def service_tunnel_decode(src : Annotated[int, 32],
                          dst : Annotated[int, 32]):
    hdr.ipv4 = ipv4_t()
    hdr.ipv4.version = 4
    hdr.ipv4.ihl = 5
    hdr.ipv4.diffserv = 0
    hdr.ipv4.total_len = hdr.ipv6.payload_length + IPV4_HDR_SIZE
    hdr.ipv4.identification = 1
    hdr.ipv4.flags = 0
    hdr.ipv4.frag_offset = 0
    hdr.ipv4.protocol = hdr.ipv6.next_header
    hdr.ipv4.ttl = hdr.ipv6.hop_limit
    hdr.ipv4.hdr_checksum = 0
    hdr.ipv4.dst_addr = dst
    hdr.ipv4.src_addr = src

    hdr.ipv6 = None
    hdr.ethernet.ether_type = IPV4_ETHTYPE
