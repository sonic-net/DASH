#ifndef _DASH_ROUTING_ACTION_ENCAP_UNDERLAY_P4_
#define _DASH_ROUTING_ACTION_ENCAP_UNDERLAY_P4_

action push_action_encap_u0(
    in headers_t hdr,
    inout metadata_t meta,
    in dash_encapsulation_t encap = dash_encapsulation_t.VXLAN,
    in bit<24> vni = 0,
    in IPv4Address underlay_sip = 0,
    in IPv4Address underlay_dip = 0,
    in EthernetAddress underlay_smac = 0,
    in EthernetAddress underlay_dmac = 0)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.ENCAP_U0;

    meta.encap_data.dash_encapsulation = encap;
    meta.encap_data.vni = vni == 0 ? meta.encap_data.vni : vni;

    meta.encap_data.underlay_smac = underlay_smac == 0 ? meta.encap_data.underlay_smac : underlay_smac;
    meta.encap_data.underlay_dmac = underlay_dmac == 0 ? meta.encap_data.underlay_dmac : underlay_dmac;
    meta.encap_data.underlay_sip = underlay_sip == 0 ? meta.encap_data.underlay_sip : underlay_sip;
    meta.encap_data.underlay_dip = underlay_dip == 0 ? meta.encap_data.underlay_dip : underlay_dip;
}

action push_action_encap_u1(
    in headers_t hdr,
    inout metadata_t meta,
    in dash_encapsulation_t encap = dash_encapsulation_t.VXLAN,
    in bit<24> vni = 0,
    in IPv4Address underlay_sip = 0,
    in IPv4Address underlay_dip = 0,
    in EthernetAddress underlay_smac = 0,
    in EthernetAddress underlay_dmac = 0)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.ENCAP_U1;

    meta.tunnel_data.dash_encapsulation = encap;
    meta.tunnel_data.vni = vni == 0 ? meta.tunnel_data.vni : vni;

    meta.tunnel_data.underlay_smac = underlay_smac == 0 ? meta.tunnel_data.underlay_smac : underlay_smac;
    meta.tunnel_data.underlay_dmac = underlay_dmac == 0 ? meta.tunnel_data.underlay_dmac : underlay_dmac;
    meta.tunnel_data.underlay_sip = underlay_sip == 0 ? meta.tunnel_data.underlay_sip : underlay_sip;
    meta.tunnel_data.underlay_dip = underlay_dip == 0 ? meta.tunnel_data.underlay_dip : underlay_dip;
}

control do_action_encap_u0(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0 == 0) {
            return;
        }

        if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            push_vxlan_tunnel_u0(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);
        }
        else if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            push_vxlan_tunnel_u0(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);
        }
    }
}

control do_action_encap_u1(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U1 == 0) {
            return;
        }

        if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);
        }
        else if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);
        }
    }
}

#endif /* _DASH_ROUTING_ACTION_ENCAP_UNDERLAY_P4_ */
