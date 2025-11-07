from py_model.libs.__utils import *
from py_model.libs.__table import *

from py_model.data_plane.dash_acl import *
from py_model.data_plane.dash_inbound import *
from py_model.data_plane.dash_pipeline import *
from py_model.data_plane.dash_underlay import *
from py_model.data_plane.dash_outbound import *
from py_model.data_plane.dash_conntrack import *

from py_model.data_plane.stages.ha import *
from py_model.data_plane.stages.eni_lookup import *
from py_model.data_plane.stages.trusted_vni import *
from py_model.data_plane.stages.pre_pipeline import *
from py_model.data_plane.stages.tunnel_stage import *
from py_model.data_plane.stages.inbound_routing import *
from py_model.data_plane.stages.metering_update import *
from py_model.data_plane.stages.direction_lookup import *
from py_model.data_plane.stages.conntrack_lookup import *
from py_model.data_plane.stages.outbound_routing import *
from py_model.data_plane.stages.outbound_mapping import *
from py_model.data_plane.stages.conntrack_lookup import *
from py_model.data_plane.stages.routing_action_apply import *
from py_model.data_plane.stages.outbound_pre_routing_action_apply import *

from py_model.data_plane.dash_tunnel import *
from py_model.data_plane.dash_counters import *
from py_model.data_plane.dash_underlay import *

