#ifndef _SIRIUS_METADATA_P4_
#define _SIRIUS_METADATA_P4_

#include "dash_headers.p4"

#define MAX_ENI 64
#define MAX_HA_SET 1

typedef dash_flow_action_t dash_routing_actions_t;

// Pipeline stages:
enum bit<16> dash_pipeline_stage_t {
    INVALID = 0,

    // Inbound stages
    INBOUND_STAGE_START = 100,
    INBOUND_ROUTING = 100, // OUTBOUND_STAGE_START

    // Outbound stages
    OUTBOUND_STAGE_START = 200,
    OUTBOUND_ROUTING = 200, // OUTBOUND_STAGE_START
    OUTBOUND_MAPPING = 201,
    OUTBOUND_PRE_ROUTING_ACTION_APPLY = 280,

    // Common stages
    ROUTING_ACTION_APPLY = 300
};

enum bit<8> dash_eni_mac_override_type_t {
    NONE = 0,
    SRC_MAC = 1,
    DST_MAC = 2
};

enum bit<8> dash_eni_mac_type_t {
    SRC_MAC = 0,
    DST_MAC = 1
};

struct conntrack_data_t {
    bool allow_in;
    bool allow_out;
}

enum bit<16> dash_tunnel_dscp_mode_t {
    PRESERVE_MODEL = 0,
    PIPE_MODEL = 1
}

struct outbound_routing_group_data_t {
    bit<16> outbound_routing_group_id;
    bool disabled;
}

struct eni_data_t {
    bit<32> cps;
    bit<32> pps;
    bit<32> flows;
    bit<1>  admin_state;
    IPv6Address pl_sip;
    IPv6Address pl_sip_mask;
    IPv4Address pl_underlay_sip;
    bit<6> dscp;
    dash_tunnel_dscp_mode_t dscp_mode;
    outbound_routing_group_data_t outbound_routing_group_data;
    IPv4Address vip;
}

struct port_map_context_t {
    bit<16> map_id;
}

struct meter_context_t {
    bit<32> meter_class_or;
    bit<32> meter_class_and;
    bit<16> meter_policy_id;
    IPv4ORv6Address meter_policy_lookup_ip;
}

// HA roles
enum bit<8> dash_ha_role_t {
    DEAD = 0,
    ACTIVE = 1,
    STANDBY = 2,
    STANDALONE = 3,
    SWITCHING_TO_ACTIVE = 4
};

// HA states
enum bit<8> dash_ha_state_t {
    DEAD = 0,
    // trying to connect to HA pair
    CONNECTING = 1,
    // bulk sync in progress
    CONNECTED = 2,
    // connection successful, bulk sync in progress
    INITIALIZING_TO_ACTIVE      = 3,
    // connection successful, bulk sync in progress
    INITIALIZING_TO_STANDBY     = 4,
    // ready to be in STANDALONE state, waiting for activation of admin role
    PENDING_STANDALONE_ACTIVATION  = 5,
    // ready to be in ACTIVE state, waiting for activation of admin role
    PENDING_ACTIVE_ACTIVATION      = 6,
    // ready to be in STANDBY state, waiting for activation of admin role
    PENDING_STANDBY_ACTIVATION     = 7,
    // activation done, fowarding traffic
    STANDALONE = 8,
    // activation done, fowarding traffic and syncing flows with HA pair
    ACTIVE = 9,
    // activation done, ready to fowarding traffic if pair fails
    STANDBY = 10,
    // going down for planned shutdown
    DESTROYING = 11,
    // gracefully transitioning from paired state to stand-alone
    SWITCHING_TO_STANDALONE = 12
};

struct ha_data_t {
    // HA scope settings
    bit<16> ha_scope_id;
    bit<16> ha_set_id;
    dash_ha_role_t ha_role;

    // HA set settings
    bit<1> local_ip_is_v6;
    IPv4ORv6Address local_ip;
    bit<1> peer_ip_is_v6;
    IPv4ORv6Address peer_ip;
    bit<16> dp_channel_dst_port;
    bit<16> dp_channel_src_port_min;
    bit<16> dp_channel_src_port_max;
}

