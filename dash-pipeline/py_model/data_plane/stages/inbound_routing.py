from py_model.libs.__table import *
from py_model.libs.__counters import *
from py_model.data_plane.dash_headers import *
from py_model.data_plane.dash_metadata import *
from py_model.data_plane.dash_routing_types import *

class inbound_routing_stage:
    @staticmethod
    def permit():
        pass

    @staticmethod
    def vxlan_decap():
        pass

    @staticmethod
    def vxlan_decap_pa_validate():
        pass

    @staticmethod
    def tunnel_decap(meter_class_or : Annotated[int, 32],
                     meter_class_and: Annotated[int, 32, {"default_value" : "4294967295"}]):
        set_meter_attrs(meter_class_or, meter_class_and)

    @staticmethod
    def tunnel_decap_pa_validate(src_vnet_id    : Annotated[int, 16, {"type" : "sai_object_id_t"}],
                                 meter_class_or : Annotated[int, 32],
                                 meter_class_and: Annotated[int, 32, {"default_value" : "4294967295"}]):
        meta.vnet_id = src_vnet_id
        set_meter_attrs(meter_class_or, meter_class_and)


    pa_validation = Table(
        key={
            "meta.vnet_id"              : (EXACT, {"type" : "sai_object_id_t"}),
            "meta.rx_encap.underlay_sip": (EXACT, {"name": "sip", "type": "sai_ip_address_t"}),
        },
        actions=[
            permit,
            (drop, {"annotations": "@defaultonly"}),
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.pa_validation",
        sai_table=SaiTable(name="pa_validation", api="dash_pa_validation",),
    )

    inbound_routing = Table(
        key={
            "meta.eni_id"               : (EXACT, {"type": "sai_object_id_t"}),
            "meta.rx_encap.vni"         : (EXACT, {"name": "VNI"}),
            "meta.rx_encap.underlay_sip": (TERNARY, {"name": "sip", "type": "sai_ip_address_t"}),
        },
        actions=[
            tunnel_decap,
            tunnel_decap_pa_validate,
            vxlan_decap,              # Deprecated, but cannot be removed until SWSS is updated.
            vxlan_decap_pa_validate,  # Deprecated, but cannot be removed until SWSS is updated.
            (drop, {"annotations": "@defaultonly"}),
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.inbound_routing",
        sai_table=SaiTable(name="inbound_routing", api="dash_inbound_routing",),
    )

    @classmethod
    def apply(cls):
        if meta.target_stage != dash_pipeline_stage_t.INBOUND_ROUTING:
            return

        py_log("info", "Applying table 'inbound_routing'")
        result = cls.inbound_routing.apply()["action_run"]
        if result == cls.tunnel_decap_pa_validate:
            py_log("info", "Applying table 'pa_validation'")
            cls.pa_validation.apply()
        elif result == drop:
            UPDATE_ENI_COUNTER("inbound_routing_entry_miss_drop")
