from sai_thrift.sai_headers import *
from sai_base_test import *
from dash_pipeline_utils import P4InternalConfigTable, P4UnderlayRoutingTable
from p4_dash_utils import *

@use_flow
class SaiThriftVnetOutboundUdpPktTest(SaiHelperSimplified):
    """ Test saithrift vnet outbound"""

    def setUp(self):
        super(SaiThriftVnetOutboundUdpPktTest, self).setUp()
        self.switch_id = 5
        self.outbound_vni = 60
        self.vnet_vni = 100
        self.eni_mac = "00:cc:cc:cc:cc:cc"
        self.dst_ca_mac = "00:dd:dd:dd:dd:dd"
        self.vip = "172.16.1.100"
        self.outbound_vni = 100
        self.ca_prefix_addr = "10.1.0.0"
        self.ca_prefix_mask = "255.255.0.0"
        self.dst_ca_ip = "10.1.2.50"
        self.dst_pa_ip = "172.16.1.20"
        self.src_vm_pa_ip = "172.16.1.1"

        # SAI attribute name
        self.ip_addr_family_attr = 'ip4'
        # SAI address family
        self.sai_ip_addr_family = SAI_IP_ADDR_FAMILY_IPV4

        self.dut_mac = get_mac("veth0")
        self.neighbor_mac = get_mac("veth1")
        P4InternalConfigTable().set(neighbor_mac = self.neighbor_mac, mac = self.dut_mac)

        underlay_routing = P4UnderlayRoutingTable()
        underlay_routing.set(ip_prefix = '::'+self.dst_pa_ip, ip_prefix_len = 128, next_hop_id = 1)
        assert(underlay_routing.get(ip_prefix = '::'+self.dst_pa_ip, ip_prefix_len = 128))

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

        self.gtve = sai_thrift_global_trusted_vni_entry_t(switch_id=self.switch_id,
                vni_range=sai_thrift_u32_range_t(min=self.outbound_vni, max=self.outbound_vni))
        status = sai_thrift_create_global_trusted_vni_entry(self.client, self.gtve)
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

        print(f"\n{self.__class__.__name__} configureVnet OK")
        self.configured = True

    def trafficTest(self):

        src_vm_ip = "10.1.1.10"

        # check VIP drop
        wrong_vip = "172.16.100.100"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=wrong_vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong vip...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check routing drop
        wrong_dst_ca = "10.200.2.50"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ip_dst=wrong_dst_ca,
                                        ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong dst CA IP to verify routing drop...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check mapping drop
        wrong_dst_ca = "10.1.211.211"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ip_dst=wrong_dst_ca,
                                        ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong dst CA IP to verify mapping drop...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check forwarding
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ip_dst=self.dst_ca_ip,
                                        ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
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
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst=self.neighbor_mac,
                                        eth_src=self.dut_mac,
                                        ip_dst=self.dst_pa_ip,
                                        ip_src=self.vip,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=self.vnet_vni,
                                        inner_frame=inner_exp_pkt)

        self.pkt_exp = vxlan_exp_pkt
        print("\tSending outbound packet...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying packet...")
        verify_packet(self, self.pkt_exp, 1)
        print ("SaiThriftVnetOutboundUdpPktTest OK")

    def runTest(self):

        self.configureVnet()
        self.trafficTest()

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
            status &= sai_thrift_remove_global_trusted_vni_entry(self.client, self.gtve)
            status &= sai_thrift_remove_direction_lookup_entry(self.client, self.dle)
            status &= sai_thrift_remove_vip_entry(self.client, self.vpe)
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
            super(SaiThriftVnetOutboundUdpPktTest, self).tearDown()

        # restore default internal_config
        P4InternalConfigTable().unset()

        # remove underlay route for dst_pa_ip
        underlay_routing = P4UnderlayRoutingTable()
        underlay_routing.unset(ip_prefix = '::'+self.dst_pa_ip, ip_prefix_len = 128)
        assert(underlay_routing.get(ip_prefix = '::'+self.dst_pa_ip, ip_prefix_len = 128) == None)


class SaiThriftVnetOutboundUdpV6PktTest(SaiThriftVnetOutboundUdpPktTest):
    """ Test saithrift vnet outbound ipv6"""

    def setUp(self):
        super(SaiThriftVnetOutboundUdpV6PktTest, self).setUp()
        self.switch_id = 5
        self.outbound_vni = 60
        self.vnet_vni = 50
        self.eni_mac = "00:aa:aa:aa:aa:aa"
        self.dst_ca_mac = "00:bb:bb:bb:bb:bb"
        self.vip = "172.16.1.200"
        self.outbound_vni = 50
        self.ca_prefix_addr = "2000:aaaa::"
        self.ca_prefix_mask = "ffff:ffff:ffff:ffff:ffff:ffff:ffff:0"
        self.dst_ca_ip = "2000:aaaa::232"

        # SAI attribute name
        self.ip_addr_family_attr = 'ip6'
        # SAI address family
        self.sai_ip_addr_family = SAI_IP_ADDR_FAMILY_IPV6

    def trafficTest(self):

        src_vm_ip = "2000:aaaa::10a"

        # check VIP drop
        wrong_vip = "172.16.100.100"
        inner_pkt = simple_udpv6_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ipv6_dst=self.dst_ca_ip,
                                        ipv6_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=wrong_vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong vip...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check routing drop
        wrong_dst_ca = "2000:bbbb::232"
        inner_pkt = simple_udpv6_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ipv6_dst=wrong_dst_ca,
                                        ipv6_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong dst CA IP to verify routing drop...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check mapping drop
        wrong_dst_ca = "2000:aaaa::d3d3"
        inner_pkt = simple_udpv6_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ipv6_dst=wrong_dst_ca,
                                        ipv6_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)
        print("\tSending packet with wrong dst CA IP to verify mapping drop...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying drop...")
        verify_no_other_packets(self)

        # check forwarding
        inner_pkt = simple_udpv6_packet(eth_dst="02:02:02:02:02:02",
                                        eth_src=self.eni_mac,
                                        ipv6_dst=self.dst_ca_ip,
                                        ipv6_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.dut_mac,
                                        eth_src=self.neighbor_mac,
                                        ip_dst=self.vip,
                                        ip_src=self.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.outbound_vni,
                                        inner_frame=inner_pkt)

        inner_exp_pkt = simple_udpv6_packet(eth_dst=self.dst_ca_mac,
                                        eth_src=self.eni_mac,
                                        ipv6_dst=self.dst_ca_ip,
                                        ipv6_src=src_vm_ip)
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst=self.neighbor_mac,
                                        eth_src=self.dut_mac,
                                        ip_dst=self.dst_pa_ip,
                                        ip_src=self.vip,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=self.vnet_vni,
                                        inner_frame=inner_exp_pkt)

        self.pkt_exp = vxlan_exp_pkt
        print("\tSending outbound packet...")
        send_packet(self, 0, vxlan_pkt)
        print("\tVerifying packet...")
        verify_packet(self, self.pkt_exp, 1)
        print ("SaiThriftVnetOutboundUdpV6PktTest OK")
