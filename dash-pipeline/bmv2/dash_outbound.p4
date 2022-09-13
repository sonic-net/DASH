#ifndef _SIRIUS_OUTBOUND_P4_
#define _SIRIUS_OUTBOUND_P4_

#include "dash_headers.p4"
#include "dash_acl.p4"
#include "dash_conntrack.p4"

control outbound(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    action route_vnet(bit<16> dst_vnet_id) {
        meta.dst_vnet_id = dst_vnet_id;
    }

    action route_vnet_direct(bit<16> dst_vnet_id,
                             bit<1> is_overlay_ip_v4_or_v6,
                             IPv4ORv6Address overlay_ip) {
        meta.dst_vnet_id = dst_vnet_id;
        meta.lkup_dst_ip_addr = overlay_ip;
        meta.is_lkup_dst_ip_v6 = is_overlay_ip_v4_or_v6;
    }

    action route_direct() {
        /* send to underlay router without any encap */
    }

    action drop() {
        meta.dropped = true;
    }

    direct_counter(CounterType.packets_and_bytes) routing_counter;

    @name("outbound_routing|dash_outbound_routing")
    table routing {
        key = {
            meta.eni_id : exact @name("meta.eni_id:eni_id");
            meta.is_overlay_ip_v6 : exact @name("meta.is_overlay_ip_v6:is_destination_v4_or_v6");
            meta.dst_ip_addr : lpm @name("meta.dst_ip_addr:destination");
        }

        actions = {
            route_vnet; /* for expressroute - ecmp of overlay */
            route_vnet_direct;
            route_direct;
            drop;
        }
        const default_action = drop;

        counters = routing_counter;
    }

    action set_tunnel_mapping(IPv4Address underlay_dip,
                              EthernetAddress overlay_dmac,
                              bit<1> use_dst_vnet_vni) {
        if (use_dst_vnet_vni == 1)
            meta.vnet_id = meta.dst_vnet_id;
        meta.encap_data.overlay_dmac = overlay_dmac;
        meta.encap_data.underlay_dip = underlay_dip;
    }

    direct_counter(CounterType.packets_and_bytes) ca_to_pa_counter;

    @name("outbound_ca_to_pa|dash_outbound_ca_to_pa")
    table ca_to_pa {
        key = {
            /* Flow for express route */
            meta.dst_vnet_id: exact @name("meta.dst_vnet_id:dst_vnet_id");
            meta.is_lkup_dst_ip_v6 : exact @name("meta.is_lkup_dst_ip_v6:is_dip_v4_or_v6");
            meta.lkup_dst_ip_addr : exact @name("meta.lkup_dst_ip_addr:dip");
        }

        actions = {
            set_tunnel_mapping;
            @defaultonly drop;
        }
        const default_action = drop;

        counters = ca_to_pa_counter;
    }

    action set_vnet_attrs(bit<24> vni) {
        meta.encap_data.vni = vni;
    }

    @name("vnet|dash_vnet")
    table vnet {
        key = {
            meta.vnet_id : exact @name("meta.vnet_id:vnet_id");
        }

        actions = {
            set_vnet_attrs;
        }
    }

    apply {
#ifdef STATEFUL_P4
           ConntrackOut.apply(0);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackOut.apply(hdr, meta);
#endif // PNA_CONNTRACK

        /* ACL */
        if (!meta.conntrack_data.allow_out) {
            acl.apply(hdr, meta, standard_metadata);
        }

#ifdef STATEFUL_P4
            ConntrackIn.apply(1);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK

        meta.lkup_dst_ip_addr = meta.dst_ip_addr;
        meta.is_lkup_dst_ip_v6 = meta.is_overlay_ip_v6;

        switch (routing.apply().action_run) {
            route_vnet_direct:
            route_vnet: {
                ca_to_pa.apply();
                vnet.apply();

                vxlan_encap(hdr,
                            meta.encap_data.underlay_dmac,
                            meta.encap_data.underlay_smac,
                            meta.encap_data.underlay_dip,
                            meta.encap_data.underlay_sip,
                            meta.encap_data.overlay_dmac,
                            meta.encap_data.vni);
             }
         }
    }
}

#endif /* _SIRIUS_OUTBOUND_P4_ */
