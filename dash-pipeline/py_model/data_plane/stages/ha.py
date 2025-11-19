from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.data_plane.dash_counters import *

class ha_stage:
    # HA scope
    @staticmethod
    def set_ha_scope_attr(
        ha_set_id                   : Annotated[int, 16, {"type" : "sai_object_id_t"}],
        dash_ha_role                : Annotated[dash_ha_role_t, {"type" : "sai_dash_ha_role_t"}],
        flow_version                : Annotated[int, 32, {"isreadonly" : "true"}],
        flow_reconcile_requested    : Annotated[int, 1],
        flow_reconcile_needed       : Annotated[int, 1, {"isreadonly" : "true"}],
        vip_v4                      : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
        vip_v6                      : Annotated[int, IPv6Address_size],
        admin_state                 : Annotated[int, 1],
        activate_role               : Annotated[int, 1],
        dash_ha_state               : Annotated[dash_ha_state_t, {"isreadonly" : "true", "type" : "sai_dash_ha_state_t"}] 
    ):
        meta.ha.ha_set_id = ha_set_id
        meta.ha.ha_role = dash_ha_role

    # HA set
    # Data plane probe related counters
    DEFINE_COUNTER("dp_probe_req_rx", MAX_HA_SET, "dp_probe_req_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER("dp_probe_req_tx", MAX_HA_SET, "dp_probe_req_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER("dp_probe_ack_rx", MAX_HA_SET, "dp_probe_ack_rx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_COUNTER("dp_probe_ack_tx", MAX_HA_SET, "dp_probe_ack_tx", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("dp_probe_failed", MAX_HA_SET, "dp_probe_failed", attr_type="stats", action_names="set_ha_set_attr")

    # Control plane data channel related counters
    DEFINE_HIT_COUNTER("cp_data_channel_connect_attempted", MAX_HA_SET, "cp_data_channel_connect_attempted", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("cp_data_channel_connect_received", MAX_HA_SET, "cp_data_channel_connect_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("cp_data_channel_connect_succeeded", MAX_HA_SET, "cp_data_channel_connect_succeeded", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("cp_data_channel_connect_failed", MAX_HA_SET, "cp_data_channel_connect_failed", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("cp_data_channel_connect_rejected", MAX_HA_SET, "cp_data_channel_connect_rejected", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("cp_data_channel_timeout_count", MAX_HA_SET, "cp_data_channel_timeout_count", attr_type="stats", action_names="set_ha_set_attr")

    # Bulk sync related counters
    DEFINE_HIT_COUNTER("bulk_sync_message_received", MAX_HA_SET, "bulk_sync_message_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("bulk_sync_message_sent", MAX_HA_SET, "bulk_sync_message_sent", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("bulk_sync_message_send_failed", MAX_HA_SET, "bulk_sync_message_send_failed", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("bulk_sync_flow_received", MAX_HA_SET, "bulk_sync_flow_received", attr_type="stats", action_names="set_ha_set_attr")
    DEFINE_HIT_COUNTER("bulk_sync_flow_sent", MAX_HA_SET, "bulk_sync_flow_sent", attr_type="stats", action_names="set_ha_set_attr")

    @staticmethod
    def set_ha_set_attr(
        local_ip_is_v6                          : Annotated[int, 1],
        local_ip                                : Annotated[int, IPv4ORv6Address_size, {"type" : "sai_ip_address_t"}],
        peer_ip_is_v6                           : Annotated[int, 1],
        peer_ip                                 : Annotated[int, IPv4ORv6Address_size, {"type" : "sai_ip_address_t"}],
        cp_data_channel_port                    : Annotated[int, 16],
        dp_channel_dst_port                     : Annotated[int, 16],
        dp_channel_min_src_port                 : Annotated[int, 16],
        dp_channel_max_src_port                 : Annotated[int, 16],
        dp_channel_probe_interval_ms            : Annotated[int, 32],
        dp_channel_probe_fail_threshold         : Annotated[int, 32],
        dp_channel_is_alive                     : Annotated[int, 1, {"isreadonly" : "true"}],
        dpu_driven_ha_switchover_wait_time_ms   : Annotated[int, 32],
    ):
        meta.ha.peer_ip_is_v6 = peer_ip_is_v6
        meta.ha.peer_ip = peer_ip

        meta.ha.dp_channel_dst_port = dp_channel_dst_port
        meta.ha.dp_channel_src_port_min = dp_channel_min_src_port
        meta.ha.dp_channel_src_port_max = dp_channel_max_src_port

    ha_scope = Table(
        key={
            "meta.ha.ha_scope_id": EXACT,
        },
        actions=[
            set_ha_scope_attr,
        ],
        tname=f"{__qualname__}.ha_scope",
        sai_table=SaiTable(api="dash_ha", order=1, isobject="true",),
    )

    ha_set = Table(
        key={
            "meta.ha.ha_set_id": (EXACT, {"type" : "sai_object_id_t"})
        },
        actions=[
            set_ha_set_attr,
        ],
        tname=f"{__qualname__}.ha_set",
        sai_table=SaiTable(api="dash_ha", order=0, isobject="true",),
    )

    @classmethod
    def apply(cls):
        # If HA scope id is not set, then HA is not enabled.
        if meta.ha.ha_scope_id == 0:
            return
        py_log("info", "Applying table 'ha_scope'")
        cls.ha_scope.apply()

        # If HA set id is not set, then HA is not enabled.
        if meta.ha.ha_set_id == 0:
            return

        py_log("info", "Applying table 'ha_set'")
        cls.ha_set.apply()

        # TODO: HA state machine handling.
