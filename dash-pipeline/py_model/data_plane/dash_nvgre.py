from py_model.libs.__utils import *

def nvgre_encap(underlay_dmac : Annotated[int, 48],
                underlay_smac : Annotated[int, 48],
                underlay_dip  : Annotated[int, 32],
                underlay_sip  : Annotated[int, 32],
                overlay_dmac  : Annotated[int, 48],
                vsid          : Annotated[int, 24]):
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

    hdr.ipv4.total_len = ETHER_HDR_SIZE + IPV4_HDR_SIZE + NVGRE_HDR_SIZE
    if hdr.inner_ipv4:
        hdr.ipv4.total_len += hdr.inner_ipv4.total_len    
    if hdr.inner_ipv6:
        hdr.ipv4.total_len += hdr.inner_ipv6.payload_length + IPV6_HDR_SIZE

    hdr.ipv4.identification = 1
    hdr.ipv4.flags = 0
    hdr.ipv4.frag_offset = 0
    hdr.ipv4.ttl = 64
    hdr.ipv4.protocol = NVGRE_PROTO
    hdr.ipv4.dst_addr = underlay_dip
    hdr.ipv4.src_addr = underlay_sip
    hdr.ipv4.hdr_checksum = 0

    hdr.nvgre = nvgre_t()
    hdr.nvgre.flags = 4
    hdr.nvgre.reserved = 0
    hdr.nvgre.version = 0
    hdr.nvgre.protocol_type = 0x6558
    hdr.nvgre.vsid = vsid
    hdr.nvgre.flow_id = 0
