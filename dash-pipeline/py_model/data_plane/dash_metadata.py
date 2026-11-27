from typing import *
from py_model.data_plane.dash_headers import *

MAX_ENI     = 64
MAX_HA_SET  = 1

dash_routing_actions_t = dash_flow_action_t

class dash_pipeline_stage_t(IntEnum):
    INVALID                             = 0

    # Inbound
    INBOUND_STAGE_STARTING              = 1 #100
    INBOUND_ROUTING                     = 2 #100

    # Outbound
    OUTBOUND_STAGE_STARTING             = 3 #200
    OUTBOUND_ROUTING                    = 4 #200
    OUTBOUND_MAPPING                    = 5 #201
    OUTBOUND_PRE_ROUTING_ACTION_APPLY   = 6 #280

    # Common
    ROUTING_ACTION_APPLY                = 7 #300

    __bitwidth__                        = 16

class dash_eni_mac_override_type_t(IntEnum):
    NONE            = 0
    SRC_MAC         = 1
    DST_MAC         = 2
    __bitwidth__    = 8

class dash_eni_mac_type_t(IntEnum):
    SRC_MAC         = 0
    DST_MAC         = 1
    __bitwidth__    = 8

class dash_eni_mode_t(IntEnum):
    VM              = 0
    FNIC            = 1
    __bitwidth__    = 8

class dash_tunnel_dscp_mode_t(IntEnum):
    PRESERVE_MODEL  = 0
    PIPE_MODEL      = 1
    __bitwidth__    = 16

class dash_ha_role_t(IntEnum):
    DEAD                = 0
    ACTIVE              = 1
    STANDBY             = 2
    STANDALONE          = 3
    SWITCHING_TO_ACTIVE = 4
    __bitwidth__        = 8

class dash_ha_state_t(IntEnum):
    DEAD                            = 0
    CONNECTING                      = 1
    CONNECTED                       = 2
    INITIALIZING_TO_ACTIVE          = 3
    INITIALIZING_TO_STANDBY         = 4
    PENDING_STANDALONE_ACTIVATION   = 5
    PENDING_ACTIVE_ACTIVATION       = 6
    PENDING_STANDBY_ACTIVATION      = 7
    STANDALONE                      = 8
    ACTIVE                          = 9
    STANDBY                         = 10
    DESTROYING                      = 11
    SWITCHING_TO_STANDALONE         = 12
    __bitwidth__                    = 8


class outbound_routing_group_data_t:
    outbound_routing_group_id : Annotated[int, 16]
    disabled                  : Annotated[int, 1]

class conntrack_data_t:
    def __init__(self, allow_in=False, allow_out=False):
        self.allow_in = allow_in
        self.allow_out = allow_out

class eni_data_t:
    cps                         : Annotated[int, 32]
    pps                         : Annotated[int, 32]
    flows                       : Annotated[int, 32]
    admin_state                 : Annotated[int, 1]
    pl_sip                      : Annotated[int, IPv6Address_size]
    pl_sip_mask                 : Annotated[int, IPv6Address_size]
    pl_underlay_sip             : Annotated[int, IPv4Address_size]
    dscp                        : Annotated[int, 6]
    dscp_mode                   : dash_tunnel_dscp_mode_t
    outbound_routing_group_data : outbound_routing_group_data_t
    vip                         : Annotated[int, IPv4Address_size]
    eni_mode                    : dash_eni_mode_t

    def __init__(self):
        self.cps = 0
        self.pps = 0
        self.flows = 0
        self.admin_state = 0
        self.pl_sip = 0
        self.pl_sip_mask = 0
        self.pl_underlay_sip = 0
        self.dscp = 0
        self.dscp_mode = dash_tunnel_dscp_mode_t.PRESERVE_MODEL
        self.outbound_routing_group_data = outbound_routing_group_data_t()
        self.vip = 0
        self.eni_mode = dash_eni_mode_t.VM

class port_map_context_t:
    map_id                      : Annotated[int, 16]
    service_rewrite_sip         : Annotated[int, IPv6Address_size]
    service_rewrite_sip_mask    : Annotated[int, IPv6Address_size]
    service_rewrite_dip         : Annotated[int, IPv6Address_size]
    service_rewrite_dip_mask    : Annotated[int, IPv6Address_size]

    def __init__(self):
        self.map_id = 0
        self.service_rewrite_sip = 0
        self.service_rewrite_sip_mask = 0
        self.service_rewrite_dip = 0
        self.service_rewrite_dip_mask = 0

