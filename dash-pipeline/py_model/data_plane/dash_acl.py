from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.libs.__counters import *


# Store inbound/outbound ACL stage tables
ACL_STAGES = {
    "inbound": [],
    "outbound": []
}

def make_keys(stage_num: int):
    key = {
        f"meta.stage{stage_num}_dash_acl_group_id":
            (EXACT, {"name": "dash_acl_group_id", "type": "sai_object_id_t",
                    "isresourcetype": "true", "objects": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"}),
        "meta.dst_ip_addr": (LIST, {"name": "dip", "type": "sai_ip_prefix_list_t", "match_type": "list"}),
        "meta.src_ip_addr": (LIST, {"name": "sip", "type": "sai_ip_prefix_list_t", "match_type": "list"}),
        "meta.ip_protocol": (LIST, {"name": "protocol", "type": "sai_u8_list_t", "match_type": "list"}),
        "meta.src_l4_port": (RANGE_LIST, {"name": "src_port", "type": "sai_u16_range_list_t", "match_type": "range_list"}),
        "meta.dst_l4_port": (RANGE_LIST, {"name": "dst_port", "type": "sai_u16_range_list_t", "match_type": "range_list"})
    }
    return key

def make_saitable(stage_num: int):
    return SaiTable(name="dash_acl_rule", api="dash_acl",
                    stage=f"acl.stage{stage_num}",
                    order=1, isobject="true",)

class acl:
    @staticmethod
    def permit():
        pass

    @staticmethod
    def permit_and_continue():
        pass

    @staticmethod
    def deny():
        meta.dropped = True

    @staticmethod
    def deny_and_continue():
        meta.dropped = True

    # Define stage counters globally for ACL stages
    DEFINE_TABLE_COUNTER("stage1_counter", CounterType.PACKETS_AND_BYTES)
    DEFINE_TABLE_COUNTER("stage2_counter", CounterType.PACKETS_AND_BYTES)
    DEFINE_TABLE_COUNTER("stage3_counter", CounterType.PACKETS_AND_BYTES)

    # Create table placeholders for ACL stages
    stage1 = Table(key={}, actions=[], tname="inbound.acl.stage1")
    stage2 = Table(key={}, actions=[], tname="inbound.acl.stage2")
    stage3 = Table(key={}, actions=[], tname="inbound.acl.stage3")

    @classmethod
    def apply(cls, direction="inbound"):
        for stage_num, acl_table, _ in ACL_STAGES[direction]:
            group_id = getattr(meta, f"stage{stage_num}_dash_acl_group_id", None)
            if not group_id:
                continue

            py_log("info", f"Applying table '{direction}.acl.stage{stage_num}'")
            result = acl_table.apply()
            action = result.get("action_run")
            if action in (cls.deny, cls.permit):
                return


def get_acl_namespace(cls_name: str, acl_cls):
    direction = "inbound" if cls_name == "inbound" else "outbound"

    class _Namespace:
        dir = direction

        def __init__(self):
            def wrap(func, name):
                def wrapped(*args, **kwargs):
                    return func(*args, **kwargs)
                wrapped.__name__ = f"{direction}.acl.{name}"
                wrapped.__qualname__ = f"{direction}.acl.{name}"
                return staticmethod(wrapped)

            self.acl = type('acl_ns', (), {
                'permit': wrap(acl_cls.permit, "permit"),
                'permit_and_continue': wrap(acl_cls.permit_and_continue, "permit_and_continue"),
                'deny': wrap(acl_cls.deny, "deny"),
                'deny_and_continue': wrap(acl_cls.deny_and_continue, "deny_and_continue"),
            })()

        def __str__(self):
            return self.dir

    return _Namespace()

def build_acl_table(stage_num: int, ns):
    tab_name = f"{ns.dir}.acl.stage{stage_num}"

    actions = [
        ns.acl.permit,
        ns.acl.permit_and_continue,
        ns.acl.deny,
        ns.acl.deny_and_continue,
    ]

    table = Table(
        key=make_keys(stage_num),
        actions=[(func, {}) for func in actions],
        default_action=ns.acl.deny,
        tname=tab_name,
        sai_table=make_saitable(stage_num),
    )

    table.default_action = ns.acl.deny

    ATTACH_TABLE_COUNTER(f"stage{stage_num}_counter", tab_name)

    for func, _ in table.actions:
        action_objs[func.__name__] = (func, {})

    group_id = getattr(meta, f"stage{stage_num}_dash_acl_group_id")
    stage = (stage_num, table, group_id)

    return stage

def setup_acl(direction: str):
    ns = get_acl_namespace(direction, acl)
    ACL_STAGES[direction] = [build_acl_table(stage, ns) for stage in range(1, 4)]


# Build both inbound and outbound ACL stages
setup_acl("inbound")
setup_acl("outbound")
