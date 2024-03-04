#ifndef _DASH_FLOW_P4_
#define _DASH_FLOW_P4_

#include "dash_headers.p4"

control Flow(inout headers_t hdr, inout metadata_t meta) {
    action flow_table_action(
        bit<32> table_size,
        bit<32> table_expire_time,
        bit<32> table_version,
        bit<32> table_key_flag,
        bit<1> table_tcp_track_state,
        bit<1> table_tcp_reset_illegal) {
    }

    action flow_entry_action(
        @SaiVal[type="sai_object_id_t"] bit<64> flow_table_id,
        bit<32> flow_version,
        @SaiVal[type="sai_u8_list_t"] bit<32> flow_protobuf,
        bit<32> flow_bidirectional,
        bit<32> flow_direction,
        bit<32> flow_reverse_key,
        bit<32> flow_policy_result,
        bit<32> flow_dest_pa,
        bit<32> flow_metering_class,
        bit<32> flow_rewrite_info,
        bit<32> flow_vendor_metadata) {
    }

    @SaiTable[name = "flow_table", api = "dash_flow", api_order = 0, isobject="true"]
    table flow_table {
        key = {
            meta.eni_id : exact @SaiVal[type = "sai_object_id_t"]; /* To-Do: Discuss what will be key? */
        }
        actions = {
            flow_table_action();
        }
    }

    @SaiTable[name = "flow", api = "dash_flow", api_order = 1, enable_bulk_get_api = "true"]
    table flow_entry {
        key = {
            meta.dst_ip_addr : exact @SaiVal[name = "dip", type = "sai_ip_address_t"]; 
            meta.src_ip_addr : exact @SaiVal[name = "sip", type = "sai_ip_address_t"]; 
            meta.ip_protocol : exact @SaiVal[name = "protocol", type = "sai_uint16_t"]; 
            meta.src_l4_port : exact @SaiVal[name = "src_port", type = "sai_uint16_t"]; 
            meta.dst_l4_port : exact @SaiVal[name = "dst_port", type = "sai_uint16_t"]; 
            meta.direction : exact @SaiVal[name = "direction",  type = "sai_uint32_t"];
            meta.eni_id : exact @SaiVal[type = "sai_object_id_t"]; /* To-Do: Disscuss key is too long */
        }
        actions = {
            flow_entry_action();
        }
    }

    apply {
        flow_table.apply();
        flow_entry.apply();
    }
}

#endif /* _DASH_FLOW_P4_ */