class meter_context_t:
    meter_class_or        : Annotated[int, 32]
    meter_class_and       : Annotated[int, 32]
    meter_policy_id       : Annotated[int, 16]
    meter_policy_lookup_ip: Annotated[int, IPv4ORv6Address_size]

    def __init__(self):
        self.meter_class_or = 0
        self.meter_class_and = 0
        self.meter_policy_id = 0
        self.meter_policy_lookup_ip = 0

class ha_data_t:
    ha_scope_id             : Annotated[int, 16]
    ha_set_id               : Annotated[int, 16]
    ha_role                 : dash_ha_role_t
    local_ip_is_v6          : Annotated[int, 1]
    local_ip                : Annotated[int, IPv4ORv6Address_size]
    peer_ip_is_v6           : Annotated[int, 1]
    peer_ip                 : Annotated[int, IPv4ORv6Address_size]
    dp_channel_dst_port     : Annotated[int, 16]
    dp_channel_src_port_min : Annotated[int, 16]
    dp_channel_src_port_max : Annotated[int, 16]

    def __init__(self):
        self.ha_scope_id = 0
        self.ha_set_id = 0
        self.ha_role = dash_ha_role_t.DEAD
        self.local_ip_is_v6 = 0
        self.local_ip = 0
        self.peer_ip_is_v6 = 0
        self.peer_ip = 0
        self.dp_channel_dst_port = 0
        self.dp_channel_src_port_min = 0
        self.dp_channel_src_port_max = 0

# if target is TARGET_DPDK_PNA
class meta_flow_data_t:
    reserved             : Annotated[int, 7]
    is_unidirectional    : Annotated[int, 1]
    direction            : dash_direction_t
    version              : Annotated[int, 32]
    actions              : dash_flow_action_t
    meter_class          : Annotated[int, dash_meter_class_t]
    idle_timeout_in_ms   : Annotated[int, 32]

    def __init__(self):
        self.reserved = 0
        self.is_unidirectional = 0
        self.direction = dash_direction_t.INVALID
        self.version = 0
        self.actions = dash_flow_action_t.NONE
        self.meter_class = 0
        self.idle_timeout_in_ms = 0

class meta_encap_data_t:
    vni                : Annotated[int, 24]
    reserved           : Annotated[int, 8]
    underlay_sip       : Annotated[int, IPv4Address_size]
    underlay_dip       : Annotated[int, IPv4Address_size]
    underlay_smac      : Annotated[int, EthernetAddress_size]
    underlay_dmac      : Annotated[int, EthernetAddress_size]
    dash_encapsulation : dash_encapsulation_t

    def __init__(self):
        self.vni = 0
        self.reserved = 0
        self.underlay_sip = 0
        self.underlay_dip = 0
        self.underlay_smac = 0
        self.underlay_dmac = 0
        self.dash_encapsulation = dash_encapsulation_t.INVALID

class meta_overlay_rewrite_data_t:
    dmac       : Annotated[int, EthernetAddress_size]
    sip        : Annotated[int, IPv4ORv6Address_size]
    dip        : Annotated[int, IPv4ORv6Address_size]
    sip_mask   : Annotated[int, IPv6Address_size]
    dip_mask   : Annotated[int, IPv6Address_size]
    sport      : Annotated[int, 16]
    dport      : Annotated[int, 16]
    reserved   : Annotated[int, 7]
    is_ipv6    : Annotated[int, 1]

    def __init__(self):
        self.dmac = 0
        self.sip = 0
        self.dip = 0
        self.sip_mask = 0
        self.dip_mask = 0
        self.sport = 0
        self.dport = 0
        self.reserved = 0
        self.is_ipv6 = 0

