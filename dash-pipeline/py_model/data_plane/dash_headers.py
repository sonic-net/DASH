from typing import *
from inspect import *
from enum import IntEnum, IntFlag

EthernetAddress_size    = 48
IPv4Address_size        = 32
IPv6Address_size        = 128
IPv4ORv6Address_size    = 128

UDP_PORT_VXLAN  = 0x12B5
UDP_PROTO       = 0x11
TCP_PROTO       = 0x06
NVGRE_PROTO     = 0x2f
IPV4_ETHTYPE    = 0x0800
IPV6_ETHTYPE    = 0x86DD
DASH_ETHTYPE    = 0x876d

class dash_direction_t(IntEnum):
    INVALID         = 0
    OUTBOUND        = 1
    INBOUND         = 2
    __bitwidth__    = 16

dash_meter_class_t = 32

class dash_packet_source_t(IntEnum):
    EXTERNAL     = 0
    PIPELINE     = 1
    DPAPP        = 2
    PEER         = 3
    __bitwidth__ = 8

class dash_packet_type_t(IntEnum):
    REGULAR         = 0
    FLOW_SYNC_REQ   = 1
    FLOW_SYNC_ACK   = 2
    DP_PROBE_REQ    = 3
    DP_PROBE_ACK    = 4
    __bitwidth__    = 4

class dash_packet_subtype_t(IntEnum):
    NONE            = 0
    FLOW_CREATE     = 1
    FLOW_UPDATE     = 2
    FLOW_DELETE     = 3
    __bitwidth__    = 4


class dash_encapsulation_t(IntEnum):
    INVALID         = 0
    VXLAN           = 1
    NVGRE           = 2
    __bitwidth__    = 16

# Flow sync state
class dash_flow_sync_state_t(IntEnum):
    FLOW_MISS                   = 0
    FLOW_CREATED                = 1
    FLOW_SYNCED                 = 2
    FLOW_PENDING_DELETE         = 3
    FLOW_PENDING_RESIMULATION   = 4
    __bitwidth__                = 8

class dash_flow_action_t(IntFlag):
    NONE            = 0
    ENCAP_U0        = (1 << 0)
    ENCAP_U1        = (1 << 1)
    SET_SMAC        = (1 << 2)
    SET_DMAC        = (1 << 3)
    SNAT            = (1 << 4)
    DNAT            = (1 << 5)
    NAT46           = (1 << 6)
    NAT64           = (1 << 7)
    SNAT_PORT       = (1 << 8)
    DNAT_PORT       = (1 << 9)
    __bitwidth__    = 32

class dash_flow_enabled_key_t(IntFlag):
    ENI_MAC     = (1 << 0)
    VNI         = (1 << 1)
    PROTOCOL    = (1 << 2)
    SRC_IP      = (1 << 3)
    DST_IP      = (1 << 4)
    SRC_PORT    = (1 << 5)
    DST_PORT    = (1 << 6)
    __bitwidth__= 16

class dash_flow_entry_bulk_get_session_mode_t(IntEnum):
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_GRPC                      = 0
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_VENDOR                    = 1
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT                     = 2
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT_WITHOUT_FLOW_STATE  = 3
    __bitwidth__                                                        = 16

class dash_flow_entry_bulk_get_session_filter_key_t(IntEnum):
    INVAILD         = 0     #FIXME:: Farhan
    FLOW_TABLE_ID   = 1
    ENI_MAC         = 2
    IP_PROTOCOL     = 3
    SRC_IP_ADDR     = 4
    DST_IP_ADDR     = 5
    SRC_L4_PORT     = 6
    DST_L4_PORT     = 7
    KEY_VERSION     = 8
    __bitwidth__    = 16

class dash_flow_entry_bulk_get_session_op_key_t(IntEnum):
    FILTER_OP_INVALID                   = 0
    FILTER_OP_EQUAL_TO                  = 1
    FILTER_OP_GREATER_THAN              = 2
    FILTER_OP_GREATER_THAN_OR_EQUAL_TO  = 3
    FILTER_OP_LESS_THAN                 = 4
    FILTER_OP_LESS_THAN_OR_EQUAL_TO     = 5
    __bitwidth__                        = 8

