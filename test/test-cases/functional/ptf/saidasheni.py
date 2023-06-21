# Copyright 2022-present Intel Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Thrift SAI interface ENI tests
"""

from unittest import skipIf

from sai_dash_utils import *
from sai_thrift.sai_headers import *


class CreateDeleteEniTest(VnetAPI):
    """
    Verifies ENI creation/deletion and association with MAC and VNI

    Configuration:
    Empty configuration
    """

    def setUp(self):
        super(CreateDeleteEniTest, self).setUp()

        self.cps = 10000         # ENI connections per second
        self.pps = 100000        # ENI packets per seconds
        self.flows = 100000      # ENI flows
        self.admin_state = True  # ENI admin state
        self.vm_vni = 10         # ENI VM VNI
        self.eni_mac = '00:11:22:33:44:55'  # ENI MAC address
        self.vm_underlay_dip = sai_ipaddress('192.168.1.5')  # ENI VM underlay DIP

        self.sip = '10.0.1.2'  # PA validation entry SIP address

    def runTest(self):
        # Not all tests are interdependent,
        # so they must be run in the following sequence:

        # Create verification
        self.createInOutAclGroupsTest()
        self.createVnetTest()
        self.createDirectionLookupTest()
        self.createEniTest()
        self.createEniEtherAddressMapTest()
        if not test_param_get('target') == 'bmv2':
            # Issue #233
            self.createInboundRoutingEntryTest()
            self.createPaValidationTest()
        self.createOutboundRoutingEntryTest()
        self.createCa2PaEntryTest()

        # Attributes verification
        if not test_param_get('target') == 'bmv2':
            # TODO: add issue
            self.dashAclGroupAttributesTest()
            self.vnetAttributesTest()
            self.directionLookupAttributesTest()
            self.eniGetAttributesTest()
            self.eniSetAndGetAttributesTest()
            self.eniEtherAddressMapAttributesTest()
            self.inboundRoutingEntryAttributesTest()
            self.paValidationEntryAttributesTest()
            self.outboundRoutingEntryAttributesTest()
            self.outboundCa2PaEntryAttributesTest()

        # Remove verification
        if not test_param_get('target') == 'bmv2':
            # TODO: add issue
            self.deleteVnetWhenMapExistTest()
            self.deleteEniWhenMapExistTest()
        # verify all entries can be removed with status success
        self.destroy_teardown_obj()
        # clear teardown_objects not to remove all entries again in tearDown
        self.teardown_objects.clear()

    def tearDown(self):
        super(CreateDeleteEniTest, self).tearDown()

    def createInOutAclGroupsTest(self):
        """
        Verifies ACL groups creation needed for ENI creation

        Note: test should be run before createEniTest
        """

        self.in_acl_group_id = self.dash_acl_group_create()
        self.out_acl_group_id = self.dash_acl_group_create()

    def createVnetTest(self):
        """
        Verifies VNET creation

        Note: test should be run before createEniTest
        """

        # vnet for ENI creation
        self.vm_vnet = self.vnet_create(vni=self.vm_vni)

        # src_vnet for Inbound routing entry
        self.outbound_vnet = self.vnet_create(vni=10000)

    def createDirectionLookupTest(self):
        """
        Verifies Direction Lookup creation
        """
        self.dir_lookup = self.direction_lookup_create(vni=self.vm_vni)

    def createEniTest(self):
        """
        Verifies ENI entry creation

        Note: ENI entry deletion is in deleteEniTest
        """

        self.eni = self.eni_create(cps=self.cps,
                                   pps=self.pps,
                                   flows=self.flows,
                                   admin_state=self.admin_state,
                                   vm_underlay_dip=self.vm_underlay_dip,
                                   vm_vni=self.vm_vni,
                                   vnet_id=self.vm_vnet,
                                   v4_meter_policy_id=0,
                                   v6_meter_policy_id=0,
                                   inbound_v4_stage1_dash_acl_group_id=self.in_acl_group_id,
                                   inbound_v4_stage2_dash_acl_group_id=self.in_acl_group_id,
                                   inbound_v4_stage3_dash_acl_group_id=self.in_acl_group_id,
                                   inbound_v4_stage4_dash_acl_group_id=self.in_acl_group_id,
                                   inbound_v4_stage5_dash_acl_group_id=self.in_acl_group_id,
                                   outbound_v4_stage1_dash_acl_group_id=self.out_acl_group_id,
                                   outbound_v4_stage2_dash_acl_group_id=self.out_acl_group_id,
                                   outbound_v4_stage3_dash_acl_group_id=self.out_acl_group_id,
                                   outbound_v4_stage4_dash_acl_group_id=self.out_acl_group_id,
                                   outbound_v4_stage5_dash_acl_group_id=self.out_acl_group_id,
                                   inbound_v6_stage1_dash_acl_group_id=0,
                                   inbound_v6_stage2_dash_acl_group_id=0,
                                   inbound_v6_stage3_dash_acl_group_id=0,
                                   inbound_v6_stage4_dash_acl_group_id=0,
                                   inbound_v6_stage5_dash_acl_group_id=0,
                                   outbound_v6_stage1_dash_acl_group_id=0,
                                   outbound_v6_stage2_dash_acl_group_id=0,
                                   outbound_v6_stage3_dash_acl_group_id=0,
                                   outbound_v6_stage4_dash_acl_group_id=0,
                                   outbound_v6_stage5_dash_acl_group_id=0)

    def createEniEtherAddressMapTest(self):
        """
        Verifies Eni Ether Address Map entry creation

        Note: test should be run after createEniTest
        """

        self.eni_mac_map_entry = self.eni_mac_map_create(eni_id=self.eni,
                                                         mac=self.eni_mac)

    def createInboundRoutingEntryTest(self):
        """
        Verifies Inbound routing entry creation

        Note: test should be run after createEniTest
        """

        self.inbound_routing_entry = self.inbound_routing_decap_validate_create(
            eni_id=self.eni, vni=self.vm_vni,
            sip=self.sip, sip_mask="255.255.255.0",
            src_vnet_id=self.outbound_vnet
        )

    def createPaValidationTest(self):
        """
        Verifies PA validation entry creation

        Note: test should be run after createEniTest
        """

        self.pa_valid_entry = self.pa_validation_create(sip=self.sip,
                                                        vnet_id=self.outbound_vnet)

    def createOutboundRoutingEntryTest(self):
        """
        Verifies Outbound routing entry creation

        Note: test should be run after createEniTest
        """
        self.overlay_ip = "192.168.2.22"

        self.outbound_routing_entry = self.outbound_routing_vnet_direct_create(
            eni_id=self.eni,
            lpm="192.168.2.0/24",
            dst_vnet_id=self.outbound_vnet,
            overlay_ip=self.overlay_ip)
        # TODO: add counter

    def createCa2PaEntryTest(self):
        """
        Verifies Outbound CA to PA entry creation

        Note: test should be run after createOutboundRoutingEntryTest
        """

        self.underlay_dip = '192.168.10.10'
        self.overlay_dmac = '55:44:33:22:11:00'

        self.ca_to_pa_entry = self.outbound_ca_to_pa_create(
            dst_vnet_id=self.outbound_vnet,
            dip=self.overlay_ip,
            underlay_dip=self.underlay_dip,
            overlay_dmac=self.overlay_dmac,
            use_dst_vnet_vni=True
        )
        # TODO: add counter

    def dashAclGroupAttributesTest(self):
        """
        Verifies getting and setting Dash ACL group entry attributes

        Note: createInOutAclGroupsTest should be run first
        """
        # verify Dash ACL group entry original attributes
        attr = sai_thrift_get_dash_acl_group_attribute(self.client,
                                                       self.in_acl_group_id,
                                                       ip_addr_family=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['ip_addr_family'], SAI_IP_ADDR_FAMILY_IPV4)

        # set and verify new values
        try:
            sai_thrift_set_dash_acl_group_attribute(self.client,
                                                    self.in_acl_group_id,
                                                    ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_dash_acl_group_attribute(self.client,
                                                           self.in_acl_group_id,
                                                           ip_addr_family=True)
            self.assertEqual(attr['ip_addr_family'], SAI_IP_ADDR_FAMILY_IPV6)
        finally:
            # set original value
            sai_thrift_set_dash_acl_group_attribute(self.client,
                                                    self.in_acl_group_id,
                                                    ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_dash_acl_group_attribute(self.client,
                                                           self.in_acl_group_id,
                                                           ip_addr_family=True)
            self.assertEqual(attr['ip_addr_family'], SAI_IP_ADDR_FAMILY_IPV4)

    def vnetAttributesTest(self):
        """
        Verifies getting and setting VNET entry attributes

        Note: createVnetTest should be run first
        """
        # verify VNET entry original attributes
        attr = sai_thrift_get_vnet_attribute(self.client,
                                             self.vm_vnet,
                                             vni=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['vni'], self.vm_vni)

        # set and verify new values
        test_vni = 632
        try:
            sai_thrift_set_vnet_attribute(self.client,
                                          self.vm_vnet,
                                          vni=test_vni)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_vnet_attribute(self.client,
                                                 self.vm_vnet,
                                                 vni=True)
            self.assertEqual(attr['vni'], test_vni)
        finally:
            # set original value
            sai_thrift_set_vnet_attribute(self.client,
                                          self.vm_vnet,
                                          vni=self.vm_vni)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_vnet_attribute(self.client,
                                                 self.vm_vnet,
                                                 vni=True)
            self.assertEqual(attr['vni'], self.vm_vni)

    def directionLookupAttributesTest(self):
        """
        Verifies getting Direction lookup entry attributes

        Note: createDirectionLookupTest should be run first
        """
        # verify Direction lookup entry original attributes
        attr = sai_thrift_get_direction_lookup_entry_attribute(self.client,
                                                               self.dir_lookup,
                                                               action=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['action'], SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)

        # setting new value cannot be verified as only one action
        # for direction lookup is available (SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)

    def eniGetAttributesTest(self):
        """
        Verifies getting ENI entry attributes

        Note: createEniTest should be run first to create ENI entry
        """
        # verify attributes initially created ENI
        attr = sai_thrift_get_eni_attribute(self.client,
                                            self.eni,
                                            cps=True,
                                            pps=True,
                                            flows=True,
                                            admin_state=True,
                                            vm_underlay_dip=True,
                                            vm_vni=True,
                                            vnet_id=True,
                                            inbound_v4_stage1_dash_acl_group_id=True,
                                            inbound_v4_stage2_dash_acl_group_id=True,
                                            inbound_v4_stage3_dash_acl_group_id=True,
                                            inbound_v4_stage4_dash_acl_group_id=True,
                                            inbound_v4_stage5_dash_acl_group_id=True,
                                            inbound_v6_stage1_dash_acl_group_id=True,
                                            inbound_v6_stage2_dash_acl_group_id=True,
                                            inbound_v6_stage3_dash_acl_group_id=True,
                                            inbound_v6_stage4_dash_acl_group_id=True,
                                            inbound_v6_stage5_dash_acl_group_id=True,
                                            outbound_v4_stage1_dash_acl_group_id=True,
                                            outbound_v4_stage2_dash_acl_group_id=True,
                                            outbound_v4_stage3_dash_acl_group_id=True,
                                            outbound_v4_stage4_dash_acl_group_id=True,
                                            outbound_v4_stage5_dash_acl_group_id=True,
                                            outbound_v6_stage1_dash_acl_group_id=True,
                                            outbound_v6_stage2_dash_acl_group_id=True,
                                            outbound_v6_stage3_dash_acl_group_id=True,
                                            outbound_v6_stage4_dash_acl_group_id=True,
                                            outbound_v6_stage5_dash_acl_group_id=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        self.assertEqual(attr['cps'], self.cps)
        self.assertEqual(attr['pps'], self.pps)
        self.assertEqual(attr['flows'], self.flows)
        self.assertEqual(attr['admin_state'], self.admin_state)
        self.assertEqual(attr['vm_underlay_dip'], self.vm_underlay_dip.addr.ip4)
        self.assertEqual(attr['vm_vni'], self.vm_vni)
        self.assertEqual(attr['vnet_id'], self.vm_vnet)
        self.assertEqual(attr['inbound_v4_stage1_dash_acl_group_id'], self.in_acl_group_id)
        self.assertEqual(attr['inbound_v4_stage2_dash_acl_group_id'], self.in_acl_group_id)
        self.assertEqual(attr['inbound_v4_stage3_dash_acl_group_id'], self.in_acl_group_id)
        self.assertEqual(attr['inbound_v4_stage4_dash_acl_group_id'], self.in_acl_group_id)
        self.assertEqual(attr['inbound_v4_stage5_dash_acl_group_id'], self.in_acl_group_id)
        self.assertEqual(attr['inbound_v6_stage1_dash_acl_group_id'], 0)
        self.assertEqual(attr['inbound_v6_stage2_dash_acl_group_id'], 0)
        self.assertEqual(attr['inbound_v6_stage3_dash_acl_group_id'], 0)
        self.assertEqual(attr['inbound_v6_stage4_dash_acl_group_id'], 0)
        self.assertEqual(attr['inbound_v6_stage5_dash_acl_group_id'], 0)
        self.assertEqual(attr['outbound_v4_stage1_dash_acl_group_id'], self.out_acl_group_id)
        self.assertEqual(attr['outbound_v4_stage2_dash_acl_group_id'], self.out_acl_group_id)
        self.assertEqual(attr['outbound_v4_stage3_dash_acl_group_id'], self.out_acl_group_id)
        self.assertEqual(attr['outbound_v4_stage4_dash_acl_group_id'], self.out_acl_group_id)
        self.assertEqual(attr['outbound_v4_stage5_dash_acl_group_id'], self.out_acl_group_id)
        self.assertEqual(attr['outbound_v6_stage1_dash_acl_group_id'], 0)
        self.assertEqual(attr['outbound_v6_stage2_dash_acl_group_id'], 0)
        self.assertEqual(attr['outbound_v6_stage3_dash_acl_group_id'], 0)
        self.assertEqual(attr['outbound_v6_stage4_dash_acl_group_id'], 0)
        self.assertEqual(attr['outbound_v6_stage5_dash_acl_group_id'], 0)

    def eniSetAndGetAttributesTest(self):
        """
        Verifies setting ENI entry attributes

        Note: createEniTest should be run first to create ENI entry
        """

        test_cps = self.cps * 2
        test_pps = self.pps * 2
        test_flows = self.flows * 2
        test_admin_state = False
        test_vm_vni = 5

        test_vm_underlay_dip = sai_ipaddress('172.2.1.5')

        test_vnet = self.vnet_create(vni=test_vm_vni)

        test_ipv6_in_acl_group_id = self.dash_acl_group_create(ipv6=True)
        test_ipv6_out_acl_group_id = self.dash_acl_group_create(ipv6=True)

        try:
            # set and verify new cps value
            sai_thrift_set_eni_attribute(self.client, self.eni, cps=test_cps)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, cps=True)
            self.assertEqual(attr['cps'], test_cps)

            # set and verify new pps value
            sai_thrift_set_eni_attribute(self.client, self.eni, pps=test_pps)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, pps=True)
            self.assertEqual(attr['pps'], test_pps)

            # set and verify new flow value
            sai_thrift_set_eni_attribute(self.client, self.eni, flows=test_flows)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, flows=True)
            self.assertEqual(attr['flows'], test_flows)

            # set and verify new admin_state value
            sai_thrift_set_eni_attribute(self.client, self.eni, admin_state=test_admin_state)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, admin_state=True)
            self.assertEqual(attr['admin_state'], test_admin_state)

            # set and verify new vm_underlay_dip value
            sai_thrift_set_eni_attribute(self.client, self.eni, vm_underlay_dip=test_vm_underlay_dip)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, vm_underlay_dip=True)
            self.assertEqual(attr['vm_underlay_dip'], test_vm_underlay_dip.addr.ip)

            # set and verify new vm_vni value
            sai_thrift_set_eni_attribute(self.client, self.eni, vm_vni=test_vm_vni)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, vm_vni=True)
            self.assertEqual(attr['vm_vni'], test_vm_vni)

            # set and verify new vnet_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, vnet_id=test_vnet)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, vnet_id=True)
            self.assertEqual(attr['vnet_id'], test_vnet)

            # set and verify new inbound_v4_stage1_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v4_stage1_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v4_stage1_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v4_stage1_dash_acl_group_id'], 0)

            # set and verify new inbound_v4_stage2_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v4_stage2_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v4_stage2_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v4_stage2_dash_acl_group_id'], 0)

            # set and verify new inbound_v4_stage3_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v4_stage3_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v4_stage3_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v4_stage3_dash_acl_group_id'], 0)

            # set and verify new inbound_v4_stage4_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v4_stage4_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v4_stage4_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v4_stage4_dash_acl_group_id'], 0)

            # set and verify new inbound_v4_stage5_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v4_stage5_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v4_stage5_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v4_stage5_dash_acl_group_id'], 0)

            # set and verify new inbound_v6_stage1_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v6_stage1_dash_acl_group_id=test_ipv6_in_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v6_stage1_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v6_stage1_dash_acl_group_id'], test_ipv6_in_acl_group_id)

            # set and verify new inbound_v6_stage2_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v6_stage2_dash_acl_group_id=test_ipv6_in_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v6_stage2_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v6_stage2_dash_acl_group_id'], test_ipv6_in_acl_group_id)

            # set and verify new inbound_v6_stage3_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v6_stage3_dash_acl_group_id=test_ipv6_in_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v6_stage3_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v6_stage3_dash_acl_group_id'], test_ipv6_in_acl_group_id)

            # set and verify new inbound_v6_stage4_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v6_stage4_dash_acl_group_id=test_ipv6_in_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v6_stage4_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v6_stage4_dash_acl_group_id'], test_ipv6_in_acl_group_id)

            # set and verify new inbound_v6_stage5_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v6_stage5_dash_acl_group_id=test_ipv6_in_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, inbound_v6_stage5_dash_acl_group_id=True)
            self.assertEqual(attr['inbound_v6_stage5_dash_acl_group_id'], test_ipv6_in_acl_group_id)

            # set and verify new outbound_v4_stage1_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v4_stage1_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v4_stage1_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v4_stage1_dash_acl_group_id'], 0)

            # set and verify new outbound_v4_stage2_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v4_stage2_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v4_stage2_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v4_stage2_dash_acl_group_id'], 0)

            # set and verify new outbound_v4_stage3_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v4_stage3_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v4_stage3_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v4_stage3_dash_acl_group_id'], 0)

            # set and verify new outbound_v4_stage4_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v4_stage4_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v4_stage4_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v4_stage4_dash_acl_group_id'], 0)

            # set and verify new outbound_v4_stage5_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v4_stage5_dash_acl_group_id=0)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v4_stage5_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v4_stage5_dash_acl_group_id'], 0)

            # set and verify new outbound_v6_stage1_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v6_stage1_dash_acl_group_id=test_ipv6_out_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v6_stage1_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v6_stage1_dash_acl_group_id'], test_ipv6_out_acl_group_id)

            # set and verify new outbound_v6_stage2_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v6_stage2_dash_acl_group_id=test_ipv6_out_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v6_stage2_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v6_stage2_dash_acl_group_id'], test_ipv6_out_acl_group_id)

            # set and verify new outbound_v6_stage3_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v6_stage3_dash_acl_group_id=test_ipv6_out_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v6_stage3_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v6_stage3_dash_acl_group_id'], test_ipv6_out_acl_group_id)

            # set and verify new outbound_v6_stage4_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v6_stage4_dash_acl_group_id=test_ipv6_out_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v6_stage4_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v6_stage4_dash_acl_group_id'], test_ipv6_out_acl_group_id)

            # set and verify new outbound_v6_stage5_dash_acl_group_id value
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v6_stage5_dash_acl_group_id=test_ipv6_out_acl_group_id)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_attribute(self.client, self.eni, outbound_v6_stage5_dash_acl_group_id=True)
            self.assertEqual(attr['outbound_v6_stage5_dash_acl_group_id'], test_ipv6_out_acl_group_id)

        finally:
            # set ENI attributes to the original values
            sai_thrift_set_eni_attribute(self.client, self.eni, cps=self.cps)
            sai_thrift_set_eni_attribute(self.client, self.eni, pps=self.pps)
            sai_thrift_set_eni_attribute(self.client, self.eni, flows=self.flows)
            sai_thrift_set_eni_attribute(self.client, self.eni, admin_state=self.admin_state)
            sai_thrift_set_eni_attribute(self.client, self.eni, vm_underlay_dip=self.vm_underlay_dip)
            sai_thrift_set_eni_attribute(self.client, self.eni, vm_vni=self.vm_vni)
            sai_thrift_set_eni_attribute(self.client, self.eni, vnet_id=self.vm_vnet)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v4_stage1_dash_acl_group_id=self.in_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v4_stage2_dash_acl_group_id=self.in_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v4_stage3_dash_acl_group_id=self.in_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v4_stage4_dash_acl_group_id=self.in_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         inbound_v4_stage5_dash_acl_group_id=self.in_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v6_stage1_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v6_stage2_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v6_stage3_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v6_stage4_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, inbound_v6_stage5_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v4_stage1_dash_acl_group_id=self.out_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v4_stage2_dash_acl_group_id=self.out_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v4_stage3_dash_acl_group_id=self.out_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v4_stage4_dash_acl_group_id=self.out_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni,
                                         outbound_v4_stage5_dash_acl_group_id=self.out_acl_group_id)
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v6_stage1_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v6_stage2_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v6_stage3_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v6_stage4_dash_acl_group_id=0)
            sai_thrift_set_eni_attribute(self.client, self.eni, outbound_v6_stage5_dash_acl_group_id=0)

            attr = sai_thrift_get_eni_attribute(self.client,
                                                self.eni,
                                                cps=True,
                                                pps=True,
                                                flows=True,
                                                admin_state=True,
                                                vm_underlay_dip=True,
                                                vm_vni=True,
                                                vnet_id=True,
                                                inbound_v4_stage1_dash_acl_group_id=True,
                                                inbound_v4_stage2_dash_acl_group_id=True,
                                                inbound_v4_stage3_dash_acl_group_id=True,
                                                inbound_v4_stage4_dash_acl_group_id=True,
                                                inbound_v4_stage5_dash_acl_group_id=True,
                                                inbound_v6_stage1_dash_acl_group_id=True,
                                                inbound_v6_stage2_dash_acl_group_id=True,
                                                inbound_v6_stage3_dash_acl_group_id=True,
                                                inbound_v6_stage4_dash_acl_group_id=True,
                                                inbound_v6_stage5_dash_acl_group_id=True,
                                                outbound_v4_stage1_dash_acl_group_id=True,
                                                outbound_v4_stage2_dash_acl_group_id=True,
                                                outbound_v4_stage3_dash_acl_group_id=True,
                                                outbound_v4_stage4_dash_acl_group_id=True,
                                                outbound_v4_stage5_dash_acl_group_id=True,
                                                outbound_v6_stage1_dash_acl_group_id=True,
                                                outbound_v6_stage2_dash_acl_group_id=True,
                                                outbound_v6_stage3_dash_acl_group_id=True,
                                                outbound_v6_stage4_dash_acl_group_id=True,
                                                outbound_v6_stage5_dash_acl_group_id=True)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            self.assertEqual(attr['cps'], self.cps)
            self.assertEqual(attr['pps'], self.pps)
            self.assertEqual(attr['flows'], self.flows)
            self.assertEqual(attr['admin_state'], self.admin_state)
            self.assertEqual(attr['vm_underlay_dip'], self.vm_underlay_dip.addr.ip4)
            self.assertEqual(attr['vm_vni'], self.vm_vni)
            self.assertEqual(attr['vnet_id'], self.vm_vnet)
            self.assertEqual(attr['inbound_v4_stage1_dash_acl_group_id'], self.in_acl_group_id)
            self.assertEqual(attr['inbound_v4_stage2_dash_acl_group_id'], self.in_acl_group_id)
            self.assertEqual(attr['inbound_v4_stage3_dash_acl_group_id'], self.in_acl_group_id)
            self.assertEqual(attr['inbound_v4_stage4_dash_acl_group_id'], self.in_acl_group_id)
            self.assertEqual(attr['inbound_v4_stage5_dash_acl_group_id'], self.in_acl_group_id)
            self.assertEqual(attr['inbound_v6_stage1_dash_acl_group_id'], 0)
            self.assertEqual(attr['inbound_v6_stage2_dash_acl_group_id'], 0)
            self.assertEqual(attr['inbound_v6_stage3_dash_acl_group_id'], 0)
            self.assertEqual(attr['inbound_v6_stage4_dash_acl_group_id'], 0)
            self.assertEqual(attr['inbound_v6_stage5_dash_acl_group_id'], 0)
            self.assertEqual(attr['outbound_v4_stage1_dash_acl_group_id'], self.out_acl_group_id)
            self.assertEqual(attr['outbound_v4_stage2_dash_acl_group_id'], self.out_acl_group_id)
            self.assertEqual(attr['outbound_v4_stage3_dash_acl_group_id'], self.out_acl_group_id)
            self.assertEqual(attr['outbound_v4_stage4_dash_acl_group_id'], self.out_acl_group_id)
            self.assertEqual(attr['outbound_v4_stage5_dash_acl_group_id'], self.out_acl_group_id)
            self.assertEqual(attr['outbound_v6_stage1_dash_acl_group_id'], 0)
            self.assertEqual(attr['outbound_v6_stage2_dash_acl_group_id'], 0)
            self.assertEqual(attr['outbound_v6_stage3_dash_acl_group_id'], 0)
            self.assertEqual(attr['outbound_v6_stage4_dash_acl_group_id'], 0)
            self.assertEqual(attr['outbound_v6_stage5_dash_acl_group_id'], 0)

    def eniEtherAddressMapAttributesTest(self):
        """
        Verifies getting and setting ENI MAC map entry attributes

        Note: createEniTest should be run first to create eni_ether_address_map_entry entry
        """
        # verify attributes initially created eni_ether_address_map_entry
        attr = sai_thrift_get_eni_ether_address_map_entry_attribute(self.client,
                                                                    eni_ether_address_map_entry=self.eni_mac_map_entry,
                                                                    eni_id=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['eni_id'], self.eni)

        try:
            # create test eni to verify set method
            test_cps = 500
            test_pps = 500
            test_flows = 500
            test_vm_underlay_ip = sai_ipaddress('172.0.15.15')

            test_eni = self.eni(cps=test_cps,
                                pps=test_pps,
                                flows=test_flows,
                                admin_state=True,
                                vm_underlay_dip=test_vm_underlay_ip,
                                vm_vni=self.vm_vni,
                                vnet_id=self.vm_vnet,
                                inbound_v4_stage1_dash_acl_group_id=0,
                                inbound_v4_stage2_dash_acl_group_id=0,
                                inbound_v4_stage3_dash_acl_group_id=0,
                                inbound_v4_stage4_dash_acl_group_id=0,
                                inbound_v4_stage5_dash_acl_group_id=0,
                                outbound_v4_stage1_dash_acl_group_id=0,
                                outbound_v4_stage2_dash_acl_group_id=0,
                                outbound_v4_stage3_dash_acl_group_id=0,
                                outbound_v4_stage4_dash_acl_group_id=0,
                                outbound_v4_stage5_dash_acl_group_id=0,
                                inbound_v6_stage1_dash_acl_group_id=0,
                                inbound_v6_stage2_dash_acl_group_id=0,
                                inbound_v6_stage3_dash_acl_group_id=0,
                                inbound_v6_stage4_dash_acl_group_id=0,
                                inbound_v6_stage5_dash_acl_group_id=0,
                                outbound_v6_stage1_dash_acl_group_id=0,
                                outbound_v6_stage2_dash_acl_group_id=0,
                                outbound_v6_stage3_dash_acl_group_id=0,
                                outbound_v6_stage4_dash_acl_group_id=0,
                                outbound_v6_stage5_dash_acl_group_id=0)

            sai_thrift_set_eni_ether_address_map_entry_attribute(
                self.client, eni_ether_address_map_entry=self.eni_mac_map_entry, eni_id=test_eni)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_ether_address_map_entry_attribute(
                self.client, eni_ether_address_map_entry=self.eni_mac_map_entry, eni_id=True)
            self.assertEqual(attr['eni_id'], test_eni)

        finally:
            # set map back to original ENI
            sai_thrift_set_eni_ether_address_map_entry_attribute(
                self.client, eni_ether_address_map_entry=self.eni_mac_map_entry, eni_id=self.eni)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_eni_ether_address_map_entry_attribute(
                self.client, eni_ether_address_map_entry=self.eni_mac_map_entry, eni_id=True)
            self.assertEqual(attr['eni_id'], self.eni)

    def paValidationEntryAttributesTest(self):
        """
        Verifies getting PA validation entry attribute

        Note: setting new attribute value cannot be verified
              because PA Validation entry has only 1 attribute value

        Note: createPaValidationTest should be run first to create PA validation entry
        """

        # verify original attributes
        attr = sai_thrift_get_pa_validation_entry_attribute(self.client,
                                                            pa_validation_entry=self.pa_valid_entry,
                                                            action=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['action'], SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT)

    def inboundRoutingEntryAttributesTest(self):
        """
        Verifies getting and setting Inbound routing entry attributes

        Note: createInboundRoutingEntryTest should be run first to create Inbound routing entry
        """

        # verify original attributes
        attr = sai_thrift_get_inbound_routing_entry_attribute(self.client,
                                                              inbound_routing_entry=self.inbound_routing_entry,
                                                              action=True,
                                                              src_vnet_id=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['action'], SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE)
        self.assertEqual(attr['src_vnet_id'], self.outbound_vnet)

        try:
            # set and verify new action
            sai_thrift_set_inbound_routing_entry_attribute(self.client,
                                                           inbound_routing_entry=self.inbound_routing_entry,
                                                           action=SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_inbound_routing_entry_attribute(self.client,
                                                                  inbound_routing_entry=self.inbound_routing_entry,
                                                                  action=True)
            self.assertEqual(attr['action'], SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP)

            # set and verify new src_vnet_id value
            test_vnet = self.vnet_create(vni=500)

            sai_thrift_set_inbound_routing_entry_attribute(self.client,
                                                           inbound_routing_entry=self.inbound_routing_entry,
                                                           src_vnet_id=test_vnet)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            attr = sai_thrift_get_inbound_routing_entry_attribute(self.client,
                                                                  inbound_routing_entry=self.inbound_routing_entry,
                                                                  src_vnet_id=True)
            self.assertEqual(attr['src_vnet_id'], test_vnet)
        finally:
            # set back original attribute value
            sai_thrift_set_inbound_routing_entry_attribute(
                self.client,
                inbound_routing_entry=self.inbound_routing_entry,
                action=SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE)
            sai_thrift_set_inbound_routing_entry_attribute(self.client,
                                                           inbound_routing_entry=self.inbound_routing_entry,
                                                           src_vnet_id=self.outbound_vnet)

            attr = sai_thrift_get_inbound_routing_entry_attribute(self.client,
                                                                  inbound_routing_entry=self.inbound_routing_entry,
                                                                  action=True,
                                                                  src_vnet_id=True)
            self.assertEqual(attr['action'], SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE)
            self.assertEqual(attr['src_vnet_id'], self.outbound_vnet)

    def outboundRoutingEntryAttributesTest(self):
        """
        Verifies getting and setting Outbound routing entry attributes

        Note: createOutboundRoutingEntryTest should be run first to create Outbound routing entry
        """

        # verify original attributes
        attr = sai_thrift_get_outbound_routing_entry_attribute(self.client,
                                                               self.outbound_routing_entry,
                                                               action=True,
                                                               dst_vnet_id=True,
                                                               overlay_ip=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['action'], SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT)
        self.assertEqual(attr['dst_vnet_id'], self.outbound_vnet)
        self.assertEqual(attr['overlay_ip'], self.overlay_ip)
        # TODO: add get counter verification

        try:
            test_action = SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
            test_dst_vnet = self.vnet_create(vni=9999)
            test_overlay_ip = "9.9.9.9"

            # set and verify new action
            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            action=test_action)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            dst_vnet_id=test_dst_vnet)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            overlay_ip=sai_ipaddress(test_overlay_ip))
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

            # verify that all set correct
            attr = sai_thrift_get_outbound_routing_entry_attribute(self.client,
                                                                   self.outbound_routing_entry,
                                                                   action=True,
                                                                   dst_vnet_id=True,
                                                                   overlay_ip=True)
            self.assertEqual(attr['action'], test_action)
            self.assertEqual(attr['dst_vnet_id'], test_dst_vnet)
            self.assertEqual(attr['overlay_ip'], test_overlay_ip)

        finally:
            # verify that original values can be set back
            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT)
            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            dst_vnet_id=self.outbound_vnet)
            sai_thrift_set_outbound_routing_entry_attribute(self.client,
                                                            self.outbound_routing_entry,
                                                            overlay_ip=self.overlay_ip)

            # verify original attributes
            attr = sai_thrift_get_outbound_routing_entry_attribute(self.client,
                                                                   self.outbound_routing_entry,
                                                                   action=True,
                                                                   dst_vnet_id=True,
                                                                   overlay_ip=True)
            self.assertEqual(attr['action'], SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT)
            self.assertEqual(attr['dst_vnet_id'], self.outbound_vnet)
            self.assertEqual(attr['overlay_ip'], self.overlay_ip)

    def outboundCa2PaEntryAttributesTest(self):
        """
        Verifies getting and setting Outbound CA to PA entry attributes

        Note: createCa2PaEntryTest should be run first
        """

        # verify original attributes
        attr = sai_thrift_get_outbound_ca_to_pa_entry_attribute(
            self.client,
            self.ca_to_pa_entry,
            underlay_dip=True,
            overlay_dmac=True,
            use_dst_vnet_vni=True
        )
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertEqual(attr['underlay_dip'], self.underlay_dip)
        self.assertEqual(attr['overlay_dmac'], self.overlay_dmac)
        self.assertEqual(attr['use_dst_vnet_vni'], True)
        # TODO: add get counter verification

        test_dip = "10.10.10.1"
        test_overlay_dmac = "AA:11:BB:22:CC:33"

        # set and verify new values
        sai_thrift_set_outbound_ca_to_pa_entry_attribute(self.client,
                                                         self.ca_to_pa_entry,
                                                         underlay_dip=sai_ipaddress(test_dip))
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        sai_thrift_set_outbound_ca_to_pa_entry_attribute(self.client,
                                                         self.ca_to_pa_entry,
                                                         overlay_dmac=test_overlay_dmac)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        sai_thrift_set_outbound_ca_to_pa_entry_attribute(self.client,
                                                         self.ca_to_pa_entry,
                                                         use_dst_vnet_vni=False)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        attr = sai_thrift_get_outbound_ca_to_pa_entry_attribute(
            self.client,
            self.ca_to_pa_entry,
            underlay_dip=True,
            overlay_dmac=True,
            use_dst_vnet_vni=True
        )
        self.assertEqual(attr['underlay_dip'], test_dip)
        self.assertEqual(attr['overlay_dmac'], test_overlay_dmac)
        self.assertEqual(attr['use_dst_vnet_vni'], False)

    def deleteVnetWhenMapExistTest(self):
        """
        Verifies Vnet entry deletion attempt when mapping with ENI exists
        Expect that Vnet entry cannot be deleted

        Note: createVnetTest and createEniTest should be run first
        """
        sai_thrift_remove_vnet(self.client, self.vm_vnet)
        self.assertEqual(self.status(), SAI_STATUS_OBJECT_IN_USE)

    def deleteEniWhenMapExistTest(self):
        """
        Verifies ENI entry deletion when mappings exist
        (e.g. vnet, eni_ether_address_map, inbound/outbound routing entries)
        Expect that ENI entry and other entries will be deleted successfully

        # TODO: clarify how to verify that other objects also has been deleted

        Note: createEniTest should be run first to create ENI
        """
        sai_thrift_remove_eni(self.client, eni_oid=self.eni)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


@skipIf(test_param_get('target') == 'bmv2', "Blocked by Issue #233. Inbound Routing is not supported in BMv2.")
class EniScaleTest(VnetAPI):
    """
    Verifies ENI scaling:
     - creation/deletion a min required number of ENI entries
     - recreation (repeated creation/deletion a min required number of ENI entries)

    Configuration:
    Empty configuration
    """
    def setUp(self):
        super(EniScaleTest, self).setUp()

        self.MIN_ENI = 64  # Expected min number of ENI entries per card
        self.vm_vni = 0    # ENI VM VNI (increments during ENIs creation)
        self.outbound_vni = 100  # VNI for inbound/outbound routing entries creation
        self.vm_underlay_dip = sai_ipaddress("10.10.0.1")

        # Create list with MIN_ENI number of unique MAC addresses for ENI creation
        self.eni_mac_list = []
        i = 0
        for last_octet in range(0, 256):
            self.eni_mac_list.append('01:01:01:00:00:' +
                                     ('%02x' % last_octet))
            i += 1
            if i == self.MIN_ENI:
                break

    def runTest(self):
        self.eniScaleTest()

        print("\n\tClear configuration")
        self.destroy_teardown_obj()    # remove all created entries
        self.teardown_objects.clear()  # clear teardown_objects to not remove all entries again in tearDown
        print("PASS")

        self.vm_vni = 0                # reset values
        self.outbound_vni = 100

        self.eniScaleTest()            # verify that the min required number on ENI entries can be created again

    def eniScaleTest(self):
        """
        Verifies creating and deleting a min required number of ENI entries.
        Also creates: vnet, inbound and outbound dash acl groups, eni ether address map entries,
                      outbound and inbound routing entries.

        Min required number of ENI entries hardcoded in MIN_ENI value.
        """

        print(f"\n\tEni Scale Test")

        for indx in range(self.MIN_ENI):
            try:
                # create ACL groups for ENI
                in_acl_group_id = self.dash_acl_group_create()
                out_acl_group_id = self.dash_acl_group_create()

                # create VNET
                self.vm_vni += 1
                vm_vnet = self.vnet_create(vni=self.vm_vni)

                # create ENI
                eni = self.eni_create(vm_underlay_dip=self.vm_underlay_dip,
                                      vm_vni=self.vm_vni,
                                      vnet_id=vm_vnet,
                                      inbound_v4_stage1_dash_acl_group_id=in_acl_group_id,
                                      inbound_v4_stage2_dash_acl_group_id=in_acl_group_id,
                                      inbound_v4_stage3_dash_acl_group_id=in_acl_group_id,
                                      inbound_v4_stage4_dash_acl_group_id=in_acl_group_id,
                                      inbound_v4_stage5_dash_acl_group_id=in_acl_group_id,
                                      outbound_v4_stage1_dash_acl_group_id=out_acl_group_id,
                                      outbound_v4_stage2_dash_acl_group_id=out_acl_group_id,
                                      outbound_v4_stage3_dash_acl_group_id=out_acl_group_id,
                                      outbound_v4_stage4_dash_acl_group_id=out_acl_group_id,
                                      outbound_v4_stage5_dash_acl_group_id=out_acl_group_id)

                # create eni_ether_address_map_entry
                self.eni_mac_map_create(eni_id=eni, mac=self.eni_mac_list[indx])

                self.outbound_vni += 1
                outbound_vnet = self.vnet_create(vni=self.outbound_vni)

                # create inbound_routing_entry
                self.inbound_routing_decap_create(eni_id=eni,
                                                  vni=self.outbound_vni,
                                                  sip="10.10.2.0",
                                                  sip_mask="255.255.255.0")

                # create outbound_routing_entry
                self.outbound_routing_vnet_direct_create(eni_id=eni,
                                                         lpm="192.168.1.0/24",
                                                         dst_vnet_id=outbound_vnet,
                                                         overlay_ip="192.168.1.10")

            except AssertionError as ae:
                if self.status() == SAI_STATUS_INSUFFICIENT_RESOURCES:
                    print(f"\nSAI_STATUS_INSUFFICIENT_RESOURCES: failed on iteration # {self.vm_vni}\n")
                    raise ae
                else:
                    print(f"\nFailed on iteration # {self.vm_vni}\n")
                    raise ae

        print("PASS")


@skipIf(test_param_get('target') == 'bmv2', "Blocked by Issue #233. Inbound Routing is not supported in BMv2.")
class CreateTwoSameEnisNegativeTest(VnetAPI):
    """
    Verifies failure in case of creation the same ENIs in one VNET
    """

    def runTest(self):

        vip = "10.1.1.1"
        vm_vni = 1
        vm_underlay_dip = "10.10.1.10"
        eni_mac = "00:01:00:00:03:14"

        self.vip_create(vip=vip)

        self.direction_lookup_create(vni=vm_vni)

        vnet = self.vnet_create(vni=vm_vni)

        # first eni and eni mac mapping
        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(vm_underlay_dip),
                                   vm_vni=vm_vni,
                                   vnet_id=vnet)

        self.eni_mac_map_create(eni_id_0, eni_mac)

        # second eni and eni mac mapping
        eni_id_1 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(vm_underlay_dip),
                                   vm_vni=vm_vni,
                                   vnet_id=vnet)

        # create ENI 1 mac mapping and expect failure
        eni_ether_address_map_entry = sai_thrift_eni_ether_address_map_entry_t(
            switch_id=self.switch_id,
            address=eni_mac)
        sai_thrift_create_eni_ether_address_map_entry(self.client,
                                                      eni_ether_address_map_entry,
                                                      eni_id=eni_id_1)

        self.assertEqual(self.status(), SAI_STATUS_FAILURE)
