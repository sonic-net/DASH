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
        /* Flow metadata */
        @SaiVal[is_filter_key="true"] bit<32> version,
        @SaiVal[type="sai_dash_direction_t"] dash_direction_t dash_direction,

        /* Flow actions */
        @SaiVal[type="sai_dash_flow_action_t"] dash_flow_action_t dash_flow_action,
        
        /* Encap metadata */
        bit<24> vni,
        bit<24> dest_vnet_vni,
        IPv4Address underlay_sip, 
        IPv4Address underlay_dip,
        EthernetAddress underlay_smac,
        EthernetAddress underlay_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t dash_encapsulation,
        IPv4Address original_overlay_sip,
        IPv4Address original_overlay_dip,
        
        /* Overlay rewrite metadata */
        bit<1> is_ipv6,
        EthernetAddress dst_mac,
        IPv4ORv6Address sip,
        IPv4ORv6Address dip,
        IPv6Address sip_mask,
        IPv6Address dip_mask,
      
        /* Meter and policy metadata */ 
        bit<16> meter_class,

        /* Reverse flow info */ 
        bit<1> is_bidirectional_flow,
        EthernetAddress reverse_eni_addr,
        bit<8> reverse_ip_protocol,
        IPv4ORv6Address src_ip_addr,
        IPv4ORv6Address dst_ip_addr, 
        bit<16> reverse_src_l4_port,
        bit<16> reverse_dst_l4_port,

        /* Extra flow metadata */ 
        @SaiVal[type="sai_u8_list_t"] bit<16> vendor_metadata,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_data_pb)
    {
        /* Set flow metadata */
        meta.conntrack_data.flow_data.version = version;
        meta.conntrack_data.flow_data.dash_direction = dash_direction;

        /* Set flow actions */
        meta.conntrack_data.flow_data.actions = dash_flow_action;

        /* Set encapsulation metadata */
        meta.encap_data.vni = vni;
        meta.encap_data.dest_vnet_vni = dest_vnet_vni;
        meta.encap_data.underlay_sip = underlay_sip;
        meta.encap_data.underlay_dip = underlay_dip;
        meta.encap_data.underlay_smac = underlay_smac;
        meta.encap_data.underlay_dmac = underlay_dmac;
        meta.encap_data.dash_encapsulation = dash_encapsulation;

        /* Set overlay rewrite metadata */
        meta.overlay_data.is_ipv6 = (is_ipv6 == 1);
        meta.overlay_data.dmac = dst_mac;
        meta.overlay_data.sip = sip;
        meta.overlay_data.dip = dip;
        meta.overlay_data.sip_mask = sip_mask;
        meta.overlay_data.dip_mask = dip_mask;

        /* Set meter and policy metadata */
        meta.meter_class = meter_class;

        /* Set reverse flow information */
        meta.conntrack_data.is_bidirectional_flow = is_bidirectional_flow;
        meta.conntrack_data.reverse_flow_key.ip_protocol = reverse_ip_protocol;
        meta.conntrack_data.reverse_flow_key.src_ip_addr = src_ip_addr;
        meta.conntrack_data.reverse_flow_key.dst_ip_addr = dst_ip_addr;
        meta.conntrack_data.reverse_flow_key.src_l4_port = reverse_src_l4_port;
        meta.conntrack_data.reverse_flow_key.dst_l4_port = reverse_dst_l4_port;
    }

    @SaiTable[name = "flow", api = "dash_flow", order = 1, enable_bulk_get_api = "true", enable_bulk_get_server = "true"]
    table flow_entry {
        key = {
            meta.conntrack_data.flow_table.id: exact @SaiVal[name = "flow_table_id", type="sai_object_id_t"];
            meta.conntrack_data.eni_addr : exact;
            meta.conntrack_data.flow_key.ip_protocol : exact;
            meta.conntrack_data.flow_key.src_ip_addr : exact;
            meta.conntrack_data.flow_key.dst_ip_addr : exact;
            meta.conntrack_data.flow_key.src_l4_port : exact;
            meta.conntrack_data.flow_key.dst_l4_port : exact;
        }

        actions = {
            set_flow_entry_attr;
        }
    }
    
    //
    // Flow bulk get session filter:
    //
    action set_flow_entry_bulk_get_session_filter_attr(
        @SaiVal[type="sai_dash_flow_entry_bulk_get_session_filter_key_t"] dash_flow_entry_bulk_get_session_filter_key_t dash_flow_entry_bulk_get_session_filter_key, 
        @SaiVal[type="sai_dash_flow_entry_bulk_get_session_op_key_t"] dash_flow_entry_bulk_get_session_op_key_t  dash_flow_entry_bulk_get_session_op_key,
        bit<64> int_value,
        IPv4ORv6Address ip_value)
    {
    }

    //
    // Flow bulk get session:
    //
    action set_flow_entry_bulk_get_session_attr(
        /* GRPC Session server IP and port */
        IPv4ORv6Address bulk_get_session_ip,
        bit<16> bulk_get_session_port,

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

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.ENI_ADDR  != 0) {
            meta.conntrack_data.flow_key.eni_addr = meta.eni_addr;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL  != 0) {
            meta.conntrack_data.flow_key.ip_protocol = meta.ip_protocol;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_IP  != 0) {
            meta.conntrack_data.flow_key.src_ip_addr = meta.src_ip_addr;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_IP  != 0) {
            meta.conntrack_data.flow_key.dst_ip_addr = meta.dst_ip_addr;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT  != 0) {
            meta.conntrack_data.flow_key.src_l4_port = meta.src_l4_port;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_PORT  != 0) {
            meta.conntrack_data.flow_key.dst_l4_port = meta.dst_l4_port;
        }

        flow_entry.apply();
        flow_entry_bulk_get_session_filter.apply();
        flow_entry_bulk_get_session.apply();
    }
}

#endif /* _DASH_STAGE_CONNTRACK_LOOKUP_P4 */