class flow_table_data_t:
    id                          : Annotated[int, 16]
    max_flow_count              : Annotated[int, 32]
    flow_enabled_key            : Annotated[int, 16]
    flow_ttl_in_milliseconds    : Annotated[int, 32]

    def __init__(self):
        self.id = 0
        self.max_flow_count = 0
        self.flow_enabled_key = 0
        self.flow_ttl_in_milliseconds = 0


class flow_key_t:
    eni_mac  : Annotated[int, EthernetAddress_size]
    vnet_id  : Annotated[int, 16]
    src_ip   : Annotated[int, IPv4ORv6Address_size]
    dst_ip   : Annotated[int, IPv4ORv6Address_size]
    src_port : Annotated[int, 16]
    dst_port : Annotated[int, 16]
    ip_proto : Annotated[int, 8]
    reserved : Annotated[int, 7]
    is_ip_v6 : Annotated[int, 1]

    def __init__(self):
        self.eni_mac = 0
        self.vnet_id = 0
        self.src_ip = 0
        self.dst_ip = 0
        self.src_port = 0
        self.dst_port = 0
        self.ip_proto = 0
        self.reserved = 0
        self.is_ip_v6 = 0

FLOW_KEY_HDR_SIZE = 46

class flow_data_t:
    reserved            : Annotated[int, 7]
    is_unidirectional   : Annotated[int, 1]
    direction           : dash_direction_t
    version             : Annotated[int, 32]
    actions             : dash_flow_action_t
    meter_class         : Annotated[int, 32]
    idle_timeout_in_ms  : Annotated[int, 32]

    def __init__(self):
        self.reserved = 0
        self.is_unidirectional = 0
        self.direction = dash_direction_t.INVALID
        self.version = 0
        self.actions = dash_flow_action_t.NONE
        self.meter_class = 0
        self.idle_timeout_in_ms = 0

FLOW_DATA_HDR_SIZE = 19

class dash_packet_meta_t:
    packet_source   : dash_packet_source_t
    packet_type     : dash_packet_type_t
    packet_subtype  : dash_packet_subtype_t
    length          : Annotated[int, 16]

    def __init__(self):
        self.packet_source = dash_packet_source_t.EXTERNAL
        self.packet_type = dash_packet_type_t.REGULAR
        self.packet_subtype = dash_packet_subtype_t.NONE
        self.length = 0

PACKET_META_HDR_SIZE = 4


class encap_data_t:
    vni                 : Annotated[int, 24]
    reserved            : Annotated[int, 8]
    underlay_sip        : Annotated[int, IPv4Address_size]
    underlay_dip        : Annotated[int, IPv4Address_size]
    underlay_smac       : Annotated[int, EthernetAddress_size]
    underlay_dmac       : Annotated[int, EthernetAddress_size]
    dash_encapsulation  : dash_encapsulation_t

    def __init__(self):
        self.vni = 0
        self.reserved = 0
        self.underlay_sip = 0
        self.underlay_dip = 0
        self.underlay_smac = 0
        self.underlay_dmac = 0
        self.dash_encapsulation = dash_encapsulation_t.INVALID

ENCAP_DATA_HDR_SIZE = 26

class overlay_rewrite_data_t:
    # smac        : Annotated[int, EthernetAddress_size]
    dmac        : Annotated[int, EthernetAddress_size]
    sip         : Annotated[int, IPv4ORv6Address_size]
    dip         : Annotated[int, IPv4ORv6Address_size]
    sip_mask    : Annotated[int, IPv6Address_size]
    dip_mask    : Annotated[int, IPv6Address_size]
    sport       : Annotated[int, 16]
    dport       : Annotated[int, 16]
    reserved    : Annotated[int, 7]
    is_ipv6     : Annotated[int, 1]

    def __init__(self):
        # self.smac = 0
        self.dmac = 0
        self.sip = 0
        self.dip = 0
        self.sip_mask = 0
        self.dip_mask = 0
        self.sport = 0
        self.dport = 0
        self.reserved = 0
        self.is_ipv6 = 0

OVERLAY_REWRITE_DATA_HDR_SIZE = 75

class ethernet_t:
    dst_addr   : Annotated[int, EthernetAddress_size]
    src_addr   : Annotated[int, EthernetAddress_size]
    ether_type : Annotated[int, 16]
    
    def __init__(self):
        self.dst_addr = 0
        self.src_addr = 0
        self.ether_type = 0

ETHER_HDR_SIZE = 14

