#ifndef _DASH_STAGE_DIRECTION_LOOKUP_P4_
#define _DASH_STAGE_DIRECTION_LOOKUP_P4_

control direction_lookup_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action set_eni_mac_type(
        dash_eni_mac_type_t eni_mac_type,
        dash_eni_mac_override_type_t eni_mac_override_type
    ) {
        meta.eni_mac_type = eni_mac_type;

        if (eni_mac_override_type == dash_eni_mac_override_type_t.SRC_MAC) {
            meta.eni_mac_type = dash_eni_mac_type_t.SRC_MAC;
        } else if (eni_mac_override_type == dash_eni_mac_override_type_t.DST_MAC) {
            meta.eni_mac_type = dash_eni_mac_type_t.DST_MAC;
        }
    }

    action set_outbound_direction(
        @SaiVal[type="sai_dash_eni_mac_override_type_t"] dash_eni_mac_override_type_t dash_eni_mac_override_type 
    ) {
        meta.direction = dash_direction_t.OUTBOUND;
        set_eni_mac_type(dash_eni_mac_type_t.SRC_MAC, dash_eni_mac_override_type);
    }

    action set_inbound_direction() {
        meta.direction = dash_direction_t.INBOUND;
        meta.eni_mac_type = dash_eni_mac_type_t.DST_MAC;
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