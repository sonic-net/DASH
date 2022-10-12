#include <core.p4>
#include <v1model.p4>
#include "dash_headers.p4"
#include "dash_metadata.p4"
#include "dash_parser.p4"
#include "dash_vxlan.p4"
#include "dash_outbound.p4"
#include "dash_inbound.p4"
#include "dash_conntrack.p4"

control dash_verify_checksum(inout headers_t hdr,
                         inout metadata_t meta)
{
    apply { }
}

control dash_compute_checksum(inout headers_t hdr,
                          inout metadata_t meta)
{
    apply { }
}

control dash_ingress(inout headers_t hdr,
                  inout metadata_t meta,
                  inout standard_metadata_t standard_metadata)
{
    action drop_action() {
        mark_to_drop(standard_metadata);
    }

    action deny() {
        meta.dropped = true;
    }

    action accept() {
    }

    @name("vip|dash_vip")
    table vip {
        key = {
            hdr.ipv4.dst_addr : exact @name("hdr.ipv4.dst_addr:VIP");
        }

        actions = {
            accept;
            @defaultonly deny;
        }

        const default_action = deny;
    }

    action set_outbound_direction() {
        meta.direction = direction_t.OUTBOUND;
    }

    action set_inbound_direction() {
        meta.direction = direction_t.INBOUND;
    }

    @name("direction_lookup|dash_direction_lookup")
    table direction_lookup {
        key = {
            hdr.vxlan.vni : exact @name("hdr.vxlan.vni:VNI");
        }

        actions = {
            set_outbound_direction;
            @defaultonly set_inbound_direction;
        }

        const default_action = set_inbound_direction;
    }

    action set_appliance(EthernetAddress neighbor_mac,
                         EthernetAddress mac) {
        meta.encap_data.underlay_dmac = neighbor_mac;
        meta.encap_data.underlay_smac = mac;
    }

    /* This table API should be implemented manually using underlay SAI */
    table appliance {
        key = {
            meta.appliance_id : ternary @name("meta.appliance_id:appliance_id");
        }

        actions = {
            set_appliance;
        }
    }

#define ACL_GROUPS_PARAM(prefix) \
    bit<16> ## prefix ##_stage1_dash_acl_group_id, \
    bit<16> ## prefix ##_stage2_dash_acl_group_id, \
    bit<16> ## prefix ##_stage3_dash_acl_group_id, \
    bit<16> ## prefix ##_stage4_dash_acl_group_id, \
    bit<16> ## prefix ##_stage5_dash_acl_group_id

#define ACL_GROUPS_COPY_TO_META(prefix) \
   meta.stage1_dash_acl_group_id = ## prefix ##_stage1_dash_acl_group_id; \
   meta.stage2_dash_acl_group_id = ## prefix ##_stage2_dash_acl_group_id; \
   meta.stage3_dash_acl_group_id = ## prefix ##_stage3_dash_acl_group_id; \
   meta.stage4_dash_acl_group_id = ## prefix ##_stage4_dash_acl_group_id; \
   meta.stage5_dash_acl_group_id = ## prefix ##_stage5_dash_acl_group_id;

    action set_eni_attrs(bit<32> cps,
                         bit<32> pps,
                         bit<32> flows,
                         bit<1> admin_state,
                         IPv4Address vm_underlay_dip,
                         bit<24> vm_vni,
                         bit<16> vnet_id,
                         ACL_GROUPS_PARAM(inbound_v4),
                         ACL_GROUPS_PARAM(inbound_v6),
                         ACL_GROUPS_PARAM(outbound_v4),
                         ACL_GROUPS_PARAM(outbound_v6)) {
        meta.eni_data.cps            = cps;
        meta.eni_data.pps            = pps;
        meta.eni_data.flows          = flows;
        meta.eni_data.admin_state    = admin_state;
        meta.encap_data.underlay_dip = vm_underlay_dip;
        /* vm_vni is the encap VNI used for tunnel between inbound DPU -> VM
         * and not a VNET identifier */
        meta.encap_data.vni          = vm_vni;
        meta.vnet_id                 = vnet_id;

        if (meta.is_overlay_ip_v6 == 1) {
            if (meta.direction == direction_t.OUTBOUND) {
                ACL_GROUPS_COPY_TO_META(outbound_v6);
            } else {
                ACL_GROUPS_COPY_TO_META(inbound_v6);
            }
        } else {
            if (meta.direction == direction_t.OUTBOUND) {
                ACL_GROUPS_COPY_TO_META(outbound_v4);
            } else {
                ACL_GROUPS_COPY_TO_META(inbound_v4);
            }
        }
    }

    @name("eni|dash_eni")
    table eni {
        key = {
            meta.eni_id : exact @name("meta.eni_id:eni_id");
        }

        actions = {
            set_eni_attrs;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    direct_counter(CounterType.packets_and_bytes) eni_counter;

    table eni_meter {
        key = {
            meta.eni_id : exact @name("meta.eni_id:eni_id");
            meta.direction : exact @name("meta.direction:direction");
            meta.dropped : exact @name("meta.dropped:dropped");
        }

        actions = { NoAction; }

        counters = eni_counter;
    }

    action permit() {
    }

    action vxlan_decap_pa_validate(bit<16> src_vnet_id) {
        meta.vnet_id = src_vnet_id;
    }

    @name("pa_validation|dash_pa_validation")
    table pa_validation {
        key = {
            meta.vnet_id: exact @name("meta.vnet_id:vnet_id");
            hdr.ipv4.src_addr : exact @name("hdr.ipv4.src_addr:sip");
        }

        actions = {
            permit;
            @defaultonly deny;
        }

        const default_action = deny;
    }

    @name("inbound_routing|dash_inbound_routing")
    table inbound_routing {
        key = {
            meta.eni_id: exact @name("meta.eni_id:eni_id");
            hdr.vxlan.vni : exact @name("hdr.vxlan.vni:VNI");
            hdr.ipv4.src_addr : ternary @name("hdr.ipv4.src_addr:sip");
        }
        actions = {
            vxlan_decap(hdr);
            vxlan_decap_pa_validate;
            @defaultonly deny;
        }

        const default_action = deny;
    }

    action set_eni(bit<16> eni_id) {
        meta.eni_id = eni_id;
    }

    @name("eni_ether_address_map|dash_eni")
    table eni_ether_address_map {
        key = {
            meta.eni_addr : exact @name("meta.eni_addr:address");
        }

        actions = {
            set_eni;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    action set_acl_group_attrs(bit<32> ip_addr_family) {
        if (ip_addr_family == 0) /* SAI_IP_ADDR_FAMILY_IPV4 */ {
            if (meta.is_overlay_ip_v6 == 1) {
                meta.dropped = true;
            }
        } else {
            if (meta.is_overlay_ip_v6 == 0) {
                meta.dropped = true;
            }
        }
    }

    @name("dash_acl_group|dash_acl")
    table acl_group {
        key = {
            meta.stage1_dash_acl_group_id : exact @name("meta.stage1_dash_acl_group_id:dash_acl_group_id");
        }
        actions = {
            set_acl_group_attrs();
        }
    }

    apply {

        /* Send packet on same port it arrived (echo) by default */
        standard_metadata.egress_spec = standard_metadata.ingress_port;

        if (vip.apply().hit) {
            /* Use the same VIP that was in packet's destination if it's
               present in the VIP table */
            meta.encap_data.underlay_sip = hdr.ipv4.dst_addr;
        }

        /* If Outer VNI matches with a reserved VNI, then the direction is Outbound - */
        direction_lookup.apply();

        appliance.apply();

        /* Outer header processing */

        if (meta.direction == direction_t.OUTBOUND) {
            vxlan_decap(hdr);
        } else if (meta.direction == direction_t.INBOUND) {
            switch (inbound_routing.apply().action_run) {
                vxlan_decap_pa_validate: {
                    pa_validation.apply();
                    vxlan_decap(hdr);
                }
            }
        }

        meta.is_overlay_ip_v6 = 0;
        meta.ip_protocol = 0;
        meta.dst_ip_addr = 0;
        meta.src_ip_addr = 0;
        if (hdr.ipv6.isValid()) {
            meta.ip_protocol = hdr.ipv6.next_header;
            meta.src_ip_addr = hdr.ipv6.src_addr;
            meta.dst_ip_addr = hdr.ipv6.dst_addr;
            meta.is_overlay_ip_v6 = 1;
        } else if (hdr.ipv4.isValid()) {
            meta.ip_protocol = hdr.ipv4.protocol;
            meta.src_ip_addr = (bit<128>)hdr.ipv4.src_addr;
            meta.dst_ip_addr = (bit<128>)hdr.ipv4.dst_addr;
        }

        /* At this point the processing is done on customer headers */

        /* Put VM's MAC in the direction agnostic metadata field */
        meta.eni_addr = meta.direction == direction_t.OUTBOUND  ?
                                          hdr.ethernet.src_addr :
                                          hdr.ethernet.dst_addr;
        eni_ether_address_map.apply();
        eni.apply();
        if (meta.eni_data.admin_state == 0) {
            deny();
        }
        acl_group.apply();

        if (meta.direction == direction_t.OUTBOUND) {
            outbound.apply(hdr, meta, standard_metadata);
        } else if (meta.direction == direction_t.INBOUND) {
            inbound.apply(hdr, meta, standard_metadata);
        }

        eni_meter.apply();

        if (meta.dropped) {
            drop_action();
        }
    }
}

control dash_egress(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    apply { }
}

V1Switch(dash_parser(),
         dash_verify_checksum(),
         dash_ingress(),
         dash_egress(),
         dash_compute_checksum(),
         dash_deparser()) main;
