from enum import Enum, auto
from py_model.libs.__utils import *
from py_model.libs.__packet_in import *
from py_model.libs.__packet_out import *

class State(Enum):
    accept                  =  auto()
    reject                  =  auto()
    start                   =  auto()
    parse_dash_hdr          =  auto()
    parse_u0_ipv4           =  auto()
    parse_u0_ipv6           =  auto()
    parse_u0_udp            =  auto()
    parse_u0_tcp            =  auto()
    parse_u0_vxlan          =  auto()
    parse_customer_ethernet =  auto()
    parse_customer_ipv4     =  auto()
    parse_customer_ipv6     =  auto()
    parse_customer_tcp      =  auto()
    parse_customer_udp      =  auto()

def dash_parser(packet: packet_in):
    py_log("info", "Parser start")
    # By default, packet is REGULAR from EXTERNAL
    hdr.packet_meta = dash_packet_meta_t()
    hdr.packet_meta.packet_source = dash_packet_source_t.EXTERNAL
    hdr.packet_meta.packet_type = dash_packet_type_t.REGULAR
    hdr.packet_meta.packet_subtype = dash_packet_subtype_t.NONE
    hdr.packet_meta.length = PACKET_META_HDR_SIZE

    state = State.start
    while True:
        state = _dash_parser(packet, hdr, state)
        if state==State.accept or state==State.reject:
            break
    return state

def _dash_parser(packet: packet_in, hdr: headers_t, state: State):
    match state:
        case State.start:
            py_log("info", "Extracting header 'u0_ethernet'")
            hdr.u0_ethernet = packet.extract(ethernet_t)
            if hdr.u0_ethernet == None:
                return State.reject
            if hdr.u0_ethernet.ether_type == IPV4_ETHTYPE:
                return State.parse_u0_ipv4
            elif hdr.u0_ethernet.ether_type == IPV6_ETHTYPE:
                return State.parse_u0_ipv6
            elif hdr.u0_ethernet.ether_type == DASH_ETHTYPE:
                return State.parse_dash_hdr
            else:
                py_log("info", "Raw Ethernet: ", hdr.u0_ethernet)
                py_log("info", "EtherType: ", hdr.u0_ethernet.ether_type)
                return State.accept

        case State.parse_u0_ipv4:
            py_log("info", "Extracting header 'u0_ipv4'")
            hdr.u0_ipv4 = packet.extract(ipv4_t)
            if hdr.u0_ipv4 == None:
                return State.reject
            if not (hdr.u0_ipv4.version == 4):
                return State.reject
            if not (hdr.u0_ipv4.ihl == 5):
                return State.reject
            if hdr.u0_ipv4.protocol == UDP_PROTO:
                return State.parse_u0_udp
            elif hdr.u0_ipv4.protocol == TCP_PROTO:
                return State.parse_u0_tcp
            else:
                return State.accept

        case State.parse_u0_ipv6:
            py_log("info", "Extracting header 'u0_ipv6'")
            hdr.u0_ipv6 = packet.extract(ipv6_t)
            if hdr.u0_ipv6 == None:
                return State.reject
            if hdr.u0_ipv6.next_header == UDP_PROTO:
                return State.parse_u0_udp
            elif hdr.u0_ipv6.next_header == TCP_PROTO:
                return State.parse_u0_tcp
            else:
                return State.accept

        case State.parse_u0_udp:
            py_log("info", "Extracting header 'u0_udp'")
            hdr.u0_udp = packet.extract(udp_t)
            if hdr.u0_udp == None:
                return State.reject
            if hdr.u0_udp.dst_port == UDP_PORT_VXLAN:
                return State.parse_u0_vxlan
            else:
                return State.accept

        case State.parse_u0_tcp:
            py_log("info", "Extracting header 'u0_tcp'")
            hdr.u0_tcp = packet.extract(tcp_t)
            if hdr.u0_tcp == None:
                return State.reject
            return State.accept

        case State.parse_u0_vxlan:
            py_log("info", "Extracting header 'u0_vxlan'")
            hdr.u0_vxlan = packet.extract(vxlan_t)
            if hdr.u0_vxlan == None:
                return State.reject
            return State.parse_customer_ethernet

        case State.parse_dash_hdr:
            py_log("info", "Extracting header 'packet_meta'")
            hdr.packet_meta = packet.extract(dash_packet_meta_t)

            if (hdr.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_CREATE
                or hdr.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_UPDATE
                or hdr.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_DELETE):
                #  Flow create/update/delete, extract flow_key
                hdr.flow_key = packet.extract(flow_key_t)

            if hdr.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_DELETE:
                #  Flow delete, extract flow_data
                hdr.flow_data = packet.extract(flow_data_t)

                if hdr.flow_data.actions != 0:
                    hdr.flow_overlay_data = packet.extract(overlay_rewrite_data_t)

                if hdr.flow_data.actions & dash_routing_actions_t.ENCAP_U0 != 0:
                    hdr.flow_u0_encap_data = packet.extract(encap_data_t)

                if hdr.flow_data.actions & dash_routing_actions_t.ENCAP_U1 != 0:
                    hdr.flow_u1_encap_data = packet.extract(encap_data_t)

            return State.parse_customer_ethernet

        case State.parse_customer_ethernet:
            py_log("info", "Extracting header 'customer_ethernet'")
            hdr.customer_ethernet = packet.extract(ethernet_t)
            if hdr.customer_ethernet == None:
                return State.reject
            if hdr.customer_ethernet.ether_type == IPV4_ETHTYPE:
                return State.parse_customer_ipv4
            elif hdr.customer_ethernet.ether_type == IPV6_ETHTYPE:
                return State.parse_customer_ipv6
            else:
                return State.accept

        case State.parse_customer_ipv4:
            py_log("info", "Extracting header 'customer_ipv4'")
            hdr.customer_ipv4 = packet.extract(ipv4_t)
            if hdr.customer_ipv4 == None:
                return State.reject
            if not (hdr.customer_ipv4.version == 4):
                return State.reject
            if not (hdr.customer_ipv4.ihl == 5):
                return State.reject
            if hdr.customer_ipv4.protocol == UDP_PROTO:
                return State.parse_customer_udp
            elif hdr.customer_ipv4.protocol == TCP_PROTO:
                return State.parse_customer_tcp
            else:
                return State.accept

        case State.parse_customer_ipv6:
            py_log("info", "Extracting header 'customer_ipv6'")
            hdr.customer_ipv6 = packet.extract(ipv6_t)
            if hdr.customer_ipv6 == None:
                return State.reject
            if hdr.customer_ipv6.next_header == UDP_PROTO:
                return State.parse_customer_udp
            elif hdr.customer_ipv6.next_header == TCP_PROTO:
                return State.parse_customer_tcp
            else:
                return State.accept

        case State.parse_customer_tcp:
            py_log("info", "Extracting header 'customer_tcp'")
            hdr.customer_tcp = packet.extract(tcp_t)
            if hdr.customer_tcp == None:
                return State.reject
            return State.accept

        case State.parse_customer_udp:
            py_log("info", "Extracting header 'customer_udp'")
            hdr.customer_udp = packet.extract(udp_t)
            if hdr.customer_udp == None:
                return State.reject
            return State.accept

