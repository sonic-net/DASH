from py_model.libs.__utils import *
from py_model.libs.__table import *

def conntrack_set_meta_from_dash_header():
    # basic metadata
    meta.direction = hdr.flow_data.direction
    meta.dash_tunnel_id = 0
    meta.routing_actions = hdr.flow_data.actions
    meta.meter_class = hdr.flow_data.meter_class

    # encapsulation metadata
    if TARGET == TARGET_DPDK_PNA:
        meta.u0_encap_data.vni = hdr.flow_u0_encap_data.vni
        meta.u0_encap_data.underlay_sip = hdr.flow_u0_encap_data.underlay_sip
        meta.u0_encap_data.underlay_dip = hdr.flow_u0_encap_data.underlay_dip
        meta.u0_encap_data.underlay_smac = hdr.flow_u0_encap_data.underlay_smac
        meta.u0_encap_data.underlay_dmac = hdr.flow_u0_encap_data.underlay_dmac
        meta.u0_encap_data.dash_encapsulation = hdr.flow_u0_encap_data.dash_encapsulation
    else:
        meta.u0_encap_data = hdr.flow_u0_encap_data

    # tunnel metadata
    if TARGET == TARGET_DPDK_PNA:
        meta.u1_encap_data.vni = hdr.flow_u1_encap_data.vni
        meta.u1_encap_data.underlay_sip = hdr.flow_u1_encap_data.underlay_sip
        meta.u1_encap_data.underlay_dip = hdr.flow_u1_encap_data.underlay_dip
        meta.u1_encap_data.underlay_smac = hdr.flow_u1_encap_data.underlay_smac
        meta.u1_encap_data.underlay_dmac = hdr.flow_u1_encap_data.underlay_dmac
        meta.u1_encap_data.dash_encapsulation = hdr.flow_u1_encap_data.dash_encapsulation
    else:
        meta.u1_encap_data = hdr.flow_u1_encap_data

        # overlay rewrite metadata
    if TARGET == TARGET_DPDK_PNA:
        meta.overlay_data.dmac = hdr.flow_overlay_data.dmac
        meta.overlay_data.sip = hdr.flow_overlay_data.sip
        meta.overlay_data.dip = hdr.flow_overlay_data.dip
        meta.overlay_data.sip_mask = hdr.flow_overlay_data.sip_mask
        meta.overlay_data.dip_mask = hdr.flow_overlay_data.dip_mask
        meta.overlay_data.is_ipv6 = hdr.flow_overlay_data.is_ipv6
    else:
        meta.overlay_data = hdr.flow_overlay_data

def conntrack_strip_dash_header():
    hdr.dp_ethernet = None
    hdr.packet_meta = None
    hdr.flow_key = None
    hdr.flow_data = None
    hdr.flow_overlay_data = None
    hdr.flow_u0_encap_data = None
    hdr.flow_u1_encap_data = None

