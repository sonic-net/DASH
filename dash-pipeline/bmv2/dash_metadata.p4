#ifndef _SIRIUS_METADATA_P4_
#define _SIRIUS_METADATA_P4_

#include "dash_headers.p4"

enum bit<32> dash_routing_actions_t {
    NONE = 0,
    STATIC_ENCAP = (1 << 0),
    NAT46 = (1 << 1),
    NAT64 = (1 << 2)
}

enum bit<16> dash_direction_t {
    INVALID = 0,
    OUTBOUND = 1,
    INBOUND = 2
}

// Pipeline stages:
enum bit<16> dash_pipeline_stage_t {
    INVALID = 0,

    // Inbound stages
    INBOUND_STAGE_START = 100,

    // Outbound stages
    OUTBOUND_STAGE_START = 200,
    OUTBOUND_ROUTING = 200, // OUTBOUND_STAGE_START
    OUTBOUND_MAPPING = 201,

    // Common stages
    ROUTING_ACTION_APPLY = 300
}

struct conntrack_data_t {
    bool allow_in;
    bool allow_out;
}

enum bit<16> dash_tunnel_dscp_mode_t {
    PRESERVE_MODEL = 0,
    PIPE_MODEL = 1
}

struct eni_data_t {
    bit<32> cps;
    bit<32> pps;
    bit<32> flows;
    bit<1>  admin_state;
    IPv6Address pl_sip;
    IPv6Address pl_sip_mask;
    IPv4Address pl_underlay_sip;
    bit<6>  dscp;
    dash_tunnel_dscp_mode_t dscp_mode;
}

struct encap_data_t {
    bit<24> vni;
    bit<24> dest_vnet_vni;
    IPv4Address underlay_sip;
    IPv4Address underlay_dip;
    EthernetAddress underlay_smac;
    EthernetAddress underlay_dmac;
    dash_encapsulation_t dash_encapsulation;
}

struct overlay_rewrite_data_t {
    bool is_ipv6;
    EthernetAddress dmac;
    IPv4ORv6Address sip;
    IPv4ORv6Address dip;
    IPv6Address sip_mask;
    IPv6Address dip_mask;
}

struct metadata_t {
    // Lookup context
    dash_direction_t direction;
    EthernetAddress eni_addr;
    bit<16> vnet_id;
    bit<16> dst_vnet_id;
    bit<16> eni_id;
    eni_data_t eni_data;
    bit<16> inbound_vm_id;
    bit<8> appliance_id;
    bit<1> is_overlay_ip_v6;
    bit<1> is_lkup_dst_ip_v6;
    bit<8> ip_protocol;
    IPv4ORv6Address dst_ip_addr;
    IPv4ORv6Address src_ip_addr;
    IPv4ORv6Address lkup_dst_ip_addr;
    conntrack_data_t conntrack_data;
    bit<16> src_l4_port;
    bit<16> dst_l4_port;
    bit<16> stage1_dash_acl_group_id;
    bit<16> stage2_dash_acl_group_id;
    bit<16> stage3_dash_acl_group_id;
    bit<16> stage4_dash_acl_group_id;
    bit<16> stage5_dash_acl_group_id;
    bit<1> meter_policy_en;
    bit<1> mapping_meter_class_override;
    bit<16> meter_policy_id;
    bit<16> policy_meter_class;
    bit<16> route_meter_class;
    bit<16> mapping_meter_class;
    bit<16> meter_class;
    bit<32> meter_bucket_index;
    bit<16> tunnel_pointer;
    bool is_fast_path_icmp_flow_redirection_packet;
    bit<1> fast_path_icmp_flow_redirection_disabled;

    // Stage transition control
    dash_pipeline_stage_t target_stage;

    // Actions
    bit<32> routing_actions;
    
    // Action data
    bool dropped;
    encap_data_t encap_data;
    overlay_rewrite_data_t overlay_data;
}

#endif /* _SIRIUS_METADATA_P4_ */
