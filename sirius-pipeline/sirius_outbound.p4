#ifndef _SIRIUS_OUTBOUND_P4_
#define _SIRIUS_OUTBOUND_P4_

#include "sirius_headers.p4"
#include "sirius_acl.p4"
#include "sirius_conntrack.p4"

control outbound(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    action set_eni(bit<16> eni) {
        meta.eni = eni;
    }

    table eni_lookup_from_vm {
        key = {
            hdr.ethernet.src_addr : exact @name("hdr.ethernet.src_addr:smac");
        }

        actions = {
            set_eni;
        }
    }

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

    direct_counter(CounterType.packets_and_bytes) routing_counter;

    table routing {
        key = {
            meta.eni : exact @name("meta.eni:eni");
            hdr.ipv4.dst_addr : lpm @name("hdr.ipv4.dst_addr:destination");
        }

        actions = {
            route_vnet; /* for expressroute - ecmp of overlay */
        }

        counters = routing_counter;
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

    direct_counter(CounterType.packets_and_bytes) ca_to_pa_counter;

    table ca_to_pa {
        key = {
            /* Flow for express route */
            meta.encap_data.dest_vnet_vni : exact @name("meta.encap_data.dest_vnet_vni:dest_vni");
            hdr.ipv4.dst_addr : exact @name("hdr.ipv4.dst_addr:dip");
        }

        actions = {
            set_tunnel_mapping;
        }

        counters = ca_to_pa_counter;
    }

    apply {
        eni_lookup_from_vm.apply();

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

        switch (routing.apply().action_run) {
            route_vnet: {
                ca_to_pa.apply();

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
