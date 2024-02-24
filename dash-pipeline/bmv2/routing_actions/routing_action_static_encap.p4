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

#ifndef DISABLE_128BIT_ARITHMETIC
    // As of 2024-Feb-09, p4c-dpdk does not yet support arithmetic
    // on 128-bit operands.  This lack of support extends to cast
    // operations.
    meta.encap_data.underlay_sip = underlay_sip == 0 ? hdr.u0_ipv4.src_addr : underlay_sip;
    meta.encap_data.underlay_dip = underlay_dip == 0 ? hdr.u0_ipv4.dst_addr : underlay_dip;
#endif

    meta.encap_data.underlay_smac = underlay_smac == 0 ? meta.encap_data.underlay_smac : underlay_smac;
    meta.encap_data.underlay_dmac = underlay_dmac == 0 ? meta.encap_data.underlay_dmac : underlay_dmac;
    
    meta.encap_data.overlay_dmac = overlay_dmac == 0 ? meta.encap_data.overlay_dmac : overlay_dmac;
}

action do_action_static_encap(
    inout headers_t hdr,
    in metadata_t meta)
{
}

#endif /* _DASH_ROUTING_ACTION_STATIC_ENCAP_P4_ */