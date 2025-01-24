#ifndef _DASH_STAGE_PORT_MAP_P4_
#define _DASH_STAGE_PORT_MAP_P4_

#include "../dash_routing_types.p4"

control outbound_port_map_stage(inout headers_t hdr,
                                    inout metadata_t meta)
{
    action set_port_map_attr() {}

    DEFINE_TABLE_COUNTER(outbound_port_map_counter)

    @SaiTable[api = "dash_outbound_port_map", order = 0, isobject="true"]
    table outbound_port_map {
        key = {
            meta.port_map_ctx.map_id: exact @SaiVal[name = "outbound_port_map_id", type = "sai_object_id_t"];
        }

        actions = {
            set_port_map_attr;
            @defaultonly drop(meta);
        }
        const default_action = drop(meta);

        ATTACH_TABLE_COUNTER(outbound_port_map_counter)
    }

    action skip_mapping() {}

    action map_to_private_link_service(
        @SaiVal[type="sai_ip_address_t"] IPv4Address backend_ip,
        bit<16> match_port_base,
        bit<16> backend_port_base)
    {
        REQUIRES((meta.routing_actions & dash_routing_actions_t.NAT46) != 0);

        // For private link, once the service is redirected, we need to update 2 things:
        // 1. The underlay IP to point to the new backend IP in order to route the packet there.
        // 2. The overlay IP and port to the new backend ip and port, so that the overlay packet will
        //    look like being sent from the new backend IP.
        
        // Update underlay
        meta.u0_encap_data.underlay_dip = backend_ip;

#ifndef DISABLE_128BIT_ARITHMETIC
        // Update overlay IP
        meta.overlay_data.dip = (meta.overlay_data.dip & ~((bit<128>)0xFFFFFFFF)) | (bit<128>)backend_ip;
#endif

        // Update overlay port
        push_action_dnat_port(
            hdr,
            meta,
            meta.dst_l4_port - match_port_base + backend_port_base);
    }

    DEFINE_TABLE_COUNTER(outbound_port_map_port_range_counter)

    @SaiTable[api = "dash_outbound_port_map", order = 1]
    table outbound_port_map_port_range {
        key = {
            meta.port_map_ctx.map_id: exact @SaiVal[name = "outbound_port_map_id", type = "sai_object_id_t"];
            meta.dst_l4_port: range @SaiVal[name = "dst_port_range"];
        }

        actions = {
            skip_mapping;
            map_to_private_link_service;
        }

        ATTACH_TABLE_COUNTER(outbound_port_map_port_range_counter)
    }

    apply {
        if (meta.port_map_ctx.map_id == 0) {
            return;
        }

        outbound_port_map.apply();
        outbound_port_map_port_range.apply();
    }
}

#endif /* _DASH_STAGE_PORT_MAP_P4_ */
