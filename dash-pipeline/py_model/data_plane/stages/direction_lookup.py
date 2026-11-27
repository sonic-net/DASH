from py_model.libs.__utils import *
from py_model.libs.__table import *

class direction_lookup_stage:
    @staticmethod
    def set_eni_mac_type(eni_mac_type: dash_eni_mac_type_t,
                         eni_mac_override_type: dash_eni_mac_override_type_t):
        meta.eni_mac_type = eni_mac_type

        if eni_mac_override_type == dash_eni_mac_override_type_t.SRC_MAC:
            meta.eni_mac_type = dash_eni_mac_type_t.SRC_MAC
        elif eni_mac_override_type == dash_eni_mac_override_type_t.DST_MAC:
            meta.eni_mac_type = dash_eni_mac_type_t.DST_MAC

    @staticmethod
    def set_outbound_direction(dash_eni_mac_override_type: Annotated[dash_eni_mac_override_type_t,
                                                           {"type" : "sai_dash_eni_mac_override_type_t"}]):
        meta.direction = dash_direction_t.OUTBOUND
        direction_lookup_stage.set_eni_mac_type(dash_eni_mac_type_t.SRC_MAC,
                                                dash_eni_mac_override_type)

    @staticmethod
    def set_inbound_direction( dash_eni_mac_override_type: Annotated[dash_eni_mac_override_type_t,
                                                                     {"type" : "sai_dash_eni_mac_override_type_t"}]
                                                                     = dash_eni_mac_override_type_t.NONE):
        meta.direction = dash_direction_t.INBOUND
        direction_lookup_stage.set_eni_mac_type(dash_eni_mac_type_t.DST_MAC,
                                                dash_eni_mac_override_type)

    direction_lookup = Table(
        key={
            "meta.rx_encap.vni": (EXACT, {"name" : "VNI"})
        },
        actions=[
            set_outbound_direction,
            set_inbound_direction,
        ],
        const_default_action=set_inbound_direction,
        tname=f"{__qualname__}.direction_lookup",
        sai_table=SaiTable(name="direction_lookup", api="dash_direction_lookup",),
    )

    @classmethod
    def apply(cls):
        # If Outer VNI matches with a reserved VNI, then the direction is Outbound
        py_log("info", "Applying table 'direction_lookup'")
        cls.direction_lookup.apply()