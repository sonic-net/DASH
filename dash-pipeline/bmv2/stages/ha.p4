#ifndef _DASH_STAGE_HA_P4_
#define _DASH_STAGE_HA_P4_

control ha_stage(inout headers_t hdr,
                 inout metadata_t meta)
{
    //
    // HA scope:
    //
    action set_ha_scope_attr(
        @SalVal[type="sai_object_id_t"] bit<16> ha_set_id,
        @SaiVal[type="sai_dash_ha_role_t"] dash_ha_role_t dash_ha_role,
        @SaiVal[isreadonly="true"] bit<32> flow_version,
        bit<1> flow_reconcile_requested,
        @SaiVal[isreadonly="true"] bit<1> flow_reconcile_needed,
        @SaiVal[type="sai_ip_address_t"] IPv4Address vip_v4,
        IPv6Address vip_v6,
        bit<1> admin_state,
        bit<1> activate_role,
        @SaiVal[isreadonly="true", type="sai_dash_ha_state_t"] dash_ha_state_t dash_ha_state
    ) {
        meta.ha.ha_set_id = ha_set_id;
        meta.ha.ha_role = dash_ha_role;
    }

    @SaiTable[api = "dash_ha", order=1, isobject="true"]
    table ha_scope {
        key = {
            meta.ha.ha_scope_id : exact;
        }
        actions = {
            set_ha_scope_attr;
        }
    }

    //
    // HA set:
    //

    // Data plane probe related counters
    DEFINE_COUNTER(dp_probe_req_rx, MAX_HA_SET, name="dp_probe_req_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_req_tx, MAX_HA_SET, name="dp_probe_req_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_ack_rx, MAX_HA_SET, name="dp_probe_ack_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER(dp_probe_ack_tx, MAX_HA_SET, name="dp_probe_ack_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(dp_probe_failed, MAX_HA_SET, name="dp_probe_failed", attr_type="stats", action_names="set_ha_set_attr")

    // Control plane data channel related counters
    DEFINE_HIT_COUNTER(cp_data_channel_connect_attempted, MAX_HA_SET, name="cp_data_channel_connect_attempted", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(cp_data_channel_connect_received, MAX_HA_SET, name="cp_data_channel_connect_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(cp_data_channel_connect_succeeded, MAX_HA_SET, name="cp_data_channel_connect_succeeded", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(cp_data_channel_connect_failed, MAX_HA_SET, name="cp_data_channel_connect_failed", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(cp_data_channel_connect_rejected, MAX_HA_SET, name="cp_data_channel_connect_rejected", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(cp_data_channel_timeout_count, MAX_HA_SET, name="cp_data_channel_timeout_count", attr_type="stats", action_names="set_ha_set_attr")

    // Bulk sync related counters
    DEFINE_HIT_COUNTER(bulk_sync_message_received, MAX_HA_SET, name="bulk_sync_message_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(bulk_sync_message_sent, MAX_HA_SET, name="bulk_sync_message_sent", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(bulk_sync_message_send_failed, MAX_HA_SET, name="bulk_sync_message_send_failed", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(bulk_sync_flow_received, MAX_HA_SET, name="bulk_sync_flow_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER(bulk_sync_flow_sent, MAX_HA_SET, name="bulk_sync_flow_sent", attr_type="stats", action_names="set_ha_set_attr")

    action set_ha_set_attr(
        bit<1> local_ip_is_v6,
        @SaiVal[type="sai_ip_address_t"] IPv4ORv6Address local_ip,
        bit<1> peer_ip_is_v6,
        @SaiVal[type="sai_ip_address_t"] IPv4ORv6Address peer_ip,
        bit<16> cp_data_channel_port,
        bit<16> dp_channel_dst_port,
        bit<16> dp_channel_min_src_port,
        bit<16> dp_channel_max_src_port,
        bit<32> dp_channel_probe_interval_ms,
        bit<32> dp_channel_probe_fail_threshold,
        @SaiVal[isreadonly="true"] bit<1> dp_channel_is_alive,
        bit<32> dpu_driven_ha_switchover_wait_time_ms
    ) {
        meta.ha.peer_ip_is_v6 = peer_ip_is_v6;
        meta.ha.peer_ip = peer_ip;

        meta.ha.dp_channel_dst_port = dp_channel_dst_port;
        meta.ha.dp_channel_src_port_min = dp_channel_min_src_port;
        meta.ha.dp_channel_src_port_max = dp_channel_max_src_port;
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
