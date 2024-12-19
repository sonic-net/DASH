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

    meta.u0_encap_data.dash_encapsulation = encap;
    meta.u0_encap_data.vni = vni == 0 ? meta.u0_encap_data.vni : vni;

    meta.u0_encap_data.underlay_smac = underlay_smac == 0 ? meta.u0_encap_data.underlay_smac : underlay_smac;
    meta.u0_encap_data.underlay_dmac = underlay_dmac == 0 ? meta.u0_encap_data.underlay_dmac : underlay_dmac;
    meta.u0_encap_data.underlay_sip = underlay_sip == 0 ? meta.u0_encap_data.underlay_sip : underlay_sip;
    meta.u0_encap_data.underlay_dip = underlay_dip == 0 ? meta.u0_encap_data.underlay_dip : underlay_dip;
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

    meta.u1_encap_data.dash_encapsulation = encap;
    meta.u1_encap_data.vni = vni == 0 ? meta.u1_encap_data.vni : vni;

    meta.u1_encap_data.underlay_smac = underlay_smac == 0 ? meta.u1_encap_data.underlay_smac : underlay_smac;
    meta.u1_encap_data.underlay_dmac = underlay_dmac == 0 ? meta.u1_encap_data.underlay_dmac : underlay_dmac;
    meta.u1_encap_data.underlay_sip = underlay_sip == 0 ? meta.u1_encap_data.underlay_sip : underlay_sip;
    meta.u1_encap_data.underlay_dip = underlay_dip == 0 ? meta.u1_encap_data.underlay_dip : underlay_dip;
}

control do_action_encap_u0(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0 == 0) {
            return;
        }

        if (meta.u0_encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            push_vxlan_tunnel_u0(hdr,
                        meta.u0_encap_data.underlay_dmac,
                        meta.u0_encap_data.underlay_smac,
                        meta.u0_encap_data.underlay_dip,
                        meta.u0_encap_data.underlay_sip,
                        meta.u0_encap_data.vni);
        }
        else if (meta.u0_encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            push_nvgre_tunnel_u0(hdr,
                        meta.u0_encap_data.underlay_dmac,
                        meta.u0_encap_data.underlay_smac,
                        meta.u0_encap_data.underlay_dip,
                        meta.u0_encap_data.underlay_sip,
                        meta.u0_encap_data.vni);
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

        if (meta.u1_encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            push_vxlan_tunnel_u1(hdr,
                        meta.u1_encap_data.underlay_dmac,
                        meta.u1_encap_data.underlay_smac,
                        meta.u1_encap_data.underlay_dip,
                        meta.u1_encap_data.underlay_sip,
                        meta.u1_encap_data.vni);
        }
        else if (meta.u1_encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            push_nvgre_tunnel_u1(hdr,
                        meta.u1_encap_data.underlay_dmac,
                        meta.u1_encap_data.underlay_smac,
                        meta.u1_encap_data.underlay_dip,
                        meta.u1_encap_data.underlay_sip,
                        meta.u1_encap_data.vni);
        }
    }
}

#endif /* _DASH_ROUTING_ACTION_ENCAP_UNDERLAY_P4_ */
