from py_model.libs.__table import *
from py_model.libs.__counters import *
from py_model.data_plane.dash_headers import *
from py_model.data_plane.dash_metadata import *
from py_model.data_plane.dash_routing_types import *
from py_model.data_plane.defines import *


class outbound_mapping_stage:
    @staticmethod
    def set_vnet_attrs(vni: Annotated[int, 24]):
        meta.u0_encap_data.vni = vni

    DEFINE_TABLE_COUNTER("ca_to_pa_counter")
    ca_to_pa = Table(
        key={
            # Flow for express route
            "meta.dst_vnet_id"      : (EXACT, {"type": "sai_object_id_t"}),
            "meta.is_lkup_dst_ip_v6": (EXACT, {"name": "dip_is_v6"}),
            "meta.lkup_dst_ip_addr" : (EXACT, {"name": "dip"}),
        },
        actions=[
            set_tunnel_mapping,
            set_private_link_mapping,
            (drop, {"annotations": "@defaultonly"}),
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.ca_to_pa",
        sai_table=SaiTable(name="outbound_ca_to_pa", api="dash_outbound_ca_to_pa",),
    )
    ATTACH_TABLE_COUNTER("ca_to_pa_counter", "ca_to_pa")

    vnet = Table(
        key={
            "meta.vnet_id": (EXACT, {"type": "sai_object_id_t"}),
        },
        actions=[
            set_vnet_attrs,
        ],
        tname=f"{__qualname__}.vnet",
        sai_table=SaiTable(name="vnet", api="dash_vnet", isobject="true",),
    )

    @classmethod
    def apply(cls):
        if meta.target_stage != dash_pipeline_stage_t.OUTBOUND_MAPPING:
            return

        py_log("info", "Applying table 'ca_to_pa'")
        action = cls.ca_to_pa.apply()["action_run"]
        if action == set_tunnel_mapping:
            py_log("info", "Applying table 'vnet'")
            cls.vnet.apply()
        elif action == drop:
            UPDATE_ENI_COUNTER("outbound_ca_pa_entry_miss_drop")
