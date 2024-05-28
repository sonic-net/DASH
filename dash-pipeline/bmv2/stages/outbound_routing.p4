#ifndef _DASH_STAGE_OUTBOUND_ROUTING_P4_
#define _DASH_STAGE_OUTBOUND_ROUTING_P4_

#include "../dash_routing_types.p4"

DEFINE_PACKET_COUNTER(outbound_routing_entry_miss_drop, MAX_ENI, attr_type="stats", action_names="set_eni_attrs", order=3)

control outbound_routing_stage(inout headers_t hdr,
                               inout metadata_t meta)
{

    action set_routing_group_attr(bit<1> admin_state) {
        meta.eni_data.routing_group_admin_state = (bool)admin_state;
    }

    @SaiTable[name = "routing_group", api = "dash_routing_group", isobject="true"]
    table routing_group {
        key = {
            meta.eni_data.routing_group_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_routing_group_attr;
            @defaultonly drop(meta);
        }
    }

    DEFINE_TABLE_COUNTER(routing_counter)

    @SaiTable[name = "outbound_routing", api = "dash_outbound_routing"]
    table routing {
        key = {
            meta.eni_data.routing_group_id : exact @SaiVal[type="sai_object_id_t"];
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
        const default_action = drop(meta);

        ATTACH_TABLE_COUNTER(routing_counter)
    }

    apply {
        if (meta.target_stage != dash_pipeline_stage_t.OUTBOUND_ROUTING) {
            return;
        }

        routing_group.apply();
        if (meta.eni_data.routing_group_admin_state) {
        routing.apply();
        } else {
            drop(meta);
        }

        if (!routing.apply().hit) {
            UPDATE_COUNTER(outbound_routing_entry_miss_drop, meta.eni_id);
        }
    }
}

#endif /* _DASH_STAGE_OUTBOUND_ROUTING_P4_ */
