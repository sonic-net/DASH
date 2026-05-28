from py_model.libs.__table import *
from py_model.libs.__counters import *
from py_model.data_plane.dash_headers import *
from py_model.data_plane.dash_metadata import *
from py_model.data_plane.dash_routing_types import *
from py_model.data_plane.defines import *


class outbound_routing_stage:
    @staticmethod
    def set_outbound_routing_group_attr(disabled: Annotated[int, 1]):
        meta.eni_data.outbound_routing_group_data.disabled = bool(disabled)

    outbound_routing_group = Table(
        key={
            "meta.eni_data.outbound_routing_group_data.outbound_routing_group_id": (
                        EXACT, {"type": "sai_object_id_t"},
            ),
        },
        actions=[
            set_outbound_routing_group_attr,
            (drop, {"annotations": "@defaultonly"}),
        ],
        tname=f"{__qualname__}.outbound_routing_group",
        sai_table=SaiTable(name="outbound_routing_group", api="dash_outbound_routing", order=1, isobject="true",),
    )

    DEFINE_TABLE_COUNTER("routing_counter")
    routing = Table(
        key={
            "meta.eni_data.outbound_routing_group_data.outbound_routing_group_id": (
                EXACT, {"type": "sai_object_id_t"},
            ),
            "meta.is_overlay_ip_v6": (
                EXACT, {"name": "destination_is_v6"},
            ),
            "meta.dst_ip_addr": (
                LPM, {"name": "destination"},
            ),
        },
        actions=[
            route_vnet,           # for express route - ecmp of overlay
            route_vnet_direct,
            route_direct,
            route_service_tunnel,
            drop,
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.routing",
        sai_table=SaiTable(name="outbound_routing", api="dash_outbound_routing",),
    )
    ATTACH_TABLE_COUNTER("routing_counter", "routing")

    @classmethod
    def apply(cls):
        py_log("info", "outbound_routing_stage")
        if meta.target_stage != dash_pipeline_stage_t.OUTBOUND_ROUTING:
            return

        py_log("info", "Applying table 'outbound_routing_group'")
        if not cls.outbound_routing_group.apply().get("hit", False):
            UPDATE_ENI_COUNTER("outbound_routing_group_miss_drop")
            drop()
            return

        if meta.eni_data.outbound_routing_group_data.disabled:
            UPDATE_ENI_COUNTER("outbound_routing_group_disabled_drop")
            drop()
            return

        py_log("info", "Applying table 'routing'")
        if not cls.routing.apply()["hit"]:
            UPDATE_ENI_COUNTER("outbound_routing_entry_miss_drop")