class conntrack_build_dash_header:
    @classmethod
    def apply(cls, packet_subtype : dash_packet_subtype_t):
        py_log("info", "conntrack_build_dash_header")

        length = 0

        hdr.flow_data = flow_data_t()
        hdr.flow_data.is_unidirectional = 0
        hdr.flow_data.version = 0
        hdr.flow_data.direction = meta.direction
        hdr.flow_data.actions = meta.routing_actions
        hdr.flow_data.meter_class = meta.meter_class
        hdr.flow_data.idle_timeout_in_ms = meta.flow_data.idle_timeout_in_ms
        length += FLOW_DATA_HDR_SIZE

        if meta.routing_actions & dash_routing_actions_t.ENCAP_U0 != 0:
            if TARGET == TARGET_DPDK_PNA:
                hdr.flow_u0_encap_data = encap_data_t()
                hdr.flow_u0_encap_data.vni = meta.u0_encap_data.vni
                hdr.flow_u0_encap_data.underlay_sip = meta.u0_encap_data.underlay_sip
                hdr.flow_u0_encap_data.underlay_dip = meta.u0_encap_data.underlay_dip
                hdr.flow_u0_encap_data.underlay_smac = meta.u0_encap_data.underlay_smac
                hdr.flow_u0_encap_data.underlay_dmac = meta.u0_encap_data.underlay_dmac
                hdr.flow_u0_encap_data.dash_encapsulation = meta.u0_encap_data.dash_encapsulation
            else:
                hdr.flow_u0_encap_data = meta.u0_encap_data
            length += ENCAP_DATA_HDR_SIZE

        if meta.routing_actions & dash_routing_actions_t.ENCAP_U1 != 0:
            if TARGET == TARGET_DPDK_PNA:
                hdr.flow_u1_encap_data = encap_data_t()
                hdr.flow_u1_encap_data.vni = meta.u1_encap_data.vni
                hdr.flow_u1_encap_data.underlay_sip = meta.u1_encap_data.underlay_sip
                hdr.flow_u1_encap_data.underlay_dip = meta.u1_encap_data.underlay_dip
                hdr.flow_u1_encap_data.underlay_smac = meta.u1_encap_data.underlay_smac
                hdr.flow_u1_encap_data.underlay_dmac = meta.u1_encap_data.underlay_dmac
                hdr.flow_u1_encap_data.dash_encapsulation = meta.u1_encap_data.dash_encapsulation
            else:
                hdr.flow_u1_encap_data = meta.u1_encap_data
            length += ENCAP_DATA_HDR_SIZE

        if meta.routing_actions != 0:
            if TARGET == TARGET_DPDK_PNA:
                hdr.flow_overlay_data = overlay_rewrite_data_t()
                hdr.flow_overlay_data.dmac = meta.overlay_data.dmac
                hdr.flow_overlay_data.sip = meta.overlay_data.sip
                hdr.flow_overlay_data.dip = meta.overlay_data.dip
                hdr.flow_overlay_data.sip_mask = meta.overlay_data.sip_mask
                hdr.flow_overlay_data.dip_mask = meta.overlay_data.dip_mask
                hdr.flow_overlay_data.is_ipv6 = meta.overlay_data.is_ipv6
            else:
                hdr.flow_overlay_data = meta.overlay_data
            length += OVERLAY_REWRITE_DATA_HDR_SIZE

        length += FLOW_KEY_HDR_SIZE

        hdr.packet_meta = dash_packet_meta_t()
        hdr.packet_meta.packet_source = dash_packet_source_t.PIPELINE
        hdr.packet_meta.packet_type = dash_packet_type_t.REGULAR
        hdr.packet_meta.packet_subtype = packet_subtype
        hdr.packet_meta.length = length + PACKET_META_HDR_SIZE

        hdr.dp_ethernet = ethernet_t()
        hdr.dp_ethernet.dst_addr = meta.cpu_mac
        hdr.dp_ethernet.src_addr = meta.u0_encap_data.underlay_smac
        hdr.dp_ethernet.ether_type = DASH_ETHTYPE

class conntrack_flow_miss_handle():
    @classmethod
    def apply(cls):
        py_log("info", "conntrack_flow_miss_handle")
        # SYN
        if (hdr.customer_tcp and hdr.customer_tcp.flags == 0x2) or hdr.customer_udp:
            conntrack_build_dash_header.apply(dash_packet_subtype_t.FLOW_CREATE)
            meta.to_dpapp = True    # trap to dpapp
            return
        # FIN/RST
        elif ((hdr.customer_tcp.flags & 0b000101) != 0) and (hdr.packet_meta.packet_source == dash_packet_source_t.DPAPP):
            # Flow should be just deleted by dpapp
            conntrack_set_meta_from_dash_header()
            return

        # should not reach here
        meta.dropped = True  # drop it

class conntrack_flow_created_handle():
    @classmethod
    def apply(cls):
        py_log("info", "conntrack_flow_created_handle")
        if hdr.customer_tcp:
            if (hdr.customer_tcp.flags & 0b000101) != 0:    # FIN/RST
                conntrack_build_dash_header.apply(dash_packet_subtype_t.FLOW_DELETE)
                meta.to_dpapp = True
                return
        # TODO update flow timestamp for aging

