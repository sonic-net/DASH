from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.data_plane.dash_counters import *

class metering_update_stage:
    # Validate IP address family against overlay IP version
    @staticmethod
    def check_ip_addr_family(ip_addr_family: Annotated[int, 32, {"type" : "sai_ip_addr_family_t", "isresourcetype" : "true"}]):
        if ip_addr_family == 0:  # SAI_IP_ADDR_FAMILY_IPV4
            if meta.is_overlay_ip_v6 == 1:
                meta.dropped = True
        else:
            if meta.is_overlay_ip_v6 == 0:
                meta.dropped = True

    # Assign meter class from policy
    @staticmethod
    def set_policy_meter_class(meter_class: Annotated[int, 32]):
        meta.meter_class = meter_class

    # MAX_METER_BUCKET = MAX_ENI(64) * NUM_BUCKETS_PER_ENI(4096)
    MAX_METER_BUCKETS = 262144
    DEFINE_BYTE_COUNTER("meter_bucket_outbound", MAX_METER_BUCKETS, name="outbound", action_names="update_meter_bucket", attr_type="stats")
    DEFINE_BYTE_COUNTER("meter_bucket_inbound", MAX_METER_BUCKETS, name="inbound", action_names="update_meter_bucket", attr_type="stats")

    @staticmethod
    def update_meter_bucket():
        pass

    meter_policy = Table(
        key = {
            "meta.meter_context.meter_policy_id": EXACT
        },
        actions = [
            check_ip_addr_family
        ],
        tname=f"{__qualname__}.meter_policy",
        sai_table = SaiTable(name="meter_policy", api="dash_meter", order=1, isobject="true")
    )

    meter_rule = Table(
        key = {
            "meta.meter_context.meter_policy_id": (EXACT, {"type" : "sai_object_id_t", "isresourcetype" : "true", "objects" : "METER_POLICY"}),
            "meta.meter_context.meter_policy_lookup_ip": (TERNARY, {"name" : "dip", "type" : "sai_ip_address_t"})
        },
        actions = [
            set_policy_meter_class,
            (NoAction, {"annotations": "@defaultonly"})
        ],
        const_default_action = NoAction,
        tname=f"{__qualname__}.meter_rule",
        sai_table = SaiTable(name="meter_rule", api="dash_meter", order=2, isobject="true")
    )

    meter_bucket = Table(
        key = {
            "meta.eni_id"       : (EXACT, {"type" : "sai_object_id_t"}),
            "meta.meter_class"  : EXACT
        },
        actions = [
            update_meter_bucket,
            (NoAction, {"annotations": "@defaultonly"})
        ],
        const_default_action = NoAction,
        tname=f"{__qualname__}.meter_bucket",
        sai_table = SaiTable(name="meter_bucket", api="dash_meter", order=0)
    )

    DEFINE_TABLE_COUNTER("eni_counter")

    eni_meter = Table(
        key = {
            "meta.eni_id"   : (EXACT, {"type" : "sai_object_id_t"}),
            "meta.direction": EXACT,
            "meta.dropped"  : EXACT
        },
        actions = [
            NoAction
        ],
        tname=f"{__qualname__}.eni_meter",
        sai_table = SaiTable(ignored = "true")
    )
    ATTACH_TABLE_COUNTER("eni_counter", "eni_meter")

    @classmethod
    def apply(cls):
        meta.meter_class = meta.meter_context.meter_class_or & meta.meter_context.meter_class_and

        # If the meter class is 0 from the SDN policies, we go through the metering policy.
        if meta.meter_class == 0:
            py_log("info", "Applying table 'meter_policy'")
            cls.meter_policy.apply()
            py_log("info", "Applying table 'meter_rule'")
            cls.meter_rule.apply()

        py_log("info", "Applying table 'meter_bucket'")
        cls.meter_bucket.apply()

        if meta.meter_class != 0:
            if meta.direction == dash_direction_t.OUTBOUND:
                UPDATE_COUNTER("meter_bucket_outbound", meta.meter_class)
            elif meta.direction == dash_direction_t.INBOUND:
                UPDATE_COUNTER("meter_bucket_inbound", meta.meter_class)

        py_log("info", "Applying table 'eni_meter'")
        cls.eni_meter.apply()
