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
#include "stages/pre_pipeline.p4"
#include "stages/direction_lookup.p4"
#include "stages/eni_lookup.p4"
#include "stages/ha.p4"
#include "stages/routing_action_apply.p4"
#include "stages/metering_update.p4"
#include "underlay.p4"

control dash_eni_stage(
      inout headers_t hdr
    , inout metadata_t meta
    )
{
    action deny() {
        meta.dropped = true;
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
                         bit<1> enable_reverse_tunnel_learning,
                         @SaiVal[type="sai_ip_address_t"] IPv4Address reverse_tunnel_sip,
                         bit<1> is_ha_flow_owner,
                         @SaiVal[type="sai_dash_encapsulation_t", default_value="SAI_DASH_ENCAPSULATION_VXLAN"]
                         dash_encapsulation_t inbound_dash_encapsulation)
    {
        meta.eni_data.cps                                                   = cps;
        meta.eni_data.pps                                                   = pps;
        meta.eni_data.flows                                                 = flows;
        meta.eni_data.admin_state                                           = admin_state;
        meta.eni_data.pl_sip                                                = pl_sip;
        meta.eni_data.pl_sip_mask                                           = pl_sip_mask;
        meta.eni_data.pl_underlay_sip                                       = pl_underlay_sip;
        meta.u0_encap_data.underlay_dip                                     = vm_underlay_dip;
        meta.eni_data.outbound_routing_group_data.outbound_routing_group_id = outbound_routing_group_id;
        meta.eni_data.inbound_dash_encapsulation                            = inbound_dash_encapsulation;
        if (dash_tunnel_dscp_mode == dash_tunnel_dscp_mode_t.PIPE_MODEL) {
            meta.eni_data.dscp = dscp;
        }
        /* vm_vni is the encap VNI used for tunnel between inbound DPU -> VM
         * and not a VNET identifier */
        meta.u0_encap_data.vni        = vm_vni;
        meta.vnet_id                  = vnet_id;

        meta.enable_reverse_tunnel_learning = enable_reverse_tunnel_learning;
        meta.reverse_tunnel_sip             = reverse_tunnel_sip;

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

    apply {
        if (!eni.apply().hit) {
            UPDATE_COUNTER(eni_miss_drop, 0);
        }
    }
}

// direction lookup, eni lookup, etc
control dash_lookup_stage(
      inout headers_t hdr
    , inout metadata_t meta
    )
{
    action deny() {
        meta.dropped = true;
    }

    apply {
        pre_pipeline_stage.apply(hdr, meta);
        direction_lookup_stage.apply(hdr, meta);
        eni_lookup_stage.apply(hdr, meta);

        dash_eni_stage.apply(hdr, meta);

        if (meta.eni_data.admin_state == 0) {
            deny();
        }
        
        UPDATE_ENI_COUNTER(eni_rx);

        if (meta.direction == dash_direction_t.OUTBOUND) {
            UPDATE_ENI_COUNTER(eni_outbound_rx);
        } else if (meta.direction == dash_direction_t.INBOUND) {
            UPDATE_ENI_COUNTER(eni_inbound_rx);
        }

        if (meta.is_fast_path_icmp_flow_redirection_packet) {
            UPDATE_ENI_COUNTER(eni_lb_fast_path_icmp_in);
        }

        if (hdr.u0_vxlan.isValid()) {
            do_tunnel_decap(hdr, meta);
        } else if (hdr.u0_nvgre.isValid()) {
            do_tunnel_decap(hdr, meta);
        } else {
            deny();
        }
    }
}

control dash_match_stage(
      inout headers_t hdr
    , inout metadata_t meta
    )
{
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
        acl_group.apply();

        if (meta.direction == dash_direction_t.OUTBOUND) {
            meta.target_stage = dash_pipeline_stage_t.OUTBOUND_ROUTING;
            outbound.apply(hdr, meta);
        } else if (meta.direction == dash_direction_t.INBOUND) {
            meta.target_stage = dash_pipeline_stage_t.INBOUND_ROUTING;
            inbound.apply(hdr, meta);
        }

    }
}

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

    apply {

#ifndef TARGET_DPDK_PNA
        meta.rx_encap.setValid();
        meta.flow_data.setValid();
        meta.u0_encap_data.setValid();
        meta.u1_encap_data.setValid();
        meta.overlay_data.setValid();
#endif // TARGET_DPDK_PNA

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

        // If packet is from DPAPP, not do common lookup
        if (hdr.packet_meta.packet_source != dash_packet_source_t.DPAPP) {
            dash_lookup_stage.apply(hdr, meta);
        }
        else {
            meta.flow_enabled = true;
        }

        if (meta.flow_enabled) {
            conntrack_lookup_stage.apply(hdr, meta);
        }

        ha_stage.apply(hdr, meta);

        if (!meta.flow_enabled ||
            (meta.flow_sync_state == dash_flow_sync_state_t.FLOW_MISS &&
             hdr.packet_meta.packet_source == dash_packet_source_t.EXTERNAL))
        {
            dash_match_stage.apply(hdr, meta);
            if (meta.dropped) {
                drop_action();
                return;
            }
        }

        if (meta.flow_enabled) {
            conntrack_flow_handle.apply(hdr, meta);
            if (meta.to_dpapp) {
#ifdef TARGET_BMV2_V1MODEL
                standard_metadata.egress_spec = 2; //FIXME hard-code vpp port
#else //FIXME DPDK_PNA
                drop_action();
#endif // TARGET_BMV2_V1MODEL
                return;
            }
        }
        else {
            hdr.packet_meta.setInvalid();
        }

        routing_action_apply.apply(hdr, meta);

        /* Underlay routing, using meta.dst_ip_addr as lookup key */
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U1 != 0) {
            meta.dst_ip_addr = (bit<128>)hdr.u1_ipv4.dst_addr;
        }
        else if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0 != 0) {
            meta.dst_ip_addr = (bit<128>)hdr.u0_ipv4.dst_addr;
        }

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
