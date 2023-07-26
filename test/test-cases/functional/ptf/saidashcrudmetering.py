# Copyright 2023-present Intel Corporation.
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
Thrift SAI interface for CRUD Metering tests
"""
import random
from unittest import skipIf

from sai_dash_utils import *
from sai_thrift.sai_headers import *


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class CreateDeleteMeteringTest(VnetApiEndpoints):

    def setUp(self):
        super(CreateDeleteMeteringTest, self).setUp()

        self.overlay_ipv6 = False
        self.meter_class = 10000
        self.meter_rule_dip = '192.168.1.5'
        self.meter_rule_dip_mask = '192.168.1.5/30'
        self.meter_rule_priority = 1
        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

    def tearDown(self):
        super(CreateDeleteMeteringTest, self).tearDown()

    def runTest(self):
        self.createMeteringPolicyTest()
        self.createMeteringBucketTest()
        self.createMeteringRuleTest()
        self.deleteMeteringPolicyTest()
        self.deleteMeteringBucketTest()
        self.deleteMeteringRuleTest()
        self.deleteEniTest()

    def createMeteringPolicyTest(self):
        """
        Verifies SAI_STATUS of Metering Policy creation.
        """
        print('createMeteringPolicyTest')

        self.metering_policy_id = self.dash_meter_policy_create()

    def createMeteringBucketTest(self):
        """
        Verifies SAI_STATUS of Metering Bucket creation.
        """
        print('createMeteringBucketTest')

        self.eni_id = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=self.metering_policy_id)

        self.metering_bucket_id = self.dash_meter_bucket_create(self.eni_id, self.meter_class)

    def createMeteringRuleTest(self):
        """
        Verifies SAI_STATUS of Metering Rule creation.
        """
        print('createMeteringRuleTest')

        self.metering_rule_id = self.dash_meter_rule_create(
            self.metering_policy_id,
            dip=self.meter_rule_dip,
            dip_mask=self.meter_rule_dip_mask,
            priority=self.meter_rule_priority,
            meter_class=self.meter_class)

    def deleteMeteringPolicyTest(self):
        """
        Verifies SAI_STATUS of Metering Policy deletion.
        """
        print('deleteMeteringPolicyTest')

        self.dash_meter_policy_remove(self.metering_policy_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def deleteMeteringBucketTest(self):
        """
        Verifies SAI_STATUS of Metering Bucket deletion.
        """
        print('deleteMeteringBucketTest')

        self.dash_meter_bucket_remove(self.metering_bucket_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def deleteMeteringRuleTest(self):
        """
        Verifies SAI_STATUS of Metering Rule deletion.
        """
        print('deleteMeteringRuleTest')

        self.dash_meter_rule_remove(self.metering_rule_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

    def deleteEniTest(self):
        """
        Verifies deletion Metering Bucket after deleting ENI.
        """
        print('deleteEniTest')

        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=self.metering_policy_id)

        self.metering_bucket_id_1 = self.dash_meter_bucket_create(self.eni_id_1, self.meter_class)

        self.eni_remove(self.eni_id_1)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        self.dash_meter_bucket_remove(self.metering_bucket_id)
        self.assertNotEqual(self.status(), SAI_STATUS_SUCCESS)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class SetGetMeteringTest(VnetApiEndpoints):

    def setUp(self):
        super(SetGetMeteringTest, self).setUp()

        self.overlay_ipv6 = False
        self.meter_class = 10000
        self.meter_rule_dip = '192.168.1.5'
        self.meter_rule_dip_mask = '192.168.1.5/30'
        self.meter_rule_priority = 1
        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        self.metering_policy_id = self.dash_meter_policy_create()

        self.eni_id = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=self.metering_policy_id)

        self.metering_bucket_id = self.dash_meter_bucket_create(self.eni_id, self.meter_class)

        self.metering_rule_id = self.dash_meter_rule_create(
            self.metering_policy_id,
            dip=self.meter_rule_dip,
            dip_mask=self.meter_rule_dip_mask,
            priority=self.meter_rule_priority,
            meter_class=self.meter_class)

    def tearDown(self):
        super(SetGetMeteringTest, self).tearDown()

    def runTest(self):
        self.setGetMeteringPolicyTest()
        self.setGetMeteringBucketTest()
        self.setGetMeteringRuleTest()

    def setGetMeteringPolicyTest(self):
        """
        Verifies getting and setting Dash Metering Policy entry attributes
        """
        print('setGetMeteringPolicyTest')

        try:
            sai_thrift_set_meter_policy_attribute(self.client,
                                                  self.metering_policy_id,
                                                  ip_addr_family=SAI_IP_ADDR_FAMILY_IPV6)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_meter_policy_attribute(self.client,
                                                         self.metering_policy_id,
                                                         ip_addr_family=True)
            self.assertEqual(attr['ip_addr_family'], SAI_IP_ADDR_FAMILY_IPV6)
        finally:
            # set original value
            sai_thrift_set_meter_policy_attribute(self.client,
                                                  self.metering_policy_id,
                                                  ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_meter_policy_attribute(self.client,
                                                         self.metering_policy_id,
                                                         ip_addr_family=True)
            self.assertEqual(attr['ip_addr_family'], SAI_IP_ADDR_FAMILY_IPV4)

    def setGetMeteringBucketTest(self):
        """
        Verifies getting and setting Dash Metering Bucket entry attributes
        """
        print('setGetMeteringBucketTest')

        sai_thrift_set_meter_bucket_attribute(self.client,
                                              self.metering_bucket_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        attr = sai_thrift_get_meter_bucket_attribute(self.client,
                                                     self.metering_bucket_id,
                                                     eni_id=True)
        self.assertEqual(attr['eni_id'], self.eni_id)

    def setGetMeteringRuleTest(self):
        """
        Verifies getting and setting Dash Metering Rule entry attributes
        """
        print('setGetMeteringRuleTest')

        try:
            sai_thrift_set_meter_rule_attribute(self.client,
                                                self.metering_rule_id,
                                                meter_class=20000)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_meter_rule_attribute(self.client,
                                                       self.metering_rule_id,
                                                       meter_class=True)
            self.assertEqual(attr['meter_class'], 20000)
        finally:
            # set original value
            sai_thrift_set_meter_rule_attribute(self.client,
                                                self.metering_rule_id,
                                                meter_class=self.meter_class)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
            attr = sai_thrift_get_meter_rule_attribute(self.client,
                                                       self.metering_rule_id,
                                                       meter_class=True)
            self.assertEqual(attr['meter_class'], self.meter_class)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class InvalidDataMeteringTest(VnetApiEndpoints):

    def setUp(self):
        super(InvalidDataMeteringTest, self).setUp()

        self.overlay_ipv6 = False
        self.meter_class = 10000
        self.meter_rule_dip = '192.168.1.5'
        self.meter_rule_dip_mask = '192.168.1.5/30'
        self.meter_rule_priority = 1
        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

    def tearDown(self):
        super(InvalidDataMeteringTest, self).tearDown()

    def runTest(self):
        self.invalidCreateMeteringPolicyTest()
        self.invalidCreateMeteringBucketTest()
        self.invalidCreateMeteringRuleTest()

    def invalidCreateMeteringPolicyTest(self):
        """
        Verifies SAI_STATUS of Metering Policy creation with invalid ip_addr_family.
        """
        print('invalidCreateMeteringPolicyTest')

        sai_thrift_create_meter_policy(self.client, ip_addr_family=random.randint(2, 100))
        self.assertNotEqual(self.status(), SAI_STATUS_SUCCESS)

    def invalidCreateMeteringBucketTest(self):
        """
        Verifies SAI_STATUS of Metering Bucket creation with invalid eni_id.
        """
        print('invalidCreateMeteringBucketTest')

        sai_thrift_create_meter_bucket(self.client, eni_id=-1, meter_class=self.meter_class)
        self.assertNotEqual(self.status(), SAI_STATUS_SUCCESS)

    def invalidCreateMeteringRuleTest(self):
        """
        Verifies SAI_STATUS of Metering rule creation with non-existent policy.
        """
        print('invalidCreateMeteringRuleTest')

        sai_thrift_create_meter_rule(
            self.client,
            meter_policy_id=-1,
            dip=sai_ipaddress(self.meter_rule_dip),
            dip_mask=sai_ipaddress(self.meter_rule_dip_mask),
            priority=self.meter_rule_priority,
            meter_class=self.meter_class)
        self.assertNotEqual(self.status(), SAI_STATUS_SUCCESS)
