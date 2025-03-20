#ifndef _DASH_STAGE_OUTBOUND_PRE_ROUTING_ACTION_APPLY_P4_
#define _DASH_STAGE_OUTBOUND_PRE_ROUTING_ACTION_APPLY_P4_

#include "tunnel_stage.p4"

#include "outbound_port_map.p4"

control outbound_pre_routing_action_apply_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        // Outbound pre-routing action apply stage is added here for certain pre processing before applying the final actions.
        if (meta.target_stage != dash_pipeline_stage_t.OUTBOUND_PRE_ROUTING_ACTION_APPLY) {
            return;
        }

        outbound_port_map_stage.apply(hdr, meta);

        tunnel_stage.apply(hdr, meta);

        // Once it is done, move to routing action apply stage.
        meta.target_stage = dash_pipeline_stage_t.ROUTING_ACTION_APPLY;
    }
}

#endif /* _DASH_STAGE_OUTBOUND_PRE_ROUTING_ACTION_APPLY_P4_ */
