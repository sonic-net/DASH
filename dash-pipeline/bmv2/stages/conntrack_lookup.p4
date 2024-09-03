#ifndef _DASH_STAGE_CONNTRACK_LOOKUP_P4
#define _DASH_STAGE_CONNTRACK_LOOKUP_P4

#include "../dash_metadata.p4"

action conntrack_set_meta_from_dash_header(in headers_t hdr, out metadata_t meta)
{
    /* basic metadata */
    meta.direction = hdr.flow_data.direction;
    meta.dash_tunnel_id = hdr.flow_data.tunnel_id;
    meta.routing_actions = hdr.flow_data.routing_actions;
    meta.meter_class = hdr.flow_data.meter_class;

    /* encapsulation metadata */
#ifdef TARGET_DPDK_PNA
    meta.encap_data.vni = hdr.flow_encap_data.vni;
    meta.encap_data.dest_vnet_vni = hdr.flow_encap_data.dest_vnet_vni;
    meta.encap_data.underlay_sip = hdr.flow_encap_data.underlay_sip;
    meta.encap_data.underlay_dip = hdr.flow_encap_data.underlay_dip;
    meta.encap_data.underlay_smac = hdr.flow_encap_data.underlay_smac;
    meta.encap_data.underlay_dmac = hdr.flow_encap_data.underlay_dmac;
    meta.encap_data.dash_encapsulation = hdr.flow_encap_data.dash_encapsulation;
#else
    meta.encap_data = hdr.flow_encap_data;
#endif // TARGET_DPDK_PNA

    /* tunnel metadata */
#ifdef TARGET_DPDK_PNA
    meta.tunnel_data.vni = hdr.flow_tunnel_data.vni;
    meta.tunnel_data.dest_vnet_vni = hdr.flow_tunnel_data.dest_vnet_vni;
    meta.tunnel_data.underlay_sip = hdr.flow_tunnel_data.underlay_sip;
    meta.tunnel_data.underlay_dip = hdr.flow_tunnel_data.underlay_dip;
    meta.tunnel_data.underlay_smac = hdr.flow_tunnel_data.underlay_smac;
    meta.tunnel_data.underlay_dmac = hdr.flow_tunnel_data.underlay_dmac;
    meta.tunnel_data.dash_encapsulation = hdr.flow_tunnel_data.dash_encapsulation;
#else
    meta.tunnel_data = hdr.flow_tunnel_data;
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
    hdr.flow_encap_data.setInvalid();
    hdr.flow_tunnel_data.setInvalid();
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
        hdr.flow_data.tunnel_id = meta.dash_tunnel_id;
        hdr.flow_data.routing_actions = meta.routing_actions;
        hdr.flow_data.meter_class = meta.meter_class;
        length = length + FLOW_DATA_HDR_SIZE;

        if (meta.routing_actions & dash_routing_actions_t.STATIC_ENCAP != 0) {
#ifdef TARGET_DPDK_PNA
            hdr.flow_encap_data.setValid();
            hdr.flow_encap_data.vni = meta.encap_data.vni;
            hdr.flow_encap_data.dest_vnet_vni = meta.encap_data.dest_vnet_vni;
            hdr.flow_encap_data.underlay_sip = meta.encap_data.underlay_sip;
            hdr.flow_encap_data.underlay_dip = meta.encap_data.underlay_dip;
            hdr.flow_encap_data.underlay_smac = meta.encap_data.underlay_smac;
            hdr.flow_encap_data.underlay_dmac = meta.encap_data.underlay_dmac;
            hdr.flow_encap_data.dash_encapsulation = meta.encap_data.dash_encapsulation;
#else
            hdr.flow_encap_data= meta.encap_data;
#endif // TARGET_DPDK_PNA
            length = length + ENCAP_DATA_HDR_SIZE;
        }

        if (meta.dash_tunnel_id != 0) {
#ifdef TARGET_DPDK_PNA
            hdr.flow_tunnel_data.setValid();
            hdr.flow_tunnel_data.vni = meta.tunnel_data.vni;
            hdr.flow_tunnel_data.dest_vnet_vni = meta.tunnel_data.dest_vnet_vni;
            hdr.flow_tunnel_data.underlay_sip = meta.tunnel_data.underlay_sip;
            hdr.flow_tunnel_data.underlay_dip = meta.tunnel_data.underlay_dip;
            hdr.flow_tunnel_data.underlay_smac = meta.tunnel_data.underlay_smac;
            hdr.flow_tunnel_data.underlay_dmac = meta.tunnel_data.underlay_dmac;
            hdr.flow_tunnel_data.dash_encapsulation = meta.tunnel_data.dash_encapsulation;
#else
            hdr.flow_tunnel_data= meta.tunnel_data;
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
        hdr.dp_ethernet.dst_addr = DPAPP_MAC;
        hdr.dp_ethernet.src_addr = meta.encap_data.underlay_smac;
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
        switch (meta.flow_state) {
            dash_flow_state_t.FLOW_MISS: {
                conntrack_flow_miss_handle.apply(hdr, meta);
            }
            dash_flow_state_t.FLOW_CREATED: {
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
        bit<1> is_unidirectional,
        dash_flow_state_t state,
        bit<32> version,
        @SaiVal[type="sai_dash_direction_t"] dash_direction_t dash_direction,
        bit<16> tunnel_id,
        bit<32> routing_actions,
        bit<32> meter_class,

        /* Flow encap related attributes */
        bit<24> encap_data_vni,
        bit<24> encap_data_dest_vnet_vni,
        IPv4Address encap_data_underlay_sip,
        IPv4Address encap_data_underlay_dip,
        EthernetAddress encap_data_underlay_smac,
        EthernetAddress encap_data_underlay_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t encap_data_dash_encapsulation,

        /* Flow tunnel related attributes */
        bit<24> tunnel_data_vni,
        bit<24> tunnel_data_dest_vnet_vni,
        IPv4Address tunnel_data_underlay_sip,
        IPv4Address tunnel_data_underlay_dip,
        EthernetAddress tunnel_data_underlay_smac,
        EthernetAddress tunnel_data_underlay_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t tunnel_data_dash_encapsulation,

        /* Flow overlay rewrite related attributes */
        bit<1> overlay_data_is_ipv6,
        EthernetAddress overlay_data_dst_mac,
        IPv4ORv6Address overlay_data_sip,
        IPv4ORv6Address overlay_data_dip,
        IPv6Address overlay_data_sip_mask,
        IPv6Address overlay_data_dip_mask,

        /* Extra flow metadata, unused */
        @SaiVal[type="sai_u8_list_t"] bit<16> vendor_metadata,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_data_pb)
    {
        meta.flow_state = state;
        // TODO check FLOW_SYNCED in ha
        // Do state FSM later
        if (state != dash_flow_state_t.FLOW_CREATED) {
            return;
        }

        /* Set basic metadata */
        meta.direction = dash_direction;
        meta.dash_tunnel_id = tunnel_id;
        meta.routing_actions = routing_actions;
        meta.meter_class = meter_class;

        /* Set encapsulation metadata */
        meta.encap_data.vni = encap_data_vni;
        meta.encap_data.dest_vnet_vni = encap_data_dest_vnet_vni;
        meta.encap_data.underlay_sip = encap_data_underlay_sip;
        meta.encap_data.underlay_dip = encap_data_underlay_dip;
        meta.encap_data.underlay_smac = encap_data_underlay_smac;
        meta.encap_data.underlay_dmac = encap_data_underlay_dmac;
        meta.encap_data.dash_encapsulation = encap_data_dash_encapsulation;


        /* Set tunnel metadata */
        meta.tunnel_data.vni = tunnel_data_vni;
        meta.tunnel_data.dest_vnet_vni = tunnel_data_dest_vnet_vni;
        meta.tunnel_data.underlay_sip = tunnel_data_underlay_sip;
        meta.tunnel_data.underlay_dip = tunnel_data_underlay_dip;
        meta.tunnel_data.underlay_smac = tunnel_data_underlay_smac;
        meta.tunnel_data.underlay_dmac = tunnel_data_underlay_dmac;
        meta.tunnel_data.dash_encapsulation = tunnel_data_dash_encapsulation;

        /* Set overlay rewrite metadata */
        meta.overlay_data.is_ipv6 = overlay_data_is_ipv6;
        meta.overlay_data.dmac = overlay_data_dst_mac;
        meta.overlay_data.sip = overlay_data_sip;
        meta.overlay_data.dip = overlay_data_dip;
        meta.overlay_data.sip_mask = overlay_data_sip_mask;
        meta.overlay_data.dip_mask = overlay_data_dip_mask;
    }

    action flow_miss() {
        meta.flow_state = dash_flow_state_t.FLOW_MISS;
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

    action set_flow_key()
    {
        hdr.flow_key.setValid();
        hdr.flow_key.is_ip_v6 = meta.is_overlay_ip_v6;
        // TODO remove hardcode flow_enabled_key later
        meta.flow_table.flow_enabled_key = dash_flow_enabled_key_t.ENI_MAC |
                                           dash_flow_enabled_key_t.VNI |
                                           dash_flow_enabled_key_t.PROTOCOL |
                                           dash_flow_enabled_key_t.SRC_IP |
                                           dash_flow_enabled_key_t.DST_IP |
                                           dash_flow_enabled_key_t.SRC_PORT |
                                           dash_flow_enabled_key_t.DST_PORT;

        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.ENI_MAC != 0) {
            hdr.flow_key.eni_mac = meta.eni_addr;
        }
        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.VNI != 0) {
            hdr.flow_key.vnet_id = meta.vnet_id;
        }
        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL != 0) {
            hdr.flow_key.ip_proto = meta.ip_protocol;
        }
        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_IP != 0) {
            hdr.flow_key.src_ip = meta.src_ip_addr;
        }
        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_IP != 0) {
            hdr.flow_key.dst_ip = meta.dst_ip_addr;
        }

        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT != 0) {
            hdr.flow_key.src_port = meta.src_l4_port;
        }

        if (meta.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_PORT != 0) {
            hdr.flow_key.dst_port = meta.dst_l4_port;
        }
    }

    apply {
        if (!hdr.flow_key.isValid()) {
            flow_table.apply();
            set_flow_key();
        }

        flow_entry.apply();
        flow_entry_bulk_get_session_filter.apply();
        flow_entry_bulk_get_session.apply();
    }
}
#endif /* _DASH_STAGE_CONNTRACK_LOOKUP_P4 */
