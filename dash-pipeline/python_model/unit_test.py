from scapy.all import *
from __main import *

vip.insert({
    "hdr.ipv4.dst_addr" : 0xC0A80A0F,
    "action"            : accept,
    "params"            : []
})

direction_lookup.insert({
    "hdr.vxlan.vni" : 16777215,
    "action"        : set_outbound_direction,
    "params"        : []
})

eni_ether_address_map.insert({
    "meta.eni_addr" : 0x204ef61acf47,
    "action"        : set_eni,
    "params"        : [12]
})

eni.insert({
    "meta.eni_id" : 12,
    "action"      : set_eni_attrs,
    "params"      : [0, 0, 0, 1, 0xC0A80A09, 16777215, 7000, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
})

routing.insert({
    "meta.eni_id"           : 12,
    "meta.is_overlay_ip_v6" : 1,
    "meta.dst_ip_addr"      : {
        "value"      : 0xABCD1234123412341234123412341234,
        "prefix_len" : 16
    },
    "action"                : route_vnet,
    "params"                : [8000, 0, 0]
})

ca_to_pa.insert({
    "meta.dst_vnet_id"       : 8000,
    "meta.is_lkup_dst_ip_v6" : 1,
    "meta.lkup_dst_ip_addr"  : 0xABCD000000000000000000000000EEEE,
    "action"                 : set_tunnel_mapping,
    "params"                 : [0xC0A80AC8, 0x305e062adf57, 1, 0, 0]
})

vnet.insert({
    "meta.vnet_id" : 8000,
    "action"       : set_vnet_attrs,
    "params"       : [78000]
})

meter_bucket.insert({
    "meta.eni_id"      : 12,
    "meta.meter_class" : 0,
    "action"           : meter_bucket_action,
    "params"           : [0, 0, 10]
})

appliance.insert({
    "meta.appliance_id" : {
        "value" : 0,
        "mask"  : 0
    },
    "action"            : set_appliance,
    "params"            : [0, 0]
})

acl.insert({
    "meta.dash_acl_group_id" : 1,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 0,
    "action"   : set_acl_outcome,
    "params"   : [1, 1]
})

acl.insert({
    "meta.dash_acl_group_id" : 2,
    "meta.src_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.dst_ip_addr"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "meta.src_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.dst_l4_port"  : [
        {
            "first" : 0,
            "last"  : 0xFFFF
        }
    ],
    "meta.ip_protocol"  : [
        {
            "value" : 0,
            "mask"  : 0
        }
    ],
    "priority" : 0,
    "action"   : set_acl_outcome,
    "params"   : [0, 1]
})

inbound_routing.insert({
    "meta.eni_id"       : 12,
    "hdr.vxlan.vni"     : 45,
    "hdr.ipv4.src_addr" : {
        "value" : 0,
        "mask"  : 0
    },
    "priority"  : 0,
    "action"    : vxlan_decap,
    "params"    : []
})

req_pkt = Ether()/\
          IP(src="192.168.10.9", dst="192.168.10.15")/\
          UDP()/\
          VXLAN(vni=16777215)/\
          Ether(src="20:4e:f6:1a:cf:47")/\
          IPv6(src="ABCD:0000:0000:0000:0000:0000:0000:AAAA", dst="ABCD:0000:0000:0000:0000:0000:0000:EEEE")/\
          UDP()/\
          Raw(load=('32ff00'))

resp_pkt = Ether()/\
           IP(src="192.168.10.55", dst="192.168.10.15")/\
           UDP()/\
           VXLAN(vni=45)/\
           Ether(dst="20:4e:f6:1a:cf:47")/\
           IPv6(src="ABCD:0000:0000:0000:0000:0000:0000:EEEE", dst="ABCD:0000:0000:0000:0000:0000:0000:AAAA")/\
           UDP()/\
           Raw(load=('32ff00'))

transformed_req_pkt = Ether(run_pipeline(bytes(req_pkt)))
transformed_resp_pkt = Ether(run_pipeline(bytes(resp_pkt)))

req_pkt.show()
resp_pkt.show()
transformed_req_pkt.show()
transformed_resp_pkt.show()