class metadata_t:
    dash_acl_group_id                           :  Annotated[int, 16]
    acl_outcome_allow                           :  Annotated[int, 1]
    acl_outcome_terminate                       :  Annotated[int, 1]
    meter_policy_en                             :  Annotated[int, 1]
    mapping_meter_class_override                :  Annotated[int, 1]
    # meter_policy_id                           :  Annotated[int, 16]
    policy_meter_class                          :  Annotated[int, 16]
    route_meter_class                           :  Annotated[int, 16]
    mapping_meter_class                         :  Annotated[int, 16]
    meter_bucket_index                          :  Annotated[int, 32]

    packet_source                               :  dash_packet_source_t
    packet_type                                 :  dash_packet_type_t
    direction                                   :  dash_direction_t
    eni_mac_type                                :  dash_eni_mac_type_t
    eni_mac_override_type                       :  dash_eni_mac_override_type_t
    rx_encap                                    :  encap_data_t
    eni_addr                                    :  Annotated[int, EthernetAddress_size]
    vnet_id                                     :  Annotated[int, 16]
    dst_vnet_id                                 :  Annotated[int, 16]
    eni_id                                      :  Annotated[int, 16]
    eni_data                                    :  eni_data_t
    inbound_vm_id                               :  Annotated[int, 16]
    appliance_id                                :  Annotated[int, 8]
    is_overlay_ip_v6                            :  Annotated[int, 1]
    is_lkup_dst_ip_v6                           :  Annotated[int, 1]
    ip_protocol                                 :  Annotated[int, 8]
    dst_ip_addr                                 :  Annotated[int, IPv4ORv6Address_size]
    src_ip_addr                                 :  Annotated[int, IPv4ORv6Address_size]
    lkup_dst_ip_addr                            :  Annotated[int, IPv4ORv6Address_size]
    src_l4_port                                 :  Annotated[int, 16]
    dst_l4_port                                 :  Annotated[int, 16]
    stage1_dash_acl_group_id                    :  Annotated[int, 16]
    stage2_dash_acl_group_id                    :  Annotated[int, 16]
    stage3_dash_acl_group_id                    :  Annotated[int, 16]
    stage4_dash_acl_group_id                    :  Annotated[int, 16]
    stage5_dash_acl_group_id                    :  Annotated[int, 16]
    tunnel_pointer                              :  Annotated[int, 16]
    is_fast_path_icmp_flow_redirection_packet   :  Annotated[int, 1]
    fast_path_icmp_flow_redirection_disabled    :  Annotated[int, 1]
    port_map_ctx                                :  port_map_context_t
    meter_context                               :  meter_context_t
    ha                                          :  ha_data_t
    conntrack_data                              :  conntrack_data_t
    flow_data                                   :  flow_data_t
    flow_sync_state                             :  dash_flow_sync_state_t
    flow_table                                  :  flow_table_data_t
    bulk_get_session_id                         :  Annotated[int, 16]
    bulk_get_session_filter_id                  :  Annotated[int, 16]
    flow_enabled                                :  Annotated[int, 1]
    to_dpapp                                    :  Annotated[int, 1]
    target_stage                                :  dash_pipeline_stage_t
    routing_actions                             :  Annotated[int, 32]
    dropped                                     :  Annotated[int, 1]
    u0_encap_data                               :  encap_data_t
    u1_encap_data                               :  encap_data_t
    overlay_data                                :  overlay_rewrite_data_t
    enable_reverse_tunnel_learning              :  Annotated[int, 1]
    reverse_tunnel_sip                          :  Annotated[int, IPv4Address_size]
    dash_tunnel_id                              :  Annotated[int, 16]
    dash_tunnel_max_member_size                 :  Annotated[int, 32]
    dash_tunnel_member_index                    :  Annotated[int, 16]
    dash_tunnel_member_id                       :  Annotated[int, 16]
    dash_tunnel_next_hop_id                     :  Annotated[int, 16]
    meter_class                                 :  Annotated[int, 32]
    local_region_id                             :  Annotated[int, 8]
    cpu_mac                                     :  Annotated[int, EthernetAddress_size]

    def __init__(self):
        self.reset()

        self.rx_encap = encap_data_t()
        self.eni_data = eni_data_t()
        self.port_map_ctx = port_map_context_t()
        self.meter_context = meter_context_t()
        self.ha = ha_data_t()
        self.conntrack_data = conntrack_data_t()
        self.flow_data = flow_data_t()
        self.flow_table = flow_table_data_t()
        self.u0_encap_data = encap_data_t()
        self.u1_encap_data = encap_data_t()
        self.overlay_data = overlay_rewrite_data_t()

        self.packet_source = dash_packet_source_t.EXTERNAL
        self.packet_type = dash_packet_type_t.REGULAR
        self.direction = dash_direction_t.INVALID
        self.eni_mac_type = dash_eni_mac_type_t.SRC_MAC
        self.eni_mac_override_type = dash_eni_mac_override_type_t.NONE
        self.flow_sync_state = dash_flow_sync_state_t.FLOW_MISS
        self.target_stage = dash_pipeline_stage_t.INVALID

    def reset(self):
        annotations = get_type_hints(type(self))
        for k, t in annotations.items():
            if t in (int, bool):
                setattr(self, k, 0)
            else:
                setattr(self, k, None)
