#include <core.p4>
#include "dash_arch_specific.p4"

#include "dash_headers.p4"
#include "dash_metadata.p4"
#include "dash_counters.p4"
#include "dash_parser.p4"
#include "dash_tunnel.p4"
#include "dash_outbound.p4"
#include "dash_inbound.p4"
#include "dash_conntrack.p4"
#include "stages/conntrack_lookup.p4"
#include "stages/direction_lookup.p4"
#include "stages/eni_lookup.p4"
#include "stages/ha.p4"
#include "stages/routing_action_apply.p4"
#include "stages/metering_update.p4"
#include "underlay.p4"

control dash_ingress(
      inout headers_t hdr
    , inout metadata_t meta
#ifdef TARGET_BMV2_V1MODEL
    , inout standard_metadata_t standard_metadata
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
    , in    pna_main_input_metadata_t  istd
    , inout pna_main_output_metadata_t ostd
#endif // TARGET_DPDK_PNA
    )
{
    action drop_action() {
#ifdef TARGET_BMV2_V1MODEL
        mark_to_drop(standard_metadata);
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
        drop_packet();
#endif // TARGET_DPDK_PNA
    }

    action deny() {
        meta.dropped = true;
    }

    action accept() {
    }

    @SaiTable[name = "vip", api = "dash_vip"]
    table vip {
        key = {
            hdr.u0_ipv4.dst_addr : exact @SaiVal[name = "VIP", type="sai_ip_address_t"];
        }

        actions = {
            accept;
            @defaultonly deny;
        }

        const default_action = deny;
    }

    action set_appliance(EthernetAddress neighbor_mac,
                         EthernetAddress mac) {
        meta.encap_data.underlay_dmac = neighbor_mac;
        meta.encap_data.underlay_smac = mac;
    }

    /* This table API should be implemented manually using underlay SAI */
    @SaiTable[ignored = "true"]
    table appliance {
        key = {
            meta.appliance_id : ternary;
        }

        actions = {
            set_appliance;
        }
    }

#define ACL_GROUPS_PARAM(prefix) \
    @SaiVal[type="sai_object_id_t"] bit<16> ## prefix ##_stage1_dash_acl_group_id, \
    @SaiVal[type="sai_object_id_t"] bit<16> ## prefix ##_stage2_dash_acl_group_id, \
    @SaiVal[type="sai_object_id_t"] bit<16> ## prefix ##_stage3_dash_acl_group_id, \
    @SaiVal[type="sai_object_id_t"] bit<16> ## prefix ##_stage4_dash_acl_group_id, \
    @SaiVal[type="sai_object_id_t"] bit<16> ## prefix ##_stage5_dash_acl_group_id

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
                         @SaiVal[type="sai_object_id_t"] bit<16> ha_scope_id,
                         @SaiVal[type="sai_ip_address_t"] IPv4Address vm_underlay_dip,
                         @SaiVal[type="sai_uint32_t"] bit<24> vm_vni,
                         @SaiVal[type="sai_object_id_t"] bit<16> vnet_id,
                         IPv6Address pl_sip,
                         IPv6Address pl_sip_mask,
                         @SaiVal[type="sai_ip_address_t"] IPv4Address pl_underlay_sip,
                         @SaiVal[type="sai_object_id_t"] bit<16> v4_meter_policy_id,
                         @SaiVal[type="sai_object_id_t"] bit<16> v6_meter_policy_id,
                         @SaiVal[type="sai_dash_tunnel_dscp_mode_t"] dash_tunnel_dscp_mode_t dash_tunnel_dscp_mode,
                         @SaiVal[type="sai_uint8_t",validonly="SAI_ENI_ATTR_DASH_TUNNEL_DSCP_MODE == SAI_DASH_TUNNEL_DSCP_MODE_PIPE_MODEL"] bit<6> dscp,
                         ACL_GROUPS_PARAM(inbound_v4),
                         ACL_GROUPS_PARAM(inbound_v6),
                         ACL_GROUPS_PARAM(outbound_v4),
                         ACL_GROUPS_PARAM(outbound_v6),
                         bit<1> disable_fast_path_icmp_flow_redirection,
                         bit<1> full_flow_resimulation_requested,
                         bit<64> max_resimulated_flow_per_second,
                         @SaiVal[type="sai_object_id_t"] bit<16> outbound_routing_group_id,
                         bit<1> is_ha_flow_owner)
    {
        meta.eni_data.cps                                                   = cps;
        meta.eni_data.pps                                                   = pps;
        meta.eni_data.flows                                                 = flows;
        meta.eni_data.admin_state                                           = admin_state;
        meta.eni_data.pl_sip                                                = pl_sip;
        meta.eni_data.pl_sip_mask                                           = pl_sip_mask;
        meta.eni_data.pl_underlay_sip                                       = pl_underlay_sip;
        meta.encap_data.underlay_dip                                        = vm_underlay_dip;
        meta.eni_data.outbound_routing_group_data.outbound_routing_group_id = outbound_routing_group_id;
        if (dash_tunnel_dscp_mode == dash_tunnel_dscp_mode_t.PIPE_MODEL) {
            meta.eni_data.dscp = dscp;
        }
        /* vm_vni is the encap VNI used for tunnel between inbound DPU -> VM
         * and not a VNET identifier */
        meta.encap_data.vni           = vm_vni;
        meta.vnet_id                  = vnet_id;

        if (meta.is_overlay_ip_v6 == 1) {
            if (meta.direction == dash_direction_t.OUTBOUND) {
                ACL_GROUPS_COPY_TO_META(outbound_v6);
                meta.meter_context.meter_policy_lookup_ip = meta.dst_ip_addr;
            } else {
                ACL_GROUPS_COPY_TO_META(inbound_v6);
                meta.meter_context.meter_policy_lookup_ip = meta.src_ip_addr;
            }

            meta.meter_context.meter_policy_id = v6_meter_policy_id;
        } else {
            if (meta.direction == dash_direction_t.OUTBOUND) {
                ACL_GROUPS_COPY_TO_META(outbound_v4);
                meta.meter_context.meter_policy_lookup_ip = meta.dst_ip_addr;
            } else {
                ACL_GROUPS_COPY_TO_META(inbound_v4);
                meta.meter_context.meter_policy_lookup_ip = meta.src_ip_addr;
            }

            meta.meter_context.meter_policy_id = v4_meter_policy_id;
        }

        meta.ha.ha_scope_id = ha_scope_id;
        meta.fast_path_icmp_flow_redirection_disabled = disable_fast_path_icmp_flow_redirection;
    }

    @SaiTable[name = "eni", api = "dash_eni", order=1, isobject="true"]
    table eni {
        key = {
            meta.eni_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_eni_attrs;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    action permit() {
    }

    action vxlan_decap() {}
    action vxlan_decap_pa_validate() {}

    action tunnel_decap(inout headers_t hdr,
                        inout metadata_t meta,
                        bit<32> meter_class_or,
                        @SaiVal[default_value="4294967295"] bit<32> meter_class_and) {
        set_meter_attrs(meta, meter_class_or, meter_class_and);
    }

    action tunnel_decap_pa_validate(inout headers_t hdr,
                                    inout metadata_t meta,
                                    @SaiVal[type="sai_object_id_t"] bit<16> src_vnet_id,
                                    bit<32> meter_class_or,
                                    @SaiVal[default_value="4294967295"] bit<32> meter_class_and) {
        meta.vnet_id = src_vnet_id;
        set_meter_attrs(meta, meter_class_or, meter_class_and);
    }

    @SaiTable[name = "pa_validation", api = "dash_pa_validation"]
    table pa_validation {
        key = {
            meta.vnet_id: exact @SaiVal[type="sai_object_id_t"];
            hdr.u0_ipv4.src_addr : exact @SaiVal[name = "sip", type="sai_ip_address_t"];
        }

        actions = {
            permit;
            @defaultonly deny;
        }

        const default_action = deny;
    }

    @SaiTable[name = "inbound_routing", api = "dash_inbound_routing"]
    table inbound_routing {
        key = {
            meta.eni_id: exact @SaiVal[type="sai_object_id_t"];
            hdr.u0_vxlan.vni : exact @SaiVal[name = "VNI"];
            hdr.u0_ipv4.src_addr : ternary @SaiVal[name = "sip", type="sai_ip_address_t"];
        }
        actions = {
            tunnel_decap(hdr, meta);
            tunnel_decap_pa_validate(hdr, meta);
            vxlan_decap;                // Deprecated, but cannot be removed until SWSS is updated.
            vxlan_decap_pa_validate;    // Deprecated, but cannot be removed until SWSS is updated.
            @defaultonly deny;
        }

        const default_action = deny;
    }

    action set_acl_group_attrs(@SaiVal[type="sai_ip_addr_family_t", isresourcetype="true"] bit<32> ip_addr_family) {
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

    @SaiTable[name = "dash_acl_group", api = "dash_acl", isobject="true"]
    table acl_group {
        key = {
            meta.stage1_dash_acl_group_id : exact @SaiVal[name = "dash_acl_group_id"];
        }
        actions = {
            set_acl_group_attrs();
        }
    }

    apply {

#ifdef TARGET_DPDK_PNA
#ifdef DPDK_PNA_SEND_TO_PORT_FIX_MERGED
        // As of 2023-Jan-26, the version of the pna.p4 header file
        // included with p4c defines send_to_port with a parameter
        // that has no 'in' direction.  The following commit in the
        // public pna repo fixes this, but this fix has not yet been
        // copied into the p4c repo.
        // https://github.com/p4lang/pna/commit/b9fdfb888e5385472c34ff773914c72b78b63058
        // Until p4c is updated with this fix, the following line will
        // give a compile-time error.
        send_to_port(istd.input_port);
#endif  // DPDK_PNA_SEND_TO_PORT_FIX_MERGED
#endif // TARGET_DPDK_PNA

        if (meta.is_fast_path_icmp_flow_redirection_packet) {
            UPDATE_COUNTER(port_lb_fast_path_icmp_in, 0);
        }

        if (vip.apply().hit) {
            /* Use the same VIP that was in packet's destination if it's
               present in the VIP table */
            meta.encap_data.underlay_sip = hdr.u0_ipv4.dst_addr;
        } else {
            UPDATE_COUNTER(vip_miss_drop, 0);

            if (meta.is_fast_path_icmp_flow_redirection_packet) {
            }
        }

        direction_lookup_stage.apply(hdr, meta);

        appliance.apply();

        /* Outer header processing */
        eni_lookup_stage.apply(hdr, meta);

        // Save the original DSCP value
        meta.eni_data.dscp_mode = dash_tunnel_dscp_mode_t.PRESERVE_MODEL;
        meta.eni_data.dscp = (bit<6>)hdr.u0_ipv4.diffserv;

        if (meta.direction == dash_direction_t.INBOUND) {
            switch (inbound_routing.apply().action_run) {
                tunnel_decap_pa_validate: {
                    pa_validation.apply();
                }
                deny: {
                    UPDATE_ENI_COUNTER(inbound_routing_entry_miss_drop);
                }
            }
        }

        do_tunnel_decap(hdr, meta);

        /* At this point the processing is done on customer headers */

        meta.is_overlay_ip_v6 = 0;
        meta.ip_protocol = 0;
        meta.dst_ip_addr = 0;
        meta.src_ip_addr = 0;
        if (hdr.customer_ipv6.isValid()) {
            meta.ip_protocol = hdr.customer_ipv6.next_header;
            meta.src_ip_addr = hdr.customer_ipv6.src_addr;
            meta.dst_ip_addr = hdr.customer_ipv6.dst_addr;
            meta.is_overlay_ip_v6 = 1;
        } else if (hdr.customer_ipv4.isValid()) {
            meta.ip_protocol = hdr.customer_ipv4.protocol;
            meta.src_ip_addr = (bit<128>)hdr.customer_ipv4.src_addr;
            meta.dst_ip_addr = (bit<128>)hdr.customer_ipv4.dst_addr;
        }

        if (hdr.customer_tcp.isValid()) {
            meta.src_l4_port = hdr.customer_tcp.src_port;
            meta.dst_l4_port = hdr.customer_tcp.dst_port;
        } else if (hdr.customer_udp.isValid()) {
            meta.src_l4_port = hdr.customer_udp.src_port;
            meta.dst_l4_port = hdr.customer_udp.dst_port;
        }

        if (!eni.apply().hit) {
            UPDATE_COUNTER(eni_miss_drop, 0);
            deny();
        }

        if (meta.eni_data.admin_state == 0) {
            deny();
        }

        conntrack_lookup_stage.apply(hdr, meta);

        UPDATE_ENI_COUNTER(eni_rx);
        if (meta.is_fast_path_icmp_flow_redirection_packet) {
            UPDATE_ENI_COUNTER(eni_lb_fast_path_icmp_in);
        }

        ha_stage.apply(hdr, meta);

        acl_group.apply();

        if (meta.direction == dash_direction_t.OUTBOUND) {
            UPDATE_ENI_COUNTER(eni_outbound_rx);

            meta.target_stage = dash_pipeline_stage_t.OUTBOUND_ROUTING;
            outbound.apply(hdr, meta);
        } else if (meta.direction == dash_direction_t.INBOUND) {
            UPDATE_ENI_COUNTER(eni_inbound_rx);
            inbound.apply(hdr, meta);
        }

        tunnel_stage.apply(hdr, meta);

        routing_action_apply.apply(hdr, meta);

        tunnel_stage_encap.apply(hdr, meta);

        /* Underlay routing */
        meta.dst_ip_addr = (bit<128>)hdr.u0_ipv4.dst_addr;

        underlay.apply(
              hdr
            , meta
    #ifdef TARGET_BMV2_V1MODEL
            , standard_metadata
    #endif // TARGET_BMV2_V1MODEL
    #ifdef TARGET_DPDK_PNA
            , istd
    #endif // TARGET_DPDK_PNA
        );

        if (meta.eni_data.dscp_mode == dash_tunnel_dscp_mode_t.PIPE_MODEL) {
            hdr.u0_ipv4.diffserv = (bit<8>)meta.eni_data.dscp;
        }

        metering_update_stage.apply(hdr, meta);

        if (meta.dropped) {
            drop_action();
        } else {
            UPDATE_ENI_COUNTER(eni_tx);

            if (meta.direction == dash_direction_t.OUTBOUND) {
                UPDATE_ENI_COUNTER(eni_outbound_tx);
            } else if (meta.direction == dash_direction_t.INBOUND) {
                UPDATE_ENI_COUNTER(eni_inbound_tx);
            }
        }
    }
}

#ifdef TARGET_BMV2_V1MODEL
#include "dash_bmv2_v1model.p4"
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
#include "dash_dpdk_pna.p4"
#endif // TARGET_DPDK_PNA
