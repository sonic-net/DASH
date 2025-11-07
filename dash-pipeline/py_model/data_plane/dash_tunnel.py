from py_model.libs.__utils import *

# Return hdr.name, creating it if None.
def ensure_hdr(hdr, name, cls):
    if getattr(hdr, name, None) is None:
        setattr(hdr, name, cls())
    return getattr(hdr, name)

if TARGET_PYTHON_V1MODEL:
    def PUSH_VXLAN_TUNNEL_DEF(underlay_id, overlay_id):
        def push_vxlan_tunnel(underlay_dmac: Annotated[int, EthernetAddress_size],
                            underlay_smac: Annotated[int, EthernetAddress_size],
                            underlay_dip: Annotated[int, IPv4Address_size],
                            underlay_sip: Annotated[int, IPv4Address_size],
                            tunnel_key: Annotated[int,  24]):

            eth = ensure_hdr(hdr, f"{underlay_id}_ethernet", ethernet_t)
            eth.dst_addr   = underlay_dmac
            eth.src_addr   = underlay_smac
            eth.ether_type = IPV4_ETHTYPE

            overlay_ipv4 = getattr(hdr, f"{overlay_id}_ipv4")  # may be None
            overlay_ipv6 = getattr(hdr, f"{overlay_id}_ipv6")  # may be None

            ipv4 = ensure_hdr(hdr, f"{underlay_id}_ipv4", ipv4_t)
            ipv4_len = overlay_ipv4.total_len if overlay_ipv4 is not None else 0
            ipv6_len = overlay_ipv6.payload_length if overlay_ipv6 is not None else 0
            ipv6_hdr = IPV6_HDR_SIZE if overlay_ipv6 is not None else 0

            ipv4.total_len      = ipv4_len + ipv6_len + ipv6_hdr + ETHER_HDR_SIZE + IPV4_HDR_SIZE + UDP_HDR_SIZE + VXLAN_HDR_SIZE
            ipv4.version        = 4
            ipv4.ihl            = 5
            ipv4.diffserv       = 0
            ipv4.identification = 1
            ipv4.flags          = 0
            ipv4.frag_offset    = 0
            ipv4.ttl            = 64
            ipv4.protocol       = UDP_PROTO
            ipv4.dst_addr       = underlay_dip
            ipv4.src_addr       = underlay_sip
            ipv4.hdr_checksum   = 0

            udp = ensure_hdr(hdr, f"{underlay_id}_udp", udp_t)
            udp.src_port = 0
            udp.dst_port = UDP_PORT_VXLAN
            udp.length   = ipv4_len + ipv6_len + ipv6_hdr + UDP_HDR_SIZE + VXLAN_HDR_SIZE + ETHER_HDR_SIZE
            udp.checksum = 0

            vxlan = ensure_hdr(hdr, f"{underlay_id}_vxlan", vxlan_t)
            vxlan.reserved   = 0
            vxlan.reserved_2 = 0
            vxlan.flags      = 0x8
            vxlan.vni        = tunnel_key

        push_vxlan_tunnel.__name__ = f"push_vxlan_tunnel_{underlay_id}"
        return push_vxlan_tunnel

if TARGET_DPDK_PNA:
    def PUSH_VXLAN_TUNNEL_DEF(underlay_id, overlay_id):
        pass

