from __table import *
from __sai_keys import *

def permit():
    meta.acl_outcome_allow = 1
    meta.acl_outcome_terminate = 1

def permit_and_continue():
    meta.acl_outcome_allow = 1
    meta.acl_outcome_terminate = 0

def deny():
    meta.acl_outcome_allow = 0
    meta.acl_outcome_terminate = 1

def deny_and_continue():
    meta.acl_outcome_allow = 0
    meta.acl_outcome_terminate = 0

dash_acl_rule = Table(
    key = {
        "meta.dash_acl_group_id": (EXACT,       {TYPE : "sai_object_id_t", ISRESOURCETYPE : "true", OBJECTS : "SAI_OBJECT_TYPE_DASH_ACL_GROUP"}),
        "meta.dst_ip_addr"      : (LIST,        {SAI_KEY_NAME : "dip"}),
        "meta.src_ip_addr"      : (LIST,        {SAI_KEY_NAME : "sip"}),
        "meta.ip_protocol"      : (LIST,        {SAI_KEY_NAME : "protocol"}),
        "meta.src_l4_port"      : (RANGE_LIST,  {SAI_KEY_NAME : "src_port"}),
        "meta.dst_l4_port"      : (RANGE_LIST,  {SAI_KEY_NAME : "dst_port"})
    },
    actions = [
        permit,
        permit_and_continue,
        deny,
        deny_and_continue
    ],
    default_action = deny,
    per_entry_stats = True,
    api_name="dash_acl"
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
            meta.dash_acl_group_id = group_id
            dash_acl_rule.apply()
            if meta.acl_outcome_terminate:
                break

    if not meta.acl_outcome_allow:
        meta.dropped = True
