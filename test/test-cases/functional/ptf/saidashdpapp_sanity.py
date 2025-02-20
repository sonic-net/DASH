from sai_thrift.sai_headers import *
from sai_base_test import *
from dash_pipeline_utils import use_flow, verify_flow, verify_no_flow

@use_flow
class SaiThriftDpappPktTest(SaiHelperSimplified):
    """ Test saithrift vnet outbound towards dpapp"""

    def setUp(self):
        super(SaiThriftDpappPktTest, self).setUp()
        self.switch_id = 5
        self.outbound_vni = 60
        self.vnet_vni = 100
        self.eni_mac = "00:cc:cc:cc:cc:cc"
        self.our_mac = "00:00:02:03:04:05"
        self.dst_ca_mac = "00:dd:dd:dd:dd:dd"
        self.vip = "172.16.1.100"
        self.ca_prefix_addr = "10.1.0.0"
        self.ca_prefix_mask = "255.255.0.0"
        self.dst_ca_ip = "10.1.2.50"
        self.dst_pa_ip = "172.16.1.20"
        self.src_vm_pa_ip = "172.16.1.1"
        self.dpapp_port = 2

        # SAI attribute name
        self.ip_addr_family_attr = 'ip4'
        # SAI address family
        self.sai_ip_addr_family = SAI_IP_ADDR_FAMILY_IPV4

        # Flag to indicate whether configureVnet were successful or not.
        self.configured = False

    def configureVnet(self):
        """Create VNET configuration"""

        vip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                      addr=sai_thrift_ip_addr_t(ip4=self.vip))
        self.vpe = sai_thrift_vip_entry_t(switch_id=self.switch_id, vip=vip)

        status = sai_thrift_create_vip_entry(self.client, self.vpe,
                                             action=SAI_VIP_ENTRY_ACTION_ACCEPT)
        assert(status == SAI_STATUS_SUCCESS)

        self.dle = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=self.outbound_vni)
        status = sai_thrift_create_direction_lookup_entry(self.client, self.dle,
                                                          action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
        assert(status == SAI_STATUS_SUCCESS)

        self.in_acl_group_id = sai_thrift_create_dash_acl_group(self.client,
                                                                ip_addr_family=self.sai_ip_addr_family)
        assert (self.in_acl_group_id != SAI_NULL_OBJECT_ID)
        self.out_acl_group_id = sai_thrift_create_dash_acl_group(self.client,
                                                                 ip_addr_family=self.sai_ip_addr_family)
        assert (self.out_acl_group_id != SAI_NULL_OBJECT_ID)

        self.vnet = sai_thrift_create_vnet(self.client, vni=self.vnet_vni)
        assert (self.vnet != SAI_NULL_OBJECT_ID)

        self.outbound_routing_group = sai_thrift_create_outbound_routing_group(self.client, disabled=False)
        assert (self.outbound_routing_group != SAI_NULL_OBJECT_ID)

        vm_underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                                  addr=sai_thrift_ip_addr_t(ip4=self.src_vm_pa_ip))
        pl_sip_mask = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6,
                addr=sai_thrift_ip_addr_t(ip6="2001:0db8:85a3:0000:0000:0000:0000:0000"))
        pl_sip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV6,
                addr=sai_thrift_ip_addr_t(ip6="2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        pl_underlay_sip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                addr=sai_thrift_ip_addr_t(ip4="10.0.0.18"))
        self.eni = sai_thrift_create_eni(self.client, cps=10000,
                                         pps=100000, flows=100000,
                                         admin_state=True,
                                         ha_scope_id=0,
                                         vm_underlay_dip=vm_underlay_dip,
                                         vm_vni=9,
                                         vnet_id=self.vnet,
                                         pl_sip = pl_sip,
                                         pl_sip_mask = pl_sip_mask,
                                         pl_underlay_sip = pl_underlay_sip,
                                         v4_meter_policy_id = 0,
                                         v6_meter_policy_id = 0,
                                         dash_tunnel_dscp_mode=SAI_DASH_TUNNEL_DSCP_MODE_PRESERVE_MODEL,
                                         dscp=0,
                                         # TODO: Enable ACL rule
                                         #inbound_v4_stage1_dash_acl_group_id = self.in_acl_group_id,
                                         #inbound_v4_stage2_dash_acl_group_id = self.in_acl_group_id,
                                         #inbound_v4_stage3_dash_acl_group_id = self.in_acl_group_id,
                                         #inbound_v4_stage4_dash_acl_group_id = self.in_acl_group_id,
                                         #inbound_v4_stage5_dash_acl_group_id = self.in_acl_group_id,
                                         #outbound_v4_stage1_dash_acl_group_id = self.out_acl_group_id,
                                         #outbound_v4_stage2_dash_acl_group_id = self.out_acl_group_id,
                                         #outbound_v4_stage3_dash_acl_group_id = self.out_acl_group_id,
                                         #outbound_v4_stage4_dash_acl_group_id = self.out_acl_group_id,
                                         #outbound_v4_stage5_dash_acl_group_id = self.out_acl_group_id,
                                         inbound_v4_stage1_dash_acl_group_id = 0,
                                         inbound_v4_stage2_dash_acl_group_id = 0,
                                         inbound_v4_stage3_dash_acl_group_id = 0,
                                         inbound_v4_stage4_dash_acl_group_id = 0,
                                         inbound_v4_stage5_dash_acl_group_id = 0,
                                         outbound_v4_stage1_dash_acl_group_id = 0,
                                         outbound_v4_stage2_dash_acl_group_id = 0,
                                         outbound_v4_stage3_dash_acl_group_id = 0,
                                         outbound_v4_stage4_dash_acl_group_id = 0,
                                         outbound_v4_stage5_dash_acl_group_id = 0,
                                         inbound_v6_stage1_dash_acl_group_id = 0,
                                         inbound_v6_stage2_dash_acl_group_id = 0,
                                         inbound_v6_stage3_dash_acl_group_id = 0,
                                         inbound_v6_stage4_dash_acl_group_id = 0,
                                         inbound_v6_stage5_dash_acl_group_id = 0,
                                         outbound_v6_stage1_dash_acl_group_id = 0,
                                         outbound_v6_stage2_dash_acl_group_id = 0,
                                         outbound_v6_stage3_dash_acl_group_id = 0,
                                         outbound_v6_stage4_dash_acl_group_id = 0,
                                         outbound_v6_stage5_dash_acl_group_id = 0,
                                         disable_fast_path_icmp_flow_redirection = 0,
                                         full_flow_resimulation_requested=False,
                                         max_resimulated_flow_per_second=0,
                                         outbound_routing_group_id=self.outbound_routing_group)

        self.eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=self.switch_id, address = self.eni_mac)
        status = sai_thrift_create_eni_ether_address_map_entry(self.client,
                                                               eni_ether_address_map_entry=self.eam,
                                                               eni_id=self.eni)
        assert(status == SAI_STATUS_SUCCESS)

        dip = sai_thrift_ip_address_t(addr_family=self.sai_ip_addr_family,
                                      addr=sai_thrift_ip_addr_t(**{self.ip_addr_family_attr: self.dst_ca_ip}))

        # TODO: Enable ACL rule for IPv6
        if self.sai_ip_addr_family == SAI_IP_ADDR_FAMILY_IPV4:
            self.out_acl_rule_id = sai_thrift_create_dash_acl_rule(self.client, dash_acl_group_id=self.out_acl_group_id, priority=10,
                                                                action=SAI_DASH_ACL_RULE_ACTION_PERMIT)
            assert(status == SAI_STATUS_SUCCESS)

        ca_prefix = sai_thrift_ip_prefix_t(addr_family=self.sai_ip_addr_family,
                                            addr=sai_thrift_ip_addr_t(**{self.ip_addr_family_attr: self.ca_prefix_addr}),
                                            mask=sai_thrift_ip_addr_t(**{self.ip_addr_family_attr: self.ca_prefix_mask}))
        self.ore = sai_thrift_outbound_routing_entry_t(switch_id=self.switch_id, outbound_routing_group_id=self.outbound_routing_group, destination=ca_prefix)
        status = sai_thrift_create_outbound_routing_entry(self.client, self.ore,
                                                          action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET,
                                                          dst_vnet_id=self.vnet,
                                                          meter_class_or=0, meter_class_and=-1,
                                                          dash_tunnel_id=0, routing_actions_disabled_in_flow_resimulation = 0)
        assert(status == SAI_STATUS_SUCCESS)

        underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                               addr=sai_thrift_ip_addr_t(ip4=self.dst_pa_ip))
        self.ocpe = sai_thrift_outbound_ca_to_pa_entry_t(switch_id=self.switch_id, dst_vnet_id=self.vnet, dip=dip)
        status = sai_thrift_create_outbound_ca_to_pa_entry(self.client, self.ocpe, action=SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_TUNNEL_MAPPING,
                                                           underlay_dip = underlay_dip,
                                                           overlay_dmac=self.dst_ca_mac, use_dst_vnet_vni = True,
                                                           meter_class_or=0, flow_resimulation_requested = False, dash_tunnel_id=0,
                                                           routing_actions_disabled_in_flow_resimulation = 0)
        assert(status == SAI_STATUS_SUCCESS)


        print(f"\n{self.__class__.__name__} configureVnet OK\n")
        self.configured = True

    def trafficUdpTest(self):

        src_vm_ip = "10.1.1.10"
        outer_smac = "00:00:05:06:06:06"

        # check forwarding
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.our_mac,
                                        eth_src=outer_smac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)

        inner_exp_pkt = simple_udp_packet(eth_dst=self.dst_ca_mac,
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip)
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst="00:00:00:00:00:00",
                                        eth_src="00:00:00:00:00:00",
                                        ip_dst=self.dst_pa_ip,
                                        ip_src=self.vip,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=self.vnet_vni,
                                        inner_frame=inner_exp_pkt)

        self.pkt_exp = vxlan_exp_pkt
        print("\tSending outbound udp packet...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying packet...")
        verify_packet(self, self.pkt_exp, 0)
        print("\tVerifying flow created...")
        verify_flow(self.eni_mac, self.vnet & 0xffff, inner_pkt)
        print(f"{self.__class__.__name__} trafficUdpTest OK\n")

    def trafficTcpTest(self):

        src_vm_ip = "10.1.1.10"
        outer_smac = "00:00:05:06:06:06"
        tcp_src_port = 0x1234
        tcp_dst_port = 0x50

        # customer packet: tcp SYN
        inner_pkt = simple_tcp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=self.eni_mac,
                                      ip_dst=self.dst_ca_ip,
                                      ip_src=src_vm_ip,
                                      tcp_sport=tcp_src_port,
                                      tcp_dport=tcp_dst_port,
                                      tcp_flags="S")
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.our_mac,
                                        eth_src=outer_smac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)

        inner_exp_pkt = simple_tcp_packet(eth_dst=self.dst_ca_mac,
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip,
                                        tcp_sport=tcp_src_port,
                                        tcp_dport=tcp_dst_port,
                                        tcp_flags="S")
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst="00:00:00:00:00:00",
                                        eth_src="00:00:00:00:00:00",
                                        ip_dst=self.dst_pa_ip,
                                        ip_src=self.vip,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=self.vnet_vni,
                                        inner_frame=inner_exp_pkt)

        self.pkt_exp = vxlan_exp_pkt
        print("\tSending outbound packet TCP SYN ...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying packet...")
        verify_packet(self, self.pkt_exp, 0)
        print("\tVerifying flow created...")
        verify_flow(self.eni_mac, self.vnet & 0xffff, inner_pkt)

        # customer packet: tcp FIN
        inner_pkt = simple_tcp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=self.eni_mac,
                                      ip_dst=self.dst_ca_ip,
                                      ip_src=src_vm_ip,
                                      tcp_sport=tcp_src_port,
                                      tcp_dport=tcp_dst_port,
                                      tcp_flags="F")
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.our_mac,
                                        eth_src=outer_smac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)

        inner_exp_pkt = simple_tcp_packet(eth_dst=self.dst_ca_mac,
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip,
                                        tcp_sport=tcp_src_port,
                                        tcp_dport=tcp_dst_port,
                                        tcp_flags="F")
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst="00:00:00:00:00:00",
                                        eth_src="00:00:00:00:00:00",
                                        ip_dst=self.dst_pa_ip,
                                        ip_src=self.vip,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=self.vnet_vni,
                                        inner_frame=inner_exp_pkt)

        self.pkt_exp = vxlan_exp_pkt
        print("\tSending outbound packet TCP FIN ...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying packet...")
        verify_packet(self, self.pkt_exp, 0)
        print("\tVerifying flow deleted...")
        verify_no_flow(self.eni_mac, self.vnet & 0xffff, inner_pkt)

        print(f"{self.__class__.__name__} trafficTcpTest OK\n")

    def runTest(self):

        self.configureVnet()
        self.trafficUdpTest()
        self.trafficTcpTest()

    def tearDown(self):

        status = True
        try:
            # Delete entries in the reverse order
            status &= sai_thrift_remove_outbound_ca_to_pa_entry(self.client, self.ocpe)
            status &= sai_thrift_remove_outbound_routing_entry(self.client, self.ore)
            if self.sai_ip_addr_family == SAI_IP_ADDR_FAMILY_IPV4:
                status &= sai_thrift_remove_dash_acl_rule(self.client, self.out_acl_rule_id)
            status &= sai_thrift_remove_eni_ether_address_map_entry(self.client, self.eam)
            status &= sai_thrift_remove_eni(self.client, self.eni)
            status &= sai_thrift_remove_vnet(self.client, self.vnet)
            status &= sai_thrift_remove_dash_acl_group(self.client, self.out_acl_group_id)
            status &= sai_thrift_remove_dash_acl_group(self.client, self.in_acl_group_id)
            status &= sai_thrift_remove_direction_lookup_entry(self.client, self.dle)
            status &= sai_thrift_remove_vip_entry(self.client, self.vpe)
            status &= sai_thrift_remove_route_entry(self.client, self.pa_route_entry)
            if self.configured:
                # Skip remove status verification if the configuration creation failed
                self.assertEqual(status, SAI_STATUS_SUCCESS)
            print(f"{self.__class__.__name__} tearDown OK")
        except:
            # Ignore errors if configuration were unsuccessful
            if self.configured:
                raise
        finally:
            # Run standard PTF teardown
            super(SaiThriftDpappPktTest, self).tearDown()


