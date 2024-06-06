//
// This file is used for defining the global and ENI counters inside DASH.
//
// These counters are added here, because they are special and working more like "global" counters, and spread across the pipeline.
// This helps us to have a better view and helps us maintaining the ABI compatibility of these counters.
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
#define DEFINE_ENI_COUNTER(name, ...) \
    DEFINE_COUNTER(name, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", __VA_ARGS__)

#define DEFINE_ENI_PACKET_COUNTER(name, ...) \
    DEFINE_PACKET_COUNTER(name, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", __VA_ARGS__)

#define DEFINE_ENI_BYTE_COUNTER(name, count, ...) \
    DEFINE_BYTE_COUNTER(name, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", __VA_ARGS__)

#define DEFINE_ENI_HIT_COUNTER(name, ...) \
    DEFINE_HIT_COUNTER(name, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", __VA_ARGS__)

#define UPDATE_ENI_COUNTER(name) \
    UPDATE_COUNTER(name, meta.eni_id)

DEFINE_ENI_COUNTER(eni_rx, order=0, name="rx")
DEFINE_ENI_COUNTER(eni_tx, order=0, name="tx")
DEFINE_ENI_COUNTER(eni_outbound_rx, order=0, name="outbound_rx")
DEFINE_ENI_COUNTER(eni_outbound_tx, order=0, name="outbound_tx")
DEFINE_ENI_COUNTER(eni_inbound_rx, order=0, name="inbound_rx")
DEFINE_ENI_COUNTER(eni_inbound_tx, order=0, name="inbound_tx")
DEFINE_ENI_COUNTER(eni_lb_fast_path_icmp_in, order=0, name="lb_fast_path_icmp_in")

//
// ENI-level flow operation counters:
//
DEFINE_ENI_HIT_COUNTER(flow_created, order=1)
DEFINE_ENI_HIT_COUNTER(flow_create_failed, order=1)
DEFINE_ENI_HIT_COUNTER(flow_updated, order=1)
DEFINE_ENI_HIT_COUNTER(flow_update_failed, order=1)
DEFINE_ENI_HIT_COUNTER(flow_updated_by_resimulation, order=1)
DEFINE_ENI_HIT_COUNTER(flow_update_by_resimulation_failed, order=1)
DEFINE_ENI_HIT_COUNTER(flow_deleted, order=1)
DEFINE_ENI_HIT_COUNTER(flow_delete_failed, order=1)
DEFINE_ENI_HIT_COUNTER(flow_aged, order=1)

//
// ENI-level data plane flow sync packet counters:
//
DEFINE_ENI_COUNTER(inline_sync_packet_rx, order=2)
DEFINE_ENI_COUNTER(inline_sync_packet_tx, order=2)
DEFINE_ENI_COUNTER(timed_sync_packet_rx, order=2)
DEFINE_ENI_COUNTER(timed_sync_packet_tx, order=2)

//
// ENI-level data plane flow sync request counters:
// - Depends on implementations, the flow sync request could be batched, hence they need to tracked separately.
// - The counters are defined as combination of following things:
//   - 3 flow sync operations: create, update, delete.
//   - 2 ways of sync: Inline sync and timed sync.
//   - Request result: succeeded, failed (unexpected) and ignored (expected and ok to ignore, e.g., more packets arrives before flow sync is acked).
//
#define DEFINE_ENI_FLOW_SYNC_COUNTERS(counter_name) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _req_sent, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _req_recv, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _req_failed, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _req_ignored, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _ack_recv, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _ack_failed, order=2) \
    DEFINE_ENI_HIT_COUNTER(inline_ ## counter_name ## _ack_ignored, order=2) \
    \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _req_sent, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _req_recv, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _req_failed, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _req_ignored, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _ack_recv, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _ack_failed, order=2) \
    DEFINE_ENI_HIT_COUNTER(timed_ ## counter_name ## _ack_ignored, order=2)

DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_create)
DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_update)
DEFINE_ENI_FLOW_SYNC_COUNTERS(flow_delete)

//
// ENI-level drop counters:
//
DEFINE_ENI_PACKET_COUNTER(outbound_routing_entry_miss_drop, order=3)
DEFINE_ENI_PACKET_COUNTER(outbound_ca_pa_entry_miss_drop, order=3)
DEFINE_ENI_PACKET_COUNTER(inbound_routing_entry_miss_drop, order=3)
DEFINE_ENI_PACKET_COUNTER(outbound_routing_group_miss_drop, order=3)
DEFINE_ENI_PACKET_COUNTER(outbound_routing_group_admin_down_drop, order=3)

#endif // __DASH_COUNTERS__
