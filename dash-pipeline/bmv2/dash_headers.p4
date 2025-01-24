#ifndef _SIRIUS_HEADERS_P4_
#define _SIRIUS_HEADERS_P4_

typedef bit<48>  EthernetAddress;
typedef bit<32>  IPv4Address;
typedef bit<128> IPv6Address;
typedef bit<128> IPv4ORv6Address;

enum bit<16> dash_direction_t {
    INVALID = 0,
    OUTBOUND = 1,
    INBOUND = 2
};

typedef bit<32> dash_meter_class_t;

enum bit<8> dash_packet_source_t {
    EXTERNAL = 0,           // Packets from external sources.
    PIPELINE = 1,           // Packets from P4 pipeline.
    DPAPP = 2,              // Packets from data plane app.
    PEER = 3                // Packets from the paired DPU.
};

enum bit<4> dash_packet_type_t {
    REGULAR = 0,            // Regular packets from external sources.
    FLOW_SYNC_REQ = 1,      // Flow sync request packet.
    FLOW_SYNC_ACK = 2,      // Flow sync ack packet.
    DP_PROBE_REQ = 3,       // Data plane probe packet.
    DP_PROBE_ACK = 4        // Data plane probe ack packet.
};

// Packet subtype for one kind of packet type
enum bit<4> dash_packet_subtype_t {
    NONE = 0,        // no op
    FLOW_CREATE = 1, // New flow creation.
    FLOW_UPDATE = 2, // Flow resimulation or any other reason causing existing flow to be updated.
    FLOW_DELETE = 3  // Flow deletion.
};

enum bit<16> dash_encapsulation_t {
    INVALID = 0,
    VXLAN = 1,
    NVGRE = 2
}

header encap_data_t {
    bit<24> vni;
    bit<8>  reserved;
    IPv4Address underlay_sip;
    IPv4Address underlay_dip;
    EthernetAddress underlay_smac;
    EthernetAddress underlay_dmac;
    dash_encapsulation_t dash_encapsulation;
}
const bit<16> ENCAP_DATA_HDR_SIZE=encap_data_t.minSizeInBytes();

