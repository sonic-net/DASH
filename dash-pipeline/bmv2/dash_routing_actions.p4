#ifndef _DASH_ROUTING_ACTIONS_P4_
#define _DASH_ROUTING_ACTIONS_P4_

#include "routing_actions/routing_action_static_encap.p4"
#include "routing_actions/routing_action_nat46.p4"
#include "routing_actions/routing_action_nat64.p4"

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

#endif /* _DASH_ROUTING_ACTIONS_P4_ */