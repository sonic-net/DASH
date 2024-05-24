//
// This file is used for defining the global and ENI counters inside DASH.
//
// These counters are added here, because they are special and working more like "global" counters, and spreaded across the pipoeline.
// This helps us to have a better view and helps us maintaining the ABI compatibiity of these counters.
//
// The other counters will go with its table, such as HA set, because they are only used in logic that is related to that single table.
// 

#ifndef __DASH_COUNTERS__
#define __DASH_COUNTERS__

//
// Port level counters
//
DEFINE_PACKET_COUNTER(vip_miss_drop, 1, attr_type="stats")
DEFINE_PACKET_COUNTER(eni_miss_drop, 1, attr_type="stats")
DEFINE_COUNTER(port_lb_fast_path_icmp_in, 1, attr_type="stats")
DEFINE_COUNTER(port_lb_fast_path_eni_miss_drop, 1, attr_type="stats")

//
// ENI level counters:
//
DEFINE_COUNTER(eni_rx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_tx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_outbound_rx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_outbound_tx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_inbound_rx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_inbound_tx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)
DEFINE_COUNTER(eni_lb_fast_path_icmp_in, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=0)

//
// ENI-level flow operation counters:
//
DEFINE_HIT_COUNTER(flow_created, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_create_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_updated, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_update_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_deleted, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_delete_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)
DEFINE_HIT_COUNTER(flow_aged, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=1)

//
// ENI-level data plane flow sync packet counters:
//
DEFINE_COUNTER(inline_sync_packet_rx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2)
DEFINE_COUNTER(inline_sync_packet_tx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2)
DEFINE_COUNTER(timed_sync_packet_rx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2)
DEFINE_COUNTER(timed_sync_packet_tx, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2)

//
// ENI-level data plane flow sync request counters:
// - Depends on implementations, the flow sync request could be batched, hence they need to tracked separately.
// - The counters are defined as combination of following things:
//   - 3 flow sync operations: create, update, delete.
//   - 2 ways of sync: Inline sync and timed sync.
//   - Request result: succeeded, failed (unexpected) and ignored (expected and ok to ignore, e.g., more packets arrives before flow sync is acked).
//
#define DEFINE_ENI_FLOW_SYNC_COUNTERS(counter_name) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_sent, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_recv, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _req_ignored, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_recv, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(inline_ ## counter_name ## _ack_ignored, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_sent, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_recv, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _req_ignored, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_recv, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_failed, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2) \
    DEFINE_HIT_COUNTER(timed_ ## counter_name ## _ack_ignored, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=2)

DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_create)
DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_update)
DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_delete)

//
// ENI-level drop counters
//
DEFINE_PACKET_COUNTER(outbound_routing_entry_miss_drop, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=3)
DEFINE_PACKET_COUNTER(outbound_ca_pa_entry_miss_drop, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=3)
DEFINE_PACKET_COUNTER(inbound_routing_entry_miss_drop, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=3)

#endif // __DASH_COUNTERS__
