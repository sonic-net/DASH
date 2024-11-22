#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from scapy.all import *
import argparse

class DASH_PACKET_META(Packet):
    name = "DASH_PACKET_META"
    fields_desc = [ ByteField("packet_source", 0),
                    BitField("packet_type", 0, 4),
                    BitField("packet_subtype", 1, 4),
                    ShortField("length", 4),
                  ]

class DASH_FLOW_KEY(Packet):
    name = "DASH_FLOW_KEY"
    fields_desc = [ MACField("eni_mac", "0:0:0:0:0:0"),
                    ShortField("vnet_id", 2),
                    IP6Field("src_ip", "::1.1.1.1"),
                    IP6Field("dst_ip", "::2.2.2.2"),
                    XShortField("src_port", 0x5566),
                    XShortField("dst_port", 0x6677),
                    ByteEnumField("ip_proto", IP_PROTOS.udp, IP_PROTOS),
                    BitField("reserved", 0, 7),
                    BitField("is_ip_v6", 0, 1),
                  ]

class DASH_FLOW_DATA(Packet):
    name = "DASH_FLOW_DATA"
    fields_desc = [
                    BitField("reserved", 0, 7),
                    BitField("is_unidirectional", 0, 1),
                    ShortEnumField("direction", 1, { 1: "OUTBOUND", 2: "INBOUND" }),
                    IntField("version", 0),
                    IntField("actions", 0),
                    IntField("meter_class", 0),
                  ]

class DASH_OVERLAY_DATA(Packet):
    name = "DASH_OVERLAY_DATA"
    fields_desc = [ MACField("dmac", 0),
                    IP6Field("sip", "::"),
                    IP6Field("dip", "::"),
                    IP6Field("sip_mask", "::"),
                    IP6Field("dip_mask", "::"),
                    BitField("reserved", 0, 7),
                    BitField("is_ipv6", 0, 1),
                  ]

class DASH_ENCAP_DATA(Packet):
    name = "DASH_ENCAP_DATA"
    fields_desc = [ BitField("vni", 1, 24),
                    BitField("reserved", 0, 8),
                    IPField("underlay_sip", "1.1.1.1"),
                    IPField("underlay_dip", "2.2.2.2"),
                    MACField("underlay_smac", "0:0:0:0:0:0"),
                    MACField("underlay_dmac", "0:0:0:0:0:0"),
                    ShortField("dash_encapsulation", 1),
                  ]


def get_mac(interface):
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline().strip()
    except:
        mac = "00:00:00:00:00:00"
    return mac

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Packet generator on behalf of DASH pipeline")
    parser.add_argument("--flow-action", type=str, default="CREATE",
                        help="Flow action, CREATE|UPDATE|DELETE")
    parser.add_argument("--flow-key", type=str,
                         help="Flow key, string style eni_mac=,vnet_id=,src_ip=,dst_ip=,...")
    parser.add_argument("--from-port", type=str, default="veth4",
                         help="DASH pipeline port name")
    parser.add_argument("--to-port", type=str, default="veth5",
                         help="cpu port name")
    args = parser.parse_args()

    dpappEther = Ether(dst=get_mac(args.to_port),
                       src=get_mac(args.from_port), type=0x876D)

    action_dic = { "CREATE":1, "UPDATE":2, "DELETE":3 }
    try:
        flow_action = action_dic[args.flow_action]
    except KeyError:
        print(f"Invalid flow action name: {args.flow_action}")
        exit(1)

    if args.flow_key:
        flow_key = dict(kv.split("=") for kv in args.flow_key.split(","))
        if "vnet_id" in flow_key:
            flow_key["vnet_id"] = int(flow_key["vnet_id"])
        if "src_port" in flow_key:
            flow_key["src_port"] = int(flow_key["src_port"])
        if "dst_port" in flow_key:
            flow_key["dst_port"] = int(flow_key["dst_port"])
        if "ip_proto" in flow_key:
            flow_key["ip_proto"] = int(flow_key["ip_proto"])
        if "is_ip_v6" in flow_key:
            flow_key["is_ip_v6"] = int(flow_key["is_ip_v6"])
    else:
        flow_key = {}

    packetMeta = DASH_PACKET_META(packet_subtype = flow_action)
    flowKey = DASH_FLOW_KEY(**flow_key)
    flowData = DASH_FLOW_DATA()
    packetMeta.length = len(packetMeta) + len(flowKey) + len(flowData)
    dashMeta = packetMeta/flowKey/flowData

    if flowKey.is_ip_v6:
        L3 = IPv6(src = flowKey.src_ip, dst = flowKey.dst_ip)
    else:
        L3 = IP(src = flowKey.src_ip.lstrip("::"), dst = flowKey.dst_ip.lstrip("::"))

    if flowKey.ip_proto == IP_PROTOS.tcp:
        L4 = TCP(sport=flowKey.src_port, dport=flowKey.dst_port)
    else:
        L4 = UDP(sport=flowKey.src_port, dport=flowKey.dst_port)

    customerPacket = Ether(dst="00:02:02:02:02:02") / L3 / L4 / ("a"*16)

    pkt = dpappEther/dashMeta/customerPacket
    sendp(pkt, iface=args.from_port, count=1)