class ipv4_t:
    version        : Annotated[int, 4]
    ihl            : Annotated[int, 4]
    diffserv       : Annotated[int, 8]
    total_len      : Annotated[int, 16]
    identification : Annotated[int, 16]
    flags          : Annotated[int, 3]
    frag_offset    : Annotated[int, 13]
    ttl            : Annotated[int, 8]
    protocol       : Annotated[int, 8]
    hdr_checksum   : Annotated[int, 16]
    src_addr       : Annotated[int, IPv4Address_size]
    dst_addr       : Annotated[int, IPv4Address_size]
    
    def __init__(self):
        self.version = 0
        self.ihl = 0
        self.diffserv = 0
        self.total_len = 0
        self.identification = 0
        self.flags = 0
        self.frag_offset = 0
        self.ttl = 0
        self.protocol = 0
        self.hdr_checksum = 0
        self.src_addr = 0
        self.dst_addr = 0

IPV4_HDR_SIZE = 20

class ipv4options_t:
    options : Annotated[int, 320]

class udp_t:
    src_port : Annotated[int, 16]
    dst_port : Annotated[int, 16]
    length   : Annotated[int, 16]
    checksum : Annotated[int, 16]

UDP_HDR_SIZE = 8

class vxlan_t:
    flags      : Annotated[int, 8]
    reserved   : Annotated[int, 24]
    vni        : Annotated[int, 24]
    reserved_2 : Annotated[int, 8]

VXLAN_HDR_SIZE = 8

class nvgre_t:
    flags         : Annotated[int, 4]
    reserved      : Annotated[int, 9]
    version       : Annotated[int, 3]
    protocol_type : Annotated[int, 16]
    vsid          : Annotated[int, 24]
    flow_id       : Annotated[int, 8]

NVGRE_HDR_SIZE = 8

class tcp_t:
    src_port    : Annotated[int, 16]
    dst_port    : Annotated[int, 16]
    seq_no      : Annotated[int, 32]
    ack_no      : Annotated[int, 32]
    data_offset : Annotated[int, 4]
    res         : Annotated[int, 3]
    ecn         : Annotated[int, 3]
    flags       : Annotated[int, 6]
    window      : Annotated[int, 16]
    checksum    : Annotated[int, 16]
    urgent_ptr  : Annotated[int, 16]

TCP_HDR_SIZE = 20

class ipv6_t:
    version        : Annotated[int, 4]
    traffic_class  : Annotated[int, 8]
    flow_label     : Annotated[int, 20]
    payload_length : Annotated[int, 16]
    next_header    : Annotated[int, 8]
    hop_limit      : Annotated[int, 8]
    src_addr       : Annotated[int, IPv6Address_size]
    dst_addr       : Annotated[int, IPv6Address_size]
    
    def __init__(self):
        self.version = 0
        self.traffic_class = 0
        self.flow_label = 0
        self.payload_length = 0
        self.next_header = 0
        self.hop_limit = 0
        self.src_addr = 0
        self.dst_addr = 0

IPV6_HDR_SIZE = 40

class headers_t:
    # packet metadata headers
    dp_ethernet        : ethernet_t
    packet_meta        : dash_packet_meta_t
    flow_key           : flow_key_t
    flow_data          : flow_data_t
    flow_overlay_data  : overlay_rewrite_data_t
    flow_u0_encap_data : encap_data_t
    flow_u1_encap_data : encap_data_t

    # Underlay 1 headers
    u1_ethernet         : ethernet_t
    u1_ipv4             : ipv4_t
    u1_ipv4options      : ipv4options_t
    u1_ipv6             : ipv6_t
    u1_udp              : udp_t
    u1_tcp              : tcp_t
    u1_vxlan            : vxlan_t
    u1_nvgre            : nvgre_t

    # Underlay 0 headers
    u0_ethernet         : ethernet_t
    u0_ipv4             : ipv4_t
    u0_ipv4options      : ipv4options_t
    u0_ipv6             : ipv6_t
    u0_udp              : udp_t
    u0_tcp              : tcp_t
    u0_vxlan            : vxlan_t
    u0_nvgre            : nvgre_t

    # Customer headers
    customer_ethernet   : ethernet_t
    customer_ipv4       : ipv4_t
    customer_ipv6       : ipv6_t
    customer_udp        : udp_t
    customer_tcp        : tcp_t

    def __init__(self):
        self.reset()

    def reset(self):
        annotations = get_annotations(type(self))
        for k in annotations:
            setattr(self, k, None)
