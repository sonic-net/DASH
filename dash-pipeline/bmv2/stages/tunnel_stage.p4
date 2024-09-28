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
        bit<24> tunnel_key)
    {
        push_action_static_encap(hdr = hdr,
                                 meta = meta,
                                 encap = dash_encapsulation,
                                 vni = tunnel_key,
                                 underlay_sip = hdr.u0_ipv4.src_addr,
                                 underlay_dip = dip,
                                 overlay_dmac = hdr.u0_ethernet.dst_addr);
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

    action select_tunnel_member(
        bit<16> dash_tunnel_member_id)
    {
        meta.dash_tunnel_member_id = dash_tunnel_member_id;
    }

    // This table is a helper table that used to select the tunnel member based on the index.
    // The entry of this table is created by DASH data plane app, when the tunnel member is created.
    @SaiTable[ignored = "true"]
    table tunnel_member_select {
        key = {
            meta.dash_tunnel_member_index : exact @SaiVal[type="sai_object_id_t", is_object_key="true"];
            meta.dash_tunnel_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            select_tunnel_member;
        }
    }

    action set_tunnel_member_attrs(
        @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_id,
        @SaiVal[type="sai_object_id_t"] bit<16> dash_tunnel_next_hop_id)
    {
        // dash_tunnel_id in tunnel member must match the metadata
        assert(meta.dash_tunnel_id == dash_tunnel_id);

        meta.dash_tunnel_next_hop_id = dash_tunnel_next_hop_id;
    }

    @SaiTable[name = "dash_tunnel_member", api = "dash_tunnel", order = 1, isobject="true"]
    table tunnel_member {
        key = {
            meta.dash_tunnel_member_id : exact @SaiVal[type="sai_object_id_t", is_object_key="true"];
        }

        actions = {
            set_tunnel_member_attrs;
        }
    }

    action set_tunnel_next_hop_attrs(
        @SaiVal[type="sai_ip_address_t"]
        IPv4Address dip,
        @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
        dash_encapsulation_t dash_encapsulation,
        bit<24> tunnel_key)
    {
        push_action_static_encap(hdr = hdr,
                                 meta = meta,
                                 encap = dash_encapsulation,
                                 vni = tunnel_key,
                                 underlay_sip = hdr.u0_ipv4.src_addr,
                                 underlay_dip = dip,
                                 overlay_dmac = hdr.u0_ethernet.dst_addr);
    }

    @SaiTable[name = "dash_tunnel_next_hop", api = "dash_tunnel", order = 2, isobject="true"]
    table tunnel_next_hop{
        key = {
            meta.dash_tunnel_next_hop_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_tunnel_next_hop_attrs;
        }
    }

    apply {
        tunnel.apply();

        // TODO: Calculate based on packet and tunnel member size.
        // Currently, we will have to use 0 here, because we don't know how many tunnel members we will have.
        meta.dash_tunnel_member_index = 0;
        tunnel_member_select.apply();

        tunnel_member.apply();
        tunnel_next_hop.apply();
    }
}

control tunnel_stage_encap(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.dash_tunnel_id != 0) {
                do_tunnel_encap(hdr, meta,
                            meta.overlay_data.dmac,
                            meta.tunnel_data.underlay_dmac,
                            meta.tunnel_data.underlay_smac,
                            meta.tunnel_data.underlay_dip,
                            meta.tunnel_data.underlay_sip,
                            meta.tunnel_data.dash_encapsulation,
                            meta.tunnel_data.vni);
        }
    }
}

#endif /* _DASH_STAGE_TUNNEL_P4_ */
