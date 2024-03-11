#ifndef _SIRIUS_METADATA_P4_
#define _SIRIUS_METADATA_P4_

#include "dash_headers.p4"

#define MAX_ENI 64
#define MAX_HA_SET 1

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
};

enum bit<8> dash_packet_source_t {
    EXTERNAL = 0,           // Packets from external sources.
    DPAPP = 1,              // Packets from data plane app.
    PEER = 2                // Packets from the paired DPU.
};

enum bit<8> dash_packet_type_t {
    REGULAR = 0,            // Regular packets from external sources.
    FLOW_SYNC_REQ = 1,      // Flow sync request packet.
    FLOW_SYNC_ACK = 2,      // Flow sync ack packet.
    DP_PROBE_REQ = 3,       // Data plane probe packet.
    DP_PROBE_ACK = 4        // Data plane probe ack packet.
};

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
};

struct conntrack_data_t {
    bool allow_in;
    bool allow_out;
}

enum bit<16> dash_tunnel_dscp_mode_t {
    INVALID = 0,
    PRESERVE_MODEL = 1,
    PIPE_MODEL = 2
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
    IPv4Address original_overlay_sip;
    IPv4Address original_overlay_dip;
}

struct overlay_rewrite_data_t {
    bool is_ipv6;
    EthernetAddress dmac;
    IPv4ORv6Address sip;
    IPv4ORv6Address dip;
    IPv6Address sip_mask;
    IPv6Address dip_mask;
}

// HA roles
enum bit<8> dash_ha_role_t {
    DEAD = 0,
    ACTIVE = 1,
    STANDBY = 2,
    STANDALONE = 3,
    SWITCHING_TO_ACTIVE = 4
};

// Flow sync state
enum bit<8> dash_ha_flow_sync_state_t {
    FLOW_MISS = 0,
    FLOW_CREATED = 1,
    FLOW_SYNCED = 2,
    FLOW_PENDING_DELETE = 3
};

// HA flow sync operations
enum bit<8> dash_ha_flow_sync_op_t {
    FLOW_CREATE = 0, // New flow creation.
    FLOW_UPDATE = 1, // Flow resimulation or any other reason causing existing flow to be updated.
    FLOW_DELETE = 2  // Flow deletion.
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

    // HA packet/flow state
    dash_ha_flow_sync_state_t flow_sync_state;
}

struct metadata_t {
    // Packet type
    dash_packet_source_t packet_source; // TODO: Parse packet source in parser.
    dash_packet_type_t packet_type; // TODO: Parse packet type in parser.

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

    // HA
    ha_data_t ha;

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
