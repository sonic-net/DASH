#include <core.p4>
#include <v1model.p4>
#include "sirius_headers.p4"
#include "sirius_metadata.p4"
#include "sirius_parser.p4"
#include "sirius_vxlan.p4"
#include "sirius_outbound.p4"
#include "sirius_conntrack.p4"
#include "sirius_acl.p4"

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

    table vnet {
        key = {
            meta.lookup_vni : exact @name("meta.lookup_vni:vni");
        }
        actions = {
            vxlan_decap(hdr);
            @defaultonly deny;
        }

        const default_action = deny;
    }

    action set_eni_attributes(bit<16> eni,
                              bit<24> vni,
                              bit<16> stage1_outbound_acl_group_id,
                              bit<16> stage1_inbound_acl_group_id,
                              bit<16> stage2_outbound_acl_group_id,
                              bit<16> stage2_inbound_acl_group_id,
                              bit<16> stage3_outbound_acl_group_id,
                              bit<16> stage3_inbound_acl_group_id,
                              bit<16> route_table_id,
                              bit<16> vnet_id,
                              bit<16> tunnel_id) {
        meta.eni = eni;
        meta.encap_data.vni = vni;
        if (meta.direction == direction_t.OUTBOUND) {
            meta.stage1_acl_group_id = stage1_outbound_acl_group_id;
            meta.stage2_acl_group_id = stage2_outbound_acl_group_id;
            meta.stage3_acl_group_id = stage3_outbound_acl_group_id;
        } else {
            meta.stage1_acl_group_id = stage1_inbound_acl_group_id;
            meta.stage2_acl_group_id = stage2_inbound_acl_group_id;
            meta.stage3_acl_group_id = stage3_inbound_acl_group_id;
        }
        meta.route_table_id = route_table_id;
        meta.vnet = vnet_id;
        meta.tunnel_id = tunnel_id;
    }

    table eni {
        key = {
            meta.eni_addr : exact @name("meta.eni_addr:eni_addr");
        }

        actions = {
            set_eni_attributes;
        }
    }

    apply {
        direction_lookup.apply();

        appliance.apply();

        /* Outer header processing */
        meta.lookup_vni = hdr.vxlan.vni;
        vxlan_decap(hdr);

        /* At this point the processing is done on customer headers */

        meta.dst_ip_addr = 0;
        meta.is_dst_ip_v6 = 0;
        if (hdr.ipv6.isValid()) {
            meta.dst_ip_addr = hdr.ipv6.dst_addr;
            meta.is_dst_ip_v6 = 1;
        } else if (hdr.ipv4.isValid()) {
            meta.dst_ip_addr = (bit<128>)hdr.ipv4.dst_addr;
        }

        /* Put VM's MAC in the direction agnostic metadata field */
        meta.eni_addr = meta.direction == direction_t.OUTBOUND  ?
                                          hdr.ethernet.src_addr :
                                          hdr.ethernet.dst_addr;

        eni.apply();
        if (meta.direction == direction_t.OUTBOUND) {
            meta.lookup_vni = meta.encap_data.vni;
        }
        vnet.apply();

        if (meta.direction == direction_t.OUTBOUND) {
#ifdef STATEFUL_P4
            ConntrackOut.apply(0);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
            ConntrackOut.apply(hdr, meta);
#endif // PNA_CONNTRACK
        } else {
#ifdef STATEFUL_P4
            ConntrackIn.apply(0);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
            ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK
        }

        /* ACL */
        if (!meta.conntrack_data.allow_out) {
            acl.apply(hdr, meta, standard_metadata);
        }

        if (meta.direction == direction_t.OUTBOUND) {
#ifdef STATEFUL_P4
            ConntrackIn.apply(1);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK
        } else if (meta.direction == direction_t.INBOUND) {
#ifdef STATEFUL_P4
            ConntrackOut.apply(1);
#endif /* STATEFUL_P4 */
#ifdef PNA_CONNTRACK
            ConntrackOut.apply(hdr, meta);
#endif //PNA_CONNTRACK

        }

        if (meta.direction == direction_t.OUTBOUND) {
            outbound.apply(hdr, meta, standard_metadata);
        }

        vxlan_encap(hdr,
                    meta.encap_data.underlay_dmac,
                    meta.encap_data.underlay_smac,
                    meta.encap_data.underlay_dip,
                    meta.encap_data.underlay_sip,
                    hdr.ethernet.dst_addr,
                    meta.encap_data.vni);

        eni_meter.apply();

        /* Send packet to port 1 by default if we reached the end of pipeline */
        if (meta.dropped) {
            drop_action();
        } else {
            standard_metadata.egress_spec = 1;
        }
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
