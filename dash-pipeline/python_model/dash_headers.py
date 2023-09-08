from typing import *
from inspect import *
from __dash_enum import *

EthernetAddress_size = 48
IPv4Address_size = 32
IPv6Address_size = 128
IPv4ORv6Address_size = 128

UDP_PORT_VXLAN = 0x12B5
UDP_PROTO      = 0x11
TCP_PROTO      = 0x06
NVGRE_PROTO    = 0x2f
IPV4_ETHTYPE   = 0x0800
IPV6_ETHTYPE   = 0x86DD

class ethernet_t:
    dst_addr   : Annotated[int, EthernetAddress_size]
    src_addr   : Annotated[int, EthernetAddress_size]
    ether_type : Annotated[int, 16]

ETHER_HDR_SIZE = 14

class ipv4_t:
    version        : Annotated[int, 4]
    ihl            : Annotated[int, 4]
    diffserv       : Annotated[int, 8]
    total_len      : Annotated[int, 16]
    identification : Annotated[int, 16]
    flags          : Annotated[int, 3]
    frag_offset    : Annotated[int, 13]
    ttl            : Annotated[int, 8]
    protocol       : Annotated[int, 8]
    hdr_checksum   : Annotated[int, 16]
    src_addr       : Annotated[int, IPv4Address_size]
    dst_addr       : Annotated[int, IPv4Address_size]

IPV4_HDR_SIZE = 20

class udp_t:
    src_port : Annotated[int, 16]
    dst_port : Annotated[int, 16]
    length   : Annotated[int, 16]
    checksum : Annotated[int, 16]

UDP_HDR_SIZE = 8

class vxlan_t:
    flags      : Annotated[int, 8]
    reserved   : Annotated[int, 24]
    vni        : Annotated[int, 24]
    reserved_2 : Annotated[int, 8]

VXLAN_HDR_SIZE = 8

class nvgre_t:
    flags         : Annotated[int, 4]
    reserved      : Annotated[int, 9]
    version       : Annotated[int, 3]
    protocol_type : Annotated[int, 16]
    vsid          : Annotated[int, 24]
    flow_id       : Annotated[int, 8]

NVGRE_HDR_SIZE = 8

class tcp_t:
    src_port    : Annotated[int, 16]
    dst_port    : Annotated[int, 16]
    seq_no      : Annotated[int, 32]
    ack_no      : Annotated[int, 32]
    data_offset : Annotated[int, 4]
    res         : Annotated[int, 3]
    ecn         : Annotated[int, 3]
    flags       : Annotated[int, 6]
    window      : Annotated[int, 16]
    checksum    : Annotated[int, 16]
    urgent_ptr  : Annotated[int, 16]

TCP_HDR_SIZE = 20

class ipv6_t:
    version        : Annotated[int, 4]
    traffic_class  : Annotated[int, 8]
    flow_label     : Annotated[int, 20]
    payload_length : Annotated[int, 16]
    next_header    : Annotated[int, 8]
    hop_limit      : Annotated[int, 8]
    src_addr       : Annotated[int, IPv6Address_size]
    dst_addr       : Annotated[int, IPv6Address_size]

IPV6_HDR_SIZE = 40

class headers_t:
    ethernet       : ethernet_t
    ipv4           : ipv4_t
    ipv6           : ipv6_t
    udp            : udp_t
    tcp            : tcp_t
    vxlan          : vxlan_t
    nvgre          : nvgre_t
    inner_ethernet : ethernet_t
    inner_ipv4     : ipv4_t
    inner_ipv6     : ipv6_t
    inner_udp      : udp_t
    inner_tcp      : tcp_t

    def __init__(self):
        self.reset()

    def reset(self):
        annotations = get_annotations(type(self))
        for k in annotations:
            setattr(self, k, None)

class dash_encapsulation_t(dash_enum):
    INVALID = 0
    VXLAN   = 1
    NVGRE   = 2
