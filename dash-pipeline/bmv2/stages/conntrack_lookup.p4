#ifndef _DASH_STAGE_CONNTRACK_LOOKUP_P4
#define _DASH_STAGE_CONNTRACK_LOOKUP_P4

#include "../dash_metadata.p4"

action conntrack_set_meta_from_dash_header(in headers_t hdr, out metadata_t meta)
{
    /* basic metadata */
    meta.direction = hdr.flow_data.direction;
    meta.dash_tunnel_id = 0;
    meta.routing_actions = (bit<32>)hdr.flow_data.actions;
    meta.meter_class = hdr.flow_data.meter_class;

    /* encapsulation metadata */
#ifdef TARGET_DPDK_PNA
    meta.u0_encap_data.vni = hdr.flow_u0_encap_data.vni;
    meta.u0_encap_data.underlay_sip = hdr.flow_u0_encap_data.underlay_sip;
    meta.u0_encap_data.underlay_dip = hdr.flow_u0_encap_data.underlay_dip;
    meta.u0_encap_data.underlay_smac = hdr.flow_u0_encap_data.underlay_smac;
    meta.u0_encap_data.underlay_dmac = hdr.flow_u0_encap_data.underlay_dmac;
    meta.u0_encap_data.dash_encapsulation = hdr.flow_u0_encap_data.dash_encapsulation;
#else
    meta.u0_encap_data = hdr.flow_u0_encap_data;
#endif // TARGET_DPDK_PNA

    /* tunnel metadata */
#ifdef TARGET_DPDK_PNA
    meta.u1_encap_data.vni = hdr.flow_u1_encap_data.vni;
    meta.u1_encap_data.underlay_sip = hdr.flow_u1_encap_data.underlay_sip;
    meta.u1_encap_data.underlay_dip = hdr.flow_u1_encap_data.underlay_dip;
    meta.u1_encap_data.underlay_smac = hdr.flow_u1_encap_data.underlay_smac;
    meta.u1_encap_data.underlay_dmac = hdr.flow_u1_encap_data.underlay_dmac;
    meta.u1_encap_data.dash_encapsulation = hdr.flow_u1_encap_data.dash_encapsulation;
#else
    meta.u1_encap_data = hdr.flow_u1_encap_data;
#endif // TARGET_DPDK_PNA

    /* overlay rewrite metadata */
#ifdef TARGET_DPDK_PNA
    meta.overlay_data.dmac = hdr.flow_overlay_data.dmac;
    meta.overlay_data.sip = hdr.flow_overlay_data.sip;
    meta.overlay_data.dip = hdr.flow_overlay_data.dip;
    meta.overlay_data.sip_mask = hdr.flow_overlay_data.sip_mask;
    meta.overlay_data.dip_mask = hdr.flow_overlay_data.dip_mask;
    meta.overlay_data.is_ipv6 = hdr.flow_overlay_data.is_ipv6;
#else
    meta.overlay_data = hdr.flow_overlay_data;
#endif // TARGET_DPDK_PNA
}

action conntrack_strip_dash_header(inout headers_t hdr)
{
    hdr.dp_ethernet.setInvalid();
    hdr.packet_meta.setInvalid();
    hdr.flow_key.setInvalid();
    hdr.flow_data.setInvalid();
    hdr.flow_overlay_data.setInvalid();
    hdr.flow_u0_encap_data.setInvalid();
    hdr.flow_u1_encap_data.setInvalid();
}

