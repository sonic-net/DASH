#ifndef _DASH_STAGE_CONNTRACK_LOOKUP_P4
#define _DASH_STAGE_CONNTRACK_LOOKUP_P4

#include "../dash_metadata.p4"

control conntrack_lookup_stage(inout headers_t hdr, inout metadata_t meta) {
    //
    // Flow table:
    //
    action set_flow_table_attr(
        bit<32> max_flow_count,
        @SaiVal[type="sai_dash_flow_enabled_key_t"] dash_flow_enabled_key_t dash_flow_enabled_key,
        bit<32> flow_ttl_in_milliseconds)
    {
        meta.conntrack_data.flow_table.max_flow_count = max_flow_count;
        meta.conntrack_data.flow_table.flow_enabled_key = dash_flow_enabled_key;
        meta.conntrack_data.flow_table.flow_ttl_in_milliseconds = flow_ttl_in_milliseconds;
    }

    @SaiTable[name = "flow_table", api = "dash_flow", order = 0, isobject="true"]
    table flow_table {
        key = {
            meta.conntrack_data.flow_table.id : exact;
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

        /* Reverse flow key */ 
        EthernetAddress reverse_flow_eni_mac,
        bit<16> reverse_flow_vnet_id,
        bit<8> reverse_flow_ip_proto,
        IPv4ORv6Address reverse_flow_src_ip,
        IPv4ORv6Address reverse_flow_dst_ip, 
        bit<16> reverse_flow_src_port,
        bit<16> reverse_flow_dst_port,

        /* Flow encap related attributes */
        bit<24> underlay0_vnet_id,
        IPv4Address underlay0_sip, 
        IPv4Address underlay0_dip,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t underlay0_dash_encapsulation,
        
        bit<24> underlay1_vnet_id,
        IPv4Address underlay1_sip, 
        IPv4Address underlay1_dip,
        EthernetAddress underlay1_smac,
        EthernetAddress underlay1_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t underlay1_dash_encapsulation,
        
        /* Flow overlay rewrite related attributes */
        EthernetAddress dst_mac,
        IPv4ORv6Address sip,
        IPv4ORv6Address dip,
        IPv6Address sip_mask,
        IPv6Address dip_mask,
      
        /* Extra flow metadata */ 
        @SaiVal[type="sai_u8_list_t"] bit<16> vendor_metadata,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_data_pb)
    {
        /* Set Flow basic metadata */
        meta.conntrack_data.flow_data.version = version;
        meta.conntrack_data.flow_data.dash_direction = dash_direction;
        meta.conntrack_data.flow_data.actions = dash_flow_action;
        meta.meter_class = meter_class;
        meta.conntrack_data.is_unidirectional_flow = is_unidirectional_flow;
        
        /* Set reverse flow key */
        meta.conntrack_data.reverse_flow_key.eni_mac = reverse_flow_eni_mac;
        meta.conntrack_data.reverse_flow_key.vnet_id = reverse_flow_vnet_id;
        meta.conntrack_data.reverse_flow_key.ip_proto = reverse_flow_ip_proto;
        meta.conntrack_data.reverse_flow_key.src_ip = reverse_flow_src_ip;
        meta.conntrack_data.reverse_flow_key.dst_ip = reverse_flow_dst_ip;
        meta.conntrack_data.reverse_flow_key.src_port = reverse_flow_src_port;
        meta.conntrack_data.reverse_flow_key.dst_port = reverse_flow_dst_port;


        /* Set encapsulation metadata */
        meta.encap_data.vni = underlay0_vnet_id;
        meta.encap_data.underlay_sip = underlay0_sip;
        meta.encap_data.underlay_dip = underlay0_dip;
        meta.encap_data.dash_encapsulation = underlay0_dash_encapsulation;

        meta.tunnel_data.vni = underlay1_vnet_id;
        meta.tunnel_data.underlay_sip = underlay1_sip;
        meta.tunnel_data.underlay_dip = underlay1_dip;
        meta.tunnel_data.dash_encapsulation = underlay1_dash_encapsulation;
        meta.tunnel_data.underlay_smac = underlay1_smac;
        meta.tunnel_data.underlay_dmac = underlay1_dmac;


        /* Set overlay rewrite metadata */
        meta.overlay_data.dmac = dst_mac;
        meta.overlay_data.sip = sip;
        meta.overlay_data.dip = dip;
        meta.overlay_data.sip_mask = sip_mask;
        meta.overlay_data.dip_mask = dip_mask;
    }

    @SaiTable[name = "flow", api = "dash_flow", order = 1, enable_bulk_get_api = "true", enable_bulk_get_server = "true"]
    table flow_entry {
        key = {
            meta.conntrack_data.flow_key.eni_mac : exact;
            meta.conntrack_data.flow_key.vnet_id : exact;
            meta.conntrack_data.flow_key.ip_proto : exact;
            meta.conntrack_data.flow_key.src_ip : exact;
            meta.conntrack_data.flow_key.dst_ip : exact;
            meta.conntrack_data.flow_key.src_port : exact;
            meta.conntrack_data.flow_key.dst_port : exact;
            meta.conntrack_data.flow_key.is_ipv6 : exact @SaiVal[name = "src_ip_is_v6"];
        }

        actions = {
            set_flow_entry_attr;
        }
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
            meta.conntrack_data.bulk_get_session_filter_id: exact @SaiVal[name = "bulk_get_session_filter_id", type="sai_object_id_t"];
        }

        actions = {
            set_flow_entry_bulk_get_session_filter_attr;
        }
    }

   @SaiTable[name = "flow_entry_bulk_get_session", api = "dash_flow", order = 3, isobject="true"]
    table flow_entry_bulk_get_session {
        key = {
            meta.conntrack_data.bulk_get_session_id: exact @SaiVal[name = "bulk_get_session_id", type="sai_object_id_t"];
        }

        actions = {
            set_flow_entry_bulk_get_session_attr;
        }
    }

    apply {
        flow_table.apply();

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.ENI_MAC != 0) {
            meta.conntrack_data.flow_key.eni_mac = meta.eni_addr;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.VNI != 0) {
             meta.conntrack_data.flow_key.vnet_id = meta.vnet_id;
        } 
        
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL != 0) {
            meta.conntrack_data.flow_key.ip_proto = meta.ip_protocol;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_IP != 0) {
            meta.conntrack_data.flow_key.src_ip = meta.src_ip_addr;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_IP != 0) {
            meta.conntrack_data.flow_key.dst_ip = meta.dst_ip_addr;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT != 0) {
            meta.conntrack_data.flow_key.src_port = meta.src_l4_port;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_PORT != 0) {
            meta.conntrack_data.flow_key.dst_port = meta.dst_l4_port;
        }

        flow_entry.apply();
        flow_entry_bulk_get_session_filter.apply();
        flow_entry_bulk_get_session.apply();
    }
}

#endif /* _DASH_STAGE_CONNTRACK_LOOKUP_P4 */
