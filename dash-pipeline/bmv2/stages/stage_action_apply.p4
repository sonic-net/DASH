#ifndef _DASH_ACTION_APPLY_P4_
#define _DASH_ACTION_APPLY_P4_

#include "../routing_actions/routing_actions.p4"

control action_apply(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        do_action_static_encap.apply(hdr, meta);
        do_action_nat46.apply(hdr, meta);
        do_action_nat64.apply(hdr, meta);
    }
}

#endif /* _DASH_ACTION_APPLY_P4_ */