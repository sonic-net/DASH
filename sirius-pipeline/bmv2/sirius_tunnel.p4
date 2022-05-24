#ifndef _SIRIUS_TUNNEL_P4_
#define _SIRIUS_TUNNEL_P4_

#include "sirius_headers.p4"
#include "sirius_acl.p4"
#include "sirius_conntrack.p4"

control Tunnel(inout headers_t hdr,
               inout metadata_t meta,
               inout standard_metadata_t standard_metadata)
{
    action set_tunnel_attributes(EthernetAddress underlay_dmac,
                                 IPv4Address underlay_dip,
                                 bit<24> vni) {
        meta.encap_data.underlay_dmac = underlay_dmac;
        meta.encap_data.underlay_dip = underlay_dip;
        meta.encap_data.vni = vni;
    }

    table tunnel {
        key = {
            meta.tunnel_id: exact @name("tunnel_id");
        }

        actions = {
            set_tunnel_attributes;
        }
    }

    apply {
        tunnel.apply();
    }
}

#endif /* _SIRIUS_TUNNEL_P4_ */