class dash_eni_stage:
    @staticmethod
    def set_eni_attrs(cps: Annotated[int, 32],
                      pps: Annotated[int, 32],
                      flows: Annotated[int, 32],
                      admin_state: Annotated[int, 1],
                      ha_scope_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      vm_underlay_dip: Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                      vm_vni: Annotated[int, 24, {"type" : "sai_uint32_t"}],
                      vnet_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      pl_sip: Annotated[int, IPv6Address_size],
                      pl_sip_mask: Annotated[int, IPv6Address_size],
                      pl_underlay_sip: Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                      v4_meter_policy_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      v6_meter_policy_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      dash_tunnel_dscp_mode: Annotated[dash_tunnel_dscp_mode_t, {"type" : "sai_dash_tunnel_dscp_mode_t"}],                      
                      dscp: Annotated[int, 6, {"type" : "sai_uint8_t",
                                               "validonly" : "SAI_ENI_ATTR_DASH_TUNNEL_DSCP_MODE == SAI_DASH_TUNNEL_DSCP_MODE_PIPE_MODEL"}],

                      inbound_v4_stage1_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v4_stage2_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v4_stage3_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v4_stage4_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v4_stage5_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],

                      inbound_v6_stage1_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v6_stage2_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v6_stage3_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v6_stage4_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      inbound_v6_stage5_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],

                      outbound_v4_stage1_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v4_stage2_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v4_stage3_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v4_stage4_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v4_stage5_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],

                      outbound_v6_stage1_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v6_stage2_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v6_stage3_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v6_stage4_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      outbound_v6_stage5_dash_acl_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],

                      disable_fast_path_icmp_flow_redirection: Annotated[int, 1],
                      full_flow_resimulation_requested: Annotated[int, 1],
                      max_resimulated_flow_per_second: Annotated[int, 64],
                      outbound_routing_group_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      enable_reverse_tunnel_learning: Annotated[int, 1],
                      reverse_tunnel_sip: Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                      is_ha_flow_owner: Annotated[int, 1],
                      flow_table_id: Annotated[int, 16, {"type" : "sai_object_id_t"}],
                      dash_eni_mode: Annotated[dash_eni_mode_t, {"type" :  "sai_dash_eni_mode_t", "create_only" : "true"}]):

        meta.eni_data.cps = cps
        meta.eni_data.pps = pps
        meta.eni_data.flows = flows
        meta.eni_data.admin_state = admin_state
        meta.eni_data.pl_sip = pl_sip
        meta.eni_data.pl_sip_mask = pl_sip_mask
        meta.eni_data.pl_underlay_sip = pl_underlay_sip
        meta.eni_data.eni_mode = dash_eni_mode
        meta.u0_encap_data.underlay_dip = vm_underlay_dip
        meta.eni_data.outbound_routing_group_data.outbound_routing_group_id = outbound_routing_group_id
        if dash_tunnel_dscp_mode == dash_tunnel_dscp_mode_t.PIPE_MODEL:
            meta.eni_data.dscp = dscp
        # vm_vni is the encap VNI used for tunnel between inbound DPU -> VM
        # and not a VNET identifier
        meta.u0_encap_data.vni = vm_vni
        meta.vnet_id = vnet_id

        meta.enable_reverse_tunnel_learning = enable_reverse_tunnel_learning
        meta.reverse_tunnel_sip = reverse_tunnel_sip

        if meta.is_overlay_ip_v6 == 1:
            if meta.direction == dash_direction_t.OUTBOUND:
                # outbound v6 ACL groups
                meta.stage1_dash_acl_group_id = outbound_v6_stage1_dash_acl_group_id
                meta.stage2_dash_acl_group_id = outbound_v6_stage2_dash_acl_group_id
                meta.stage3_dash_gacl_group_id = outbound_v6_stage3_dash_acl_group_id
                meta.stage4_dash_acl_group_id = outbound_v6_stage4_dash_acl_group_id
                meta.stage5_dash_acl_group_id = outbound_v6_stage5_dash_acl_group_id
                meta.meter_context.meter_policy_lookup_ip = meta.dst_ip_addr
            else:
                # inbound v6 ACL groups
                meta.stage1_dash_acl_group_id = inbound_v6_stage1_dash_acl_group_id
                meta.stage2_dash_acl_group_id = inbound_v6_stage2_dash_acl_group_id
                meta.stage3_dash_acl_group_id = inbound_v6_stage3_dash_acl_group_id
                meta.stage4_dash_acl_group_id = inbound_v6_stage4_dash_acl_group_id
                meta.stage5_dash_acl_group_id = inbound_v6_stage5_dash_acl_group_id
                meta.meter_context.meter_policy_lookup_ip = meta.src_ip_addr

            meta.meter_context.meter_policy_id = v6_meter_policy_id
        else:
            if meta.direction == dash_direction_t.OUTBOUND:
                # outbound v4 ACL groups
                meta.stage1_dash_acl_group_id = outbound_v4_stage1_dash_acl_group_id
                meta.stage2_dash_acl_group_id = outbound_v4_stage2_dash_acl_group_id
                meta.stage3_dash_acl_group_id = outbound_v4_stage3_dash_acl_group_id
                meta.stage4_dash_acl_group_id = outbound_v4_stage4_dash_acl_group_id
                meta.stage5_dash_acl_group_id = outbound_v4_stage5_dash_acl_group_id
                meta.meter_context.meter_policy_lookup_ip = meta.dst_ip_addr
            else:
                # inbound v4 ACL groups
                meta.stage1_dash_acl_group_id = inbound_v4_stage1_dash_acl_group_id
                meta.stage2_dash_acl_group_id = inbound_v4_stage2_dash_acl_group_id
                meta.stage3_dash_acl_group_id = inbound_v4_stage3_dash_acl_group_id
                meta.stage4_dash_acl_group_id = inbound_v4_stage4_dash_acl_group_id
                meta.stage5_dash_acl_group_id = inbound_v4_stage5_dash_acl_group_id
                meta.meter_context.meter_policy_lookup_ip = meta.src_ip_addr

            meta.meter_context.meter_policy_id = v4_meter_policy_id

        meta.ha.ha_scope_id = ha_scope_id
        meta.fast_path_icmp_flow_redirection_disabled = disable_fast_path_icmp_flow_redirection

        meta.flow_table.id = flow_table_id
        
    eni = Table(
        key={
            "meta.eni_id": (EXACT, {"type" : "sai_object_id_t"})
        },
        actions=[
            set_eni_attrs,
            (deny, {"annotations": "@defaultonly"})
        ],
        const_default_action=deny,
        tname=f"{__qualname__}.eni",
        sai_table=SaiTable(name="eni", api="dash_eni", order=1, isobject="true",),
)

    @classmethod
    def apply(cls):
        py_log("info", "Applying table 'eni' ")
        if not cls.eni.apply()["hit"]:
            UPDATE_COUNTER("eni_miss_drop", 0)

class dash_lookup_stage:
    @classmethod
    def apply(cls):
        pre_pipeline_stage.apply()
        direction_lookup_stage.apply()
        eni_lookup_stage.apply()
        dash_eni_stage.apply()

        # Admin state check
        if meta.eni_data.admin_state == 0:
            deny()

        # Counters
        UPDATE_ENI_COUNTER("eni_rx")

        if meta.direction == dash_direction_t.OUTBOUND:
            UPDATE_ENI_COUNTER("eni_outbound_rx")
        elif meta.direction == dash_direction_t.INBOUND:
            UPDATE_ENI_COUNTER("eni_inbound_rx")

        if meta.is_fast_path_icmp_flow_redirection_packet:
            UPDATE_ENI_COUNTER("eni_lb_fast_path_icmp_in")

        # Tunnel decap
        do_tunnel_decap()

