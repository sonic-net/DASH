#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from scapy.all import *

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
                    ByteEnumField("ip_proto", 6, IP_PROTOS),
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


dpappEther = Ether(dst="02:fe:23:f0:e4:13",src="00:01:01:01:01:01",type=0x876D)

packetMeta = DASH_PACKET_META()
flowKey = DASH_FLOW_KEY()
flowData = DASH_FLOW_DATA()
packetMeta.length = len(packetMeta) + len(flowKey) + len(flowData)
dashMeta = packetMeta/flowKey/flowData

customerPacket = Ether(dst="00:02:02:02:02:02",type=0x0800) / \
                 IP(src = "10.1.0.10", dst="10.1.1.1")/TCP(sport=4096, dport=4096)/("a"*64)

pkt = dpappEther/dashMeta/customerPacket
sendp(pkt, iface="veth4", count=1)