#ifdef TARGET_DPDK_PNA
// redefine encap_data_t -> meta_encap_data_t
// redefine overlay_rewrite_data_t -> meta_overlay_rewrite_data_t
// header in struct is not well supported for target dpdk-pna
struct meta_flow_data_t {
    bit<7> reserved;
    bit<1> is_unidirectional;
    dash_direction_t direction;
    bit<32> version;
    dash_flow_action_t actions;
    dash_meter_class_t meter_class;
    bit<32> idle_timeout_in_ms;
}
struct meta_encap_data_t {
    bit<24> vni;
    bit<8>  reserved;
    IPv4Address underlay_sip;
    IPv4Address underlay_dip;
    EthernetAddress underlay_smac;
    EthernetAddress underlay_dmac;
    dash_encapsulation_t dash_encapsulation;
}

struct meta_overlay_rewrite_data_t {
    EthernetAddress dmac;
    IPv4ORv6Address sip;
    IPv4ORv6Address dip;
    IPv6Address sip_mask;
    IPv6Address dip_mask;
    bit<16> sport;
    bit<16> dport;
    bit<7> reserved;
    bit<1> is_ipv6;
}
#endif // TARGET_DPDK_PNA

struct metadata_t {
    // Packet type
    dash_packet_source_t packet_source; // TODO: Parse packet source in parser.
    dash_packet_type_t packet_type; // TODO: Parse packet type in parser.

    // Lookup context
    dash_direction_t direction;
    dash_eni_mac_type_t eni_mac_type;
    dash_eni_mac_override_type_t eni_mac_override_type;
#ifdef TARGET_DPDK_PNA
    meta_encap_data_t rx_encap;
#else
    encap_data_t rx_encap;
#endif // TARGET_DPDK_PNA
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
    bit<16> src_l4_port;
    bit<16> dst_l4_port;
    bit<16> stage1_dash_acl_group_id;
    bit<16> stage2_dash_acl_group_id;
    bit<16> stage3_dash_acl_group_id;
    bit<16> stage4_dash_acl_group_id;
    bit<16> stage5_dash_acl_group_id;
    bit<16> tunnel_pointer;
    bool is_fast_path_icmp_flow_redirection_packet;
    bit<1> fast_path_icmp_flow_redirection_disabled;
    port_map_context_t port_map_ctx;
    meter_context_t meter_context;

    // HA
    ha_data_t ha;

    // Flow data
    conntrack_data_t conntrack_data;
#ifdef TARGET_DPDK_PNA
    meta_flow_data_t flow_data;
#else
    flow_data_t flow_data;
#endif // TARGET_DPDK_PNA
    dash_flow_sync_state_t flow_sync_state;
    flow_table_data_t flow_table;
    bit<16> bulk_get_session_id;
    bit<16> bulk_get_session_filter_id;
    bool flow_enabled;
    bool to_dpapp;

    // Stage transition control
    dash_pipeline_stage_t target_stage;

    // Actions
    bit<32> routing_actions;

    // Action data
    bool dropped;
#ifdef TARGET_DPDK_PNA
    meta_encap_data_t u0_encap_data;
    meta_encap_data_t u1_encap_data;
    meta_overlay_rewrite_data_t overlay_data;
#else
    encap_data_t u0_encap_data;
    encap_data_t u1_encap_data;
    overlay_rewrite_data_t overlay_data;
#endif // TARGET_DPDK_PNA
    bit<1> enable_reverse_tunnel_learning;
    IPv4Address reverse_tunnel_sip;
    bit<16> dash_tunnel_id;
    bit<32> dash_tunnel_max_member_size;
    bit<16> dash_tunnel_member_index;
    bit<16> dash_tunnel_member_id;
    bit<16> dash_tunnel_next_hop_id;
    bit<32> meter_class;
    bit<8> local_region_id;
    EthernetAddress cpu_mac;
}

#endif /* _SIRIUS_METADATA_P4_ */