control conntrack_build_dash_header(inout headers_t hdr, in metadata_t meta,
        dash_packet_subtype_t packet_subtype)
{
    apply {
        bit<16> length = 0;

        hdr.flow_data.setValid();
        hdr.flow_data.is_unidirectional = 0;
        hdr.flow_data.version = 0;
        hdr.flow_data.direction = meta.direction;
        hdr.flow_data.actions = (dash_flow_action_t)meta.routing_actions;
        hdr.flow_data.meter_class = meta.meter_class;
        hdr.flow_data.idle_timeout_in_ms = meta.flow_data.idle_timeout_in_ms;
        length = length + FLOW_DATA_HDR_SIZE;

        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0 != 0) {
#ifdef TARGET_DPDK_PNA
            hdr.flow_u0_encap_data.setValid();
            hdr.flow_u0_encap_data.vni = meta.u0_encap_data.vni;
            hdr.flow_u0_encap_data.underlay_sip = meta.u0_encap_data.underlay_sip;
            hdr.flow_u0_encap_data.underlay_dip = meta.u0_encap_data.underlay_dip;
            hdr.flow_u0_encap_data.underlay_smac = meta.u0_encap_data.underlay_smac;
            hdr.flow_u0_encap_data.underlay_dmac = meta.u0_encap_data.underlay_dmac;
            hdr.flow_u0_encap_data.dash_encapsulation = meta.u0_encap_data.dash_encapsulation;
#else
            hdr.flow_u0_encap_data= meta.u0_encap_data;
#endif // TARGET_DPDK_PNA
            length = length + ENCAP_DATA_HDR_SIZE;
        }

        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U1 != 0) {
#ifdef TARGET_DPDK_PNA
            hdr.flow_u1_encap_data.setValid();
            hdr.flow_u1_encap_data.vni = meta.u1_encap_data.vni;
            hdr.flow_u1_encap_data.underlay_sip = meta.u1_encap_data.underlay_sip;
            hdr.flow_u1_encap_data.underlay_dip = meta.u1_encap_data.underlay_dip;
            hdr.flow_u1_encap_data.underlay_smac = meta.u1_encap_data.underlay_smac;
            hdr.flow_u1_encap_data.underlay_dmac = meta.u1_encap_data.underlay_dmac;
            hdr.flow_u1_encap_data.dash_encapsulation = meta.u1_encap_data.dash_encapsulation;
#else
            hdr.flow_u1_encap_data= meta.u1_encap_data;
#endif // TARGET_DPDK_PNA
            length = length + ENCAP_DATA_HDR_SIZE;
        }

        if (meta.routing_actions != 0) {
#ifdef TARGET_DPDK_PNA
            hdr.flow_overlay_data.setValid();
            hdr.flow_overlay_data.dmac = meta.overlay_data.dmac;
            hdr.flow_overlay_data.sip = meta.overlay_data.sip;
            hdr.flow_overlay_data.dip = meta.overlay_data.dip;
            hdr.flow_overlay_data.sip_mask = meta.overlay_data.sip_mask;
            hdr.flow_overlay_data.dip_mask = meta.overlay_data.dip_mask;
            hdr.flow_overlay_data.is_ipv6 = meta.overlay_data.is_ipv6;
#else
            hdr.flow_overlay_data= meta.overlay_data;
#endif // TARGET_DPDK_PNA
            length = length + OVERLAY_REWRITE_DATA_HDR_SIZE;
        }

        length = length + FLOW_KEY_HDR_SIZE;

        hdr.packet_meta.setValid();
        hdr.packet_meta.packet_source = dash_packet_source_t.PIPELINE;
        hdr.packet_meta.packet_type = dash_packet_type_t.REGULAR;
        hdr.packet_meta.packet_subtype = packet_subtype;
        hdr.packet_meta.length = length + PACKET_META_HDR_SIZE;

        hdr.dp_ethernet.setValid();
        hdr.dp_ethernet.dst_addr = meta.cpu_mac;
        hdr.dp_ethernet.src_addr = meta.u0_encap_data.underlay_smac;
        hdr.dp_ethernet.ether_type = DASH_ETHTYPE;
    }
}

control conntrack_flow_miss_handle(inout headers_t hdr, inout metadata_t meta)
{
    apply {
        if ((hdr.customer_tcp.isValid() && hdr.customer_tcp.flags == 0x2 /* SYN */)
            || hdr.customer_udp.isValid()) {
            conntrack_build_dash_header.apply(hdr, meta, dash_packet_subtype_t.FLOW_CREATE);
            meta.to_dpapp = true; // trap to dpapp
            return;
        }
        else if ((hdr.customer_tcp.flags & 0b000101 /* FIN/RST */) != 0
                && hdr.packet_meta.packet_source == dash_packet_source_t.DPAPP) {
            /* Flow should be just deleted by dpapp */
            conntrack_set_meta_from_dash_header(hdr, meta);
            return;
        }

        // should not reach here
        meta.dropped = true; // drop it
    }
}