def dash_deparser(packet: packet_out):
    py_log("info", "Deparser start")

    packet.emit(hdr.dp_ethernet)
    packet.emit(hdr.packet_meta)
    packet.emit(hdr.flow_key)
    packet.emit(hdr.flow_data)
    packet.emit(hdr.flow_overlay_data)
    packet.emit(hdr.flow_u0_encap_data)
    packet.emit(hdr.flow_u1_encap_data)

    packet.emit(hdr.u1_ethernet)
    packet.emit(hdr.u1_ipv4)
    packet.emit(hdr.u1_ipv4options)
    packet.emit(hdr.u1_ipv6)
    packet.emit(hdr.u1_udp)
    packet.emit(hdr.u1_tcp)
    packet.emit(hdr.u1_vxlan)
    packet.emit(hdr.u1_nvgre)

    packet.emit(hdr.u0_ethernet)
    packet.emit(hdr.u0_ipv4)
    packet.emit(hdr.u0_ipv4options)
    packet.emit(hdr.u0_ipv6)
    packet.emit(hdr.u0_udp)
    packet.emit(hdr.u0_tcp)
    packet.emit(hdr.u0_vxlan)
    packet.emit(hdr.u0_nvgre)
    packet.emit(hdr.customer_ethernet)
    packet.emit(hdr.customer_ipv4)
    packet.emit(hdr.customer_ipv6)
    packet.emit(hdr.customer_tcp)
    packet.emit(hdr.customer_udp)

    py_log("info", "Deparser end")

