#ifndef _DASH_STAGE_DIRECTION_LOOKUP_P4_
#define _DASH_STAGE_DIRECTION_LOOKUP_P4_

control direction_lookup_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action set_outbound_direction() {
        meta.direction = dash_direction_t.OUTBOUND;
    }

    action set_inbound_direction() {
        meta.direction = dash_direction_t.INBOUND;
    }

    @SaiTable[name = "direction_lookup", api = "dash_direction_lookup"]
    table direction_lookup {
        key = {
            hdr.u0_vxlan.vni : exact @SaiVal[name = "VNI"];
        }

        actions = {
            set_outbound_direction;
            @defaultonly set_inbound_direction;
        }

        const default_action = set_inbound_direction;
    }

    apply {
        /* If Outer VNI matches with a reserved VNI, then the direction is Outbound - */
        direction_lookup.apply();
    }
}

#endif /* _DASH_STAGE_DIRECTION_LOOKUP_P4_ */