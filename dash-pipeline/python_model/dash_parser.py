from dash_headers import *
from enum import Enum, auto
from __packet_in import *
from __packet_out import *

class State(Enum):
    accept                =  auto()
    reject                =  auto()
    start                 =  auto()
    parse_ipv4            =  auto()
    parse_ipv6            =  auto()
    parse_udp             =  auto()
    parse_tcp             =  auto()
    parse_vxlan           =  auto()
    parse_inner_ethernet  =  auto()
    parse_inner_ipv4      =  auto()
    parse_inner_ipv6      =  auto()
    parse_inner_tcp       =  auto()
    parse_inner_udp       =  auto()

def dash_parser(packet: packet_in, hdr: headers_t):
    state = State.start
    while True:
        state = _dash_parser(packet, hdr, state)
        if state==State.accept or state==State.reject:
            break
    return state

def _dash_parser(packet: packet_in, hdr: headers_t, state: State):
    match state:
        case State.start:
            hdr.ethernet = packet.extract(ethernet_t)
            if hdr.ethernet == None:
                return State.reject
            if hdr.ethernet.ether_type == IPV4_ETHTYPE:
                return State.parse_ipv4
            elif hdr.ethernet.ether_type == IPV6_ETHTYPE:
                return State.parse_ipv6
            else:
                return State.accept

        case State.parse_ipv4:
            hdr.ipv4 = packet.extract(ipv4_t)
            if hdr.ipv4 == None:
                return State.reject
            if not (hdr.ipv4.version == 4):
                return State.reject
            if not (hdr.ipv4.ihl == 5):
                return State.reject
            if hdr.ipv4.protocol == UDP_PROTO:
                return State.parse_udp
            elif hdr.ipv4.protocol == TCP_PROTO:
                return State.parse_tcp
            else:
                return State.accept

        case State.parse_ipv6:
            hdr.ipv6 = packet.extract(ipv6_t)
            if hdr.ipv6 == None:
                return State.reject
            if hdr.ipv6.next_header == UDP_PROTO:
                return State.parse_udp
            elif hdr.ipv6.next_header == TCP_PROTO:
                return State.parse_tcp
            else:
                return State.accept

        case State.parse_udp:
            hdr.udp = packet.extract(udp_t)
            if hdr.udp == None:
                return State.reject
            if hdr.udp.dst_port == UDP_PORT_VXLAN:
                return State.parse_vxlan
            else:
                return State.accept

        case State.parse_tcp:
            hdr.tcp = packet.extract(tcp_t)
            if hdr.tcp == None:
                return State.reject
            return State.accept

        case State.parse_vxlan:
            hdr.vxlan = packet.extract(vxlan_t)
            if hdr.vxlan == None:
                return State.reject
            return State.parse_inner_ethernet

        case State.parse_inner_ethernet:
            hdr.inner_ethernet = packet.extract(ethernet_t)
            if hdr.inner_ethernet == None:
                return State.reject
            if hdr.inner_ethernet.ether_type == IPV4_ETHTYPE:
                return State.parse_inner_ipv4
            elif hdr.inner_ethernet.ether_type == IPV6_ETHTYPE:
                return State.parse_inner_ipv6
            else:
                return State.accept

        case State.parse_inner_ipv4:
            hdr.inner_ipv4 = packet.extract(ipv4_t)
            if hdr.inner_ipv4 == None:
                return State.reject
            if not (hdr.inner_ipv4.version == 4):
                return State.reject
            if not (hdr.inner_ipv4.ihl == 5):
                return State.reject
            if hdr.inner_ipv4.protocol == UDP_PROTO:
                return State.parse_inner_udp
            elif hdr.inner_ipv4.protocol == TCP_PROTO:
                return State.parse_inner_tcp
            else:
                return State.accept

        case State.parse_inner_ipv6:
            hdr.inner_ipv6 = packet.extract(ipv6_t)
            if hdr.inner_ipv6 == None:
                return State.reject
            if hdr.inner_ipv6.next_header == UDP_PROTO:
                return State.parse_inner_udp
            elif hdr.inner_ipv6.next_header == TCP_PROTO:
                return State.parse_inner_tcp
            else:
                return State.accept

        case State.parse_inner_tcp:
            hdr.inner_tcp = packet.extract(tcp_t)
            if hdr.inner_tcp == None:
                return State.reject
            return State.accept

        case State.parse_inner_udp:
            hdr.inner_udp = packet.extract(udp_t)
            if hdr.inner_udp == None:
                return State.reject
            return State.accept

def dash_deparser(packet: packet_out, hdr: headers_t):
    packet.emit(hdr.ethernet)
    packet.emit(hdr.ipv4)
    packet.emit(hdr.ipv6)
    packet.emit(hdr.udp)
    packet.emit(hdr.tcp)
    packet.emit(hdr.vxlan)
    packet.emit(hdr.nvgre)
    packet.emit(hdr.inner_ethernet)
    packet.emit(hdr.inner_ipv4)
    packet.emit(hdr.inner_ipv6)
    packet.emit(hdr.inner_tcp)
    packet.emit(hdr.inner_udp)
