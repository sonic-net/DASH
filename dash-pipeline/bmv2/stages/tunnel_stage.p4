#ifndef _DASH_STAGE_TUNNEL_P4_
#define _DASH_STAGE_TUNNEL_P4_

control tunnel_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action set_tunnel_attrs(
            @SaiVal[type="sai_ip_address_t"]
            IPv4Address dip,
            @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
            dash_encapsulation_t dash_encapsulation,
            bit<24> tunnel_key) {
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0 == 0) {
            meta.tunnel_pointer = 0;
            push_action_encap_u0(hdr = hdr,
                                 meta = meta,
                                 encap = dash_encapsulation,
                                 vni = tunnel_key,
                                 underlay_sip = hdr.customer_ipv4.src_addr,
                                 underlay_dip = dip);
        }
        else {
            meta.tunnel_pointer = 1;
            push_action_encap_u1(hdr = hdr,
                                 meta = meta,
                                 encap = dash_encapsulation,
                                 vni = tunnel_key,
                                 underlay_sip = hdr.u0_ipv4.src_addr,
                                 underlay_dip = dip);
        }
    }

    @SaiTable[name = "dash_tunnel", api = "dash_tunnel", order = 0, isobject="true"]
    table tunnel {
        key = {
            meta.dash_tunnel_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_tunnel_attrs;
        }
    }

    apply {
        if (meta.dash_tunnel_id != 0) {
            tunnel.apply();
        }
    }
}

#endif /* _DASH_STAGE_TUNNEL_P4_ */
