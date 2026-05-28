from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.libs.__counters import *
from py_model.data_plane.dash_routing_types import *
from py_model.data_plane.routing_actions.routing_action_nat_port import *


class outbound_port_map_stage:
    @staticmethod
    def set_port_map_attr(self):
        pass

    @staticmethod
    def skip_mapping(self):
        pass

    @staticmethod
    def map_to_private_link_service(backend_ip          : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                                    match_port_base     : Annotated[int, 16],
                                    backend_port_base   : Annotated[int, 16]):
        assert (meta.routing_actions & dash_routing_actions_t.NAT46) != 0

        # For private link, once the service is redirected, we need to update 2 things:
        # 1. The underlay IP to point to the new backend IP in order to route the packet there.
        # 2. The overlay IP and port to the new backend ip and port, so that the overlay packet will
        #    look like being sent from the new backend IP.

        # Update underlay IP to backend
        meta.u0_encap_data.underlay_dip = backend_ip

        # Python support arithmetic on 128-bit operands
        # Update overlay IP
        meta.overlay_data.dip = (meta.overlay_data.dip & meta.overlay_data.dip_mask) | int(backend_ip)

        # Update overlay port with DNAT
        push_action_dnat_port(meta.dst_l4_port - match_port_base + backend_port_base)


    DEFINE_TABLE_COUNTER("outbound_port_map_counter")
    outbound_port_map = Table(
        key={
            "meta.port_map_ctx.map_id": (EXACT, {"name": "outbound_port_map_id",
                                                 "type": "sai_object_id_t"})
        },
        actions=[
            set_port_map_attr,
            (drop, {"annotations": "@defaultonly"}),
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.outbound_port_map",
        sai_table=SaiTable(api="dash_outbound_port_map", order=0, isobject="true",),
    )
    ATTACH_TABLE_COUNTER("outbound_port_map_counter", "outbound_port_map")


    DEFINE_TABLE_COUNTER("outbound_port_map_port_range_counter")
    outbound_port_map_port_range = Table(
        key={
            "meta.port_map_ctx.map_id"  : (EXACT, {"name": "outbound_port_map_id", "type": "sai_object_id_t"}),
            "meta.dst_l4_port"          : (RANGE, {"name": "dst_port_range"})
        },
        actions=[
            skip_mapping,
            map_to_private_link_service,
            (drop, {"annotations": "@defaultonly"}),
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.outbound_port_map_port_range",
        sai_table=SaiTable(api="dash_outbound_port_map", order=1, single_match_priority="true",),
    )
    ATTACH_TABLE_COUNTER("outbound_port_map_port_range_counter", "outbound_port_map_port_range")
    @classmethod
    def apply(cls):
        py_log("info", "outbound_routing_stage")
        if meta.port_map_ctx.map_id == 0:
            return

        py_log("info", "Applying table 'outbound_port_map'")
        if not cls.outbound_port_map.apply().hit:
            UPDATE_ENI_COUNTER("outbound_port_map_miss_drop")
            return

        py_log("info", "Applying table 'outbound_port_map_port_range'")
        if not cls.outbound_port_map_port_range.apply().hit:
            UPDATE_ENI_COUNTER("outbound_port_map_port_range_entry_miss_drop")
