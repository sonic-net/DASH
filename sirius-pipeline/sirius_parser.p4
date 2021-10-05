#ifndef _SIRIUS_PARSER_P4_
#define _SIRIUS_PARSER_P4_

#include "sirius_headers.p4"

error {
    IPv4IncorrectVersion,
    IPv4OptionsNotSupported
}

#define UDP_PORT_VXLAN 4789
#define UDP_PROTO 17
#define TCP_PROTO 6
#define IPV4_ETHTYPE 0x800
#define IPV6_ETHTYPE 0x86dd

parser sirius_parser(packet_in packet,
                out headers_t hd,
                inout metadata_t meta,
                inout standard_metadata_t standard_meta)
{
    state start {
        packet.extract(hd.ethernet);
        transition select(hd.ethernet.ether_type) {
            0x0800:  parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hd.ipv4);
        verify(hd.ipv4.version == 4w4, error.IPv4IncorrectVersion);
        verify(hd.ipv4.ihl == 4w5, error.IPv4OptionsNotSupported);
        transition select(hd.ipv4.protocol) {
            UDP_PROTO: parse_udp;
            TCP_PROTO: parse_tcp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hd.udp);
        transition select(hd.udp.dst_port) {
            UDP_PORT_VXLAN: parse_vxlan;
            default: accept;
         }
    }

    state parse_tcp {
        packet.extract(hd.tcp);
        transition accept;
    }

    state parse_vxlan {
        packet.extract(hd.vxlan);
        transition parse_inner_ethernet;
    }

    state parse_inner_ethernet {
        packet.extract(hd.inner_ethernet);
        transition select(hd.ethernet.ether_type) {
            IPV4_ETHTYPE: parse_inner_ipv4;
            default: accept;
        }
    }

    state parse_inner_ipv4 {
        packet.extract(hd.inner_ipv4);
        verify(hd.inner_ipv4.version == 4w4, error.IPv4IncorrectVersion);
        verify(hd.inner_ipv4.ihl == 4w5, error.IPv4OptionsNotSupported);
        transition select(hd.inner_ipv4.protocol) {
            UDP_PROTO: parse_inner_udp;
            TCP_PROTO: parse_inner_tcp;
            default: accept;
        }
    }

    state parse_inner_tcp {
        packet.extract(hd.inner_tcp);
        transition accept;
    }

    state parse_inner_udp {
        packet.extract(hd.inner_udp);
        transition accept;
    }
}

control sirius_deparser(packet_out packet,
                   in headers_t hdr)
{
    apply {
	packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv6);
        packet.emit(hdr.udp);
        packet.emit(hdr.tcp);
        packet.emit(hdr.vxlan);
        packet.emit(hdr.inner_ethernet);
        packet.emit(hdr.inner_ipv4);
        packet.emit(hdr.inner_ipv6);
        packet.emit(hdr.inner_tcp);
        packet.emit(hdr.inner_udp);
    }
}

#endif /* _SIRIUS_PARSER_P4_ */