control conntrack_flow_created_handle(inout headers_t hdr, inout metadata_t meta)
{
    apply {
        if (hdr.customer_tcp.isValid()) {
            if ((hdr.customer_tcp.flags & 0b000101 /* FIN/RST */) != 0) {
                conntrack_build_dash_header.apply(hdr, meta, dash_packet_subtype_t.FLOW_DELETE);
                meta.to_dpapp = true; // trap to dpapp
                return;
            }
        }

        // TODO update flow timestamp for aging
    }
}


control conntrack_flow_handle(inout headers_t hdr, inout metadata_t meta)
{
    apply {
        switch (meta.flow_sync_state) {
            dash_flow_sync_state_t.FLOW_MISS: {
                conntrack_flow_miss_handle.apply(hdr, meta);
            }
            dash_flow_sync_state_t.FLOW_CREATED: {
                conntrack_flow_created_handle.apply(hdr, meta);
            }
        }

        // Drop dash header if not sending to dpapp
        if (!meta.to_dpapp) {
            conntrack_strip_dash_header(hdr);
        }
    }
}


control conntrack_lookup_stage(inout headers_t hdr, inout metadata_t meta) {
    //
    // Flow table:
    //
    action set_flow_table_attr(
        bit<32> max_flow_count,
        @SaiVal[type="sai_dash_flow_enabled_key_t"] dash_flow_enabled_key_t dash_flow_enabled_key,
        bit<32> flow_ttl_in_milliseconds)
    {
        meta.flow_table.max_flow_count = max_flow_count;
        meta.flow_table.flow_enabled_key = dash_flow_enabled_key;
        meta.flow_table.flow_ttl_in_milliseconds = flow_ttl_in_milliseconds;
    }

    @SaiTable[name = "flow_table", api = "dash_flow", order = 0, isobject="true"]
    table flow_table {
        key = {
            meta.flow_table.id : exact;
        }

        actions = {
            set_flow_table_attr;
        }
    }

    //
    // Flow entry:
    //
    action set_flow_entry_attr(
        /* Flow basic metadata */
        bit<32> version,
        @SaiVal[type="sai_dash_direction_t"] dash_direction_t dash_direction,
        @SaiVal[type="sai_dash_flow_action_t"] dash_flow_action_t dash_flow_action,
        bit<32> meter_class,
        bit<1> is_unidirectional_flow,
        @SaiVal[type="sai_dash_flow_sync_state_t"] dash_flow_sync_state_t dash_flow_sync_state,

        /* Reverse flow key */
        EthernetAddress reverse_flow_eni_mac,
        bit<16> reverse_flow_vnet_id,
        bit<8> reverse_flow_ip_proto,
        IPv4ORv6Address reverse_flow_src_ip,
        IPv4ORv6Address reverse_flow_dst_ip,
        bit<16> reverse_flow_src_port,
        bit<16> reverse_flow_dst_port,
        bit<1> reverse_flow_dst_ip_is_v6,

        /* Flow encap related attributes */
        bit<24> underlay0_vnet_id,
        @SaiVal[type="sai_ip_address_t"] IPv4Address underlay0_sip,
        @SaiVal[type="sai_ip_address_t"] IPv4Address underlay0_dip,
        EthernetAddress underlay0_smac,
        EthernetAddress underlay0_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t underlay0_dash_encapsulation,

        bit<24> underlay1_vnet_id,
        @SaiVal[type="sai_ip_address_t"] IPv4Address underlay1_sip,
        @SaiVal[type="sai_ip_address_t"] IPv4Address underlay1_dip,
        EthernetAddress underlay1_smac,
        EthernetAddress underlay1_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t underlay1_dash_encapsulation,

        /* Flow overlay rewrite related attributes */
        EthernetAddress dst_mac,
        IPv4ORv6Address sip,
        IPv4ORv6Address dip,
        IPv6Address sip_mask,
        IPv6Address dip_mask,
        bit<1> dip_is_v6,

        /* Extra flow metadata */
        @SaiVal[type="sai_u8_list_t"] bit<16> vendor_metadata,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_data_pb)
    {
        /* Set Flow basic metadata */
        meta.flow_data.version = version;
        meta.flow_data.direction = dash_direction;
        meta.flow_data.actions = dash_flow_action;
        meta.flow_data.meter_class = meter_class;
        meta.flow_data.is_unidirectional= is_unidirectional_flow;

        /* Also set basic metadata */
        meta.flow_sync_state = dash_flow_sync_state;
        meta.direction = dash_direction;
        meta.routing_actions = dash_flow_action;
        meta.meter_class = meter_class;

        /* Reverse flow key is not used by now */
        ;

        /* Set encapsulation metadata */
        meta.u0_encap_data.vni = underlay0_vnet_id;
        meta.u0_encap_data.underlay_sip = underlay0_sip;
        meta.u0_encap_data.underlay_dip = underlay0_dip;
        meta.u0_encap_data.dash_encapsulation = underlay0_dash_encapsulation;
        meta.u0_encap_data.underlay_smac = underlay0_smac;
        meta.u0_encap_data.underlay_dmac = underlay0_dmac;

        meta.u1_encap_data.vni = underlay1_vnet_id;
        meta.u1_encap_data.underlay_sip = underlay1_sip;
        meta.u1_encap_data.underlay_dip = underlay1_dip;
        meta.u1_encap_data.dash_encapsulation = underlay1_dash_encapsulation;
        meta.u1_encap_data.underlay_smac = underlay1_smac;
        meta.u1_encap_data.underlay_dmac = underlay1_dmac;

        /* Set overlay rewrite metadata */
        meta.overlay_data.dmac = dst_mac;
        meta.overlay_data.sip = sip;
        meta.overlay_data.dip = dip;
        meta.overlay_data.sip_mask = sip_mask;
        meta.overlay_data.dip_mask = dip_mask;
        meta.overlay_data.is_ipv6 = dip_is_v6;
    }

    action flow_miss() {
        meta.flow_sync_state = dash_flow_sync_state_t.FLOW_MISS;
    }

    @SaiTable[name = "flow", api = "dash_flow", order = 1, enable_bulk_get_api = "true", enable_bulk_get_server = "true"]
    table flow_entry {
        key = {
            hdr.flow_key.eni_mac : exact;
            hdr.flow_key.vnet_id : exact;
            hdr.flow_key.src_ip : exact;
            hdr.flow_key.dst_ip : exact;
            hdr.flow_key.src_port : exact;
            hdr.flow_key.dst_port : exact;
            hdr.flow_key.ip_proto : exact;
            hdr.flow_key.is_ip_v6 : exact @SaiVal[name = "src_ip_is_v6"];
        }

        actions = {
            set_flow_entry_attr;
            @defaultonly flow_miss;
        }
        const default_action = flow_miss;
    }

    //
    // Flow bulk get session filter:
    // For API generation only and has no effect on the dataplane
    //
    action set_flow_entry_bulk_get_session_filter_attr(
        @SaiVal[type="sai_dash_flow_entry_bulk_get_session_filter_key_t"] dash_flow_entry_bulk_get_session_filter_key_t dash_flow_entry_bulk_get_session_filter_key,
        @SaiVal[type="sai_dash_flow_entry_bulk_get_session_op_key_t"] dash_flow_entry_bulk_get_session_op_key_t  dash_flow_entry_bulk_get_session_op_key,
        bit<64> int_value,
        IPv4ORv6Address ip_value,
        bit<48> mac_value)
    {
    }

    //
    // Flow bulk get session:
    // For API generation only and has no effect on the dataplane
    //
    action set_flow_entry_bulk_get_session_attr(
        /* Mode and limitation */
        @SaiVal[type="sai_dash_flow_entry_bulk_get_session_mode_t"] dash_flow_entry_bulk_get_session_mode_t dash_flow_entry_bulk_get_session_mode,
        bit<32> bulk_get_entry_limitation,

        /* GRPC Session server IP and port */
        IPv4ORv6Address bulk_get_session_server_ip,
        bit<16> bulk_get_session_server_port,

        /* Session filters */
        @SaiVal[type="sai_object_id_t"] bit<16> first_flow_entry_bulk_get_session_filter_id,
        @SaiVal[type="sai_object_id_t"] bit<16> second_flow_entry_bulk_get_session_filter_id,
        @SaiVal[type="sai_object_id_t"] bit<16> third_flow_entry_bulk_get_session_filter_id,
        @SaiVal[type="sai_object_id_t"] bit<16> fourth_flow_entry_bulk_get_session_filter_id,
        @SaiVal[type="sai_object_id_t"] bit<16> fifth_flow_entry_bulk_get_session_filter_id)
    {
    }


    @SaiTable[name = "flow_entry_bulk_get_session_filter", api = "dash_flow", order = 2, isobject="true"]
    table flow_entry_bulk_get_session_filter {
        key = {
            meta.bulk_get_session_filter_id: exact @SaiVal[name = "bulk_get_session_filter_id", type="sai_object_id_t"];
        }

        actions = {
            set_flow_entry_bulk_get_session_filter_attr;
        }
    }

   @SaiTable[name = "flow_entry_bulk_get_session", api = "dash_flow", order = 3, isobject="true"]
    table flow_entry_bulk_get_session {
        key = {
            meta.bulk_get_session_id: exact @SaiVal[name = "bulk_get_session_id", type="sai_object_id_t"];
        }

        actions = {
            set_flow_entry_bulk_get_session_attr;
        }
    }

    action set_flow_key(bit<16> flow_enabled_key)
    {
        hdr.flow_key.setValid();
        hdr.flow_key.is_ip_v6 = meta.is_overlay_ip_v6;

        if (flow_enabled_key & dash_flow_enabled_key_t.ENI_MAC != 0) {
            hdr.flow_key.eni_mac = meta.eni_addr;
        }
        if (flow_enabled_key & dash_flow_enabled_key_t.VNI != 0) {
            hdr.flow_key.vnet_id = meta.vnet_id;
        }
        if (flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL != 0) {
            hdr.flow_key.ip_proto = meta.ip_protocol;
        }
        if (flow_enabled_key & dash_flow_enabled_key_t.SRC_IP != 0) {
            hdr.flow_key.src_ip = meta.src_ip_addr;
        }
        if (flow_enabled_key & dash_flow_enabled_key_t.DST_IP != 0) {
            hdr.flow_key.dst_ip = meta.dst_ip_addr;
        }

        if (flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT != 0) {
            hdr.flow_key.src_port = meta.src_l4_port;
        }

        if (flow_enabled_key & dash_flow_enabled_key_t.DST_PORT != 0) {
            hdr.flow_key.dst_port = meta.dst_l4_port;
        }
    }

    apply {
        if (!hdr.flow_key.isValid()) {
            bit<16> flow_enabled_key;

            if (flow_table.apply().hit) {
                meta.flow_data.idle_timeout_in_ms = meta.flow_table.flow_ttl_in_milliseconds;
                flow_enabled_key = meta.flow_table.flow_enabled_key;
            }
            else {
                // Enable all keys by default
                flow_enabled_key = dash_flow_enabled_key_t.ENI_MAC |
                                   dash_flow_enabled_key_t.VNI |
                                   dash_flow_enabled_key_t.PROTOCOL |
                                   dash_flow_enabled_key_t.SRC_IP |
                                   dash_flow_enabled_key_t.DST_IP |
                                   dash_flow_enabled_key_t.SRC_PORT |
                                   dash_flow_enabled_key_t.DST_PORT;
            }

            set_flow_key(flow_enabled_key);
        }

        flow_entry.apply();
        flow_entry_bulk_get_session_filter.apply();
        flow_entry_bulk_get_session.apply();
    }
}
#endif /* _DASH_STAGE_CONNTRACK_LOOKUP_P4 */
