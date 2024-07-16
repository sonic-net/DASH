#ifndef _DASH_ROUTING_ACTION_REVERSE_TUNNEL_P4_
#define _DASH_ROUTING_ACTION_REVERSE_TUNNEL_P4_

action push_action_reverse_tunnel(
    in headers_t hdr,
    inout metadata_t meta,
    in bit<16> dash_reverse_tunnel_id)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.REVERSE_TUNNEL;

    meta.dash_reverse_tunnel_id = dash_reverse_tunnel_id;
}

control do_action_reverse_tunnel(
    inout headers_t hdr,
    inout metadata_t meta)
{
    //
    // Reverse Tunnel
    //
    action set_reverse_tunnel_attrs(
        @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"] dash_encapsulation_t dash_encapsulation,
        bit<24> tunnel_key
    ) {
        meta.reverse_tunnel_data.dash_encapsulation = dash_encapsulation;
        meta.reverse_tunnel_data.vni = tunnel_key;
    }

    @SaiTable[name = "dash_reverse_tunnel", api = "dash_reverse_tunnel", order = 0, isobject="true"]
    table reverse_tunnel {
        key = {
            meta.dash_reverse_tunnel_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_reverse_tunnel_attrs;
        }
    }

    //
    // Reverse tunnel member
    //
    action set_reverse_tunnel_member_attrs(
        @SaiVal[type="sai_object_id_t"] bit<16> dash_reverse_tunnel_next_hop_id
    ) {
        meta.dash_reverse_tunnel_next_hop_id = dash_reverse_tunnel_next_hop_id;
    }

    @SaiTable[name = "dash_reverse_tunnel", api = "dash_reverse_tunnel", order = 1, isobject="true"]
    table reverse_tunnel_member {
        key = {
            meta.dash_reverse_tunnel_id : exact @SaiVal[type="sai_object_id_t"];
            meta.dash_reverse_tunnel_member_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_reverse_tunnel_member_attrs;
        }
    }

    //
    // Reverse tunnel next hop
    //
    action set_reverse_tunnel_next_hop_attrs(
        @SaiVal[type="sai_ip_address_t"] IPv4Address dip,
        @SaiVal[type="sai_ip_address_t"] IPv4Address sip
    ) {
        meta.reverse_tunnel_data.underlay_dip = dip;
        meta.reverse_tunnel_data.underlay_sip = sip;
    }

    @SaiTable[name = "dash_reverse_tunnel", api = "dash_reverse_tunnel", order = 2, isobject="true"]
    table reverse_tunnel_next_hop {
        key = {
            meta.dash_reverse_tunnel_next_hop_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_reverse_tunnel_next_hop_attrs;
        }
    }

    apply {
        if (meta.routing_actions & dash_routing_actions_t.REVERSE_TUNNEL == 0) {
            return;
        }
    
        if (!reverse_tunnel.apply().hit) {
            UPDATE_ENI_COUNTER(reverse_tunnel_miss_drop);
            return;
        }

        meta.dash_reverse_tunnel_member_id = 0; // TODO: ECMP group selection!

        if (!reverse_tunnel_member.apply().hit) {
            UPDATE_ENI_COUNTER(reverse_tunnel_member_miss_drop);
            return;
        }
    
        if (!reverse_tunnel_next_hop.apply().hit) {
            UPDATE_ENI_COUNTER(reverse_tunnel_next_hop_miss_drop);
            return;
        }
    }
}

#endif /* _DASH_ROUTING_ACTION_REVERSE_TUNNEL_P4_ */
