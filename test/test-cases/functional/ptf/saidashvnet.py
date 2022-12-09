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

from copy import copy
from unittest import skipIf

from ptf.testutils import test_param_get
from sai_base_test import *
from sai_thrift.sai_headers import *
from sai_dash_utils import *


@group("draft")
@disabled  # This is a Demo test. It should not be executed on CI
class Vnet2VnetCTTest(VnetAPI):
    """
    Vnet to Vnet scenario test case Inbound
    """

    def runTest(self):
        self.configureTest()
        import pdb
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
@skipIf(test_param_get('bmv2'), "Blocked by Issue #233. Inbound Routing is not supported in BMv2.")
class Vnet2VnetInboundTest(VnetAPI):
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
@skipIf(test_param_get('bmv2'), "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteVnetDirectTest(VnetAPI):
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
        self.ENI_MAC = "00:01:00:00:03:14"
        self.SRC_VM_VNI = 1
        self.DST_VM_VNI = 2

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.VIP_ADDRESS)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.SRC_VM_VNI)
        vnet_id_1 = self.vnet_create(self.SRC_VM_VNI)

        eni_id = self.eni_create(vm_vni=self.SRC_VM_VNI,
                                 vm_underlay_dip=sai_ipaddress("10.10.1.10"),
                                 vnet_id=vnet_id_1)
        self.eni_mac_map_create(eni_id, self.ENI_MAC)  # ENI MAC address

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
        inner_pkt = simple_udp_packet(eth_src=self.ENI_MAC,
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
@skipIf(test_param_get('bmv2'), "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteDirectTest(VnetAPI):
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
        self.ENI_MAC = "00:01:00:00:03:14"
        self.SRC_VM_VNI = 1

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.VIP_ADDRESS)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.SRC_VM_VNI)

        vnet_id_1 = self.vnet_create(self.SRC_VM_VNI)

        eni_id = self.eni_create(vm_vni=self.SRC_VM_VNI,
                                 vm_underlay_dip=sai_ipaddress("10.10.1.10"),
                                 vnet_id=vnet_id_1)
        self.eni_mac_map_create(eni_id, self.ENI_MAC)  # ENI MAC address

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
        inner_pkt = simple_udp_packet(eth_src=self.ENI_MAC,
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
@skipIf(test_param_get('bmv2'), "Blocked on BMv2 by Issue #236")
class VnetRouteTest(VnetAPI):
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
