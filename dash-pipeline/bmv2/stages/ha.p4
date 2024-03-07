#ifndef _DASH_STAGE_HA_P4_
#define _DASH_STAGE_HA_P4_

control ha_stage(inout headers_t hdr,
                 inout metadata_t meta)
{
    //
    // ENI-level flow operation counters:
    //
    DEFINE_HIT_COUNTER(flow_created_counter, MAX_ENI, name="flow_created", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_create_failed_counter, MAX_ENI, name="flow_create_failed", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_updated_counter, MAX_ENI, name="flow_updated", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_update_failed_counter, MAX_ENI, name="flow_update_failed", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_deleted_counter, MAX_ENI, name="flow_deleted", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_delete_failed_counter, MAX_ENI, name="flow_delete_failed", attr_type="stats", action_names="set_eni_attrs", order=1)
    DEFINE_HIT_COUNTER(flow_aged_counter, MAX_ENI, name="flow_aged", attr_type="stats", action_names="set_eni_attrs", order=1)

    //
    // ENI-level flow sync packet counters:
    //
    DEFINE_COUNTER(inline_sync_packet_rx_counter, MAX_ENI, name="inline_sync_packet_rx", attr_type="stats", action_names="set_eni_attrs", order=2)
    DEFINE_COUNTER(inline_sync_packet_tx_counter, MAX_ENI, name="inline_sync_packet_tx", attr_type="stats", action_names="set_eni_attrs", order=2)
    DEFINE_COUNTER(timed_sync_packet_rx_counter, MAX_ENI, name="timed_sync_packet_rx", attr_type="stats", action_names="set_eni_attrs", order=2)
    DEFINE_COUNTER(timed_sync_packet_tx_counter, MAX_ENI, name="timed_sync_packet_tx", attr_type="stats", action_names="set_eni_attrs", order=2)

    //
    // ENI-level flow sync request counters:
    // - Depends on implementations, the flow sync request could be batched, hence they need to tracked separately.
    // - The counters are defined as combination of following things:
    //   - 3 flow sync operations: create, update, delete.
    //   - 2 ways of sync: Inline sync and timed sync.
    //   - Request result: succeeded, failed (unexpected) and ignored (expected and ok to ignore, e.g., more packets arrives before flow sync is acked).
    //
    #define DEFINE_ENI_FLOW_SYNC_COUNTERS(counter_name) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_sent_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _req_sent), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_recv_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _req_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_failed_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _req_failed), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_ignored_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _req_failed), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_recv_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _ack_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_failed_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _ack_failed_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_ignored_counter, MAX_ENI, name=PP_STR(inline_ ## counter_name ## _ack_ignored_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_sent_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _req_sent), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_recv_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _req_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_failed_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _req_failed), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_ignored_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _req_failed), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_recv_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _ack_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_failed_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _ack_failed_recv), attr_type="stats", action_names="set_eni_attrs", order=2) \
        DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_ignored_counter, MAX_ENI, name=PP_STR(timed_ ## counter_name ## _ack_ignored_recv), attr_type="stats", action_names="set_eni_attrs", order=2)

    DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_create)
    DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_update)
    DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_delete)

    //
    // HA scope:
    //
    action set_ha_scope_attr(
        @SalVal[type="sai_object_id_t"] bit<16> ha_set_id,
        @SaiVal[type="sai_dash_ha_role_t"] dash_ha_role_t ha_role,
        @SaiVal[isreadonly="true"] bit<32> flow_version
    ) {
        meta.ha.ha_set_id = ha_set_id;
        meta.ha.ha_role = ha_role;
    }

    @SaiTable[api = "dash_ha", order=1, isobject="true"]
    table ha_scope {
        key = {
            meta.ha.ha_scope_id : exact @SaiVal[type="sai_object_id_t"];
        }
        actions = {
            set_ha_scope_attr;
        }
    }

    //
    // HA set:
    //
    DEFINE_COUNTER(dp_probe_req_rx, MAX_HA_SET, name="dp_probe_req_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_req_tx, MAX_HA_SET, name="dp_probe_req_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_ack_rx, MAX_HA_SET, name="dp_probe_ack_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_ack_tx, MAX_HA_SET, name="dp_probe_ack_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(dp_probe_failed, MAX_HA_SET, name="dp_probe_failed", attr_type="stats", action_names="set_ha_set_attr")

    action set_ha_set_attr(
        bit<1> local_ip_is_v6,
        @SaiVal[type="sai_ip_address_t"] IPv4ORv6Address local_ip,
        bit<1> peer_ip_is_v6,
        @SaiVal[type="sai_ip_address_t"] IPv4ORv6Address peer_ip,
        bit<16> dp_channel_dst_port,
        bit<16> dp_channel_src_port_min,
        bit<16> dp_channel_src_port_max,
        bit<32> dp_channel_probe_interval_ms,
        bit<32> dp_channel_probe_fail_threshold
    ) {
        meta.ha.peer_ip_is_v6 = peer_ip_is_v6;
        meta.ha.peer_ip = peer_ip;
        
        meta.ha.dp_channel_dst_port = dp_channel_dst_port;
        meta.ha.dp_channel_src_port_min = dp_channel_src_port_min;
        meta.ha.dp_channel_src_port_max = dp_channel_src_port_max;
    }

    @SaiTable[api = "dash_ha", order=0, isobject="true"]
    table ha_set {
        key = {
            meta.ha.ha_set_id : exact @SaiVal[type="sai_object_id_t"];
        }
        actions = {
            set_ha_set_attr;
        }
    }

    apply {
        // If HA scope id is not set, then HA is not enabled.
        if (meta.ha.ha_scope_id == 0) {
            return;
        }
        ha_scope.apply();

        // If HA set id is not set, then HA is not enabled.
        if (meta.ha.ha_set_id == 0) {
            return;
        }
        ha_set.apply();
    
        // TODO: HA state machine handling.
    }
}

#endif /* _DASH_STAGE_HA_P4_ */
