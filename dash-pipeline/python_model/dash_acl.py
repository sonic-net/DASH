from __table import *

def set_acl_outcome(allow: Annotated[int, 1], terminate: Annotated[int, 1]):
    meta.acl_outcome_allow = allow
    meta.acl_outcome_terminate = terminate

acl = Table(
    key = {
        "meta.acl_group_id" : EXACT,
        "meta.dst_tag_map"  : TERNARY,
        "meta.src_tag_map"  : TERNARY,
        "meta.src_ip_addr"  : TERNARY_LIST,
        "meta.dst_ip_addr"  : TERNARY_LIST,
        "meta.ip_protocol"  : TERNARY_LIST,
        "meta.src_l4_port"  : RANGE_LIST,
        "meta.dst_l4_port"  : RANGE_LIST
    },
    actions = [
        set_acl_outcome
    ]
)

def acl_apply():
    group_ids = [
        meta.stage1_dash_acl_group_id,
        meta.stage2_dash_acl_group_id,
        meta.stage3_dash_acl_group_id,
        meta.stage4_dash_acl_group_id,
        meta.stage5_dash_acl_group_id
    ]

    meta.acl_outcome_allow = False
    for group_id in group_ids:
        if group_id != 0:
            meta.acl_group_id = group_id
            acl.apply()
            if meta.acl_outcome_terminate:
                break

    if not meta.acl_outcome_allow:
        meta.dropped = True