header overlay_rewrite_data_t {
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
const bit<16> OVERLAY_REWRITE_DATA_HDR_SIZE=overlay_rewrite_data_t.minSizeInBytes();

header ethernet_t {
    EthernetAddress dst_addr;
    EthernetAddress src_addr;
    bit<16>         ether_type;
}

const bit<16> ETHER_HDR_SIZE=112/8;

header ipv4_t {
    bit<4>      version;
    bit<4>      ihl;
    bit<8>      diffserv;
    bit<16>     total_len;
    bit<16>     identification;
    bit<3>      flags;
    bit<13>     frag_offset;
    bit<8>      ttl;
    bit<8>      protocol;
    bit<16>     hdr_checksum;
    IPv4Address src_addr;
    IPv4Address dst_addr;
}

const bit<16> IPV4_HDR_SIZE=160/8;

header ipv4options_t {
    varbit<320> options;
}

header udp_t {
    bit<16>  src_port;
    bit<16>  dst_port;
    bit<16>  length;
    bit<16>  checksum;
}

const bit<16> UDP_HDR_SIZE=64/8;

header vxlan_t {
    bit<8>  flags;
    bit<24> reserved;
    bit<24> vni;
    bit<8>  reserved_2;
}

const bit<16> VXLAN_HDR_SIZE=64/8;

header nvgre_t {
    bit<4>  flags;
    bit<9>  reserved;
    bit<3>  version;
    bit<16> protocol_type;
    bit<24> vsid;
    bit<8>  flow_id;
}

const bit<16> NVGRE_HDR_SIZE=64/8;

header tcp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

const bit<16> TCP_HDR_SIZE=160/8;

header ipv6_t {
    bit<4>      version;
    bit<8>      traffic_class;
    bit<20>     flow_label;
    bit<16>     payload_length;
    bit<8>      next_header;
    bit<8>      hop_limit;
    IPv6Address src_addr;
    IPv6Address dst_addr;
}

const bit<16> IPV6_HDR_SIZE=320/8;


// Flow sync state
enum bit<8> dash_flow_sync_state_t {
    FLOW_MISS = 0,                  // Flow not created yet
    FLOW_CREATED = 1,               // Flow is created but not synched or waiting for ack
    FLOW_SYNCED = 2,                // Flow has been synched to its peer
    FLOW_PENDING_DELETE = 3,        // Flow is pending deletion, waiting for ack
    FLOW_PENDING_RESIMULATION = 4   // Flow is marked as pending resimulation
}

enum bit<32> dash_flow_action_t {
    NONE = 0,
    ENCAP_U0 = (1 << 0),
    ENCAP_U1 = (1 << 1),
    SET_SMAC = (1 << 2),
    SET_DMAC = (1 << 3),
    SNAT  = (1 << 4),
    DNAT  = (1 << 5),
    NAT46 = (1 << 6),
    NAT64 = (1 << 7),
    SNAT_PORT = (1 << 8),
    DNAT_PORT = (1 << 9)
}

enum bit<16> dash_flow_enabled_key_t {
    ENI_MAC = (1 << 0),
    VNI = (1 << 1),
    PROTOCOL = (1 << 2),
    SRC_IP = (1 << 3),
    DST_IP = (1 << 4),
    SRC_PORT = (1 << 5),
    DST_PORT = (1 << 6)
}

enum bit<16> dash_flow_entry_bulk_get_session_mode_t {
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_GRPC = 0,
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_VENDOR = 1,
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT = 2,
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT_WITHOUT_FLOW_STATE = 3
}

enum bit<16> dash_flow_entry_bulk_get_session_filter_key_t {
    INVAILD = 0,
    FLOW_TABLE_ID = 1,
    ENI_MAC = 2,
    IP_PROTOCOL = 3,
    SRC_IP_ADDR = 4,
    DST_IP_ADDR = 5,
    SRC_L4_PORT = 6,
    DST_L4_PORT = 7,
    KEY_VERSION = 8
}

enum bit<8> dash_flow_entry_bulk_get_session_op_key_t {
    FILTER_OP_INVALID = 0,
    FILTER_OP_EQUAL_TO = 1,
    FILTER_OP_GREATER_THAN = 2,
    FILTER_OP_GREATER_THAN_OR_EQUAL_TO = 3,
    FILTER_OP_LESS_THAN = 4,
    FILTER_OP_LESS_THAN_OR_EQUAL_TO = 5
}

struct flow_table_data_t {
    bit<16> id;
    bit<32> max_flow_count;
    bit<16> flow_enabled_key;
    bit<32> flow_ttl_in_milliseconds;
}

header flow_key_t {
    EthernetAddress eni_mac;
    bit<16> vnet_id;
    IPv4ORv6Address src_ip;
    IPv4ORv6Address dst_ip;
    bit<16> src_port;
    bit<16> dst_port;
    bit<8> ip_proto;
    bit<7> reserved;
    bit<1> is_ip_v6;
}
const bit<16> FLOW_KEY_HDR_SIZE=flow_key_t.minSizeInBytes();

header flow_data_t {
    bit<7> reserved;
    bit<1> is_unidirectional;
    dash_direction_t direction;
    bit<32> version;
    dash_flow_action_t actions;
    dash_meter_class_t meter_class;
    bit<32> idle_timeout_in_ms;
}
const bit<16> FLOW_DATA_HDR_SIZE=flow_data_t.minSizeInBytes();

// dash packet metadata
header dash_packet_meta_t {
    dash_packet_source_t packet_source;
    dash_packet_type_t packet_type;
    dash_packet_subtype_t packet_subtype;
    bit<16>     length;
}
const bit<16> PACKET_META_HDR_SIZE=dash_packet_meta_t.minSizeInBytes();

#define DASH_ETHTYPE 0x876d

struct headers_t {
    /* packet metadata headers */
    ethernet_t   dp_ethernet;
    dash_packet_meta_t    packet_meta;
    flow_key_t   flow_key;
    flow_data_t  flow_data; // flow common data
    overlay_rewrite_data_t flow_overlay_data;
    encap_data_t flow_u0_encap_data;
    encap_data_t flow_u1_encap_data;

    /* Underlay 1 headers */
    ethernet_t    u1_ethernet;
    ipv4_t        u1_ipv4;
    ipv4options_t u1_ipv4options;
    ipv6_t        u1_ipv6;
    udp_t         u1_udp;
    tcp_t         u1_tcp;
    vxlan_t       u1_vxlan;
    nvgre_t       u1_nvgre;

    /* Underlay 0 headers */
    ethernet_t    u0_ethernet;
    ipv4_t        u0_ipv4;
    ipv4options_t u0_ipv4options;
    ipv6_t        u0_ipv6;
    udp_t         u0_udp;
    tcp_t         u0_tcp;
    vxlan_t       u0_vxlan;
    nvgre_t       u0_nvgre;

    /* Customer headers */
    ethernet_t    customer_ethernet;
    ipv4_t        customer_ipv4;
    ipv6_t        customer_ipv6;
    udp_t         customer_udp;
    tcp_t         customer_tcp;
}

#endif /* _SIRIUS_HEADERS_P4_ */
