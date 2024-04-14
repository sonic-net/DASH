#ifndef _DASH_OUTBOUND_P4_
#define _DASH_OUTBOUND_P4_

#include "dash_headers.p4"
#include "dash_acl.p4"
#include "dash_conntrack.p4"
#include "stages/outbound_routing.p4"
#include "stages/outbound_mapping.p4"

control outbound(inout headers_t hdr,
                 inout metadata_t meta)
{
    apply {
#ifdef STATEFUL_P4
           ConntrackOut.apply(0);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackOut.apply(hdr, meta);
#endif // PNA_CONNTRACK

        /* ACL */
        if (!meta.conntrack_data.allow_out) {
            acl.apply(hdr, meta);
        }

#ifdef STATEFUL_P4
            ConntrackIn.apply(1);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK

        meta.lkup_dst_ip_addr = meta.dst_ip_addr;
        meta.is_lkup_dst_ip_v6 = meta.is_overlay_ip_v6;

        outbound_routing_stage.apply(hdr, meta);
        outbound_mapping_stage.apply(hdr, meta);
    }
}

#endif /* _DASH_OUTBOUND_P4_ */
