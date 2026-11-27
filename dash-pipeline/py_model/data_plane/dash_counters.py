from py_model.libs.__utils import *
from py_model.libs.__counters import *

# Port level
DEFINE_PACKET_COUNTER("vip_miss_drop", 1, attr_type="stats")
DEFINE_PACKET_COUNTER("eni_miss_drop", 1, attr_type="stats")
DEFINE_COUNTER("port_lb_fast_path_icmp_in", 1, attr_type="stats")
DEFINE_COUNTER("port_lb_fast_path_eni_miss_drop", 1, attr_type="stats")

# ENI level
DEFINE_ENI_COUNTER("eni_rx", "rx")
DEFINE_ENI_COUNTER("eni_tx", "tx")
DEFINE_ENI_COUNTER("eni_outbound_rx", "outbound_rx")
DEFINE_ENI_COUNTER("eni_outbound_tx", "outbound_tx")
DEFINE_ENI_COUNTER("eni_inbound_rx", "inbound_rx")
DEFINE_ENI_COUNTER("eni_inbound_tx", "inbound_tx")
DEFINE_ENI_COUNTER("eni_lb_fast_path_icmp_in", "lb_fast_path_icmp_in")

# ENI-level flow operation counters (hits)
DEFINE_ENI_HIT_COUNTER("flow_created")
DEFINE_ENI_HIT_COUNTER("flow_create_failed")
DEFINE_ENI_HIT_COUNTER("flow_updated")
DEFINE_ENI_HIT_COUNTER("flow_update_failed")
DEFINE_ENI_HIT_COUNTER("flow_updated_by_resimulation")
DEFINE_ENI_HIT_COUNTER("flow_update_by_resimulation_failed")
DEFINE_ENI_HIT_COUNTER("flow_deleted")
DEFINE_ENI_HIT_COUNTER("flow_delete_failed")
DEFINE_ENI_HIT_COUNTER("flow_aged")

# ENI-level data plane flow sync packet counters
DEFINE_ENI_COUNTER("inline_sync_packet_rx")
DEFINE_ENI_COUNTER("inline_sync_packet_tx")
DEFINE_ENI_COUNTER("timed_sync_packet_rx")
DEFINE_ENI_COUNTER("timed_sync_packet_tx")

# ENI-level data plane flow sync request counters:
DEFINE_ENI_FLOW_SYNC_COUNTERS("flow_create")
DEFINE_ENI_FLOW_SYNC_COUNTERS("flow_update")
DEFINE_ENI_FLOW_SYNC_COUNTERS("flow_delete")

# ENI-level drop counters
DEFINE_ENI_PACKET_COUNTER("outbound_routing_entry_miss_drop")
DEFINE_ENI_PACKET_COUNTER("outbound_ca_pa_entry_miss_drop")
DEFINE_ENI_PACKET_COUNTER("inbound_routing_entry_miss_drop")
DEFINE_ENI_PACKET_COUNTER("outbound_routing_group_miss_drop")
DEFINE_ENI_PACKET_COUNTER("outbound_routing_group_disabled_drop")
DEFINE_ENI_PACKET_COUNTER("outbound_port_map_miss_drop")
DEFINE_ENI_PACKET_COUNTER("outbound_port_map_port_range_entry_miss_drop")
DEFINE_ENI_PACKET_COUNTER("eni_trusted_vni_entry_miss_drop")

