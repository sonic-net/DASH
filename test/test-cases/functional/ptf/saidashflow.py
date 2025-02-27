# DASH Flow Test
#
# Test cases covered:
#   0. Flow hit (ENI AMC, VNI, 5 tuple), UDP packet, flow action: NONE
#   1. Flow miss (ENI AMC, VNI, 5 tuple), UDP packet, flow action: NONE
#   2. Flow hit (ENI AMC, VNI, 5 tuple), UDP packet, flow action: ENCAP_U0
#   3. Flow hit (ENI AMC, VNI, 5 tuple), UDP packet, flow action: SET_DMAC  (overlay dmac rewrite)
#   4. Flow hit (ENI AMC, VNI, 5 tuple), UDP packet, flow action: ENCAP_U0 | SET_DMAC
# SET_SMAC, SNAT, DNAT, SNAT_PORT, DNAT_PORT are not yet implemented so they are not covered in the test cases.
#   NAT46 and NAT64 are not yet supported (ipv6 address not supported) so they are not covered in the test cases.
#   ENCAP_U1 implementation seems to have some error.
import copy

from sai_thrift.sai_headers import *
from sai_base_test import *

from sai_dash_utils import VnetAPI
from p4_dash_utils import *

# Flow test class. 
class FlowTest(object):
    def __init__(self,
                saithrift,
                name = "Flow Test",
                # Parameters for the flow table. We always create a new flow table 
                max_flow_count = 1000, 
                dash_flow_enabled_key = (SAI_DASH_FLOW_ENABLED_KEY_ENI_MAC | SAI_DASH_FLOW_ENABLED_KEY_VNI | SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL | SAI_DASH_FLOW_ENABLED_KEY_SRC_IP | SAI_DASH_FLOW_ENABLED_KEY_DST_IP | SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT | SAI_DASH_FLOW_ENABLED_KEY_DST_PORT),
                flow_ttl_in_milliseconds = 1,
                # Indicate that an entry should be created
                create_entry = False,
                switch_id = 0,
                vnet_vni = 100,
                vnet_id = None,
                outbound_vni = 60,
                eni_mac = "00:00:00:00:00:00",
                outer_smac = "00:00:00:00:00:00",
                outer_dmac = "00:00:00:00:00:00",
                outer_sip = "0.0.0.0",
                outer_dip = "0.0.0.0",
                inner_smac = "00:00:00:00:00:00",
                inner_dmac = "00:00:00:00:00:00",
                inner_sip = "10.1.2.51",
                inner_dip = "10.1.2.50",
                protocol = 17,
                inner_sport = 1234,
                inner_dport = 90,
                priority = 1,
                action = SAI_DASH_FLOW_ACTION_NONE,
                exp_receive = False,
                # Expected packet fields (overide values)
                exp_u0_smac = "00:00:00:00:00:00",
                exp_u0_dmac = "00:00:00:00:00:00",
                exp_u0_sip = None,
                exp_u0_dip = None,
                exp_u1_smac = "00:00:00:00:00:00",
                exp_u1_dmac = "00:00:00:00:00:00",
                exp_u1_sip = None,
                exp_u1_dip = None,
                exp_inner_smac = "00:00:00:00:00:00",
                exp_inner_dmac = "00:00:00:00:00:00",
                exp_inner_sip = None,
                exp_inner_dip = None,
                exp_inner_sport = None,
                exp_inner_dport = None):
        
        # Initialize parameters of the test. For setting the state of switch target, e.g. creating entries, they will done in the runTest function.
        self.saithrift = saithrift
        self.name = name
        self.client = saithrift.client
        self.ft = None
        self.max_flow_count = max_flow_count
        self.dash_flow_enabled_key = dash_flow_enabled_key
        self.flow_ttl_in_milliseconds = flow_ttl_in_milliseconds
        self.fe = None
        self.create_entry = create_entry
        self.switch_id = switch_id
        self.outbound_vni = outbound_vni
        self.vnet_vni = vnet_vni
        self.vnet_id = vnet_id
        self.eni_mac = eni_mac
        self.outer_smac = outer_smac
        self.outer_dmac = outer_dmac
        self.outer_sip = outer_sip
        self.outer_dip = outer_dip
        self.inner_smac = inner_smac
        self.inner_dmac = inner_dmac
        self.inner_sip = inner_sip
        self.inner_dip = inner_dip
        self.protocol = protocol
        self.inner_sport = inner_sport
        self.inner_dport = inner_dport
        self.priority = priority
        self.action = action
        self.exp_receive = exp_receive
        self.exp_u0_smac = exp_u0_smac
        self.exp_u0_dmac = exp_u0_dmac
        self.exp_u0_sip = exp_u0_sip
        self.exp_u0_dip = exp_u0_dip
        self.exp_u1_smac = exp_u1_smac
        self.exp_u1_dmac = exp_u1_dmac
        self.exp_u1_sip = exp_u1_sip
        self.exp_u1_dip = exp_u1_dip
        self.exp_inner_smac = exp_inner_smac
        self.exp_inner_dmac = exp_inner_dmac
        self.exp_inner_sip = exp_inner_sip
        self.exp_inner_dip = exp_inner_dip
        self.exp_inner_sport = exp_inner_sport
        self.exp_inner_dport = exp_inner_dport


        self.meta = copy.copy(self.__dict__)
        # del self.meta["saithrift"]

    # Since we may adjust the flow table and flow entry for each test, we do not add them to the teardown stack.
    def create_flow_table(self, *args, **kwargs):
        # print("Creating flow table...\n", args)
        ft = sai_thrift_create_flow_table(self.client, *args, **kwargs)
        assert (ft != SAI_NULL_OBJECT_ID)
        return ft

    def remove_flow_table(self):
        # print("Removing flow table...\n", self.ft.__repr__())
        status = sai_thrift_remove_flow_table(self.client, self.ft)
        assert (status == SAI_STATUS_SUCCESS)
        return status

    def create_flow_entry(self, entry, *args, **kwargs):
        # print("Creating flow entry...\n", self.fe.__repr__())
        status = sai_thrift_create_flow_entry(self.client, entry, *args, **kwargs)
        assert (status == SAI_STATUS_SUCCESS)
        return status
    
    def remove_flow_entry(self):
        # print("Removing flow entry...\n", self.fe.__repr__())
        status= sai_thrift_remove_flow_entry(self.client, self.fe)
        assert (status == SAI_STATUS_SUCCESS)
        return status


    def runTest(self):
        self.ft = self.create_flow_table(max_flow_count = self.max_flow_count, 
                                  dash_flow_enabled_key = self.dash_flow_enabled_key, 
                                  flow_ttl_in_milliseconds = self.flow_ttl_in_milliseconds)
        if self.create_entry == True:
            # Create flow entry
            sip_t = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                        addr=sai_thrift_ip_addr_t(ip4=self.inner_sip))
            dip_t = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                    addr=sai_thrift_ip_addr_t(ip4=self.inner_dip))
            exp_u0_dip_t = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                    addr=sai_thrift_ip_addr_t(ip4=self.exp_u0_dip))
            exp_u0_sip_t = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                    addr=sai_thrift_ip_addr_t(ip4=self.exp_u0_sip))  
            # Assemble flow entry
            self.fe = sai_thrift_flow_entry_t(switch_id=self.switch_id, eni_mac=self.eni_mac, vnet_id=self.vnet_vni, ip_proto=self.protocol, src_ip=sip_t, dst_ip=dip_t, src_port=self.inner_sport, dst_port=self.inner_dport)
            self.create_flow_entry(
                entry = self.fe, 
                # Flow basic metadata 
                action = SAI_FLOW_ENTRY_ACTION_SET_FLOW_ENTRY_ATTR,
                version=4,
                dash_direction=SAI_DASH_DIRECTION_OUTBOUND,
                dash_flow_action=self.action,
                meter_class=None,
                is_unidirectional_flow=True,
                dash_flow_sync_state=SAI_DASH_FLOW_SYNC_STATE_FLOW_SYNCED,
                # Reverse flow key
                reverse_flow_eni_mac=self.eni_mac,
                reverse_flow_vnet_id=self.vnet_vni,
                reverse_flow_ip_proto=self.protocol,
                reverse_flow_src_ip=dip_t,
                reverse_flow_dst_ip=sip_t,
                reverse_flow_src_port=self.inner_dport,
                reverse_flow_dst_port=self.inner_sport,
                # reverse_flow_dst_ip_is_v6=False,
                # Flow encap related attributes
                underlay0_vnet_id=self.vnet_vni,
                underlay0_sip=exp_u0_sip_t,
                underlay0_dip=exp_u0_dip_t,
                underlay0_smac=self.exp_u0_smac,
                underlay0_dmac=self.exp_u0_dmac,
                underlay0_dash_encapsulation=SAI_DASH_ENCAPSULATION_VXLAN,
                underlay1_vnet_id=None,
                underlay1_sip=None,
                underlay1_dip=None,
                underlay1_smac="00:00:00:00:00:00",
                underlay1_dmac="00:00:00:00:00:00",
                underlay1_dash_encapsulation=SAI_DASH_ENCAPSULATION_INVALID,
                # Flow overlay rewrite related attributes
                dst_mac=self.exp_inner_dmac,
                # sip=self.exp_inner_sip,
                # dip=self.exp_inner_dip,
                sip=None,
                dip=None,
                sip_mask=None,
                dip_mask=None,
                # dip_is_v6=False,
                # Extra flow metadata
                vendor_metadata=None,
                flow_data_pb=None
                )
        
        # Assemble test packet sent by VM
        inner_pkt = simple_udp_packet(                            
            eth_dst=self.inner_dmac,
            eth_src=self.inner_smac,
            ip_dst=self.exp_inner_dip,
            ip_src=self.exp_inner_sip,
            udp_sport=self.exp_inner_sport,
            udp_dport=self.exp_inner_dport
            )
        vxlan_pkt = simple_vxlan_packet(
            eth_dst=self.outer_dmac,
            ip_dst=self.outer_dip,
            ip_src=self.outer_sip,
            udp_sport=11638,
            with_udp_chksum=False,
            vxlan_vni=self.outbound_vni,
            inner_frame=inner_pkt)

        # Assemble expected packet from ENI
        inner_exp_pkt = simple_udp_packet(
            eth_dst=self.exp_inner_dmac,
            eth_src=self.exp_inner_smac,
            ip_dst=self.exp_inner_dip,
            ip_src=self.exp_inner_sip,
            udp_sport=self.exp_inner_sport,
            udp_dport=self.exp_inner_dport)
        if self.action & SAI_DASH_FLOW_ACTION_ENCAP_U0:
            vxlan_exp_pkt = simple_vxlan_packet(
                eth_dst=self.exp_u0_dmac,
                eth_src=self.exp_u0_smac,
                ip_dst=self.exp_u0_dip,
                ip_src=self.exp_u0_sip,
                udp_sport=0, # hard-coded in dash_tunnel.p4
                udp_dport=4789, # hard-coded in dash_tunnel.p4
                with_udp_chksum=False,
                vxlan_vni=self.vnet_vni,
                inner_frame=inner_exp_pkt)
            pkt_exp = vxlan_exp_pkt
            if self.action & SAI_DASH_FLOW_ACTION_ENCAP_U1:
                vxlan_exp_pkt = simple_vxlan_packet(
                    eth_dst=self.exp_u1_dmac,
                    eth_src=self.exp_u1_smac,
                    ip_dst=self.exp_u1_dip,
                    ip_src=self.exp_u1_sip,
                    udp_sport=0, # hard-coded in dash_tunnel.p4
                    udp_dport=4789, # hard-coded in dash_tunnel.p4
                    with_udp_chksum=False,
                    vxlan_vni=self.vnet_vni,
                    inner_frame=pkt_exp)
                pkt_exp = vxlan_exp_pkt
        else: 
            # print("Expected packet without encap...")
            pkt_exp = inner_exp_pkt

        # print("Sending packet...\n", vxlan_pkt.__repr__())
        print("Sending packet...")
        send_packet(self.saithrift, 0, vxlan_pkt)
        if self.exp_receive:
            # print("Verifying packet...", pkt_exp.__repr__())
            print("Verifying packet...")
            verify_packet(self.saithrift, pkt_exp, 0)
        else:
            print("Verifying drop...")
            verify_no_other_packets(self.saithrift)
        print(f"{self.__class__.__name__} {self.name} OK\n")

        # Clean up flow table and flow entry
        if self.create_entry == True:
            self.remove_flow_entry()
        self.remove_flow_table()
        

