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
        @SaiVal[is_filter_key="true"] bit<32> flow_version,
        @SaiVal[type="sai_dash_direction_t"] dash_direction_t dash_direction,

        /* Flow actions */
        @SaiVal[type="sai_dash_flow_action_t"] dash_flow_action_t dash_flow_action,
        
        /* Encap metadata */
        bit<24> vni,
        bit<24> dest_vnet_vni,
        IPv4ORv6Address underlay_sip, 
        IPv4ORv6Address underlay_dip,
        EthernetAddress underlay_smac,
        EthernetAddress underlay_dmac,
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t dash_encapsulation,
        IPv4ORv6Address original_overlay_sip,
        IPv4ORv6Address original_overlay_dip,
        
        /* Overlay rewrite metadata */
        EthernetAddress src_mac,
        IPv4ORv6Address src_ip,
        bit<1> src_ip_is_v6,
        IPv4ORv6Address dst_ip,
        bit<1> dst_ip_is_v6,
        IPv6Address src_ip_mask,
        IPv6Address dst_ip_mask,
      
        /* Meter and policy metadata */ 
        bit<16> meter_class,

        /* Reverse flow info */ 
        bit<1> is_bidirectional_flow,
        bit<8> reverse_flow_protocol,
        IPv4ORv6Address reverse_flow_dst_ip,
        bit<1> reverse_flow_dst_ip_is_v6,
        IPv4ORv6Address reverse_flow_src_ip,
        bit<1> reverse_flow_src_ip_is_v6,
        bit<16> reverse_flow_src_port,
        bit<16> reverse_flow_dst_port,

        /* Extra flow metadata */ 
        @SaiVal[type="sai_u8_list_t"] bit<16> vendor_metadata,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_data_pb)
    {
        /* Set flow actions */
        meta.conntrack_data.flow_data.actions = dash_flow_action;

        /* Set encapsulation metadata */
        meta.encap_data.vni = vni;
        meta.encap_data.dest_vnet_vni = dest_vnet_vni;
        //meta.encap_data.underlay_sip = underlay_sip;
        //meta.encap_data.underlay_dip = underlay_dip;
        meta.encap_data.underlay_smac = underlay_smac;
        meta.encap_data.underlay_dmac = underlay_dmac;
        meta.encap_data.dash_encapsulation = dash_encapsulation;
        //meta.encap_data.original_overlay_sip = original_overlay_sip;
        //meta.encap_data.original_overlay_dip = original_overlay_dip; 

        /* Set overlay rewrite metadata */
        // meta.overlay_data.src_mac = src_mac;
        // meta.overlay_data.src_ip = src_ip;
        // meta.overlay_data.src_ip_is_v6 = src_ip_is_v6;
        // meta.overlay_data.dst_ip = dst_ip;
        // meta.overlay_data.dst_ip_is_v6 = dst_ip_is_v6;
        // meta.overlay_data.src_ip_mask = src_ip_mask;
        // meta.overlay_data.dst_ip_mask = dst_ip_mask;

        /* Set meter and policy metadata */
        meta.meter_class = meter_class;

        /* Set reverse flow information */

        /* Set additional flow metadata */
        //meta.conntrack_data.flow_data.vendor_metadata = vendor_metadata;
        //meta.conntrack_data.flow_data.flow_data_pb = flow_data_pb;
    }

    @SaiTable[name = "flow", api = "dash_flow", order = 1, enable_bulk_get_api = "true", enable_bulk_get_server = "true"]
    table flow_entry {
        key = {
            meta.conntrack_data.flow_table.id: exact @SaiVal[name = "flow_table_id", type="sai_object_id_t"];
            meta.conntrack_data.flow_key.ip_protocol  : exact @SaiVal[name = "protocol"]; 
            meta.conntrack_data.flow_key.src_ip_addr : exact @SaiVal[name = "src_ip"]; 
            meta.conntrack_data.flow_key.dst_ip_addr : exact @SaiVal[name = "dst_ip"]; 
            meta.conntrack_data.flow_key.src_l4_port : exact @SaiVal[name = "src_port"]; 
            meta.conntrack_data.flow_key.dst_l4_port : exact @SaiVal[name = "dst_port"]; 
        }

        actions = {
            set_flow_entry_attr;
        }
    }

    apply {
        flow_table.apply();

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.PROTOCOL  != 0) {
            meta.conntrack_data.flow_key.ip_protocol = meta.ip_protocol;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_IP  != 0) {
            meta.conntrack_data.flow_key.src_ip_addr = meta.src_ip_addr;
        }
        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_IP  != 0) {
            meta.conntrack_data.flow_key.dst_ip_addr = meta.dst_ip_addr ;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.SRC_PORT  != 0) {
            meta.conntrack_data.flow_key.src_l4_port = meta.src_l4_port;
        }

        if (meta.conntrack_data.flow_table.flow_enabled_key & dash_flow_enabled_key_t.DST_PORT  != 0) {
            meta.conntrack_data.flow_key.dst_l4_port = meta.dst_l4_port;
        }

        flow_entry.apply();
    }
}

#endif /* _DASH_STAGE_CONNTRACK_LOOKUP_P4 */
