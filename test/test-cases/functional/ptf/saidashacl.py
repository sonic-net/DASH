import copy

from sai_thrift.sai_headers import *
from sai_base_test import *

from sai_dash_utils import VnetAPI


class Tag(object):
    def __init__(self, saithrift, ip, mask, tag):
        self.saithrift = saithrift
        self.ip = ip
        self.mask = mask
        self.tag = tag
        self.prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                        addr=sai_thrift_ip_addr_t(ip4=self.ip),
                                        mask=sai_thrift_ip_addr_t(ip4=self.mask))
        self.src_tag_entry = sai_thrift_src_tag_entry_t(switch_id=self.saithrift.switch_id, sip=self.prefix)
        self.saithrift.create_entry(sai_thrift_create_src_tag_entry,
                                    sai_thrift_remove_src_tag_entry, self.src_tag_entry, tag_map=self.tag)
        self.dst_tag_entry = sai_thrift_dst_tag_entry_t(switch_id=self.saithrift.switch_id, dip=self.prefix)
        self.saithrift.create_entry(sai_thrift_create_dst_tag_entry,
                                    sai_thrift_remove_dst_tag_entry, self.dst_tag_entry, tag_map=self.tag)


class AclRuleTest(object):
    def __init__(self,
                 saithrift,
                 acl_group,
                 protocol = 17,
                 stag = None,
                 dtag = None,
                 sip = None,
                 dip = None,
                 src_port = 1234,
                 dst_port = 80,
                 priority = 1,
                 action = SAI_DASH_ACL_RULE_ACTION_DENY,
                 exp_receive = False,
                 test_sip = None,
                 test_dip = None):
        self.saithrift = saithrift
        self.acl_group = acl_group
        self.protocol = protocol
        self.sip = sip
        self.dip = dip
        self.priority = priority
        self.action = action
        self.exp_receive = exp_receive
        self.stag = stag
        self.dtag = dtag
        self.src_port = src_port
        self.dst_port = dst_port
        if self.dip:
            dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                            addr=sai_thrift_ip_addr_t(ip4=self.dip))
        if self.sip:
            sip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                        addr=sai_thrift_ip_addr_t(ip4=self.sip))
        if self.acl_group is not None:
            self.saithrift.create_obj(sai_thrift_create_dash_acl_rule,
                                      sai_thrift_remove_dash_acl_rule,
                                      dash_acl_group_id=self.acl_group,
                                      protocol=self.protocol,
                                      src_tag=self.stag,
                                      src_tag_mask=self.stag,
                                      dst_tag=self.dtag,
                                      dst_tag_mask=self.dtag,
                                      sip=sip,
                                      dip=dip,
                                      src_port = self.src_port,
                                      dst_port = self.dst_port,
                                      priority=self.priority,
                                      action=self.action)
        if test_sip:
            self.test_sip = test_sip
        else:
            self.test_sip = self.sip
        if test_dip:
            self.test_dip = test_dip
        else:
            self.test_dip = self.dip
        self.meta = copy.copy(self.__dict__)
        del self.meta["saithrift"]

    def runTest(self):
        inner_pkt = simple_udp_packet(eth_dst=self.saithrift.dst_ca_mac,
                                      eth_src=self.saithrift.eni_mac,
                                      ip_dst=self.test_dip,
                                      ip_src=self.test_sip,
                                      udp_sport=self.src_port,
                                      udp_dport=self.dst_port
                                      )
        vxlan_pkt = simple_vxlan_packet(eth_dst=self.saithrift.our_mac,
                                        ip_dst=self.saithrift.vip,
                                        ip_src=self.saithrift.src_vm_pa_ip,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=self.saithrift.outbound_vni,
                                        inner_frame=inner_pkt)
        inner_exp_pkt = simple_udp_packet(eth_dst=self.saithrift.dst_ca_mac,
                                          eth_src=self.saithrift.eni_mac,
                                          ip_dst=self.test_dip,
                                          ip_src=self.test_sip,
                                          udp_sport=self.src_port,
                                          udp_dport=self.dst_port)
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst="00:00:00:00:00:00",
                                            eth_src="00:00:00:00:00:00",
                                            ip_dst=self.saithrift.dst_pa_ip,
                                            ip_src=self.saithrift.vip,
                                            udp_sport=0,
                                            with_udp_chksum=False,
                                            vxlan_vni=self.saithrift.vnet_vni,
                                            inner_frame=inner_exp_pkt)
        vxlan_exp_pkt[IP].chksum = 0
        vxlan_exp_pkt[IP][UDP][VXLAN].flags = 0

        pkt_exp = vxlan_exp_pkt
        print("Sending packet...\n", vxlan_pkt.__repr__())
        send_packet(self.saithrift, 0, vxlan_pkt)
        print("\n")
        if self.exp_receive:
            print("Verifying packet...\n", pkt_exp.__repr__())
            verify_packet(self.saithrift, pkt_exp, 0)
        else:
            print("Verifying drop...")
            verify_no_other_packets(self.saithrift)
        print("\n")
        print("Acl test {} OK".format(self.meta))


