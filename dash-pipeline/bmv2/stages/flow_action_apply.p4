#ifndef _DASH_STAGE_FLOW_ACTION_APPLY_P4_
#define _DASH_STAGE_FLOW_ACTION_APPLY_P4_

#include "../flow_actions/flow_actions.p4"

control  flow_action_apply(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        do_action_encap.apply(hdr, meta);
        do_action_overlay_rewrite.apply(hdr, meta);
    }
}

#endif /* _DASH_STAGE_ACTION_APPLY_P4_ */