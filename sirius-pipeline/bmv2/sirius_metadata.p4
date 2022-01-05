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
    bit<16> eni;
    bit<16> vm_id;
    bit<8> appliance_id;
    conntrack_data_t conntrack_data;
}

#endif /* _SIRIUS_METADATA_P4_ */
