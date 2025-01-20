#ifndef _SIRIUS_INBOUND_P4_
#define _SIRIUS_INBOUND_P4_

#include "dash_headers.p4"
#include "dash_service_tunnel.p4"
#include "dash_acl.p4"
#include "routing_actions/routing_actions.p4"
#include "dash_conntrack.p4"
#include "stages/inbound_routing.p4"

control inbound(inout headers_t hdr,
                inout metadata_t meta)
{
    apply {
#ifdef STATEFUL_P4
        ConntrackIn.apply(0);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);

        if ((IPv4Address)meta.overlay_data.sip != 0) {
            do_action_nat64.apply(hdr, meta);
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

        inbound_routing_stage.apply(hdr, meta);

        meta.routing_actions = dash_routing_actions_t.ENCAP_U0;
        do_tunnel_encap(hdr,
                     meta,
                     meta.u0_encap_data.underlay_dmac,
                     meta.u0_encap_data.underlay_smac,
                     meta.u0_encap_data.underlay_dip,
                     meta.u0_encap_data.underlay_sip,
                     meta.eni_data.inbound_dash_encapsulation,
                     meta.u0_encap_data.vni);
    }
}

#endif /* _SIRIUS_INBOUND_P4_ */
