#ifndef _DASH_STAGE_OUTBOUND_REVERSE_reverse_routing_P4_
#define _DASH_STAGE_OUTBOUND_REVERSE_reverse_routing_P4_

control outbound_reverse_routing_stage(
    inout headers_t hdr,
    inout metadata_t meta
) {
    //
    // Reverse routing group table
    //
    action set_outbound_reverse_routing_group_attr(bit<1> disabled) {
        meta.outbound_reverse_routing_data.disabled = (bool)disabled;
    }

    @SaiTable[name = "outbound_reverse_routing_group", api = "dash_outbound_reverse_routing", order = 0, isobject="true"]
    table outbound_reverse_routing_group {
        key = {
            meta.outbound_reverse_routing_data.routing_group_id: exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_outbound_reverse_routing_group_attr;
        }
    }

    //
    // Reverse routing table
    //
    action set_outbound_reverse_routing_entry_attr(
        @SaiVal[type="sai_object_id_t"] bit<16> dash_reverse_tunnel_id,
        dash_routing_actions_t routing_actions_disabled_in_flow_resimulation
    ) {
        push_action_reverse_tunnel(hdr, meta, dash_reverse_tunnel_id);
        meta.routing_actions_disabled_in_flow_resimulation = meta.routing_actions_disabled_in_flow_resimulation | routing_actions_disabled_in_flow_resimulation;
    }

    DEFINE_TABLE_COUNTER(reverse_routing_counter)

    @SaiTable[name = "outbound_reverse_routing", api = "dash_outbound_reverse_routing", order = 1]
    table reverse_routing {
        key = {
            meta.outbound_reverse_routing_data.routing_group_id : exact @SaiVal[name="outbound_reverse_routing_group_id", type="sai_object_id_t"];
            meta.is_overlay_ip_v6 : exact @SaiVal[name = "source_is_v6"];
            meta.src_ip_addr : lpm @SaiVal[name = "source"];
        }

        actions = {
            set_outbound_reverse_routing_entry_attr;
        }

        size = 4 * 1024 * 1024;

        ATTACH_TABLE_COUNTER(reverse_routing_counter)
    }

    apply {
        // If reverse routing stage tables are not hit, we don't need to drop the packet.
        // This simply means no reverse routing is needed, and we can continue to the next stage.
        if (!outbound_reverse_routing_group.apply().hit) {
            return;
        }

        if (meta.outbound_reverse_routing_data.disabled) {
            return;
        }
        
        reverse_routing.apply();
    }
}

#endif /* _DASH_STAGE_OUTBOUND_REVERSE_reverse_routing_P4_ */
