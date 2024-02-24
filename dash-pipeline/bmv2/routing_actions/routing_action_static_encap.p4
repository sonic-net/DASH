#ifndef _DASH_ROUTING_ACTION_STATIC_ENCAP_P4_
#define _DASH_ROUTING_ACTION_STATIC_ENCAP_P4_

action set_action_static_encap(
    in headers_t hdr,
    inout metadata_t meta,
    in dash_encapsulation_t encap = dash_encapsulation_t.VXLAN,
    in bit<24> vni = 0,
    in IPv4Address underlay_sip = 0,
    in IPv4Address underlay_dip = 0,
    in EthernetAddress underlay_smac = 0,
    in EthernetAddress underlay_dmac = 0,
    in EthernetAddress overlay_dmac = 0)
{
    meta.pending_actions = meta.pending_actions | dash_routing_actions_t.STATIC_ENCAP;

    meta.encap_data.dash_encapsulation = encap;
    meta.encap_data.vni = vni == 0 ? meta.encap_data.vni : vni;

    meta.encap_data.underlay_smac = underlay_smac == 0 ? meta.encap_data.underlay_smac : underlay_smac;
    meta.encap_data.underlay_dmac = underlay_dmac == 0 ? meta.encap_data.underlay_dmac : underlay_dmac;
    meta.encap_data.underlay_sip = underlay_sip == 0 ? meta.encap_data.underlay_sip : underlay_sip;
    meta.encap_data.underlay_dip = underlay_dip == 0 ? meta.encap_data.underlay_dip : underlay_dip;
    
    meta.overlay_data.dmac = overlay_dmac == 0 ? meta.overlay_data.dmac : overlay_dmac;
}

control do_action_static_encap(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.pending_actions & dash_routing_actions_t.STATIC_ENCAP == 0) {
            return;
        }
        
        if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            if (meta.tunnel_pointer == 0) {
                push_vxlan_tunnel_u0(hdr,
                            meta.overlay_data.dmac,
                            meta.encap_data.underlay_dmac,
                            meta.encap_data.underlay_smac,
                            meta.encap_data.underlay_dip,
                            meta.encap_data.underlay_sip,
                            meta.encap_data.vni);
            } else if (meta.tunnel_pointer == 1) {
                push_vxlan_tunnel_u1(hdr,
                            meta.overlay_data.dmac,
                            meta.encap_data.underlay_dmac,
                            meta.encap_data.underlay_smac,
                            meta.encap_data.underlay_dip,
                            meta.encap_data.underlay_sip,
                            meta.encap_data.vni);
            }
        }
        else if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            if (meta.tunnel_pointer == 0) {
                push_vxlan_tunnel_u0(hdr,
                            meta.overlay_data.dmac,
                            meta.encap_data.underlay_dmac,
                            meta.encap_data.underlay_smac,
                            meta.encap_data.underlay_dip,
                            meta.encap_data.underlay_sip,
                            meta.encap_data.vni);
            } else if (meta.tunnel_pointer == 1) {
                push_vxlan_tunnel_u1(hdr,
                            meta.overlay_data.dmac,
                            meta.encap_data.underlay_dmac,
                            meta.encap_data.underlay_smac,
                            meta.encap_data.underlay_dip,
                            meta.encap_data.underlay_sip,
                            meta.encap_data.vni);
            }
        }
    
        meta.tunnel_pointer = meta.tunnel_pointer + 1;
    }
}

#endif /* _DASH_ROUTING_ACTION_STATIC_ENCAP_P4_ */