class dash_match_stage:
    @staticmethod
    def set_acl_group_attrs(ip_addr_family: Annotated[int, 32, {"type" : "sai_ip_addr_family_t",
                                                                "isresourcetype" : "true"}]):
        if ip_addr_family == 0:  # SAI_IP_ADDR_FAMILY_IPV4
            if meta.is_overlay_ip_v6 == 1:
                meta.dropped = True
        else:
            if meta.is_overlay_ip_v6 == 0:
                meta.dropped = True
                
    acl_group = Table(
        key={
            "meta.stage1_dash_acl_group_id": (EXACT, {"name" : "dash_acl_group_id"})
        },
        actions=[
            set_acl_group_attrs
        ],
        tname=f"{__qualname__}.acl_group",
        sai_table=SaiTable(name="dash_acl_group", api="dash_acl", isobject="true",),
    )

    @classmethod
    def apply(cls):
        if meta.dropped:
            return

        py_log("info", "Applying table 'acl_group' ")
        cls.acl_group.apply()

        if meta.direction == dash_direction_t.OUTBOUND:
            meta.target_stage = dash_pipeline_stage_t.OUTBOUND_ROUTING
            outbound.apply()
        elif meta.direction == dash_direction_t.INBOUND:
            meta.target_stage = dash_pipeline_stage_t.INBOUND_ROUTING
            inbound.apply()

class dash_ingress:
    @staticmethod
    def drop_action():
        if TARGET == TARGET_PYTHON_V1MODEL:
            mark_to_drop(standard_metadata)

        if TARGET == TARGET_DPDK_PNA:
            pass

    @classmethod
    def apply(cls):
        if TARGET != TARGET_DPDK_PNA:
            meta.rx_encap = encap_data_t()
            meta.flow_data = flow_data_t()
            meta.u0_encap_data = encap_data_t()
            meta.u1_encap_data = encap_data_t()
            meta.overlay_data = overlay_rewrite_data_t()

        # If packet is from DPAPP, not do common lookup
        if hdr.packet_meta.packet_source != dash_packet_source_t.DPAPP:
            dash_lookup_stage.apply()
        else:
            meta.flow_enabled = True

        if meta.flow_enabled:
            conntrack_lookup_stage.apply()

        ha_stage.apply()
        

        if (not meta.flow_enabled or
           (meta.flow_sync_state == dash_flow_sync_state_t.FLOW_MISS and
            hdr.packet_meta.packet_source == dash_packet_source_t.EXTERNAL)):

            # TODO: revisit it after inbound route HLD done
            trusted_vni_stage.apply()
            dash_match_stage.apply()

            if meta.dropped:
                cls.drop_action()
                return

        if meta.flow_enabled:
            conntrack_flow_handle.apply()
            
            if meta.to_dpapp:
                if TARGET == TARGET_PYTHON_V1MODEL:
                    standard_metadata.egress_spec = 2  # FIXME hard-code vpp port
                elif TARGET == TARGET_DPDK_PNA:
                    cls.drop_action()
                return
        else:
            hdr.packet_meta = None
        
        routing_action_apply.apply()

        # Underlay routing: using meta.dst_ip_addr as lookup key
        if meta.routing_actions & dash_routing_actions_t.ENCAP_U1 != 0:
            meta.dst_ip_addr = hdr.u1_ipv4.dst_addr
        elif meta.routing_actions & dash_routing_actions_t.ENCAP_U0 != 0:
            meta.dst_ip_addr = hdr.u0_ipv4.dst_addr

        underlay.apply()
        

        if meta.eni_data.dscp_mode == dash_tunnel_dscp_mode_t.PIPE_MODEL:
            hdr.u0_ipv4.diffserv = meta.eni_data.dscp

        metering_update_stage.apply()

        if meta.dropped:
            cls.drop_action()
        else:
            UPDATE_ENI_COUNTER("eni_tx")
            if meta.direction == dash_direction_t.OUTBOUND:
                UPDATE_ENI_COUNTER("eni_outbound_tx")
            elif meta.direction == dash_direction_t.INBOUND:
                UPDATE_ENI_COUNTER("eni_inbound_tx")