if TARGET_PYTHON_V1MODEL:
    def PUSH_NVGRE_TUNNEL_DEF(underlay_id, overlay_id):
        def push_nvgre_tunnel(underlay_dmac: Annotated[int, EthernetAddress_size],
                            underlay_smac: Annotated[int, EthernetAddress_size],
                            underlay_dip: Annotated[int, IPv4Address_size],
                            underlay_sip: Annotated[int, IPv4Address_size],
                            tunnel_key: Annotated[int,  24]):

            eth = ensure_hdr(hdr, f"{underlay_id}_ethernet", ethernet_t)
            eth.dst_addr   = underlay_dmac
            eth.src_addr   = underlay_smac
            eth.ether_type = IPV4_ETHTYPE

            overlay_ipv4 = getattr(hdr, f"{overlay_id}_ipv4")  # may be None
            overlay_ipv6 = getattr(hdr, f"{overlay_id}_ipv6")  # may be None

            ipv4_len = overlay_ipv4.total_len if overlay_ipv4 is not None else 0
            ipv6_len = overlay_ipv6.payload_length if overlay_ipv6 is not None else 0
            ipv6_hdr = IPV6_HDR_SIZE if overlay_ipv6 is not None else 0

            ipv4 = ensure_hdr(hdr, f"{underlay_id}_ipv4", ipv4_t)
            ipv4.total_len = ipv4_len + ipv6_len + ipv6_hdr + ETHER_HDR_SIZE + IPV4_HDR_SIZE + NVGRE_HDR_SIZE
            ipv4.total_len += ETHER_HDR_SIZE + IPV4_HDR_SIZE + NVGRE_HDR_SIZE

            ipv4.version        = 4
            ipv4.ihl            = 5
            ipv4.diffserv       = 0
            ipv4.identification = 1
            ipv4.flags          = 0
            ipv4.frag_offset    = 0
            ipv4.ttl            = 64
            ipv4.protocol       = NVGRE_PROTO
            ipv4.dst_addr       = underlay_dip
            ipv4.src_addr       = underlay_sip
            ipv4.hdr_checksum   = 0

            nvgre = ensure_hdr(hdr, f"{underlay_id}_nvgre", nvgre_t)
            nvgre.flags         = 4
            nvgre.reserved      = 0
            nvgre.version       = 0
            nvgre.protocol_type = 0x6558
            nvgre.vsid          = tunnel_key
            nvgre.flow_id       = 0

        push_nvgre_tunnel.__name__ = f"push_nvgre_tunnel_{underlay_id}"
        return push_nvgre_tunnel

if TARGET_DPDK_PNA:
    def PUSH_NVGRE_TUNNEL_DEF(underlay_id, overlay_id):
        pass

push_vxlan_tunnel_u0 = PUSH_VXLAN_TUNNEL_DEF("u0", "customer")
push_vxlan_tunnel_u1 = PUSH_VXLAN_TUNNEL_DEF("u1", "u0")
push_nvgre_tunnel_u0 = PUSH_NVGRE_TUNNEL_DEF("u0", "customer")
push_nvgre_tunnel_u1 = PUSH_NVGRE_TUNNEL_DEF("u1", "u0")

def do_tunnel_encap( underlay_dmac : Annotated[int,  EthernetAddress_size],
                     underlay_smac : Annotated[int,  EthernetAddress_size],
                     underlay_dip  : Annotated[int,  IPv4Address_size],
                     underlay_sip  : Annotated[int,  IPv4Address_size],
                     dash_encapsulation : dash_encapsulation_t,
                     tunnel_key: Annotated[int,  24]):
    if dash_encapsulation == dash_encapsulation_t.VXLAN:
        if meta.tunnel_pointer == 0:
            push_vxlan_tunnel_u0(underlay_dmac, underlay_smac, underlay_dip, underlay_sip, tunnel_key)
        elif meta.tunnel_pointer == 1:
            push_vxlan_tunnel_u1(underlay_dmac, underlay_smac, underlay_dip, underlay_sip, tunnel_key)
    
    elif dash_encapsulation == dash_encapsulation_t.NVGRE:
        if meta.tunnel_pointer == 0:
            push_nvgre_tunnel_u0(underlay_dmac, underlay_smac, underlay_dip, underlay_sip, tunnel_key)
        elif meta.tunnel_pointer == 1:
            push_nvgre_tunnel_u1(underlay_dmac, underlay_smac, underlay_dip, underlay_sip, tunnel_key)

    meta.tunnel_pointer += 1

#  Tunnel decap can only pop u0 because that's what was parsed.
#  If the packet has more than one tunnel on ingress, BM will
#  reparse it.
#  It is also assumed, that if DASH pushes more than one tunnel,
#  they won't need to pop them */
def do_tunnel_decap():
    hdr.u0_ethernet = None
    hdr.u0_ipv4 = None
    hdr.u0_ipv6 = None
    hdr.u0_nvgre = None
    hdr.u0_vxlan = None
    hdr.u0_udp = None

    meta.tunnel_pointer = 0
