from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.data_plane.dash_counters import *


class eni_lookup_stage:
    @staticmethod
    def set_eni(eni_id: Annotated[int, 16, {"type" : "sai_object_id_t"}]):
        meta.eni_id = eni_id

    eni_ether_address_map = Table(
        key={
            "meta.eni_addr": (EXACT, {"name" : "address", "type" : "sai_mac_t"})
        },
        actions=[
            set_eni,
            (deny, {"annotations": "@defaultonly"})
        ],
        const_default_action=deny,
        tname=f"{__qualname__}.eni_ether_address_map",
        sai_table=SaiTable(name="eni_ether_address_map", api="dash_eni", order=0,),
    )

    @classmethod
    def apply(cls):
        # Put VM's MAC in direction agnostic metadata field
        if meta.eni_mac_type == dash_eni_mac_type_t.SRC_MAC:
            meta.eni_addr = hdr.customer_ethernet.src_addr
        else:
            meta.eni_addr = hdr.customer_ethernet.dst_addr

        py_log("info", "Applying table 'eni_ether_address_map' ")
        if not cls.eni_ether_address_map.apply()["hit"]:
            UPDATE_COUNTER("eni_miss_drop", 0)
            if meta.is_fast_path_icmp_flow_redirection_packet:
                UPDATE_COUNTER("port_lb_fast_path_eni_miss_drop", 0)
                pass
