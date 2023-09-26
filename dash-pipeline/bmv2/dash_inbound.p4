#ifndef _SIRIUS_INBOUND_P4_
#define _SIRIUS_INBOUND_P4_

#include "dash_headers.p4"
#include "dash_service_tunnel.p4"
#include "dash_vxlan.p4"
#include "dash_acl.p4"
#include "dash_conntrack.p4"

control inbound(inout headers_t hdr,
                inout metadata_t meta)
{
    action msee_ecmp(tuple<IPv4, MAC>) {
        meta.encap_data.underlay_dip = ip[i];
        meta.encap_data.underlay_dmac = mac[i];
    }

    @name("msee|dash_msee")
    table msee {
        key = {
            meta.eni_id : exact @name("meta.eni_id:eni_id");
        }

        actions = {
            msee_ecmp;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    apply {
#ifdef STATEFUL_P4
            ConntrackIn.apply(0);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);

        if (meta.flag_mvp == 1) {
            meta.encap_data.original_overlay_sip = 0; //FIXME: ER gateway private ip?
            meta.encap_data.original_overlay_dip = (IPv4Address)hdr.ipv6.dst_addr;
            service_tunnel_decode(hdr,
                                  meta.encap_data.original_overlay_sip,
                                  meta.encap_data.original_overlay_dip);
            msee.apply();
        }
#endif // PNA_CONNTRACK

        /* ACL */
        if (!meta.conntrack_data.allow_in) {
            acl.apply(hdr, meta);
        }

#ifdef STATEFUL_P4
            ConntrackOut.apply(1);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
        ConntrackOut.apply(hdr, meta);
#endif //PNA_CONNTRACK

        vxlan_encap(hdr,
                    meta.encap_data.underlay_dmac,
                    meta.encap_data.underlay_smac,
                    meta.encap_data.underlay_dip,
                    meta.encap_data.underlay_sip,
                    hdr.ethernet.dst_addr,
                    meta.encap_data.vni);
    }
}

#endif /* _SIRIUS_INBOUND_P4_ */
