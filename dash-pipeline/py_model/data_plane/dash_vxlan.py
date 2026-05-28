from py_model.libs.__utils import *

def vxlan_encap(underlay_dmac : Annotated[int, EthernetAddress_size],
                underlay_smac : Annotated[int, EthernetAddress_size],
                underlay_dip  : Annotated[int, IPv4Address_size],
                underlay_sip  : Annotated[int, IPv4Address_size],
                overlay_dmac  : Annotated[int, EthernetAddress_size],
                vni           : Annotated[int, 24]):
    hdr.inner_ethernet = hdr.ethernet
    hdr.inner_ethernet.dst_addr = overlay_dmac
    hdr.ethernet = None

    hdr.inner_ipv4 = hdr.ipv4
    hdr.ipv4 = None
    hdr.inner_ipv6 = hdr.ipv6
    hdr.ipv6 = None
    hdr.inner_tcp = hdr.tcp
    hdr.tcp = None
    hdr.inner_udp = hdr.udp
    hdr.udp = None

    hdr.ethernet = ethernet_t()
    hdr.ethernet.dst_addr = underlay_dmac
    hdr.ethernet.src_addr = underlay_smac
    hdr.ethernet.ether_type = IPV4_ETHTYPE

    hdr.ipv4 = ipv4_t()
    hdr.ipv4.version = 4
    hdr.ipv4.ihl = 5
    hdr.ipv4.diffserv = 0

    hdr.ipv4.total_len = ETHER_HDR_SIZE + IPV4_HDR_SIZE + UDP_HDR_SIZE + VXLAN_HDR_SIZE
    if hdr.inner_ipv4:
        hdr.ipv4.total_len += hdr.inner_ipv4.total_len    
    if hdr.inner_ipv6:
        hdr.ipv4.total_len += hdr.inner_ipv6.payload_length + IPV6_HDR_SIZE

    hdr.ipv4.identification = 1
    hdr.ipv4.flags = 0
    hdr.ipv4.frag_offset = 0
    hdr.ipv4.ttl = 64
    hdr.ipv4.protocol = UDP_PROTO
    hdr.ipv4.dst_addr = underlay_dip
    hdr.ipv4.src_addr = underlay_sip
    hdr.ipv4.hdr_checksum = 0

    hdr.udp = udp_t()
    hdr.udp.src_port = 0
    hdr.udp.dst_port = UDP_PORT_VXLAN
    hdr.udp.length = UDP_HDR_SIZE + VXLAN_HDR_SIZE + ETHER_HDR_SIZE

    if hdr.inner_ipv4:
        hdr.udp.length += hdr.inner_ipv4.total_len
    if hdr.inner_ipv6:
        hdr.udp.length += hdr.inner_ipv6.payload_length + IPV6_HDR_SIZE

    hdr.udp.checksum = 0

    hdr.vxlan = vxlan_t()
    hdr.vxlan.reserved = 0
    hdr.vxlan.reserved_2 = 0
    hdr.vxlan.flags = 0
    hdr.vxlan.vni = vni

def vxlan_decap():
    hdr.ethernet = hdr.inner_ethernet
    hdr.inner_ethernet = None

    hdr.ipv4 = hdr.inner_ipv4
    hdr.inner_ipv4 = None

    hdr.ipv6 = hdr.inner_ipv6
    hdr.inner_ipv6 = None

    hdr.vxlan = None
    hdr.udp = None

    hdr.tcp = hdr.inner_tcp
    hdr.inner_tcp = None

    hdr.udp = hdr.inner_udp
    hdr.inner_udp = None
