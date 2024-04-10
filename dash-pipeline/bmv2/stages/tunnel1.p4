#ifndef _DASH_STAGE_TUNNEL1_P4_
#define _DASH_STAGE_TUNNEL1_P4_

control tunnel1_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action set_tunnel1_attrs(
            @SaiVal[type="sai_ip_address_t"]
            IPv4Address underlay_dip,
            @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
            dash_encapsulation_t dash_encapsulation,
            bit<24> tunnel_key) {
    push_action_static_encap(hdr = hdr,
                            meta = meta,
                            encap = dash_encapsulation,
                            vni = tunnel_key,
                            underlay_sip = hdr.u0_ipv4.src_addr,
                            underlay_dip = underlay_dip,
                            overlay_dmac = hdr.u0_ethernet.dst_addr);
    }

    @SaiTable[name = "tunnel1", api = "dash_tunnel", order = 0, isobject="true"]
    table tunnel1 {
        key = {
            meta.tunnel1_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_tunnel1_attrs;
        }
    }

    apply {
        if (tunnel1.apply().hit) {
            do_action_static_encap.apply(hdr, meta);
        }
    }
}

#endif /* _DASH_STAGE_TUNNEL1_P4_ */