@use_flow
class SaiThriftDashFlowTest(VnetAPI):
    """ DASH Flow Test"""

    def create_entry(self, create_func, remove_func, entry, *args, **kwargs):
        status = create_func(self.client, entry, *args, **kwargs)
        assert (status == SAI_STATUS_SUCCESS)
        self.add_teardown_obj(remove_func, (self.client, entry))
        return status

    def create_obj(self, create_func, remove_func, *args, **kwargs):
        obj = create_func(self.client, *args, **kwargs)
        assert (obj != SAI_NULL_OBJECT_ID)
        self.add_teardown_obj(remove_func, (self.client, obj))
        return obj

    # Set up the switch to support a Vnet with an ENI
    def setUpSwitch(self):
        self.switch_id = 5
        self.outbound_vni = 60 # reserved vni for outbound direction lookup
        self.vnet_vni = 100
        self.eni_mac = "00:cc:cc:cc:cc:cc"
        self.underlay_dmac = "00:dd:dd:dd:dd:dd"
        self.dst_ca_mac = "00:ee:ee:ee:ee:ee"
        self.vip = "172.16.1.100"
        self.dst_ca_ip = "10.1.2.50"
        self.dst_pa_ip = "172.16.1.20"
        self.dst_port = 90
        self.vm_mac = "00:00:02:03:04:05"
        self.src_vm_ca_ip = "10.1.2.51"
        self.src_vm_pa_ip = "172.16.1.1"
        self.src_vm_port = 1234

        self.overlay_write_smac = "00:aa:aa:aa:aa:aa"
        self.overlay_write_dmac = "00:bb:bb:bb:bb:bb"

        # Add a VIP entry (pre-pipeline)
        vip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                      addr=sai_thrift_ip_addr_t(ip4=self.vip))
        self.vpe = sai_thrift_vip_entry_t(
            switch_id=self.switch_id, vip=vip)
        self.create_entry(sai_thrift_create_vip_entry, sai_thrift_remove_vip_entry,
                          self.vpe, action=SAI_VIP_ENTRY_ACTION_ACCEPT)


        # Add a direction lookup entry
        self.dle = sai_thrift_direction_lookup_entry_t(
            switch_id=self.switch_id, vni=self.outbound_vni)
        self.create_entry(sai_thrift_create_direction_lookup_entry, sai_thrift_remove_direction_lookup_entry,
                          self.dle, action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)


        # Create a Vnet entry (in outbound mapping stage)
        self.vnet_id = self.create_obj(
            sai_thrift_create_vnet, sai_thrift_remove_vnet, vni=self.vnet_vni)

        self.outbound_routing_group = self.create_obj(
            sai_thrift_create_outbound_routing_group, sai_thrift_remove_outbound_routing_group, disabled=False)

        vm_underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                                  addr=sai_thrift_ip_addr_t(ip4=self.src_vm_pa_ip))
        pl_sip_mask = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6,
                addr=sai_thrift_ip_addr_t(ip6="2001:0db8:85a3:0000:0000:0000:0000:0000"))
        pl_sip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6,
                addr=sai_thrift_ip_addr_t(ip6="2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        pl_underlay_sip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                addr=sai_thrift_ip_addr_t(ip4="10.0.0.18"))
        self.eni = self.create_obj(sai_thrift_create_eni, sai_thrift_remove_eni, cps=10000,
                                pps=100000, flows=100000,
                                admin_state=True,
                                ha_scope_id=0,
                                vm_underlay_dip=vm_underlay_dip,
                                vm_vni=9,
                                vnet_id=self.vnet_vni,
                                pl_sip = pl_sip,
                                pl_sip_mask = pl_sip_mask,
                                pl_underlay_sip = pl_underlay_sip,
                                v4_meter_policy_id=0,
                                v6_meter_policy_id=0,
                                dash_tunnel_dscp_mode=SAI_DASH_TUNNEL_DSCP_MODE_PRESERVE_MODEL,
                                dscp=0,
                                inbound_v4_stage1_dash_acl_group_id=self.in_v4_stage1_acl_group_id,
                                inbound_v4_stage2_dash_acl_group_id=self.in_v4_stage2_acl_group_id,
                                inbound_v4_stage3_dash_acl_group_id=self.in_v4_stage3_acl_group_id,
                                inbound_v4_stage4_dash_acl_group_id=0,
                                inbound_v4_stage5_dash_acl_group_id=0,
                                outbound_v4_stage1_dash_acl_group_id=self.out_v4_stage1_acl_group_id,
                                outbound_v4_stage2_dash_acl_group_id=self.out_v4_stage2_acl_group_id,
                                outbound_v4_stage3_dash_acl_group_id=self.out_v4_stage3_acl_group_id,
                                outbound_v4_stage4_dash_acl_group_id=0,
                                outbound_v4_stage5_dash_acl_group_id=0,
                                inbound_v6_stage1_dash_acl_group_id=self.in_v6_stage1_acl_group_id,
                                inbound_v6_stage2_dash_acl_group_id=self.in_v6_stage2_acl_group_id,
                                inbound_v6_stage3_dash_acl_group_id=self.in_v6_stage3_acl_group_id,
                                inbound_v6_stage4_dash_acl_group_id=0,
                                inbound_v6_stage5_dash_acl_group_id=0,
                                outbound_v6_stage1_dash_acl_group_id=self.out_v6_stage1_acl_group_id,
                                outbound_v6_stage2_dash_acl_group_id=self.out_v6_stage2_acl_group_id,
                                outbound_v6_stage3_dash_acl_group_id=self.out_v6_stage3_acl_group_id,
                                outbound_v6_stage4_dash_acl_group_id=0,
                                outbound_v6_stage5_dash_acl_group_id=0,
                                disable_fast_path_icmp_flow_redirection=0,
                                full_flow_resimulation_requested=False,
                                max_resimulated_flow_per_second=0,
                                outbound_routing_group_id=0)

        self.eam = sai_thrift_eni_ether_address_map_entry_t(
            switch_id=self.switch_id, address=self.vm_mac)

        self.create_entry(sai_thrift_create_eni_ether_address_map_entry,
                          sai_thrift_remove_eni_ether_address_map_entry, self.eam, eni_id=self.eni)

        dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                      addr=sai_thrift_ip_addr_t(ip4=self.dst_ca_ip))

        ca_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                           addr=sai_thrift_ip_addr_t(
                                               ip4="10.1.0.0"),
                                           mask=sai_thrift_ip_addr_t(ip4="255.255.0.0"))
        self.ore = sai_thrift_outbound_routing_entry_t(
            switch_id=self.switch_id, outbound_routing_group_id=self.outbound_routing_group, destination=ca_prefix)

        self.create_entry(sai_thrift_create_outbound_routing_entry, sai_thrift_remove_outbound_routing_entry,
                          self.ore, action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET, dst_vnet_id=self.vnet_id,
                          meter_class_or=0, meter_class_and=-1, dash_tunnel_id=0, routing_actions_disabled_in_flow_resimulation = 0)

        underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                               addr=sai_thrift_ip_addr_t(ip4=self.dst_pa_ip))
        self.ocpe = sai_thrift_outbound_ca_to_pa_entry_t(
            switch_id=self.switch_id, dst_vnet_id=self.vnet_id, dip=dip)

        self.create_entry(sai_thrift_create_outbound_ca_to_pa_entry, sai_thrift_remove_outbound_ca_to_pa_entry,
                          self.ocpe, action=SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_TUNNEL_MAPPING,
                          underlay_dip=underlay_dip, overlay_dmac=self.dst_ca_mac, use_dst_vnet_vni=True,
                          meter_class_or=0, dash_tunnel_id=0,
                          flow_resimulation_requested = False, routing_actions_disabled_in_flow_resimulation = 0)

    def setupTest(self):
        # Test case 0: flow hit (5 tuple) 
        # action: none
        # expected: pass
        self.tests.append(FlowTest(saithrift = self,
                        name = "FlowHitActionNone",
                        create_entry = True,
                        switch_id = self.switch_id,
                        vnet_vni = self.vnet_vni,
                        vnet_id = self.vnet_id,
                        outbound_vni = self.outbound_vni,
                        eni_mac = self.vm_mac,
                        outer_smac = "00:00:00:00:00:00",
                        outer_dmac = "00:00:00:00:00:00",
                        outer_sip = self.src_vm_pa_ip,
                        outer_dip = self.vip,
                        inner_smac = self.vm_mac,
                        inner_dmac = self.dst_ca_mac,
                        protocol = 17,
                        inner_sip = self.src_vm_ca_ip,
                        inner_dip = self.dst_ca_ip,
                        inner_sport = self.src_vm_port,
                        inner_dport = self.dst_port,
                        priority = 1,
                        action = SAI_DASH_FLOW_ACTION_NONE,
                        exp_receive = True,
                        exp_inner_smac = self.vm_mac,
                        exp_inner_dmac = self.dst_ca_mac,
                        exp_inner_sip = self.src_vm_ca_ip,
                        exp_inner_dip = self.dst_ca_ip,
                        exp_inner_sport = self.src_vm_port,
                        exp_inner_dport = self.dst_port
                        ))
            
        # Test case 1: flow miss (5 tuple) 
        # action: none
        # expected: pass
        self.tests.append(FlowTest(saithrift = self,
                        name = "FlowMissActionNone",
                        create_entry = False,
                        switch_id = self.switch_id,
                        vnet_vni = self.vnet_vni,
                        vnet_id = self.vnet_id,
                        outbound_vni = self.outbound_vni,
                        eni_mac = self.vm_mac,
                        outer_smac = "00:00:00:00:00:00",
                        outer_dmac = "00:00:00:00:00:00",
                        outer_sip = self.src_vm_pa_ip,
                        outer_dip = self.vip,
                        inner_smac = self.vm_mac,
                        inner_dmac = self.dst_ca_mac,
                        protocol = 17,
                        inner_sip = self.src_vm_ca_ip,
                        inner_dip = self.dst_ca_ip,
                        inner_sport = self.src_vm_port,
                        inner_dport = self.dst_port,
                        priority = 1,
                        action = SAI_DASH_FLOW_ACTION_NONE,
                        exp_receive = False,
                        exp_inner_smac = self.vm_mac,
                        exp_inner_dmac = self.dst_ca_mac,
                        exp_inner_sip = self.src_vm_ca_ip,
                        exp_inner_dip = self.dst_ca_ip,
                        exp_inner_sport = self.src_vm_port,
                        exp_inner_dport = self.dst_port
                        ))

        # Test case 2: flow hit (5 tuple) 
        # action: encap_u0
        # expected: pass
        self.tests.append(FlowTest(saithrift = self,
                        name = "FlowHitActionEncapU0",   
                        create_entry = True,
                        switch_id = self.switch_id,
                        vnet_vni = self.vnet_vni,
                        vnet_id = self.vnet_id,
                        outbound_vni = self.outbound_vni,
                        eni_mac = self.vm_mac,
                        outer_smac = "00:00:00:00:00:00",
                        outer_dmac = "00:00:00:00:00:00",
                        outer_sip = self.src_vm_pa_ip,
                        outer_dip = self.vip,
                        inner_smac = self.vm_mac,
                        inner_dmac = self.dst_ca_mac,
                        protocol = 17,
                        inner_sip = self.src_vm_ca_ip,
                        inner_dip = self.dst_ca_ip,
                        inner_sport = self.src_vm_port,
                        inner_dport = self.dst_port,
                        priority = 1,
                        action = SAI_DASH_FLOW_ACTION_ENCAP_U0,
                        exp_receive = True,
                        exp_u0_smac = self.eni_mac,
                        exp_u0_dmac = self.underlay_dmac,
                        exp_u0_sip = self.src_vm_pa_ip,
                        exp_u0_dip = self.dst_pa_ip,
                        exp_inner_smac = self.vm_mac,
                        exp_inner_dmac = self.dst_ca_mac,
                        exp_inner_sip = self.src_vm_ca_ip,
                        exp_inner_dip = self.dst_ca_ip,
                        exp_inner_sport = self.src_vm_port,
                        exp_inner_dport = self.dst_port
                        ))

        # # Test case xx: flow hit (5 tuple) 
        # # action: encap_u0 | encap_u1
        # # expected: pass
        # self.tests.append(FlowTest(saithrift = self,
        #                 name = "FlowHitActionEncapU0EncapU1",   
        #                 create_entry = True,
        #                 switch_id = self.switch_id,
        #                 vnet_vni = self.vnet_vni,
        #                 vnet_id = self.vnet_id,
        #                 outbound_vni = self.outbound_vni,
        #                 eni_mac = self.vm_mac,
        #                 outer_smac = "00:00:00:00:00:00",
        #                 outer_dmac = "00:00:00:00:00:00",
        #                 outer_sip = self.src_vm_pa_ip,
        #                 outer_dip = self.vip,
        #                 inner_smac = self.vm_mac,
        #                 inner_dmac = self.dst_ca_mac,
        #                 protocol = 17,
        #                 inner_sip = self.src_vm_ca_ip,
        #                 inner_dip = self.dst_ca_ip,
        #                 inner_sport = self.src_vm_port,
        #                 inner_dport = self.dst_port,
        #                 priority = 1,
        #                 action = SAI_DASH_FLOW_ACTION_ENCAP_U0 | SAI_DASH_FLOW_ACTION_ENCAP_U1,
        #                 exp_receive = True,
        #                 exp_u0_smac = self.eni_mac,
        #                 exp_u0_dmac = self.underlay_dmac,
        #                 exp_u0_sip = self.src_vm_pa_ip,
        #                 exp_u0_dip = self.dst_pa_ip,
        #                 exp_u1_smac = "11:22:33:44:55:66",
        #                 exp_u1_dmac = "77:88:99:aa:bb:cc",
        #                 exp_u1_sip = "200.0.1.2",
        #                 exp_u1_dip = "200.3.4.5",
        #                 exp_inner_smac = self.vm_mac,
        #                 exp_inner_dmac = self.dst_ca_mac,
        #                 exp_inner_sip = self.src_vm_ca_ip,
        #                 exp_inner_dip = self.dst_ca_ip,
        #                 exp_inner_sport = self.src_vm_port,
        #                 exp_inner_dport = self.dst_port
        #                 ))

        # Test case 3: flow hit (5 tuple) 
        # action: overlay dmac rewrite
        # expected: pass
        self.tests.append(FlowTest(saithrift = self,
                        name = "FlowHitActionSetDmac",
                        create_entry = True,
                        switch_id = self.switch_id,
                        vnet_vni = self.vnet_vni,
                        vnet_id = self.vnet_id,
                        outbound_vni = self.outbound_vni,
                        eni_mac = self.vm_mac,
                        outer_smac = "00:00:00:00:00:00",
                        outer_dmac = "00:00:00:00:00:00",
                        outer_sip = self.src_vm_pa_ip,
                        outer_dip = self.vip,
                        inner_smac = self.vm_mac,
                        inner_dmac = self.dst_ca_mac,
                        protocol = 17,
                        inner_sip = self.src_vm_ca_ip,
                        inner_dip = self.dst_ca_ip,
                        inner_sport = self.src_vm_port,
                        inner_dport = self.dst_port,
                        priority = 1,
                        action = SAI_DASH_FLOW_ACTION_SET_DMAC,
                        exp_receive = True,
                        exp_inner_smac = self.vm_mac,
                        exp_inner_dmac = self.overlay_write_dmac,
                        exp_inner_sip = self.src_vm_ca_ip,
                        exp_inner_dip = self.dst_ca_ip,
                        exp_inner_sport = self.src_vm_port,
                        exp_inner_dport = self.dst_port
                        ))
        
        # Test case 4: flow hit (5 tuple) 
        # action: encap_u0 + overlay dmac rewrite
        # expected: pass
        self.tests.append(FlowTest(saithrift = self,
                        name = "FlowHitActionEncapU0SetDmac",
                        create_entry = True,
                        switch_id = self.switch_id,
                        vnet_vni = self.vnet_vni,
                        vnet_id = self.vnet_id,
                        outbound_vni = self.outbound_vni,
                        eni_mac = self.vm_mac,
                        outer_smac = "00:00:00:00:00:00",
                        outer_dmac = "00:00:00:00:00:00",
                        outer_sip = self.src_vm_pa_ip,
                        outer_dip = self.vip,
                        inner_smac = self.vm_mac,
                        inner_dmac = self.dst_ca_mac,
                        protocol = 17,
                        inner_sip = self.src_vm_ca_ip,
                        inner_dip = self.dst_ca_ip,
                        inner_sport = self.src_vm_port,
                        inner_dport = self.dst_port,
                        priority = 1,
                        action = SAI_DASH_FLOW_ACTION_ENCAP_U0 | SAI_DASH_FLOW_ACTION_SET_DMAC,
                        exp_receive = True,
                        exp_u0_smac = self.eni_mac,
                        exp_u0_dmac = self.underlay_dmac,
                        exp_u0_sip = self.src_vm_pa_ip,
                        exp_u0_dip = self.dst_pa_ip,
                        exp_inner_smac = self.vm_mac,
                        exp_inner_dmac = self.overlay_write_dmac,
                        exp_inner_sip = self.src_vm_ca_ip,
                        exp_inner_dip = self.dst_ca_ip,
                        exp_inner_sport = self.src_vm_port,
                        exp_inner_dport = self.dst_port
                        ))

        # Test case 5: flow hit (5 tuple) 
        # action: encap_u0 + overlay smac rewrite
        # expected: pass
        # status: failed due to lack of implementation for overlay smac rewrite
        # self.tests.append(FlowTest(saithrift = self,
        #                 create_entry = True,
        #                 switch_id = self.switch_id,
        #                 vnet_vni = self.vnet_vni,
        #                 vnet_id = self.vnet_id,
        #                 outbound_vni = self.outbound_vni,
        #                 eni_mac = self.vm_mac,
        #                 outer_smac = "00:00:00:00:00:00",
        #                 outer_dmac = "00:00:00:00:00:00",
        #                 outer_sip = self.src_vm_pa_ip,
        #                 outer_dip = self.vip,
        #                 inner_smac = self.vm_mac,
        #                 inner_dmac = self.dst_ca_mac,
        #                 protocol = 17,
        #                 inner_sip = self.src_vm_ca_ip,
        #                 inner_dip = self.dst_ca_ip,
        #                 inner_sport = self.src_vm_port,
        #                 inner_dport = self.dst_port,
        #                 priority = 1,
        #                 action = SAI_DASH_FLOW_ACTION_ENCAP_U0 | SAI_DASH_FLOW_ACTION_SET_DMAC,
        #                 exp_receive = True,
        #                 exp_u0_smac = self.eni_mac,
        #                 exp_u0_dmac = self.underlay_dmac,
        #                 exp_u0_sip = self.src_vm_pa_ip,
        #                 exp_u0_dip = self.dst_pa_ip,
        #                 exp_inner_smac = self.overlay_write_smac,
        #                 exp_inner_dmac = self.dst_ca_mac,
        #                 exp_inner_sip = self.src_vm_ca_ip,
        #                 exp_inner_dip = self.dst_ca_ip,
        #                 exp_inner_sport = self.src_vm_port,
        #                 exp_inner_dport = self.dst_port
        #                 ))

    def setUp(self):
        super(SaiThriftDashFlowTest, self).setUp()
        self.cleaned_up = False
        self.teardown_stack = []
        self.tests = []

        try:
            self.setUpSwitch()
            self.setupTest()
        except AssertionError as ae:
            self.destroy_teardown_obj()
            raise ae

    def runTest(self):
        for test in self.tests:
            print("\n\n")
            test.runTest()

    def tearDown(self):
        super(SaiThriftDashFlowTest, self).tearDown()