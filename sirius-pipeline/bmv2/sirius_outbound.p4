#ifndef _SIRIUS_OUTBOUND_P4_
#define _SIRIUS_OUTBOUND_P4_

#include "sirius_headers.p4"
#include "sirius_acl.p4"
#include "sirius_conntrack.p4"

control outbound(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    action set_vni(bit<24> vni) {
        meta.encap_data.vni = vni;
    }

    table eni_to_vni {
        key = {
            meta.eni : exact @name("meta.eni:eni");
        }

        actions = {
            set_vni;
        }
    }

    action route_vnet(bit<24> dest_vnet_vni) {
        meta.encap_data.dest_vnet_vni = dest_vnet_vni;
    }

    direct_counter(CounterType.packets_and_bytes) routing_v4_counter;

    table routing_v4 {
        key = {
            meta.eni : exact @name("meta.eni:eni");
            hdr.ipv4.dst_addr : lpm @name("hdr.ipv4.dst_addr:destination");
        }

        actions = {
            route_vnet; /* for expressroute - ecmp of overlay */
        }

        counters = routing_v4_counter;
    }

    direct_counter(CounterType.packets_and_bytes) routing_v6_counter;

    table routing_v6 {
        key = {
            meta.eni : exact @name("meta.eni:eni");
            hdr.ipv6.dst_addr : lpm @name("hdr.ipv6.dst_addr:destination");
        }

        actions = {
            route_vnet; /* for expressroute - ecmp of overlay */
        }

        counters = routing_v6_counter;
    }

    action set_tunnel_mapping(IPv4Address underlay_dip,
                              EthernetAddress overlay_dmac,
                              bit<1> use_dst_vni) {
        /*
           if (use_dst_vni)
               vni = meta.encap_data.vni;
          else
              vni = meta.encap_data.dest_vnet_vni;
        */
        meta.encap_data.vni = meta.encap_data.vni * (bit<24>)(~use_dst_vni) + meta.encap_data.dest_vnet_vni * (bit<24>)use_dst_vni;
        meta.encap_data.overlay_dmac = overlay_dmac;
        meta.encap_data.underlay_dip = underlay_dip;
    }

    direct_counter(CounterType.packets_and_bytes) ca_v4_to_pa_counter;

    table ca_v4_to_pa {
        key = {
            /* Flow for express route */
            meta.encap_data.dest_vnet_vni : exact @name("meta.encap_data.dest_vnet_vni:dest_vni");
            hdr.ipv4.dst_addr : exact @name("hdr.ipv4.dst_addr:dip");
        }

        actions = {
            set_tunnel_mapping;
        }

        counters = ca_v4_to_pa_counter;
    }

    direct_counter(CounterType.packets_and_bytes) ca_v6_to_pa_counter;

    table ca_v6_to_pa {
        key = {
            /* Flow for express route */
            meta.encap_data.dest_vnet_vni : exact @name("meta.encap_data.dest_vnet_vni:dest_vni");
            hdr.ipv6.dst_addr : exact @name("hdr.ipv6.dst_addr:dip");
        }

        actions = {
            set_tunnel_mapping;
        }

        counters = ca_v6_to_pa_counter;
    }

    apply {
        eni_to_vni.apply();

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

        bool do_v6 = false;
        bool do_action = false;
        if (hdr.ipv6.isValid()) {
            do_v6 = true;
            switch (routing_v6.apply().action_run) {
                route_vnet: {
                    ca_v6_to_pa.apply();
                    do_action = true;
                }
            }
        } else {
            switch (routing_v4.apply().action_run) {
                route_vnet: {
                    ca_v4_to_pa.apply();
                    do_action = true;
                }
            }
        }

        if (do_action) {
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

#endif /* _SIRIUS_OUTBOUND_P4_ */