class conntrack_flow_handle():
    @classmethod
    def apply(cls):
        match meta.flow_sync_state:
            case dash_flow_sync_state_t.FLOW_MISS:
                conntrack_flow_miss_handle.apply()
            case dash_flow_sync_state_t.FLOW_CREATED:
                conntrack_flow_created_handle.apply()

        # Drop dash header if not sending to dpapp
        if not meta.to_dpapp:
            conntrack_strip_dash_header()


class conntrack_lookup_stage:
    # Flow table:
    @staticmethod
    def set_flow_table_attr(max_flow_count          : Annotated[int, 32],
                            dash_flow_enabled_key   : Annotated[dash_flow_enabled_key_t, {"type" : "sai_dash_flow_enabled_key_t"}],
                            flow_ttl_in_milliseconds: Annotated[int, 32]):
        meta.flow_table.max_flow_count = max_flow_count
        meta.flow_table.flow_enabled_key = dash_flow_enabled_key
        meta.flow_table.flow_ttl_in_milliseconds = flow_ttl_in_milliseconds

    # Flow entry:
    @staticmethod
    def set_flow_entry_attr(
        # Flow basic metadata
        version                     : Annotated[int, 32],
        dash_direction              : Annotated[dash_direction_t, {"type" : "sai_dash_direction_t"}],
        dash_flow_action            : Annotated[dash_flow_action_t, {"type" : "sai_dash_flow_action_t"}],
        meter_class                 : Annotated[int, 32],
        is_unidirectional_flow      : Annotated[int, 1],
        dash_flow_sync_state        : Annotated[dash_flow_sync_state_t, {"type" : "sai_dash_flow_sync_state_t"}],

        # Reverse flow key
        reverse_flow_eni_mac        : Annotated[int, EthernetAddress_size],
        reverse_flow_vnet_id        : Annotated[int, 16],
        reverse_flow_ip_proto       : Annotated[int, 8],
        reverse_flow_src_ip         : Annotated[int, IPv4ORv6Address_size],
        reverse_flow_dst_ip         : Annotated[int, IPv4ORv6Address_size],
        reverse_flow_src_port       : Annotated[int, 16],
        reverse_flow_dst_port       : Annotated[int, 16],
        reverse_flow_dst_ip_is_v6   : Annotated[int, 1],

        # Flow encap related attributes
        underlay0_vnet_id           : Annotated[int, 24],
        underlay0_sip               : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
        underlay0_dip               : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
        underlay0_smac              : Annotated[int, EthernetAddress_size],
        underlay0_dmac              : Annotated[int, EthernetAddress_size],
        underlay0_dash_encapsulation: Annotated[dash_encapsulation_t, {"type" : "sai_dash_encapsulation_t"}],

        underlay1_vnet_id           : Annotated[int, 24],
        underlay1_sip               : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
        underlay1_dip               : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
        underlay1_smac              : Annotated[int, EthernetAddress_size],
        underlay1_dmac              : Annotated[int, EthernetAddress_size],
        underlay1_dash_encapsulation: Annotated[dash_encapsulation_t, {"type" : "sai_dash_encapsulation_t"}],

        # Flow overlay rewrite related attributes
        dst_mac                     : Annotated[int, EthernetAddress_size],
        sip                         : Annotated[int, IPv4ORv6Address_size],
        dip                         : Annotated[int, IPv4ORv6Address_size],
        sip_mask                    : Annotated[int, IPv6Address_size],
        dip_mask                    : Annotated[int, IPv6Address_size],
        dip_is_v6                   : Annotated[int, 1],

        # Extra flow metadata
        vendor_metadata             : Annotated[int, 16, {"type" : "sai_u8_list_t"}],
        flow_data_pb                : Annotated[int, 16, {"type" : "sai_u8_list_t"}]
    ):
        # Set Flow basic metadata
        meta.flow_data.version = version
        meta.flow_data.direction = dash_direction
        meta.flow_data.actions = dash_flow_action
        meta.flow_data.meter_class = meter_class
        meta.flow_data.is_unidirectional = is_unidirectional_flow

        # Also set basic metadata
        meta.flow_sync_state = dash_flow_sync_state
        meta.flow_sync_state = dash_flow_sync_state
        meta.direction = dash_direction
        meta.routing_actions = dash_flow_action
        meta.meter_class = meter_class

        # Reverse flow key is not used by now

        # Set encapsulation metadata
        meta.u0_encap_data.vni = underlay0_vnet_id
        meta.u0_encap_data.underlay_sip = underlay0_sip
        meta.u0_encap_data.underlay_dip = underlay0_dip
        meta.u0_encap_data.dash_encapsulation = underlay0_dash_encapsulation
        meta.u0_encap_data.underlay_smac = underlay0_smac
        meta.u0_encap_data.underlay_dmac = underlay0_dmac

        meta.u1_encap_data.vni = underlay1_vnet_id
        meta.u1_encap_data.underlay_sip = underlay1_sip
        meta.u1_encap_data.underlay_dip = underlay1_dip
        meta.u1_encap_data.dash_encapsulation = underlay1_dash_encapsulation
        meta.u1_encap_data.underlay_smac = underlay1_smac
        meta.u1_encap_data.underlay_dmac = underlay1_dmac

        # Set overlay rewrite metadata
        meta.overlay_data.dmac = dst_mac
        meta.overlay_data.sip = sip
        meta.overlay_data.dip = dip
        meta.overlay_data.sip_mask = sip_mask
        meta.overlay_data.dip_mask = dip_mask
        meta.overlay_data.is_ipv6 = dip_is_v6

    @staticmethod
    def flow_miss():
        meta.flow_sync_state = dash_flow_sync_state_t.FLOW_MISS

    # Flow bulk get session filter:
    # For API generation only and has no effect on the dataplane
    @staticmethod
    def set_flow_entry_bulk_get_session_filter_attr(
        dash_flow_entry_bulk_get_session_filter_key     : Annotated[dash_flow_entry_bulk_get_session_filter_key_t,
                                                                    {"type" : "sai_dash_flow_entry_bulk_get_session_filter_key_t"}],
        dash_flow_entry_bulk_get_session_op_key         : Annotated[dash_flow_entry_bulk_get_session_op_key_t,
                                                                    {"type" : "sai_dash_flow_entry_bulk_get_session_op_key_t"}],
        int_value                                       : Annotated[int, 64],
        ip_value                                        : Annotated[int, IPv4ORv6Address_size],
        mac_value                                       : Annotated[int, EthernetAddress_size]
    ):
        pass

    # Flow bulk get session:
    # For API generation only and has no effect on the dataplane
    @staticmethod
    def set_flow_entry_bulk_get_session_attr(
        dash_flow_entry_bulk_get_session_mode           : Annotated[dash_flow_entry_bulk_get_session_mode_t,
                                                                    {"type" : "sai_dash_flow_entry_bulk_get_session_mode_t"}],
        # Mode and limitation
        bulk_get_entry_limitation                       : Annotated[int, 32],

        # GRPC Session server IP and port
        bulk_get_session_server_ip                      : Annotated[int, IPv4ORv6Address_size],
        bulk_get_session_server_port                    : Annotated[int, 16],

        # Session filters
        first_flow_entry_bulk_get_session_filter_id     : Annotated[int, 16, {"type" : "sai_object_id_t"}],
        second_flow_entry_bulk_get_session_filter_id    : Annotated[int, 16, {"type" : "sai_object_id_t"}],
        third_flow_entry_bulk_get_session_filter_id     : Annotated[int, 16, {"type" : "sai_object_id_t"}],
        fourth_flow_entry_bulk_get_session_filter_id    : Annotated[int, 16, {"type" : "sai_object_id_t"}],
        fifth_flow_entry_bulk_get_session_filter_id     : Annotated[int, 16, {"type" : "sai_object_id_t"}],
    ):
        pass

    flow_table = Table(
        key={
            "meta.flow_table.id": EXACT,
        },
        actions=[
            set_flow_table_attr,
        ],
        tname=f"{__qualname__}.flow_table",
        sai_table=SaiTable(name="flow_table", api="dash_flow", order=0, isobject="true",),
    )

    flow_entry = Table(
        key={
            "hdr.flow_key.eni_mac"     : EXACT,
            "hdr.flow_key.vnet_id"     : EXACT,
            "hdr.flow_key.src_ip"      : EXACT,
            "hdr.flow_key.dst_ip"      : EXACT,
            "hdr.flow_key.src_port"    : EXACT,
            "hdr.flow_key.dst_port"    : EXACT,
            "hdr.flow_key.ip_proto"    : EXACT,
            "hdr.flow_key.is_ip_v6"    : (EXACT, {"name" : "src_ip_is_v6"})
        },
        actions=[
            set_flow_entry_attr,
            (flow_miss, {"annotations": "@defaultonly"}),
        ],
        const_default_action=flow_miss,
        tname=f"{__qualname__}.flow_entry",
        sai_table=SaiTable(name="flow", api="dash_flow", order=1, enable_bulk_get_api="true", enable_bulk_get_server="true",),
    )

    flow_entry_bulk_get_session_filter = Table(
        key={
            "meta.bulk_get_session_filter_id": (EXACT, {"name" : "bulk_get_session_filter_id", "type" : "sai_object_id_t"})
        },
        actions=[
            set_flow_entry_bulk_get_session_filter_attr,
        ],
        tname=f"{__qualname__}.flow_entry_bulk_get_session_filter",
        sai_table=SaiTable(name="flow_entry_bulk_get_session_filter", api="dash_flow", order=2, isobject="true",),
    )

    flow_entry_bulk_get_session = Table(
        key={
            "meta.bulk_get_session_id": (EXACT, {"name" : "bulk_get_session_id", "type" : "sai_object_id_t"})
        },
        actions=[
            set_flow_entry_bulk_get_session_attr,
        ],
        tname=f"{__qualname__}.flow_entry_bulk_get_session",
        sai_table=SaiTable(name="flow_entry_bulk_get_session", api="dash_flow", order=3, isobject="true",),
    )

    @staticmethod
    def set_flow_key(flow_enabled_key: Annotated[int, 16]):
        hdr.flow_key = flow_key_t()
        hdr.flow_key.is_ip_v6 = meta.is_overlay_ip_v6

        if flow_enabled_key & dash_flow_enabled_key_t.ENI_MAC != 0:
            hdr.flow_key.eni_mac = meta.eni_addr
        if flow_enabled_key & dash_flow_enabled_key_t.VNI != 0:
            hdr.flow_key.vnet_id = meta.vnet_id
        if flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL != 0:
            hdr.flow_key.ip_proto = meta.ip_protocol
        if flow_enabled_key & dash_flow_enabled_key_t.SRC_IP != 0:
            hdr.flow_key.src_ip = meta.src_ip_addr
        if flow_enabled_key & dash_flow_enabled_key_t.DST_IP != 0:
            hdr.flow_key.dst_ip = meta.dst_ip_addr
        if flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT != 0:
            hdr.flow_key.src_port = meta.src_l4_port
        if flow_enabled_key & dash_flow_enabled_key_t.DST_PORT != 0:
            hdr.flow_key.dst_port = meta.dst_l4_port

    @classmethod
    def apply(cls):
        py_log("info", "conntrack_lookup_stage")
        if hdr.flow_key is None:
            py_log("info", "Applying table 'flow_table' ")
            if cls.flow_table.apply()["hit"]:
                meta.flow_data.idle_timeout_in_ms = meta.flow_table.flow_ttl_in_milliseconds
                flow_enabled_key = meta.flow_table.flow_enabled_key
            else:
                # Enable all keys by default
                flow_enabled_key = (dash_flow_enabled_key_t.ENI_MAC |
                                    dash_flow_enabled_key_t.VNI |
                                    dash_flow_enabled_key_t.PROTOCOL |
                                    dash_flow_enabled_key_t.SRC_IP |
                                    dash_flow_enabled_key_t.DST_IP |
                                    dash_flow_enabled_key_t.SRC_PORT |
                                    dash_flow_enabled_key_t.DST_PORT)

            cls.set_flow_key(flow_enabled_key)

        py_log("info", "Applying table 'flow_entry' ")
        cls.flow_entry.apply()
        py_log("info", "Applying table 'flow_entry_bulk_get_session_filter'")
        cls.flow_entry_bulk_get_session_filter.apply()
        py_log("info", "Applying table 'flow_entry_bulk_get_session'")
        cls.flow_entry_bulk_get_session.apply()