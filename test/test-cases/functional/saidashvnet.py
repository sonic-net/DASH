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
Thrift SAI interface VNet tests
"""

from sai_thrift.sai_headers import *
from sai_base_test import *

from copy import copy
import pdb


class VNetObjects(SaiHelperSimplified):
    def setUp(self):
        super(VNetObjects, self).setUp()
        self.teardown_objects = list()

    def tearDown(self):
        super(VNetObjects, self).tearDown()

    def add_teardown_obj(self, func, *args):
        self.teardown_objects.insert(0, (func, *args))

    def destroy_teardown_obj(self):
        for obj_func, obj_args in self.teardown_objects:
            obj_func(obj_args)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


class VNetAPI(VNetObjects):
    def setUp(self):
        super(VNetAPI, self).setUp()

    def tearDown(self):
        self.destroy_teardown_obj()
        super(VNetAPI, self).tearDown()

    def vip_create(self, vip):
        """
        Add VIP for Appliance
        """

        sai_vip_entry = sai_thrift_vip_entry_t(switch_id=self.switch_id, vip=sai_ipaddress(vip))
        sai_thrift_create_vip_entry(self.client, sai_vip_entry, action=SAI_VIP_ENTRY_ACTION_ACCEPT)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.vip_remove, sai_vip_entry)

    def vip_remove(self, vip_entry):
        sai_thrift_remove_vip_entry(self.client, vip_entry)

    def eni_create(self, **kwargs):
        """
        Create ENI
        """

        default_kwargs = {
            "admin_state": True,
            "vm_underlay_dip": sai_ipaddress("0.0.0.0"),
            "vm_vni": 1,
            "vnet_id": 1,
            "inbound_v4_stage1_dash_acl_group_id": 0,
            "inbound_v4_stage2_dash_acl_group_id": 0,
            "inbound_v4_stage3_dash_acl_group_id": 0,
            "inbound_v4_stage4_dash_acl_group_id": 0,
            "inbound_v4_stage5_dash_acl_group_id": 0,
            "outbound_v4_stage1_dash_acl_group_id": 0,
            "outbound_v4_stage2_dash_acl_group_id": 0,
            "outbound_v4_stage3_dash_acl_group_id": 0,
            "outbound_v4_stage4_dash_acl_group_id": 0,
            "outbound_v4_stage5_dash_acl_group_id": 0,
            "inbound_v6_stage1_dash_acl_group_id": 0,
            "inbound_v6_stage2_dash_acl_group_id": 0,
            "inbound_v6_stage3_dash_acl_group_id": 0,
            "inbound_v6_stage4_dash_acl_group_id": 0,
            "inbound_v6_stage5_dash_acl_group_id": 0,
            "outbound_v6_stage1_dash_acl_group_id": 0,
            "outbound_v6_stage2_dash_acl_group_id": 0,
            "outbound_v6_stage3_dash_acl_group_id": 0,
            "outbound_v6_stage4_dash_acl_group_id": 0,
            "outbound_v6_stage5_dash_acl_group_id": 0
        }
        default_kwargs.update(kwargs)
        eni_id = sai_thrift_create_eni(self.client, **default_kwargs)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertNotEqual(eni_id, 0)
        self.add_teardown_obj(self.eni_remove, eni_id)

        return eni_id

    def eni_remove(self, eni_id):
        sai_thrift_remove_eni(self.client, eni_id)

    def direction_lookup_create(self, vni, drop=False):
        """
        Create direction lookup entry
        """

        act = SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION
        if drop:
            act = SAI_DIRECTION_LOOKUP_ENTRY_ACTION_DENY
        direction_lookup_entry = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=vni)
        sai_thrift_create_direction_lookup_entry(self.client, direction_lookup_entry, action=act)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.direction_lookup_remove, direction_lookup_entry)

    def direction_lookup_remove(self, direction_lookup_entry):
        sai_thrift_remove_direction_lookup_entry(self.client, direction_lookup_entry)

    def eni_mac_map_create(self, eni_id, mac):
        """
        Create ENI - MAC mapping
        """

        eni_ether_address_map_entry = sai_thrift_eni_ether_address_map_entry_t(switch_id=self.switch_id, address=mac)
        sai_thrift_create_eni_ether_address_map_entry(self.client, eni_ether_address_map_entry, eni_id=eni_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.eni_mac_map_remove, eni_ether_address_map_entry)

    def eni_mac_map_remove(self, eni_ether_address_map_entry):
        sai_thrift_remove_eni_ether_address_map_entry(self.client, eni_ether_address_map_entry)

    def vnet_create(self, vni):
        """
        Create VNET
        """

        vnet_id = sai_thrift_create_vnet(self.client, vni=vni)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertNotEqual(vnet_id, 0)
        self.add_teardown_obj(self.vnet_remove, vnet_id)

        return vnet_id

    def vnet_remove(self, vnet_id):
        sai_thrift_remove_vnet(self.client, vnet_id)

    def inbound_routing_decap_validate_create(self, eni_id, vni, sip, sip_mask, src_vnet_id):
        """
        Create inbound routing entry with
        SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE action
        """

        inbound_routing_entry = sai_thrift_inbound_routing_entry_t(
                                        switch_id=self.switch_id, vni=vni,
                                        eni_id=eni_id, sip=sai_ipaddress(sip),
                                        sip_mask=sai_ipaddress(sip_mask), priority=0)
        sai_thrift_create_inbound_routing_entry(self.client, inbound_routing_entry,
                                                action=SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE,
                                                src_vnet_id=src_vnet_id)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.inbound_routing_remove, inbound_routing_entry)

    def inbound_routing_decap_create(self, eni_id, vni, sip, sip_mask):
        """
        Create inbound routing entry with
        SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP action
        """

        inbound_routing_entry = sai_thrift_inbound_routing_entry_t(
            switch_id=self.switch_id, vni=vni,
            eni_id=eni_id, sip=sai_ipaddress(sip),
            sip_mask=sai_ipaddress(sip_mask), priority=0)
        sai_thrift_create_inbound_routing_entry(self.client, inbound_routing_entry,
                                                action=SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.inbound_routing_remove, inbound_routing_entry)

    def inbound_routing_remove(self, inbound_routing_entry):
        sai_thrift_remove_inbound_routing_entry(self.client, inbound_routing_entry)

    def pa_validation_create(self, sip, vnet_id):
        """
        Create source PA validation entry
        """

        pa_validation_entry = sai_thrift_pa_validation_entry_t(switch_id=self.switch_id,
                                                               sip=sai_ipaddress(sip),
                                                               vnet_id=vnet_id)
        sai_thrift_create_pa_validation_entry(self.client,
                                              pa_validation_entry,
                                              action=SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.pa_validation_remove, pa_validation_entry)

    def pa_validation_remove(self, pa_validation_entry):
        sai_thrift_remove_pa_validation_entry(self.client, pa_validation_entry)

    def outbound_routing_vnet_direct_create(self, eni_id, lpm, dst_vnet_id, overlay_ip):
        """
        Create outband vnet direct routing entry
        """

        outbound_routing_entry = sai_thrift_outbound_routing_entry_t(
                                switch_id=self.switch_id, eni_id=eni_id,
                                destination=sai_ipprefix(lpm))
        sai_thrift_create_outbound_routing_entry(self.client, outbound_routing_entry,
                                                 dst_vnet_id=dst_vnet_id, overlay_ip=sai_ipaddress(overlay_ip),
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_routing_vnet_direct_remove, outbound_routing_entry)

    def outbound_routing_direct_create(self, eni_id, lpm):
        """
        Create outband vnet direct routing entry
        """

        outbound_routing_entry = sai_thrift_outbound_routing_entry_t(
                                switch_id=self.switch_id, eni_id=eni_id,
                                destination=sai_ipprefix(lpm))
        sai_thrift_create_outbound_routing_entry(self.client, outbound_routing_entry,
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_routing_vnet_direct_remove, outbound_routing_entry)

    def outbound_routing_vnet_direct_remove(self, entry):
        sai_thrift_remove_outbound_routing_entry(self.client, entry)

    def outbound_ca_to_pa_create(self, dst_vnet_id, dip, underlay_dip):
        """
        Create outband CA PA mapping
        """

        ca_to_pa_entry = sai_thrift_outbound_ca_to_pa_entry_t(switch_id=self.switch_id,
                                                              dst_vnet_id=dst_vnet_id, dip=sai_ipaddress(dip))
        sai_thrift_create_outbound_ca_to_pa_entry(self.client, ca_to_pa_entry,
                                                  underlay_dip=sai_ipaddress(underlay_dip), use_dst_vnet_vni=True)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_ca_to_pa_remove, ca_to_pa_entry)

    def outbound_ca_to_pa_remove(self, ca_to_pa_entry):
        sai_thrift_remove_outbound_ca_to_pa_entry(self.client, ca_to_pa_entry)

    def router_interface_create(self, port, src_mac=None):
        """
        RIF create
        """

        rif = sai_thrift_create_router_interface(self.client,
                                                 type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                 virtual_router_id=self.default_vrf,
                                                 src_mac_address=src_mac, port_id=port)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.router_interface_remove, rif)

        return rif

    def router_interface_remove(self, rif):
        sai_thrift_remove_router_interface(self.client, rif)

    def nexthop_create(self, rif, ip):
        """
        Nexthop create
        """

        nhop = sai_thrift_create_next_hop(
            self.client,
            ip=sai_ipaddress(ip),
            router_interface_id=rif,
            type=SAI_NEXT_HOP_TYPE_IP)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.nexthop_remove, nhop)

        return nhop

    def nexthop_remove(self, nhop):
        sai_thrift_remove_next_hop(self.client, nhop)

    def neighbor_create(self, rif, ip, dmac):
        """
        Neighbor create
        """

        neighbor_entry = sai_thrift_neighbor_entry_t(
            rif_id=rif, ip_address=sai_ipaddress(ip))
        sai_thrift_create_neighbor_entry(
            self.client, neighbor_entry, dst_mac_address=dmac)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.neighbor_remove, neighbor_entry)

    def neighbor_remove(self, entry):
        sai_thrift_remove_neighbor_entry(self.client, entry)

    def route_create(self, prefix, nhop):
        """
        Route create
        """

        route_entry = sai_thrift_route_entry_t(
            vr_id=self.default_vrf, destination=sai_ipprefix(prefix))
        sai_thrift_create_route_entry(
            self.client, route_entry, next_hop_id=nhop)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.route_remove, route_entry)

    def route_remove(self, entry):
        sai_thrift_remove_route_entry(self.client, entry)


@group("draft")
class Vnet2VnetCTTest(VNetAPI):
    """
    Vnet to Vnet scenario test case Inbound
    """

    def runTest(self):
        self.configureTest()

        pdb.set_trace()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create("10.10.1.1")  # Appliance VIP
        self.direction_lookup_create(1)  # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        eni_id = self.eni_create(vm_vni=1)  # VM VNI = 1
        self.eni_mac_map_create(eni_id, "00:01:00:00:03:14")  # ENI MAC address
        vnet_id_2 = self.vnet_create(2)  # VNET VNI = 2
        # inbound routing
        self.inbound_routing_decap_validate_create(eni_id, 2,  # routing VNI lookup = 2
                                                   "10.10.2.0", "255.255.255.0", vnet_id_2)
        self.pa_validation_create("10.10.2.10", vnet_id_2)
        # outbound routing
        self.outbound_routing_vnet_direct_create(eni_id, "192.168.1.0/24", vnet_id_2, "192.168.1.1")
        self.outbound_ca_to_pa_create(vnet_id_2,      # DST vnet id
                                      "192.168.1.1",  # DST IP addr
                                      "10.10.2.10")   # Underlay DIP
        # underlay routing
        self.router_interface_create(self.port0)
        rif1 = self.router_interface_create(self.port1, src_mac="00:77:66:55:44:00")
        nhop = self.nexthop_create(rif1, "10.10.2.10")
        self.neighbor_create(rif1, "10.10.2.10", "aa:bb:cc:11:22:33")
        self.route_create("10.10.2.0/24", nhop)


@group("draft")
class Vnet2VnetInboundTest(VNetAPI):
    """
    Inbound Vnet to Vnet scenario test case
    """

    def setUp(self):
        super(Vnet2VnetInboundTest, self).setUp()
        """
        Configuration
        +----------+-----------+
        | port0    | port0_rif |
        +----------+-----------+
        | port1    | port1_rif |
        +----------+-----------+
        """
        self.PA_VALIDATION_SIP = "10.10.2.10"  # PA validation PERMIT
        self.ENI_MAC = "00:01:00:00:03:14"     # ENI MAC address
        self.VM_VNI = 1     # DST VM VNI (Inbound VNI)
        self.ROUTE_VNI = 2  # Inbound route VNI

        self.VIP_ADDRESS = "10.1.1.1"  # Appliance IP address

        self.OUTER_DMAC = "aa:bb:cc:dd:ee:11"  # DST MAC for outer VxLAN pkt and Neighbor MAC
        self.OUTER_DIP = "10.10.1.10"          # DST IP for outer IP pkt and Next-hop/Neighbor IP

        # SDN Appliance rif`s MAC addresses
        self.RIF0_RIF_MAC = "00:77:66:55:44:00"
        self.RIF1_RIF_MAC = "00:88:77:66:55:00"

    def runTest(self):
        self.configureTest()
        self.vnet2VnetInboundPaValidatePermitTest()
        self.vnet2VnetInboundDenyVniTest()
        self.vnet2VnetInboundRouteInvalidVniTest()
        self.vnet2VnetInboundInvalidEniMacTest()
        self.vnet2VnetInboundInvalidPaSrcIpTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        # Underlay routing
        self.router_interface_create(self.port0, src_mac=self.RIF0_RIF_MAC)
        rif1 = self.router_interface_create(self.port1, src_mac=self.RIF1_RIF_MAC)

        nhop = self.nexthop_create(rif1, self.OUTER_DIP)
        self.neighbor_create(rif1, self.OUTER_DIP, self.OUTER_DMAC)
        self.route_create("10.10.1.0/24", nhop)

        # Overlay routing
        self.vip_create(self.VIP_ADDRESS)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.VM_VNI)

        vnet1 = self.vnet_create(self.VM_VNI)
        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.OUTER_DIP),
                                 vm_vni=self.VM_VNI,
                                 vnet_id=vnet1)
        self.eni_mac_map_create(eni_id, self.ENI_MAC)

        vnet2 = self.vnet_create(self.ROUTE_VNI)

        # Inbound routing PA Validate
        self.inbound_routing_decap_validate_create(eni_id, vni=self.ROUTE_VNI,  # routing VNI lookup = 2
                                                   sip="10.10.2.0", sip_mask="255.255.255.0", src_vnet_id=vnet2)
        # PA validation entry with Permit action
        self.pa_validation_create(self.PA_VALIDATION_SIP, vnet2)

        # Create VxLAN packets
        self.inner_pkt = simple_tcp_packet(eth_dst=self.ENI_MAC,
                                           eth_src="20:30:40:50:60:70",
                                           ip_dst="192.168.0.1",
                                           ip_src="192.168.1.1",
                                           ip_id=108,
                                           ip_ttl=64)

        self.vxlan_pkt = simple_vxlan_packet(eth_dst=self.RIF0_RIF_MAC,
                                             eth_src="aa:bb:cc:11:22:33",
                                             ip_dst=self.VIP_ADDRESS,
                                             ip_src=self.PA_VALIDATION_SIP,
                                             ip_id=0,
                                             ip_ttl=64,
                                             ip_flags=0x2,
                                             with_udp_chksum=False,
                                             vxlan_vni=self.ROUTE_VNI,
                                             inner_frame=self.inner_pkt)

        self.exp_vxlan_pkt = simple_vxlan_packet(eth_dst=self.OUTER_DMAC,
                                                 eth_src=self.RIF1_RIF_MAC,
                                                 ip_dst=self.OUTER_DIP,
                                                 ip_src=self.VIP_ADDRESS,
                                                 ip_id=0,
                                                 ip_ttl=64,
                                                 ip_flags=0x2,
                                                 with_udp_chksum=False,
                                                 vxlan_vni=self.VM_VNI,
                                                 inner_frame=self.inner_pkt)

        # Create Eth packets for verify_no_packet method
        self.inner_eth_packet = simple_eth_packet(eth_dst=self.inner_pkt.getlayer('Ether').dst,
                                                  eth_src=self.inner_pkt.getlayer('Ether').src, eth_type=0x800)
        self.outer_eth_packet = simple_eth_packet(eth_dst=self.exp_vxlan_pkt.getlayer('Ether').dst,
                                                  eth_src=self.exp_vxlan_pkt.getlayer('Ether').src, eth_type=0x800)

    def vnet2VnetInboundPaValidatePermitTest(self):
        """
        Inbound VNET to VNET test with PA validation entry Permit action
        Verifies correct packet routing
        """

        print("Sending VxLAN IPv4 packet, expect VxLAN packet routed")

        send_packet(self, self.dev_port0, self.vxlan_pkt)
        verify_packet(self, self.exp_vxlan_pkt, self.dev_port1, timeout=1)

        print('\n', self.vnet2VnetInboundPaValidatePermitTest.__name__, ' OK')

    def vnet2VnetInboundDenyVniTest(self):
        """
        Inbound VNET to VNET test with SAI_DIRECTION_LOOKUP_ENTRY_ACTION_DENY action
        Verifies packet drop
        """

        # drop direction lookup VNI
        drop_vni = 3
        self.direction_lookup_create(drop_vni, drop=True)

        # VNI matches Direction lookup Deny action
        vxlan_pkt_invalid_vni = copy(self.vxlan_pkt)
        vxlan_pkt_invalid_vni.getlayer('VXLAN').vni = drop_vni

        print("Sending VxLAN IPv4 packet with VNI that matches direction lookup action Deny, expect drop")

        send_packet(self, self.dev_port0, vxlan_pkt_invalid_vni)
        verify_no_packet(self, self.inner_eth_packet, self.dev_port1, timeout=1)
        verify_no_packet(self, self.outer_eth_packet, self.dev_port1, timeout=1)

        print('\n', self.vnet2VnetInboundDenyVniTest.__name__, ' OK')

    def vnet2VnetInboundInvalidEniMacTest(self):
        """
        Inbound VNET to VNET test
        Verifies packet drop in case of invalid ENI MAC address
        """

        # Invalid CA (ENI) DST MAC
        vxlan_pkt_invalid_dmac = copy(self.vxlan_pkt)
        vxlan_pkt_invalid_dmac.getlayer('VXLAN').getlayer('Ether').dst = "9e:ba:ce:98:d9:e2"

        print("Sending VxLAN IPv4 packet with invalid destination mac, expect drop")

        send_packet(self, self.dev_port0, vxlan_pkt_invalid_dmac)
        verify_no_packet(self, self.inner_eth_packet, self.dev_port1, timeout=1)
        verify_no_packet(self, self.outer_eth_packet, self.dev_port1, timeout=1)

        print('\n', self.vnet2VnetInboundInvalidEniMacTest.__name__, ' OK')

    def vnet2VnetInboundInvalidPaSrcIpTest(self):
        """
        Inbound VNET to VNET test
        Verifies packet drop in case of invalid Physical source IP address
        """

        # Invalid PA IP
        vxlan_pkt_invalid_pa_ip = copy(self.vxlan_pkt)
        vxlan_pkt_invalid_pa_ip.getlayer('IP').src = "192.168.56.12"

        print("Sending VxLAN IPv4 packet with invalid pa validation ip, expect drop")

        send_packet(self, self.dev_port0, vxlan_pkt_invalid_pa_ip)
        verify_no_packet(self, self.inner_eth_packet, self.dev_port1, timeout=1)
        verify_no_packet(self, self.outer_eth_packet, self.dev_port1, timeout=1)

        print('\n', self.vnet2VnetInboundInvalidPaSrcIpTest.__name__, ' OK')

    def vnet2VnetInboundRouteInvalidVniTest(self):
        """
        Inbound VNET to VNET test scenario
        Verifies packet drop in case of invalid routing VNI lookup
        """

        vxlan_pkt_invalid_vni = copy(self.vxlan_pkt)
        vxlan_pkt_invalid_vni.getlayer('VXLAN').vni = 1000

        print("Sending VxLAN IPv4 packet with invalid routing VNI lookup, expect drop")

        send_packet(self, self.dev_port0, vxlan_pkt_invalid_vni)
        verify_no_packet(self, self.inner_eth_packet, self.dev_port1, timeout=1)
        verify_no_packet(self, self.outer_eth_packet, self.dev_port1, timeout=1)

        print('\n', self.vnet2VnetInboundRouteInvalidVniTest.__name__, ' OK')

@group("draft")
class Vnet2VnetOutboundRouteVnetDirectTest(VNetAPI):
    """
    Outbound VNet to VNet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action
    """

    def setUp(self):
        super(Vnet2VnetOutboundRouteVnetDirectTest, self).setUp()
        """
        Configuration
        +----------+-----------+
        | port0    | port0_rif |
        +----------+-----------+
        | port1    | port1_rif |
        +----------+-----------+
        """
        self.VIP_ADDRESS = "10.1.1.1"  # Appliance IP address
        self.SRC_VM_VNI = 1
        self.DST_VM_VNI = 2

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.VIP_ADDRESS)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.SRC_VM_VNI)

        eni_id = self.eni_create(vm_vni=self.SRC_VM_VNI)  # VM VNI = 1
        self.eni_mac_map_create(eni_id, "00:01:00:00:03:14")  # ENI MAC address
        vnet_id_2 = self.vnet_create(self.DST_VM_VNI)  # VNET VNI = 2
        # outbound routing
        self.outbound_routing_vnet_direct_create(eni_id, "192.168.1.0/24", vnet_id_2,
                                                 overlay_ip="192.168.1.10")
        self.outbound_ca_to_pa_create(vnet_id_2,  # DST vnet id
                                      "192.168.1.10",  # DST IP addr
                                      "10.10.2.10")  # Underlay DIP
        # underlay routing
        self.router_interface_create(self.port1)
        rif0 = self.router_interface_create(self.port0, src_mac="00:77:66:55:44:00")
        nhop = self.nexthop_create(rif0, "10.10.2.10")
        self.neighbor_create(rif0, "10.10.2.10", "aa:bb:cc:11:22:33")
        self.route_create("10.10.2.0/24", nhop)

    def runTest(self):
        self.configureTest()

        # send packet and check
        inner_pkt = simple_udp_packet(eth_src="00:00:00:09:03:14",
                                      eth_dst="20:30:40:50:60:70",
                                      ip_dst="192.168.1.1",
                                      ip_src="192.168.0.1",
                                      ip_ttl=64,
                                      ip_ihl=5,
                                      with_udp_chksum=True)

        vxlan_pkt = simple_vxlan_packet(eth_dst="00:00:cc:11:22:33",
                                        eth_src="00:00:66:00:44:00",
                                        ip_dst=self.VIP_ADDRESS,
                                        ip_src="10.10.1.10",
                                        with_udp_chksum=True,
                                        vxlan_vni=self.SRC_VM_VNI,
                                        ip_ttl=0,
                                        ip_ihl=5,
                                        ip_id=0,
                                        udp_sport=5000,
                                        vxlan_flags=0x8,
                                        vxlan_reserved0=None,
                                        vxlan_reserved1=0,
                                        vxlan_reserved2=0,
                                        ip_flags=0x2,
                                        inner_frame=inner_pkt)

        exp_vxlan_pkt = simple_vxlan_packet(eth_dst="aa:bb:cc:11:22:33",
                                            eth_src="00:77:66:55:44:00",
                                            ip_dst="10.10.2.10",
                                            ip_src=self.VIP_ADDRESS,
                                            with_udp_chksum=True,
                                            vxlan_vni=self.DST_VM_VNI,
                                            ip_ttl=0,
                                            ip_ihl=5,
                                            ip_id=0,
                                            udp_sport=5000,
                                            vxlan_flags=0x8,
                                            vxlan_reserved0=None,
                                            vxlan_reserved1=0,
                                            vxlan_reserved2=0,
                                            ip_flags=0x2,
                                            inner_frame=inner_pkt)

        print("Sending VxLAN IPv4 packet, expect VxLAN IPv4 packet forwarded")
        send_packet(self, self.dev_port1, vxlan_pkt)
        verify_packet(self, exp_vxlan_pkt, self.dev_port0)


@group("draft")
class Vnet2VnetOutboundRouteDirectTest(VNetAPI):
    """
    Outbound VNet to VNet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT action
    """

    def setUp(self):
        super(Vnet2VnetOutboundRouteDirectTest, self).setUp()
        """
        Configuration
        +----------+-----------+
        | port0    | port0_rif |
        +----------+-----------+
        | port1    | port1_rif |
        +----------+-----------+
        """

        self.VIP_ADDRESS = "10.1.1.1"  # Appliance VIP address
        self.SRC_VM_VNI = 1

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.VIP_ADDRESS)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.SRC_VM_VNI)

        eni_id = self.eni_create(vm_vni=self.SRC_VM_VNI)  # VM VNI = 1
        self.eni_mac_map_create(eni_id, "00:01:00:00:03:14")  # ENI MAC address

        # outbound routing
        self.outbound_routing_direct_create(eni_id, "192.168.1.0/24")

        # underlay routing
        self.router_interface_create(self.port1)
        rif0 = self.router_interface_create(self.port0, src_mac="00:77:66:55:44:00")
        nhop = self.nexthop_create(rif0, "10.10.2.10")
        self.neighbor_create(rif0, "10.10.2.10", "aa:bb:cc:11:22:33")
        self.route_create("10.10.2.0/24", nhop)

    def runTest(self):
        self.configureTest()

        # send packet and check
        inner_pkt = simple_udp_packet(eth_src="00:00:00:09:03:14",
                                      eth_dst="20:30:40:50:60:70",
                                      ip_dst="192.168.1.1",
                                      ip_src="192.168.0.1",
                                      ip_ttl=64,
                                      ip_ihl=5,
                                      with_udp_chksum=True)

        vxlan_pkt = simple_vxlan_packet(eth_dst="00:00:cc:11:22:33",
                                        eth_src="00:00:66:00:44:00",
                                        ip_dst=self.VIP_ADDRESS,
                                        ip_src="10.10.1.10",
                                        with_udp_chksum=True,
                                        vxlan_vni=self.SRC_VM_VNI,
                                        ip_ttl=0,
                                        ip_ihl=5,
                                        ip_id=0,
                                        udp_sport=5000,
                                        vxlan_flags=0x8,
                                        vxlan_reserved0=None,
                                        vxlan_reserved1=0,
                                        vxlan_reserved2=0,
                                        ip_flags=0x2,
                                        inner_frame=inner_pkt)

        direct_pkt = simple_udp_packet(eth_src="00:77:66:55:44:00",
                                       eth_dst="aa:bb:cc:11:22:33",
                                       ip_dst="192.168.1.1",
                                       ip_src="192.168.0.1",
                                       ip_ttl=63,
                                       ip_ihl=5,
                                       with_udp_chksum=True)

        print("Sending VxLAN IPv4 packet, expected UDP packet forwarded")
        send_packet(self, self.dev_port1, vxlan_pkt)
        verify_packet(self, direct_pkt, self.dev_port0)

@group("draft")
class VnetRouteTest(VNetAPI):
    """
    Vnet to Vnet scenario test case Outbound
    """

    def setUp(self):
        super(VnetRouteTest, self).setUp()
        """
        Configuration
        +----------+-----------+
        | port0    | port0_rif |
        +----------+-----------+
        | port1    | port1_rif |
        +----------+-----------+
        """
        self.RIF_SRC_MAC = "44:33:33:22:55:66"
        self.NEIGH_DMAC = "aa:bb:cc:11:22:33"

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        # underlay routing
        self.router_interface_create(self.port1)
        rif0 = self.router_interface_create(self.port0, src_mac=self.RIF_SRC_MAC)
        nhop = self.nexthop_create(rif0, "10.10.2.10")
        self.neighbor_create(rif0, "10.10.2.10", self.NEIGH_DMAC)
        self.route_create("10.10.2.2/24", nhop)

    def runTest(self):
        self.configureTest()

        out_pkt = simple_udp_packet(eth_src="00:00:00:01:03:14",
                                    eth_dst="20:30:40:50:60:70",
                                    ip_dst="10.10.2.2",
                                    ip_src="10.10.20.20",
                                    ip_ttl=64)
        exp_pkt = simple_udp_packet(eth_src=self.RIF_SRC_MAC,
                                    eth_dst=self.NEIGH_DMAC,
                                    ip_dst="10.10.2.2",
                                    ip_src="10.10.20.20",
                                    ip_ttl=64)

        print("Sending simple UDP packet, expecting routed packet")
        send_packet(self, self.dev_port1, out_pkt)
        verify_packet(self, exp_pkt, self.dev_port0)