class SaiThriftDashAclTest(VnetAPI):
    """ Test saithrift DASH ACL"""

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

    def setUpSwitch(self):
        self.switch_id = 5
        self.outbound_vni = 60
        self.vnet_vni = 100
        self.eni_mac = "00:cc:cc:cc:cc:cc"
        self.our_mac = "00:00:02:03:04:05"
        self.dst_ca_mac = "00:dd:dd:dd:dd:dd"
        self.vip = "172.16.1.100"
        self.outbound_vni = 100
        self.dst_ca_ip = "10.1.2.50"
        self.dst_pa_ip = "172.16.1.20"
        self.src_vm_pa_ip = "172.16.1.1"

        vip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                      addr=sai_thrift_ip_addr_t(ip4=self.vip))
        self.vpe = sai_thrift_vip_entry_t(
            switch_id=self.switch_id, vip=vip)
        self.create_entry(sai_thrift_create_vip_entry, sai_thrift_remove_vip_entry,
                          self.vpe, action=SAI_VIP_ENTRY_ACTION_ACCEPT)

        self.dle = sai_thrift_direction_lookup_entry_t(
            switch_id=self.switch_id, vni=self.outbound_vni)
        self.create_entry(sai_thrift_create_direction_lookup_entry, sai_thrift_remove_direction_lookup_entry,
                          self.dle, action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)

        self.in_v4_stage1_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        self.in_v4_stage2_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        self.in_v4_stage3_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)

        self.out_v4_stage1_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        self.out_v4_stage2_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        self.out_v4_stage3_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)

        self.in_v6_stage1_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
        self.in_v6_stage2_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
        self.in_v6_stage3_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)

        self.out_v6_stage1_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
        self.out_v6_stage2_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
        self.out_v6_stage3_acl_group_id = self.create_obj(
            sai_thrift_create_dash_acl_group, sai_thrift_remove_dash_acl_group, ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)

        self.vnet = self.create_obj(
            sai_thrift_create_vnet, sai_thrift_remove_vnet, vni=self.vnet_vni)

        vm_underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                                  addr=sai_thrift_ip_addr_t(ip4=self.src_vm_pa_ip))
        self.eni = self.create_obj(sai_thrift_create_eni, sai_thrift_remove_eni, cps=10000,
                                   pps=100000, flows=100000,
                                   admin_state=True,
                                   vm_underlay_dip=vm_underlay_dip,
                                   vm_vni=9,
                                   vnet_id=self.vnet,
                                   v4_meter_policy_id=0,
                                   v6_meter_policy_id=0,
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
                                   outbound_v6_stage5_dash_acl_group_id=0)

        self.eam = sai_thrift_eni_ether_address_map_entry_t(
            switch_id=self.switch_id, address=self.eni_mac)

        self.create_entry(sai_thrift_create_eni_ether_address_map_entry,
                          sai_thrift_remove_eni_ether_address_map_entry, self.eam, eni_id=self.eni)

        dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                      addr=sai_thrift_ip_addr_t(ip4=self.dst_ca_ip))

        ca_prefix = sai_thrift_ip_prefix_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                           addr=sai_thrift_ip_addr_t(
                                               ip4="10.1.0.0"),
                                           mask=sai_thrift_ip_addr_t(ip4="255.255.0.0"))
        self.ore = sai_thrift_outbound_routing_entry_t(
            switch_id=self.switch_id, eni_id=self.eni, destination=ca_prefix)

        self.create_entry(sai_thrift_create_outbound_routing_entry, sai_thrift_remove_outbound_routing_entry,
                          self.ore, action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET, dst_vnet_id=self.vnet,
                          meter_policy_en=False, meter_class=0)

        underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                               addr=sai_thrift_ip_addr_t(ip4=self.dst_pa_ip))
        self.ocpe = sai_thrift_outbound_ca_to_pa_entry_t(
            switch_id=self.switch_id, dst_vnet_id=self.vnet, dip=dip)

        self.create_entry(sai_thrift_create_outbound_ca_to_pa_entry, sai_thrift_remove_outbound_ca_to_pa_entry,
                          self.ocpe, underlay_dip=underlay_dip, overlay_dmac=self.dst_ca_mac, use_dst_vnet_vni=True,
                          meter_class=0, meter_class_override=False)

    def setupTest(self):
        self.tests.append(AclRuleTest(self,
                                      acl_group=self.out_v4_stage1_acl_group_id,
                                      protocol=17,
                                      sip="10.1.1.1",
                                      dip=self.dst_ca_ip,
                                      priority=1,
                                      action=SAI_DASH_ACL_RULE_ACTION_PERMIT,
                                      exp_receive=True))
        self.tests.append(AclRuleTest(self,
                                      acl_group=self.out_v4_stage1_acl_group_id,
                                      protocol=17,
                                      sip="10.1.1.2",
                                      dip=self.dst_ca_ip,
                                      priority=2,
                                      action=SAI_DASH_ACL_RULE_ACTION_DENY,
                                      exp_receive=False))

        self.tag1 = Tag(self, ip = "10.1.2.4", mask = "255.255.255.254", tag = 0x11)
        self.tests.append(AclRuleTest(self,
                                      acl_group=self.out_v4_stage1_acl_group_id,
                                      protocol=17,
                                      stag = 0x1,
                                      priority=3,
                                      src_port=1234,
                                      action=SAI_DASH_ACL_RULE_ACTION_PERMIT,
                                      exp_receive=True,
                                      test_sip = "10.1.2.4",
                                      test_dip = self.dst_ca_ip))
        self.tests.append(AclRuleTest(self,
                                      acl_group=None,
                                      exp_receive=True,
                                      src_port=1234,
                                      test_sip = "10.1.2.5",
                                      test_dip = self.dst_ca_ip))
        self.tests.append(AclRuleTest(self,
                                      acl_group=self.out_v4_stage1_acl_group_id,
                                      protocol=17,
                                      stag = 0x10,
                                      priority=3,
                                      src_port=4321,
                                      action=SAI_DASH_ACL_RULE_ACTION_DENY,
                                      exp_receive=False,
                                      test_sip = "10.1.2.4",
                                      test_dip = self.dst_ca_ip))
        self.tests.append(AclRuleTest(self,
                                      acl_group=None,
                                      exp_receive=False,
                                      src_port=4321,
                                      test_sip = "10.1.2.5",
                                      test_dip = self.dst_ca_ip))
        self.tests.append(AclRuleTest(self,
                                      acl_group=None,
                                      exp_receive=False,
                                      src_port=1111,
                                      test_sip = "10.1.2.4",
                                      test_dip = self.dst_ca_ip))

        self.tag2 = Tag(self, ip = self.dst_ca_ip, mask = "255.255.255.255", tag = 0x100)
        self.tests.append(AclRuleTest(self,
                                      acl_group=self.out_v4_stage1_acl_group_id,
                                      protocol=17,
                                      dtag = 0x100,
                                      priority=3,
                                      src_port=2222,
                                      action=SAI_DASH_ACL_RULE_ACTION_PERMIT,
                                      exp_receive=True,
                                      test_sip = "10.1.2.6",
                                      test_dip = self.dst_ca_ip))

    def setUp(self):
        super(SaiThriftDashAclTest, self).setUp()
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
        super(SaiThriftDashAclTest, self).tearDown()
