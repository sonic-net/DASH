#ifndef _DASH_FLOW_ACTION_ENCAP_P4_
#define _DASH_FLOW_ACTION_ENCAP_P4_

control do_action_encap(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.conntrack_data.flow_data.actions & dash_flow_action_t.ENCAP == 0) {
            return;
        }
        
        if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
            push_vxlan_tunnel_u0(hdr,
                        meta.overlay_data.dmac,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);
            
            meta.tunnel_pointer = meta.tunnel_pointer + 1;

            if (meta.tunnel_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
                push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.tunnel_data.underlay_dmac,
                        meta.tunnel_data.underlay_smac,
                        meta.tunnel_data.underlay_dip,
                        meta.tunnel_data.underlay_sip,
                        meta.tunnel_data.vni);
                meta.tunnel_pointer = meta.tunnel_pointer + 1;
            }
            else if (meta.tunnel_data.dash_encapsulation == dash_encapsulation_t.NVGRE){
                push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.tunnel_data.underlay_dmac,
                        meta.tunnel_data.underlay_smac,
                        meta.tunnel_data.underlay_dip,
                        meta.tunnel_data.underlay_sip,
                        meta.tunnel_data.vni);
                meta.tunnel_pointer = meta.tunnel_pointer + 1;
            }
        }
        else if (meta.encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE) {
            push_vxlan_tunnel_u0(hdr,
                        meta.overlay_data.dmac,
                        meta.encap_data.underlay_dmac,
                        meta.encap_data.underlay_smac,
                        meta.encap_data.underlay_dip,
                        meta.encap_data.underlay_sip,
                        meta.encap_data.vni);

            meta.tunnel_pointer = meta.tunnel_pointer + 1;

            if (meta.tunnel_data.dash_encapsulation == dash_encapsulation_t.VXLAN) {
                push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.tunnel_data.underlay_dmac,
                        meta.tunnel_data.underlay_smac,
                        meta.tunnel_data.underlay_dip,
                        meta.tunnel_data.underlay_sip,
                        meta.tunnel_data.vni);
                meta.tunnel_pointer = meta.tunnel_pointer + 1;
            }
            else if (meta.tunnel_data.dash_encapsulation == dash_encapsulation_t.NVGRE){
                push_vxlan_tunnel_u1(hdr,
                        meta.encap_data.underlay_dmac,
                        meta.tunnel_data.underlay_dmac,
                        meta.tunnel_data.underlay_smac,
                        meta.tunnel_data.underlay_dip,
                        meta.tunnel_data.underlay_sip,
                        meta.tunnel_data.vni);
                meta.tunnel_pointer = meta.tunnel_pointer + 1;
            }
        }

        meta.tunnel_pointer = meta.tunnel_pointer + 1;
    }
}


#endif /* _DASH_FLOW_ACTION_ENCAP_P4_ */
