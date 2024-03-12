#ifndef _DASH_FLOW_P4_
#define _DASH_FLOW_P4_

#include "dash_metadata.p4"

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

    @SaiTable[name = "flow_table", api = "dash_flow", api_order = 0, isobject="true"]
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
        bit<32> flow_version,
        bit<1> flow_bidirectional,
        @SaiVal[type="sai_dash_direction_t"] dash_direction_t dash_direction,
        bit<64> flow_reverse_key,

        /* Flow actions */
        @SaiVal[type="sai_dash_flow_action_t"] dash_flow_action_t dash_flow_action,
        
        /* Encap metadata */
        @SaiVal[type="sai_dash_encapsulation_t"] dash_encapsulation_t dash_encapsulation,
        EthernetAddress underlay_smac,
        EthernetAddress underlay_dmac,
        IPv4ORv6Address underlay_sip,
        IPv4ORv6Address underlay_dip,
        bit<24> vni,
       
        /* Overlay rewrite metadata */
        EthernetAddress smac,
        IPv4ORv6Address sip,
        IPv4ORv6Address dip,
        IPv6Address sip_mask,
        IPv6Address dip_mask,
      
        /* Meter and policy metadata */ 
        bit<16> meter_class,
        
        /* Extra flow metadata */ 
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_vendor_metadata,

        /* Mock attributes for special functions on flow table and flow */ 
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_protobuf,
        bit<64> flow_target_server,
        bit<64> flow_entry_filter
        )
    {
        meta.conntrack_data.flow_data.actions = dash_flow_action;
        // TODO: All action data should be set here.
    }

    @SaiTable[name = "flow", api = "dash_flow", api_order = 1, enable_bulk_get_api = "true"]
    table flow_entry {
        key = {
            meta.conntrack_data.flow_table.id: exact @SaiVal[type="sai_object_id_t"];
            meta.direction : exact @SaiVal[type="sai_dash_direction_t"];
            meta.ip_protocol : exact @SaiVal[name = "protocol"]; 
            meta.src_ip_addr : exact @SaiVal[name = "src_ip"]; 
            meta.dst_ip_addr : exact @SaiVal[name = "dst_ip"]; 
            meta.src_l4_port : exact @SaiVal[name = "src_port"]; 
            meta.dst_l4_port : exact @SaiVal[name = "dst_port"]; 
        }
        actions = {
            set_flow_entry_attr;
        }
    }

    apply {
        flow_table.apply();

        // TODO: Fix flow lookup key here according to key flags.

        flow_entry.apply();
    }
}

#endif /* _DASH_FLOW_P4_ */
