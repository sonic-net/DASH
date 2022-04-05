#include <core.p4>
#include <v1model.p4>
#include "sirius_headers.p4"
#include "sirius_metadata.p4"
#include "sirius_parser.p4"
#include "sirius_vxlan.p4"
#include "sirius_outbound.p4"
#include "sirius_inbound.p4"
#include "sirius_conntrack.p4"

control sirius_verify_checksum(inout headers_t hdr,
                         inout metadata_t meta)
{
    apply { }
}

control sirius_compute_checksum(inout headers_t hdr,
                          inout metadata_t meta)
{
    apply { }
}

control sirius_ingress(inout headers_t hdr,
                  inout metadata_t meta,
                  inout standard_metadata_t standard_metadata)
{
    action drop_action() {
        mark_to_drop(standard_metadata);
    }

    action set_direction(direction_t direction) {
        meta.direction = direction;
    }

    table direction_lookup {
        key = {
            hdr.vxlan.vni : exact @name("hdr.vxlan.vni:vni");
        }

        actions = {
            set_direction;
        }
    }

    action set_appliance(EthernetAddress neighbor_mac,
                         EthernetAddress mac,
                         IPv4Address ip) {
        meta.encap_data.underlay_dmac = neighbor_mac;
        meta.encap_data.underlay_smac = mac;
        meta.encap_data.underlay_sip = ip;
    }

    table appliance {
        key = {
            meta.appliance_id : ternary @name("meta.appliance_id:appliance_id");
        }

        actions = {
            set_appliance;
        }
    }

    direct_counter(CounterType.packets_and_bytes) eni_counter;

    table eni_meter {
        key = {
            meta.eni : exact @name("meta.eni:eni");
            meta.direction : exact @name("meta.direction:direction");
            meta.dropped : exact @name("meta.dropped:dropped");
        }

        actions = { NoAction; }

        counters = eni_counter;
    }

    action permit() {
        meta.dropped = false;
    }

    action deny() {
        meta.dropped = true;
    }

    table inbound_routing {
        key = {
            hdr.vxlan.vni : exact @name("hdr.vxlan.vni:vni");
        }
        actions = {
            vxlan_decap(hdr);
            @defaultonly deny;
        }

        const default_action = deny;
    }

    apply {
        direction_lookup.apply();

        appliance.apply();

        /* Outer header processing */

        if (meta.direction == direction_t.OUTBOUND) {
            vxlan_decap(hdr);
        } else if (meta.direction == direction_t.INBOUND) {
            inbound_routing.apply();
        }

        /* At this point the processing is done on customer headers */

        if (meta.direction == direction_t.OUTBOUND) {
            outbound.apply(hdr, meta, standard_metadata);
        } else if (meta.direction == direction_t.INBOUND) {
            inbound.apply(hdr, meta, standard_metadata);
        }

        eni_meter.apply();

        /* Send packet to port 1 by default if we reached the end of pipeline */
        standard_metadata.egress_spec = 1;
    }
}

control sirius_egress(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    apply { }
}

V1Switch(sirius_parser(),
         sirius_verify_checksum(),
         sirius_ingress(),
         sirius_egress(),
         sirius_compute_checksum(),
         sirius_deparser()) main;
