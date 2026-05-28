from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.libs.__counters import *

class trusted_vni_stage:
    @staticmethod
    def permit():
        pass

    global_trusted_vni = Table(
        key={
            "meta.rx_encap.vni": (RANGE, {"name" : "vni_range"})
        },
        actions=[
            permit,
        ],
        tname=f"{__qualname__}.global_trusted_vni",
        sai_table=SaiTable(api="dash_trusted_vni", single_match_priority="true", order=0, isobject="false",),
    )

    # eni_trusted_vni: matches on eni_id + vni range
    eni_trusted_vni = Table(
        key={
            "meta.eni_id"       : (EXACT, {"type" : "sai_object_id_t"}),
            "meta.rx_encap.vni" : (RANGE, {"name" : "vni_range"})
        },
        actions=[
            permit,
            (deny, {"annotations": "@defaultonly"})
        ],
        const_default_action=deny,
        tname=f"{__qualname__}.eni_trusted_vni",
        sai_table=SaiTable(api="dash_trusted_vni", single_match_priority="true", order=1,),
    )

    @classmethod
    def apply(cls):
        py_log("info", "Applying table 'global_trusted_vni'")
        if cls.global_trusted_vni.apply()["hit"]:
            return

        py_log("info", "Applying table 'eni_trusted_vni'")
        if not cls.eni_trusted_vni.apply()["hit"]:
            UPDATE_ENI_COUNTER("eni_trusted_vni_entry_miss_drop")
            pass
