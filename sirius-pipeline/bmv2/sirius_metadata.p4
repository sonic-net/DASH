#ifndef _SIRIUS_METADATA_P4_
#define _SIRIUS_METADATA_P4_

#include "sirius_headers.p4"

struct encap_data_t {
    bit<24> vni;
    bit<24> dest_vnet_vni;
    IPv4Address underlay_sip;
    IPv4Address underlay_dip;
    EthernetAddress underlay_smac;
    EthernetAddress underlay_dmac;
    EthernetAddress overlay_dmac;
}

enum direction_t {
    INVALID,
    OUTBOUND,
    INBOUND
}

struct conntrack_data_t {
    bool allow_in;
    bool allow_out;
}

struct metadata_t {
    bool dropped;
    direction_t direction;
    encap_data_t encap_data;
    EthernetAddress eni_addr;
    bit<16> eni;
    bit<16> stage1_acl_group_id;
    bit<16> stage2_acl_group_id;
    bit<16> stage3_acl_group_id;
    bit<16> acl_group_id;
    bit<16> route_table_id;
    bit<16> tunnel_id;
    bit<16> vnet;
    bit<24> lookup_vni;
    bit<16> vm_id;
    bit<8> appliance_id;
    bit<1> is_dst_ip_v6;
    IPv4ORv6Address dst_ip_addr;
    conntrack_data_t conntrack_data;
}

#endif /* _SIRIUS_METADATA_P4_ */
