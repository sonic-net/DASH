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
        /* flow metadata */
        @SaiVal[type="sai_object_id_t"] bit<64> flow_table_id,
        bit<32> flow_version,
        @SaiVal[type="sai_u8_list_t"] bit<16> flow_protobuf,
        bit<32> flow_bidirectional,
        bit<32> flow_direction,
        bit<64> flow_reverse_key,
        bit<32> flow_vendor_metadata,
        /* encap metadata */
        bit<24> vni,
        bit<24> dest_vnet_vni,
        IPv4Address underlay_sip,
        IPv4Address underlay_dip,
        EthernetAddress underlay_smac,
        EthernetAddress underlay_dmac,
        @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
        dash_encapsulation_t dash_encapsulation,
        IPv4Address original_overlay_sip,
        IPv4Address original_overlay_dip,
        /* overlay_rewrite metadata */
        EthernetAddress dest_mac,
        IPv4ORv6Address sip,
        IPv4ORv6Address dip,
        IPv6Address sip_mask,
        IPv6Address dip_mask,
        /* meter and policy metadata */ 
        bit<1> meter_policy_en,
        bit<1> mapping_meter_class_override,
        bit<16> meter_policy_id,
        bit<16> policy_meter_class,
        bit<16> route_meter_class,
        bit<16> mapping_meter_class,
        bit<16> meter_class,
        bit<32> meter_bucket_index) {
    }

    @SaiTable[name = "flow_table", api = "dash_flow", api_order = 0, isobject="true"]
    table flow_table {
        key = {
            meta.flow_table_id : exact @SaiVal[type = "sai_uint64_t"]; 
        }
        actions = {
            flow_table_action();
        }
    }

    @SaiTable[name = "flow", api = "dash_flow", api_order = 1, enable_bulk_get_api = "true"]
    table flow_entry {
        key = {
            meta.dst_ip_addr : exact @SaiVal[name = "dst_ip", type = "sai_ip_address_t"]; 
            meta.src_ip_addr : exact @SaiVal[name = "src_ip", type = "sai_ip_address_t"]; 
            meta.ip_protocol : exact @SaiVal[name = "protocol", type = "sai_uint16_t"]; 
            meta.src_l4_port : exact @SaiVal[name = "src_port", type = "sai_uint16_t"]; 
            meta.dst_l4_port : exact @SaiVal[name = "dst_port", type = "sai_uint16_t"]; 
            meta.direction : exact @SaiVal[name = "direction",  type = "sai_uint32_t"];
            meta.eni_id: exact @SaiVal[name = "eni_id", type = "sai_uint16_t"]; 
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
