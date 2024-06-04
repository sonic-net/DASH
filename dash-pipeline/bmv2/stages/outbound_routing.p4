#ifndef _DASH_STAGE_OUTBOUND_ROUTING_P4_
#define _DASH_STAGE_OUTBOUND_ROUTING_P4_

#include "../dash_routing_types.p4"

control outbound_routing_stage(inout headers_t hdr,
                               inout metadata_t meta)
{
    DEFINE_TABLE_COUNTER(routing_counter)

    @SaiTable[name = "outbound_routing", api = "dash_outbound_routing"]
    table routing {
        key = {
            meta.eni_id : exact @SaiVal[type="sai_object_id_t"];
            meta.is_overlay_ip_v6 : exact @SaiVal[name = "destination_is_v6"];
            meta.dst_ip_addr : lpm @SaiVal[name = "destination"];
        }

        actions = {
            route_vnet(hdr, meta); /* for expressroute - ecmp of overlay */
            route_vnet_direct(hdr, meta);
            route_direct(hdr, meta);
            route_service_tunnel(hdr, meta);
            drop(meta);
        }
        size = 4194304;
        const default_action = drop(meta);

        ATTACH_TABLE_COUNTER(routing_counter)
    }

    apply {
        if (meta.target_stage != dash_pipeline_stage_t.OUTBOUND_ROUTING) {
            return;
        }

        if (!routing.apply().hit) {
            UPDATE_ENI_COUNTER(outbound_routing_entry_miss_drop);
        }
    }
}

#endif /* _DASH_STAGE_OUTBOUND_ROUTING_P4_ */