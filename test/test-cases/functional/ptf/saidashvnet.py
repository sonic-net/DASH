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
Thrift SAI interface VNET tests
"""

from unittest import skipIf

from sai_thrift.sai_headers import *
from sai_dash_utils import *


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class UnderlayRouteTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    L3 Underlay bidirectional routing test case
    Verifies correct L3 underlay routing when overlay configuration exist
    """

    def runTest(self):
        self.configureTest()

        self.verifyOverlayOutboundConfigTest()

        self.l3UnderlayHost1toHost2RoutingTest()
        self.l3UnderlayHost2toHost1RoutingTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        # configure overlay outbound
        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

        # configure underlay
        self.host_1 = self.tx_host
        self.host_2 = self.rx_host

        #self.configure_underlay(self.host_1, self.host_2)

    def verifyOverlayOutboundConfigTest(self):

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=False)
        print("Overlay config OK\n")

    def l3UnderlayHost1toHost2RoutingTest(self):

        host_1_pkt = simple_udp_packet(eth_src=self.host_1.mac,
                                       eth_dst=self.host_1.peer.mac,
                                       ip_dst=self.host_2.ip,
                                       ip_src=self.host_1.ip,
                                       ip_ttl=64)
        host_1_exp_pkt = simple_udp_packet(eth_src=self.host_2.peer.mac,
                                           eth_dst=self.host_2.mac,
                                           ip_dst=self.host_2.ip,
                                           ip_src=self.host_1.ip,
                                           ip_ttl=63)

        print("Sending simple UDP packet host_1 -> host_2, expecting routed packet")
        send_packet(self, self.host_1.port, host_1_pkt)
        verify_packet(self, host_1_exp_pkt, self.host_2.port)
        print("Underlay Host 1 to Host 2 OK\n")

    def l3UnderlayHost2toHost1RoutingTest(self):

        host_2_pkt = simple_udp_packet(eth_src=self.host_2.mac,
                                       eth_dst=self.host_2.peer.mac,
                                       ip_dst=self.host_1.ip,
                                       ip_src=self.host_2.ip,
                                       ip_ttl=64)
        host_2_exp_pkt = simple_udp_packet(eth_src=self.host_1.peer.mac,
                                           eth_dst=self.host_1.mac,
                                           ip_dst=self.host_1.ip,
                                           ip_src=self.host_2.ip,
                                           ip_ttl=63)

        print("Sending simple UDP packet host_2 -> host_1, expecting routed packet")
        send_packet(self, self.host_2.port, host_2_pkt)
        verify_packet(self, host_2_exp_pkt, self.host_1.port)
        print("Underlay Host 2 to Host 1 OK\n")


@group("draft")
class Vnet2VnetInboundDecapPaValidateSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        #self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=True)
        self.vnet2VnetInboundNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet)
        # PA validation entry with Permit action
        self.pa_validation_create(self.tx_host.ip, src_vnet)

    def vnet2VnetInboundRoutingTest(self, tx_equal_to_rx):
        """
        Inbound VNET to VNET test
        Verifies correct packet routing
        """

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetInboundRoutingTest.__name__, ' OK')

    def vnet2VnetInboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong CA Dst MAC
        - wrong PA Validation IP: pa validation missmatch
        - wrong Physical SIP: routing missmatch
        - wrong VIP
        - wrong VNI
        """

        invalid_vni = 1000
        invalid_ca_dst_mac = "9e:ba:ce:98:d9:e2"
        invalid_pa_sip = "10.10.5.1"  # routing missmatch
        invalid_vip = "10.10.10.10"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_vni=invalid_vni,
                                              invalid_outer_src_ip=invalid_pa_sip,
                                              invalid_inner_dst_mac=invalid_ca_dst_mac,
                                              invalid_vip=invalid_vip)

        invalid_pa_valid_ip = "10.10.1.25"  # pa validation missmatch
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_outer_src_ip=invalid_pa_valid_ip)

        print('\n', self.vnet2VnetInboundNegativeTest.__name__, ' OK')


@group("draft")
class Vnet2VnetInboundDecapPaValidateSinglePortOverlayIpv6Test(Vnet2VnetInboundDecapPaValidateSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def setUp(self):
        super(Vnet2VnetInboundDecapPaValidateSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundDecapPaValidateTwoPortsTest(Vnet2VnetInboundDecapPaValidateSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)

    Verifies positive scenario
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)
        self.vnet2VnetInboundNegativeTest()


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundDecapPaValidateTwoPortsOverlayIpv6Test(Vnet2VnetInboundDecapPaValidateSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)

    Verifies positive scenario
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetInboundDecapSinglePortTest(Vnet2VnetInboundDecapPaValidateSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP inbound routing entry action
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def configureTest(self):
        """
        Setup DUT overlay in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host.ip_prefix.split('/')
        self.inbound_routing_decap_create(eni_id, vni=self.tx_host.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

    def vnet2VnetInboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong CA Dst MAC
        - wrong VIP
        - wrong VNI
        - wrong Physical SIP: routing missmatch
        """

        invalid_vni = 1000
        invalid_ca_dst_mac = "9e:ba:ce:98:d9:e2"
        invalid_vip = "10.10.10.10"
        invalid_pa_sip = "10.10.3.22"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_vni=invalid_vni,
                                              invalid_inner_dst_mac=invalid_ca_dst_mac,
                                              invalid_vip=invalid_vip,
                                              invalid_outer_src_ip=invalid_pa_sip)

        print('\n', self.vnet2VnetInboundNegativeTest.__name__, ' OK')


@group("draft")
class Vnet2VnetInboundDecapSinglePortOverlayIpv6Test(Vnet2VnetInboundDecapSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP inbound routing entry action
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def setUp(self):
        super(Vnet2VnetInboundDecapSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundDecapTwoPortsTest(Vnet2VnetInboundDecapSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP inbound routing entry action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)

    Verifies positive scenario
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)
        self.vnet2VnetInboundNegativeTest()


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundDecapTwoPortsOverlayIpv6Test(Vnet2VnetInboundDecapSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP inbound routing entry action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)

    Verifies positive scenario
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound Vnet to Vnet scenario test case with single eni and
    multiple inbound routing entries (3 PA validate and 1 Decap)
    with underlay config (neighbour + next hop) but without underlay routes

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host (ENI 0) with PA validation 0
    tx_host_1 -> rx_host (ENI 0) with PA validation 1
    tx_host_2 -> rx_host (ENI 0) with PA validation 2
    tx_host_3 -> rx_host (ENI 0) without PA validation
        Negative scenarios:
    tx_host_0 -> rx_host invalid VNI
    tx_host_1 -> rx_host Invalid ENI mac
    tx_host_2 -> rx_host Invalid PA IP
    tx_host_3 -> rx_host invalid VIP
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=True)
        self.vnet2VnetInboundRoutingNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="8.0.0.1",
                                                      ip_prefix="8.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.2.1",
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="9.0.0.1",
                                                      ip_prefix="9.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="192.168.3.1",
                                                      client_vni=30)

        self.tx_host_3 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="11.0.0.1",
                                                      ip_prefix="11.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:AA:00:23:CC:20",
                                                      client_ip="192.168.4.1",
                                                      client_vni=40)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)
        src_vnet_2 = self.vnet_create(vni=self.tx_host_2.client.vni)

        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        # ENI configuration
        eni_id = self.eni_create(vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing decap
        addr_mask = self.tx_host_3.ip_prefix.split('/')
        self.inbound_routing_decap_create(eni_id, vni=self.tx_host_3.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

        # Inbound routing decap PA Validate tx_host_0
        addr_mask = self.tx_host_0.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_0)
        # PA validation entry with Permit action tx_host_0
        self.pa_validation_create(self.tx_host_0.ip, src_vnet_0)

        # Inbound routing decap PA Validate tx_host_1
        addr_mask = self.tx_host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_1)
        # PA validation entry with Permit action tx_host_1
        self.pa_validation_create(self.tx_host_1.ip, src_vnet_1)

        # Inbound routing decap PA Validate tx_host_2
        addr_mask = self.tx_host_2.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_2.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_2)
        # PA validation entry with Permit action tx_host_2
        self.pa_validation_create(self.tx_host_2.ip, src_vnet_2)

    def vnet2VnetInboundRoutingPositiveTest(self, tx_equal_to_rx):
        """
        Inbound VNET to VNET test
        Verifies correct packet routing:
        tx_host_0 -> rx_host (ENI 0) with PA validation 0
        tx_host_1 -> rx_host (ENI 0) with PA validation 1
        tx_host_2 -> rx_host (ENI 0) with PA validation 2
        tx_host_3 -> rx_host (ENI 0) without PA validation
        """

        print("\nVerifying Inbound pkt send tx_host_0 -> rx_host ...")
        self.verify_traffic_scenario(client=self.tx_host_0, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print("\nVerifying Inbound pkt send tx_host_1 -> rx_host ...")
        self.verify_traffic_scenario(client=self.tx_host_1, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print("\nVerifying Inbound pkt send tx_host_2 -> rx_host ...")
        self.verify_traffic_scenario(client=self.tx_host_2, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print("\nVerifying Inbound pkt send tx_host_3 -> rx_host ...")
        self.verify_traffic_scenario(client=self.tx_host_3, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print('\n', self.vnet2VnetInboundRoutingPositiveTest.__name__, ' OK')

    def vnet2VnetInboundRoutingNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        tx_host_0 -> rx_host invalid VNI
        tx_host_1 -> rx_host Invalid ENI mac
        tx_host_2 -> rx_host Invalid PA IP
        tx_host_3 -> rx_host invalid VIP
        """

        invalid_vni = 200
        invalid_ca_dst_mac = "9e:ba:ce:98:d9:e2"
        invalid_pa_sip = "10.10.5.1"  # routing missmatch
        invalid_vip = "10.10.10.10"

        print("\nVerifying Inbound pkt drop with invalid VNI tx_host_0 -> rx_host ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_0, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_vni=invalid_vni)
        print("OK")

        print("\nVerifying Inbound pkt drop with invalid ENI mac tx_host_1 -> rx_host ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_1, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_inner_dst_mac=invalid_ca_dst_mac)
        print("OK")

        print("\nVerifying Inbound pkt drop with invalid PA IP tx_host_2 -> rx_host ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_2, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_outer_src_ip=invalid_pa_sip)
        print("OK")

        print("\nVerifying Inbound pkt drop with invalid VIP tx_host_3 -> rx_host ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_3, server=self.rx_host,
                                              fake_mac=False,
                                              invalid_vip=invalid_vip)
        print("OK")

        print('\n', self.vnet2VnetInboundRoutingNegativeTest.__name__, ' OK')


@group("draft")
class Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortOverlayIpv6Test(Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with single eni and
    multiple inbound routing entries (3 PA validate and 1 Decap)
    with underlay config (neighbour + next hop) but without underlay routes

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host (ENI 0) with PA validation 0
    tx_host_1 -> rx_host (ENI 0) with PA validation 1
    tx_host_2 -> rx_host (ENI 0) with PA validation 2
    tx_host_3 -> rx_host (ENI 0) without PA validation
    """

    def setUp(self):
        super(Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="8.0.0.1",
                                                      ip_prefix="8.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="cccc::60",
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="9.0.0.1",
                                                      ip_prefix="9.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="dddd::14",
                                                      client_vni=30)

        self.tx_host_3 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="11.0.0.1",
                                                      ip_prefix="11.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:AA:00:23:CC:20",
                                                      client_ip="eeee::80",
                                                      client_vni=40)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)
        src_vnet_2 = self.vnet_create(vni=self.tx_host_2.client.vni)

        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        # ENI configuration
        eni_id = self.eni_create(vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing decap
        addr_mask = self.tx_host_3.ip_prefix.split('/')
        self.inbound_routing_decap_create(eni_id, vni=self.tx_host_3.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

        # Inbound routing decap PA Validate tx_host_0
        addr_mask = self.tx_host_0.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_0)
        # PA validation entry with Permit action tx_host_0
        self.pa_validation_create(self.tx_host_0.ip, src_vnet_0)

        # Inbound routing decap PA Validate tx_host_1
        addr_mask = self.tx_host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_1)
        # PA validation entry with Permit action tx_host_1
        self.pa_validation_create(self.tx_host_1.ip, src_vnet_1)

        # Inbound routing decap PA Validate tx_host_2
        addr_mask = self.tx_host_2.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_2.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_2)
        # PA validation entry with Permit action tx_host_2
        self.pa_validation_create(self.tx_host_2.ip, src_vnet_2)

@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundMultiplePaValidatesSingleEniTwoPortsTest(Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with single eni and
    multiple inbound routing entries (3 PA validate and 1 Decap)
    with underlay config (2 neighbours, 2 next-hops, 5 routes)

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host (ENI 0) with PA validation 0
    tx_host_1 -> rx_host (ENI 0) with PA validation 1
    tx_host_2 -> rx_host (ENI 0) with PA validation 2
    tx_host_3 -> rx_host (ENI 0) without PA validation
    """

    def runTest(self):
        self.configureTest()
        #self.configure_underlay()

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=False)

    def configure_underlay(self):

        rif_0 = self.router_interface_create(self.tx_host_0.peer.port,
                                             src_mac=self.tx_host_0.peer.mac)
        nhop_0 = self.nexthop_create(rif_0, self.tx_host_0.ip)
        self.neighbor_create(rif_0, self.tx_host_0.ip, self.tx_host_0.mac)

        self.route_create(self.tx_host_0.ip_prefix, nhop_0)
        self.route_create(self.tx_host_1.ip_prefix, nhop_0)
        self.route_create(self.tx_host_2.ip_prefix, nhop_0)
        self.route_create(self.tx_host_3.ip_prefix, nhop_0)

        rif_1 = self.router_interface_create(self.rx_host.peer.port,
                                             src_mac=self.rx_host.peer.mac)
        nhop_1 = self.nexthop_create(rif_1, self.rx_host.ip)
        self.neighbor_create(rif_1, self.rx_host.ip, self.rx_host.mac)
        self.route_create(self.rx_host.ip_prefix, nhop_1)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundMultiplePaValidatesSingleEniTwoPortsOverlayIpv6Test(Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with single eni and
    multiple inbound routing entries (3 PA validate and 1 Decap)
    with underlay config (2 neighbours, 2 next-hops, 5 routes)

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host (ENI 0) with PA validation 0
    tx_host_1 -> rx_host (ENI 0) with PA validation 1
    tx_host_2 -> rx_host (ENI 0) with PA validation 2
    tx_host_3 -> rx_host (ENI 0) without PA validation
    """

    def runTest(self):
        self.configureTest()
        #self.configure_underlay()

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=False)

    def configure_underlay(self):

        rif_0 = self.router_interface_create(self.tx_host_0.peer.port,
                                             src_mac=self.tx_host_0.peer.mac)
        nhop_0 = self.nexthop_create(rif_0, self.tx_host_0.ip)
        self.neighbor_create(rif_0, self.tx_host_0.ip, self.tx_host_0.mac)

        self.route_create(self.tx_host_0.ip_prefix, nhop_0)
        self.route_create(self.tx_host_1.ip_prefix, nhop_0)
        self.route_create(self.tx_host_2.ip_prefix, nhop_0)
        self.route_create(self.tx_host_3.ip_prefix, nhop_0)

        rif_1 = self.router_interface_create(self.rx_host.peer.port,
                                             src_mac=self.rx_host.peer.mac)
        nhop_1 = self.nexthop_create(rif_1, self.rx_host.ip)
        self.neighbor_create(rif_1, self.rx_host.ip, self.rx_host.mac)
        self.route_create(self.rx_host.ip_prefix, nhop_1)


@group("draft")
class Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound Vnet to Vnet scenario test case with
    multiple inbound routing entries (2 PA validate and 1 Decap)
    with underlay config (neighbour + next hop) but without underlay routes

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host_0 (ENI 0) with PA validation
    tx_host_1 -> rx_host_1 (ENI 1) with PA validation
    tx_host_2 -> rx_host_0 (ENI 0) without PA validation
        Negative scenarios:
    tx_host_0 -> rx_host_1
    tx_host_1 -> rx_host_0
    tx_host_2 -> rx_host_1
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=True)
        self.vnet2VnetInboundRoutingNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.2.1",
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="9.0.0.1",
                                                      ip_prefix="9.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="192.168.3.1",
                                                      client_vni=30)

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip="192.168.4.1",
                                                      client_vni=20)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host_0.client.vni)
        self.direction_lookup_create(self.rx_host_1.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        # ENI 0 configuration
        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.rx_host_0.ip),
                                   vm_vni=self.rx_host_0.client.vni,
                                   vnet_id=dst_vnet_0)
        self.eni_mac_map_create(eni_id_0, self.rx_host_0.client.mac)  # ENI MAC

        # Inbound routing decap
        addr_mask = self.tx_host_2.ip_prefix.split('/')
        self.inbound_routing_decap_create(eni_id_0, vni=self.tx_host_2.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

        # Inbound routing decap PA Validate
        addr_mask = self.tx_host_0.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id_0, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_0)
        # PA validation entry with Permit action
        self.pa_validation_create(self.tx_host_0.ip, src_vnet_0)

        # ENI 1 configuration
        eni_id_1 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.rx_host_1.ip),
                                   vm_vni=self.rx_host_1.client.vni,
                                   vnet_id=dst_vnet_1)
        self.eni_mac_map_create(eni_id_1, self.rx_host_1.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id_1, vni=self.tx_host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_1)
        # PA validation entry with Permit action
        self.pa_validation_create(self.tx_host_1.ip, src_vnet_1)

    def vnet2VnetInboundRoutingPositiveTest(self, tx_equal_to_rx):
        """
        Inbound VNET to VNET test
        Verifies correct packet routing:
        tx_host_0 -> rx_host_0 (ENI 0) with PA validation
        tx_host_1 -> rx_host_1 (ENI 1) with PA validation
        tx_host_2 -> rx_host_0 (ENI 0) without PA validation
        """

        print("\nVerifying Inbound pkt send tx_host_0 -> rx_host_0 ...")
        self.verify_traffic_scenario(client=self.tx_host_0, server=self.rx_host_0,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print("\nVerifying Inbound pkt send tx_host_1 -> rx_host_1 ...")
        self.verify_traffic_scenario(client=self.tx_host_1, server=self.rx_host_1,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")

        print("\nVerifying Inbound pkt send tx_host_2 -> rx_host_0 ...")
        self.verify_traffic_scenario(client=self.tx_host_2, server=self.rx_host_0,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)
        print("OK")


        print('\n', self.vnet2VnetInboundRoutingPositiveTest.__name__, ' OK')

    def vnet2VnetInboundRoutingNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        tx_host_0 -> rx_host_1
        tx_host_1 -> rx_host_0
        tx_host_2 -> rx_host_1
        """

        print("\nVerifying Inbound pkt drop tx_host_0 -> rx_host_1 ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_0, server=self.rx_host_1,
                                              fake_mac=False, valid_pkt_drop=True)
        print("OK")

        print("\nVerifying Inbound pkt drop tx_host_1 -> rx_host_0 ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_1, server=self.rx_host_0,
                                              fake_mac=False, valid_pkt_drop=True)
        print("OK")

        print("\nVerifying Inbound pkt drop tx_host_2 -> rx_host_1 ...")
        self.verify_negative_traffic_scenario(client=self.tx_host_2, server=self.rx_host_1,
                                              fake_mac=False, valid_pkt_drop=True)
        print("OK")

        print('\n', self.vnet2VnetInboundRoutingNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortOverlayIpv6Test(Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    multiple inbound routing entries (2 PA validate and 1 Decap)
    with underlay config (neighbour + next hop) but without underlay routes

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host_0 (ENI 0) with PA validation
    tx_host_1 -> rx_host_1 (ENI 1) with PA validation
    tx_host_2 -> rx_host_0 (ENI 0) without PA validation
        Negative scenarios:
    tx_host_0 -> rx_host_1
    tx_host_1 -> rx_host_0
    tx_host_2 -> rx_host_1
    """

    def setUp(self):
        super(Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="cccc::30",
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="9.0.0.1",
                                                      ip_prefix="9.0.0.0/24",
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="dddd::40",
                                                      client_vni=30)

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip="eeee::50",
                                                      client_vni=20)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host_0.client.vni)
        self.direction_lookup_create(self.rx_host_1.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        # ENI 0 configuration
        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.rx_host_0.ip),
                                   vm_vni=self.rx_host_0.client.vni,
                                   vnet_id=dst_vnet_0)
        self.eni_mac_map_create(eni_id_0, self.rx_host_0.client.mac)  # ENI MAC

        # Inbound routing decap
        addr_mask = self.tx_host_2.ip_prefix.split('/')
        self.inbound_routing_decap_create(eni_id_0, vni=self.tx_host_2.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

        # Inbound routing decap PA Validate
        self.inbound_routing_decap_validate_create(eni_id_0, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_0)
        # PA validation entry with Permit action
        self.pa_validation_create(self.tx_host_0.ip, src_vnet_0)

        # ENI 1 configuration
        eni_id_1 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.rx_host_1.ip),
                                   vm_vni=self.rx_host_1.client.vni,
                                   vnet_id=dst_vnet_1)
        self.eni_mac_map_create(eni_id_1, self.rx_host_1.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id_1, vni=self.tx_host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet_1)
        # PA validation entry with Permit action
        self.pa_validation_create(self.tx_host_1.ip, src_vnet_1)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundMultiplePaValidatesMultipleEniTwoPortsTest(Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with
    multiple inbound routing entries (2 PA validate and 1 Decap)
    with underlay config (2 neighbours, 2 next-hops, 3 routes)

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host_0 (ENI 0) with PA validation
    tx_host_1 -> rx_host_1 (ENI 1) with PA validation
    tx_host_2 -> rx_host_0 (ENI 0) without PA validation
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay()

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=False)

    def configure_underlay(self):
        rif_0 = self.router_interface_create(self.tx_host_0.peer.port,
                                             src_mac=self.tx_host_0.peer.mac)
        nhop_0 = self.nexthop_create(rif_0, self.tx_host_0.ip)
        self.neighbor_create(rif_0, self.tx_host_0.ip, self.tx_host_0.mac)
        self.route_create(self.tx_host_0.ip_prefix, nhop_0)
        self.route_create(self.tx_host_2.ip_prefix, nhop_0)

        rif_1 = self.router_interface_create(self.rx_host_0.peer.port,
                                             src_mac=self.rx_host_0.peer.mac)
        nhop_1 = self.nexthop_create(rif_1, self.rx_host_0.ip)
        self.neighbor_create(rif_1, self.rx_host_0.ip, self.rx_host_0.mac)
        self.route_create(self.rx_host_1.ip_prefix, nhop_1)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundMultiplePaValidatesMultipleEniTwoPortsOverlayIpv6Test(Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    multiple inbound routing entries (2 PA validate and 1 Decap)
    with underlay config (2 neighbours, 2 next-hops, 3 routes)

    Connections:
        Positive scenarios:
    tx_host_0 -> rx_host_0 (ENI 0) with PA validation
    tx_host_1 -> rx_host_1 (ENI 1) with PA validation
    tx_host_2 -> rx_host_0 (ENI 0) without PA validation
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay()

        self.vnet2VnetInboundRoutingPositiveTest(tx_equal_to_rx=False)

    def configure_underlay(self):
        rif_0 = self.router_interface_create(self.tx_host_0.peer.port,
                                             src_mac=self.tx_host_0.peer.mac)
        nhop_0 = self.nexthop_create(rif_0, self.tx_host_0.ip)
        self.neighbor_create(rif_0, self.tx_host_0.ip, self.tx_host_0.mac)
        self.route_create(self.tx_host_0.ip_prefix, nhop_0)
        self.route_create(self.tx_host_2.ip_prefix, nhop_0)

        rif_1 = self.router_interface_create(self.rx_host_0.peer.port,
                                             src_mac=self.rx_host_0.peer.mac)
        nhop_1 = self.nexthop_create(rif_1, self.rx_host_0.ip)
        self.neighbor_create(rif_1, self.rx_host_0.ip, self.rx_host_0.mac)
        self.route_create(self.rx_host_1.ip_prefix, nhop_1)


@group("draft")
class Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action with multiple PA validate entries
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, add_routes=False)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.20",
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.2.1",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.189",
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="192.168.3.1",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_3 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.200", # for PA validate missmatch
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:AA:00:23:CC:20",
                                                      client_ip="192.168.4.1",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_4 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.2.20", # for Inbound route missmatch
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:BB:00:00:AC:A0",
                                                      client_ip="192.168.4.1",
                                                      client_vni=self.tx_host_0.client.vni)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host_0.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host_0.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet)
        # PA validation entries with Permit action
        self.pa_validation_create(self.tx_host_0.ip, src_vnet)
        self.pa_validation_create(self.tx_host_1.ip, src_vnet)
        self.pa_validation_create(self.tx_host_2.ip, src_vnet)

    def vnet2VnetInboundRoutingTest(self, tx_equal_to_rx):
        """
        Inbound VNET to VNET test
        Verifies correct packet routing
        """

        print(f"\nPA validate {self.tx_host_0.ip} verification, expect pass")
        self.verify_traffic_scenario(client=self.tx_host_0, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nPA validate {self.tx_host_1.ip} verification, expect pass")
        self.verify_traffic_scenario(client=self.tx_host_1, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nPA validate {self.tx_host_2.ip} verification, expect pass")
        self.verify_traffic_scenario(client=self.tx_host_2, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nPA validate {self.tx_host_3.ip} verification, expect drop - PA validation missmatch")
        self.verify_negative_traffic_scenario(client=self.tx_host_3, server=self.rx_host,
                                              fake_mac=False, valid_pkt_drop=True)

        print(f"\nPA validate {self.tx_host_4.ip} verification, expect drop - Inbound route missmatch")
        self.verify_negative_traffic_scenario(client=self.tx_host_4, server=self.rx_host,
                                              fake_mac=False, valid_pkt_drop=True)


@group("draft")
class Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortIpv6Test(Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action with multiple PA validate entries
    with underlay config (neighbour + next hop) but without underlay routes

    Verifies positive and negative scenarios
    """

    def setUp(self):
        super(Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortIpv6Test, self).setUp(overlay_ipv6=True)

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, add_routes=False)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """
        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.15",
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="cccc::40",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.100",
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:20",
                                                      client_ip="dddd::50",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_3 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.1.3", # for PA validate missmatch
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:AA:00:23:CC:20",
                                                      client_ip="eeee::60",
                                                      client_vni=self.tx_host_0.client.vni)

        self.tx_host_4 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip="10.10.12.20", # for Inbound route missmatch
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:BB:00:00:AC:A0",
                                                      client_ip="2603::10",
                                                      client_vni=self.tx_host_0.client.vni)

        self.vip_create(self.tx_host_0.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host_0.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                 vm_vni=self.rx_host.client.vni,
                                 vnet_id=dst_vnet)
        self.eni_mac_map_create(eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host_0.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id, vni=self.tx_host_0.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=src_vnet)
        # PA validation entries with Permit action
        self.pa_validation_create(self.tx_host_0.ip, src_vnet)
        self.pa_validation_create(self.tx_host_1.ip, src_vnet)
        self.pa_validation_create(self.tx_host_2.ip, src_vnet)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetSingleInboundRouteMultiplePaValidateTwoPortsTest(Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortTest):
    """
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action with multiple PA validate entries
    with full underlay config (2 neighbours + 2 next hops + 2 routes)

    Verifies positive and negative scenarios
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetSingleInboundRouteMultiplePaValidateTwoPortsIpv6Test(Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound Vnet to Vnet scenario test case with
    TUNNEL_DECAP_PA_VALIDATE inbound routing entry action with multiple PA validate entries
    with underlay config (2 neighbours + 2 next hops + 2 routes)

    Verifies positive and negative scenarios
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, self.rx_host)

        self.vnet2VnetInboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundEniSetUpDownSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound Vnet to Vnet test scenario
    Verifies packets forwarding/drop in accordance with ENI admin state
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)
        self.eni_set_admin_state(self.eni_id, "down")
        self.vnet2VnetEniDownTrafficTest()
        self.eni_set_admin_state(self.eni_id, "up")
        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT overlay in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        self.eni_id = self.eni_create(admin_state=True,
                                      vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
                                      vm_vni=self.rx_host.client.vni,
                                      vnet_id=dst_vnet)
        self.eni_mac_map_create(self.eni_id, self.rx_host.client.mac)  # ENI MAC

        # Inbound routing PA Validate
        addr_mask = self.tx_host.ip_prefix.split('/')
        self.inbound_routing_decap_create(self.eni_id, vni=self.tx_host.client.vni,
                                          sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]))

    def vnet2VnetEniUpTrafficTest(self, tx_equal_to_rx):
        """
        Verifies inbound packet routing when ENI admin state is UP
        """

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=False, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetEniUpTrafficTest.__name__, ' OK')

    def vnet2VnetEniDownTrafficTest(self):
        """
        Verifies inbound packet drop when ENI admin state is DOWN
        """

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=False, valid_pkt_drop=True)

        print('\n', self.vnet2VnetEniDownTrafficTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundEniSetUpDownTwoPortsTest(Vnet2VnetInboundEniSetUpDownSinglePortTest):
    """
    Inbound Vnet to Vnet test scenario
    Verifies packets forwarding/drop in accordance with ENI admin state
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)
        self.eni_set_admin_state(self.eni_id, "down")
        self.vnet2VnetEniDownTrafficTest()
        self.eni_set_admin_state(self.eni_id, "up")
        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)


@group("draft")
class Vnet2VnetOutboundRouteVnetDirectSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=True)
        self.vnet2VnetOutboundNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC
        # outbound routing
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id, "192.168.1.0/24", dst_vnet,
                                                 overlay_ip="192.168.1.10")
        self.outbound_ca_to_pa_create(dst_vnet,  # DST vnet id
                                      "192.168.1.10",  # DST IP addr
                                      self.rx_host.ip,  # Underlay DIP
                                      overlay_dmac=self.rx_host.client.mac)

    def vnet2VnetOutboundRoutingTest(self, tx_equal_to_rx):
        """
        Outbound VNET to VNET test
        Verifies correct packet routing
        """

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetOutboundRoutingTest.__name__, ' OK')

    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "192.168.200.200"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
class Vnet2VnetOutboundRouteVnetDirectSinglePortOverlayIpv6Test(Vnet2VnetOutboundRouteVnetDirectSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetOutboundRouteVnetDirectSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC
        # outbound routing
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id, "bbbb::0/64", dst_vnet,
                                                 overlay_ip="bbbb::bc")
        self.outbound_ca_to_pa_create(dst_vnet,  # DST vnet id
                                      "bbbb::bc",  # DST IP addr
                                      self.rx_host.ip,  # Underlay DIP
                                      overlay_dmac=self.rx_host.client.mac)

    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "dddd::dc"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteVnetDirectTwoPortsTest(Vnet2VnetOutboundRouteVnetDirectSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundNegativeTest()


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteVnetDirectTwoPortsOverlayIpv6Test(Vnet2VnetOutboundRouteVnetDirectSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundRouteVnetSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=True)
        self.vnet2VnetOutboundNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetOutboundRoutingTest(self, tx_equal_to_rx):
        """
        Outbound VNET to VNET test
        Verifies correct packet routing
        """

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetOutboundRoutingTest.__name__, ' OK')


    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "192.168.200.200"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "192.168.1.200"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
class Vnet2VnetOutboundRouteVnetSinglePortOverlayIpv6Test(Vnet2VnetOutboundRouteVnetSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action
    with underlay config (neighbour + next hop) but without underlay routes
    """
    def setUp(self):
        super(Vnet2VnetOutboundRouteVnetSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="bbbb::0/64",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "dddd::dc"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "bbbb::dc"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteVnetTwoPortsTest(Vnet2VnetOutboundRouteVnetSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundNegativeTest()


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteVnetTwoPortsOverlayIpv6Test(Vnet2VnetOutboundRouteVnetSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundEniSetUpDownSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario
    Verifies packets forwarding/drop in accordance with ENI admin state
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)
        self.eni_set_admin_state(self.eni_id, "down")
        self.vnet2VnetEniDownTrafficTest()
        self.eni_set_admin_state(self.eni_id, "up")
        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        self.eni_id = self.eni_create(admin_state=True,
                                      vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                      vm_vni=self.tx_host.client.vni,
                                      vnet_id=src_vnet,
                                      outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(self.eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetEniUpTrafficTest(self, tx_equal_to_rx):
        """
        Verifies correct outbound packet routing when ENI admin state is UP
        """

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetEniUpTrafficTest.__name__, ' OK')

    def vnet2VnetEniDownTrafficTest(self):
        """
        Verifies outbound packet drop when ENI admin state is DOWN
        """

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, valid_pkt_drop=True)

        print('\n', self.vnet2VnetEniDownTrafficTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundEniSetUpDownTwoPortsTest(Vnet2VnetOutboundEniSetUpDownSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario
    Verifies packets forwarding/drop in accordance with ENI admin state
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)
        self.eni_set_admin_state(self.eni_id, "down")
        self.vnet2VnetEniDownTrafficTest()
        self.eni_set_admin_state(self.eni_id, "up")
        self.vnet2VnetEniUpTrafficTest(tx_equal_to_rx=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteDirectSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT action
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.outboundRouteDirectTest(tx_equal_to_rx=True)
        self.outboundRouteDirectNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.client.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet)

        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)

        # outbound routing
        self.outbound_routing_direct_create(eni_id, "192.168.1.0/24")

    def outboundRouteDirectTest(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx,
                                     route_direct=True)

    def outboundRouteDirectNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "192.168.200.200"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "192.168.1.200"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.outboundRouteDirectNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteDirectSinglePortOverlayIpv6Test(Vnet2VnetOutboundRouteDirectSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT action
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetOutboundRouteDirectSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.vip_create(self.tx_host.client.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet)

        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)

        # outbound routing
        self.outbound_routing_direct_create(eni_id, "bbbb::0/64")

    def outboundRouteDirectNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "dddd::dc"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "bbbb::dc"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.outboundRouteDirectNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteDirectTwoPortsTest(Vnet2VnetOutboundRouteDirectSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.outboundRouteDirectTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundRouteDirectTwoPortsOverlayIpv6Test(Vnet2VnetOutboundRouteDirectSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with Outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT action
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.outboundRouteDirectTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action and multiple CA2PA entries
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        # Reconfigure configuration for tx equal to rx
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=True)
        self.vnet2VnetOutboundNegativeTest()

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.1.17",
                                                      client_vni=self.rx_host_0.client.vni)

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:08:18",
                                                      client_ip="192.168.1.199",
                                                      client_vni=self.rx_host_0.client.vni)

        self.rx_host_3 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:E1",
                                                      client_ip="192.168.1.77",
                                                      client_vni=self.rx_host_0.client.vni)

        self.vip_create(self.tx_host.peer.ip)

        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host_0.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_3.client.ip,
                                      underlay_dip=self.rx_host_3.ip,
                                      overlay_dmac=self.rx_host_3.client.mac,
                                      use_dst_vnet_vni=False)

    def vnet2VnetOutboundRoutingTest(self, tx_equal_to_rx):
        """
        Outbound VNET to VNET test
        Verifies correct packet routing
        """

        print(f"\nVerify outbound route to CA {self.rx_host_0.client.ip}, expect pass")
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_0,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nVerify outbound route to CA {self.rx_host_1.client.ip}, expect pass")
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_1,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nVerify outbound route to CA {self.rx_host_2.client.ip}, expect pass")
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_2,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print(f"\nVerify outbound route to CA {self.rx_host_3.client.ip} and use_dst_vnet=False, expect pass")
        self.rx_host_3.client.vni = self.tx_host.client.vni
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_3,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetOutboundRoutingTest.__name__, ' OK')

    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "192.168.200.200"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "192.168.1.200"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortIpv6Test(Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action and multiple CA2PA entries
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="bbbb:0000:0000:0000:1234::00",
                                                      client_vni=self.rx_host_0.client.vni)

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:08:18",
                                                      client_ip="bbbb:0000:0000:0000:0000:ab12::00",
                                                      client_vni=self.rx_host_0.client.vni)

        self.rx_host_3 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:10:00:00:AA:E1",
                                                      client_ip="bbbb::40",
                                                      client_vni=self.rx_host_0.client.vni)

        self.vip_create(self.tx_host.peer.ip)

        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host_0.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="bbbb::0/64",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host_3.client.ip,
                                      underlay_dip=self.rx_host_3.ip,
                                      overlay_dmac=self.rx_host_3.client.mac,
                                      use_dst_vnet_vni=False)

    def vnet2VnetOutboundNegativeTest(self):
        """
        Verifies negative scenarios (packet drop):
        - wrong VIP
        - routing drop (CA Dst IP does not match any routing entry)
        - wrong CA Src MAC (does not match any ENI)
        - mapping drop (CA Dst IP matches routing entry prefix but drops by ca_to_pa)
        """

        invalid_vip = "10.10.10.10"
        wrong_inner_dst_ip = "bbbb:0000:0000:1111::00"
        wrong_inner_src_ca_mac = "00:aa:00:aa:00:aa"

        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_vip=invalid_vip,
                                              invalid_inner_dst_ip=wrong_inner_dst_ip,
                                              invalid_inner_src_mac=wrong_inner_src_ca_mac)

        wrong_inner_dst_ip = "bbbb::33"
        self.verify_negative_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                              fake_mac=True, invalid_inner_dst_ip=wrong_inner_dst_ip)

        print('\n', self.vnet2VnetOutboundNegativeTest.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetSingleOutboundRouteMultipleCa2PaTwoPortsTest(Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action and multiple CA2PA entries
    with full underlay config (2 neighbours + 2 next hops + 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetSingleOutboundRouteMultipleCa2PaTwoPortsIpv6Test(Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6
    Outbound Vnet to Vnet test scenario with outbound routing entry
    SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action and multiple CA2PA entries
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundRoutingTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=True)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.2.1",
                                                      client_vni=3)

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.2.0/24",
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)

    def vnet2VnetOutboundDstVnetIdTrueTest(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_0,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetOutboundDstVnetIdTrueTest.__name__, ' OK')

    def vnet2VnetOutboundDstVnetIdFalseTest(self, tx_equal_to_rx):

        # For use_dst_vnet_vni=False verification change rx client vni to tx client vni
        self.rx_host_1.client.vni = self.tx_host.client.vni

        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_1,
                                     connection=self.connection, fake_mac=True, tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.vnet2VnetOutboundDstVnetIdFalseTest.__name__, ' OK')


@group("draft")
class Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortOverlayIpv6Test(Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="cccc::30",
                                                      client_vni=3)

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="bbbb::0/64",
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="cccc::0/64",
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundDstVnetIdRouteVnetTwoPortsTest(Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundDstVnetIdRouteVnetTwoPortsOverlayIpv6Test(Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortTest(Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=True)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="192.168.2.1",
                                                      client_vni=3)

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                                 dst_vnet_id=dst_vnet_0,
                                                 overlay_ip="192.168.1.111")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip="192.168.1.111",
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.2.0/24",
                                                 dst_vnet_id=dst_vnet_1,
                                                 overlay_ip="192.168.2.222")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip="192.168.2.222",
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)


@group("draft")
class Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortOverlayIpv6Test(Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip="cccc::30",
                                                      client_vni=3)

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id, lpm="bbbb::0/64",
                                                 dst_vnet_id=dst_vnet_0,
                                                 overlay_ip="bbbb::bc")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip="bbbb::bc",
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id, lpm="cccc::0/64",
                                                 dst_vnet_id=dst_vnet_1,
                                                 overlay_ip="cccc::bc")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip="cccc::bc",
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundDstVnetIdRouteVnetDirectTwoPortsTest(Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundDstVnetIdRouteVnetDirectTwoPortstOverlayIpv6Test(Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario that verifies
    CA to PA entry use_dst_vnet_vni attribute True and False values
    when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.vnet2VnetOutboundDstVnetIdTrueTest(tx_equal_to_rx=False)
        self.vnet2VnetOutboundDstVnetIdFalseTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundOutboundMultipleConfigsSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Inbound and Outbound Vnet to Vnet test scenario
    Verifies overlay routing with multiple inbound/outbound configurations
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.host_0, self.host_2, add_routes=False)

        self.outboundHost0toHost2Test(tx_equal_to_rx=True)
        self.inboundHost2toHost0Test(tx_equal_to_rx=True)

        self.outboundHost3toHost1Test(tx_equal_to_rx=True)
        self.inboundHost1toHost3Test(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        host_0.client (vni 1) ca ip: 192.168.0.1 (eni_0) <---> host_2.client (vni 2) ca ip: 192.168.1.1
        host_1.client (vni 10) ca ip: 192.168.2.1 <---> (eni_3) host_3.client (vni 20) ca ip: 192.168.3.1
        """

        self.host_0 = self.tx_host

        self.host_1 = self.define_neighbor_network(port=self.host_0.port,
                                                   mac=self.host_0.mac,
                                                   ip=self.host_0.ip,
                                                   ip_prefix=self.host_0.ip_prefix,
                                                   peer_port=self.host_0.peer.port,
                                                   peer_mac=self.host_0.peer.mac,
                                                   peer_ip=self.host_0.peer.ip,
                                                   client_mac="00:03:00:00:05:16",
                                                   client_ip="192.168.2.1",
                                                   client_vni=10)
        self.host_2 = self.rx_host

        self.host_3 = self.define_neighbor_network(port=self.host_2.port,
                                                   mac=self.host_2.mac,
                                                   ip=self.host_2.ip,
                                                   ip_prefix=self.host_2.ip_prefix,
                                                   peer_port=self.host_2.peer.port,
                                                   peer_mac=self.host_2.peer.mac,
                                                   peer_ip=self.host_2.peer.ip,
                                                   client_mac="00:04:00:00:06:17",
                                                   client_ip="192.168.3.1",
                                                   client_vni=20)
        # Overlay routing
        self.vip_create(self.host_0.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.host_0.client.vni)
        self.direction_lookup_create(self.host_3.client.vni)

        host_0_vnet = self.vnet_create(vni=self.host_0.client.vni)
        host_1_vnet = self.vnet_create(vni=self.host_1.client.vni)

        host_2_vnet = self.vnet_create(vni=self.host_2.client.vni)
        host_3_vnet = self.vnet_create(vni=self.host_3.client.vni)

        outbound_routing_group_id_0 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_3 = self.outbound_routing_group_create(disabled=False)

        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.host_0.ip),
                                   vm_vni=self.host_0.client.vni,
                                   vnet_id=host_0_vnet,
                                   outbound_routing_group_id=outbound_routing_group_id_0)
        self.eni_mac_map_create(eni_id_0, self.host_0.client.mac)

        eni_id_3 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.host_3.ip),
                                   vm_vni=self.host_3.client.vni,
                                   vnet_id=host_3_vnet,
                                   outbound_routing_group_id=outbound_routing_group_id_3)
        self.eni_mac_map_create(eni_id_3, self.host_3.client.mac)

        # ENI 0 inbound/outbound routing
        addr_mask = self.host_2.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id=eni_id_0, vni=self.host_2.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=host_2_vnet)
        self.pa_validation_create(sip=self.host_2.ip,
                                  vnet_id=host_2_vnet)

        self.outbound_routing_vnet_create(outbound_routing_group_id_0, lpm="192.168.1.0/24",
                                          dst_vnet_id=host_2_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=host_2_vnet,
                                      dip=self.host_2.client.ip,
                                      underlay_dip=self.host_2.ip,
                                      overlay_dmac=self.host_2.client.mac)

        # ENI 3 inbound/outbound routing
        addr_mask = self.host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id=eni_id_3, vni=self.host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=host_1_vnet)
        self.pa_validation_create(sip=self.host_1.ip,
                                  vnet_id=host_1_vnet)

        self.outbound_routing_vnet_create(outbound_routing_group_id_3, lpm="192.168.2.0/24",
                                          dst_vnet_id=host_1_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=host_1_vnet,
                                      dip=self.host_1.client.ip,
                                      underlay_dip=self.host_1.ip,
                                      overlay_dmac=self.host_1.client.mac)

    def outboundHost0toHost2Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.host_0,
                                     server=self.host_2,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.outboundHost0toHost2Test.__name__, ' OK')

    def inboundHost2toHost0Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.host_2,
                                     server=self.host_0,
                                     connection=self.connection,
                                     fake_mac=False,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.inboundHost2toHost0Test.__name__, ' OK')

    def outboundHost3toHost1Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.host_3,
                                     server=self.host_1,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.outboundHost3toHost1Test.__name__, ' OK')

    def inboundHost1toHost3Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.host_1,
                                     server=self.host_3,
                                     connection=self.connection,
                                     fake_mac=False,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.inboundHost1toHost3Test.__name__, ' OK')


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundOutboundMultipleConfigsSinglePortOverlayIpv6Test(Vnet2VnetInboundOutboundMultipleConfigsSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound and Outbound Vnet to Vnet test scenario
    Verifies overlay routing with multiple inbound/outbound configurations
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        host_0.client (vni 1) ca ipv6: aaaa::10 (eni_0) <---> host_2.client (vni 2) ca ipv6: bbbb::20
        host_1.client (vni 10) ca ipv6: cccc::30        <---> (eni_3) host_3.client (vni 20) ca ipv6: dddd::40
        """

        self.host_0 = self.tx_host

        self.host_1 = self.define_neighbor_network(port=self.host_0.port,
                                                   mac=self.host_0.mac,
                                                   ip=self.host_0.ip,
                                                   ip_prefix=self.host_0.ip_prefix,
                                                   peer_port=self.host_0.peer.port,
                                                   peer_mac=self.host_0.peer.mac,
                                                   peer_ip=self.host_0.peer.ip,
                                                   client_mac="00:03:00:00:05:16",
                                                   client_ip="cccc::30",
                                                   client_vni=10)
        self.host_2 = self.rx_host

        self.host_3 = self.define_neighbor_network(port=self.host_2.port,
                                                   mac=self.host_2.mac,
                                                   ip=self.host_2.ip,
                                                   ip_prefix=self.host_2.ip_prefix,
                                                   peer_port=self.host_2.peer.port,
                                                   peer_mac=self.host_2.peer.mac,
                                                   peer_ip=self.host_2.peer.ip,
                                                   client_mac="00:04:00:00:06:17",
                                                   client_ip="dddd::40",
                                                   client_vni=20)
        # Overlay routing
        self.vip_create(self.host_0.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.host_0.client.vni)
        self.direction_lookup_create(self.host_3.client.vni)

        host_0_vnet = self.vnet_create(vni=self.host_0.client.vni)
        host_1_vnet = self.vnet_create(vni=self.host_1.client.vni)

        host_2_vnet = self.vnet_create(vni=self.host_2.client.vni)
        host_3_vnet = self.vnet_create(vni=self.host_3.client.vni)

        outbound_routing_group_id_0 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_3 = self.outbound_routing_group_create(disabled=False)

        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.host_0.ip),
                                   vm_vni=self.host_0.client.vni,
                                   vnet_id=host_0_vnet,
                                   outbound_routing_group_id=outbound_routing_group_id_0)
        self.eni_mac_map_create(eni_id_0, self.host_0.client.mac)

        eni_id_3 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.host_3.ip),
                                   vm_vni=self.host_3.client.vni,
                                   vnet_id=host_3_vnet,
                                   outbound_routing_group_id=outbound_routing_group_id_3)
        self.eni_mac_map_create(eni_id_3, self.host_3.client.mac)

        # ENI 0 inbound/outbound routing
        addr_mask = self.host_2.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id=eni_id_0, vni=self.host_2.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=host_2_vnet)
        self.pa_validation_create(sip=self.host_2.ip,
                                  vnet_id=host_2_vnet)

        self.outbound_routing_vnet_create(outbound_routing_group_id_0, lpm="bbbb::0/64",
                                          dst_vnet_id=host_2_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=host_2_vnet,
                                      dip=self.host_2.client.ip,
                                      underlay_dip=self.host_2.ip,
                                      overlay_dmac=self.host_2.client.mac)

        # ENI 3 inbound/outbound routing
        addr_mask = self.host_1.ip_prefix.split('/')
        self.inbound_routing_decap_validate_create(eni_id=eni_id_3, vni=self.host_1.client.vni,
                                                   sip=addr_mask[0], sip_mask=num_to_dotted_quad(addr_mask[1]),
                                                   src_vnet_id=host_1_vnet)
        self.pa_validation_create(sip=self.host_1.ip,
                                  vnet_id=host_1_vnet)

        self.outbound_routing_vnet_create(outbound_routing_group_id_3, lpm="cccc::0/64",
                                          dst_vnet_id=host_1_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=host_1_vnet,
                                      dip=self.host_1.client.ip,
                                      underlay_dip=self.host_1.ip,
                                      overlay_dmac=self.host_1.client.mac)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundOutboundMultipleConfigsTwoPortsTest(Vnet2VnetInboundOutboundMultipleConfigsSinglePortTest):
    """
    Inbound and Outbound Vnet to Vnet test scenario
    Verifies overlay routing with multiple inbound/outbound configurations
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.host_0, self.host_2,
        #                        add_routes=True)

        self.outboundHost0toHost2Test(tx_equal_to_rx=False)
        self.inboundHost2toHost0Test(tx_equal_to_rx=False)

        self.outboundHost3toHost1Test(tx_equal_to_rx=False)
        self.inboundHost1toHost3Test(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundOutboundMultipleConfigsTwoPortsOverlayIpv6Test(Vnet2VnetInboundOutboundMultipleConfigsSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Inbound and Outbound Vnet to Vnet test scenario
    Verifies overlay routing with multiple inbound/outbound configurations
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.host_0, self.host_2,
        #                        add_routes=True)

        self.outboundHost0toHost2Test(tx_equal_to_rx=False)
        self.inboundHost2toHost0Test(tx_equal_to_rx=False)

        self.outboundHost3toHost1Test(tx_equal_to_rx=False)
        self.inboundHost1toHost3Test(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario when multiple ENI and
    Outbound routing entries exist with the same CA IP prefixes
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, add_routes=False)

        self.outboundEni0Test(tx_equal_to_rx=True)
        self.outboundEni1Test(tx_equal_to_rx=True)
        self.outboundEni2Test(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        192.168.0.1         -> 192.168.1.1
        tx_host_0 (vni 1)   -> rx_host_0 (vni 2)
        tx_host_1 (vni 10)  -> rx_host_1 (vni 20)
        tx_host_2 (vni 100) -> rx_host_2 (vni 200)
        """

        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip=self.tx_host_0.client.ip,
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:04:00:00:06:17",
                                                      client_ip=self.tx_host_0.client.ip,
                                                      client_vni=100)

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip=self.rx_host.client.ip,
                                                      client_vni=20)

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:06:00:00:07:18",
                                                      client_ip=self.rx_host.client.ip,
                                                      client_vni=200)

        # Overlay routing
        self.vip_create(self.tx_host_0.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host_0.client.vni)
        self.direction_lookup_create(self.tx_host_1.client.vni)
        self.direction_lookup_create(self.tx_host_2.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)
        src_vnet_2 = self.vnet_create(vni=self.tx_host_2.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)
        dst_vnet_2 = self.vnet_create(vni=self.rx_host_2.client.vni)

        outbound_routing_group_id_0 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_1 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_2 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_3 = self.outbound_routing_group_create(disabled=False)

        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_0.ip),
                                   vm_vni=self.tx_host_0.client.vni,
                                   vnet_id=src_vnet_0,
                                   outbound_routing_group_id=outbound_routing_group_id_0)
        self.eni_mac_map_create(eni_id=eni_id_0, mac=self.tx_host_0.client.mac)

        eni_id_1 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_1.ip),
                                   vm_vni=self.tx_host_1.client.vni,
                                   vnet_id=src_vnet_1,
                                   outbound_routing_group_id=outbound_routing_group_id_1)
        self.eni_mac_map_create(eni_id=eni_id_1, mac=self.tx_host_1.client.mac)

        eni_id_2 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_2.ip),
                                   vm_vni=self.tx_host_2.client.vni,
                                   vnet_id=src_vnet_2,
                                   outbound_routing_group_id=outbound_routing_group_id_2)
        self.eni_mac_map_create(eni_id=eni_id_2, mac=self.tx_host_2.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id_0, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id_1, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)

        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id_2, lpm="192.168.1.0/24",
                                                 dst_vnet_id=dst_vnet_2,
                                                 overlay_ip="192.168.1.111")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_2,
                                      dip="192.168.1.111",
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)

    def outboundEni0Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.tx_host_0,
                                     server=self.rx_host_0,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.outboundEni0Test.__name__, ' OK')

    def outboundEni1Test(self, tx_equal_to_rx):

        # For use_dst_vnet_vni=False verification change rx client vni to tx client vni
        self.rx_host_1.client.vni = self.tx_host_1.client.vni

        self.verify_traffic_scenario(client=self.tx_host_1,
                                     server=self.rx_host_1,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.outboundEni1Test.__name__, ' OK')

    def outboundEni2Test(self, tx_equal_to_rx):

        self.verify_traffic_scenario(client=self.tx_host_2,
                                     server=self.rx_host_2,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.outboundEni2Test.__name__, ' OK')


@group("draft")
class Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortOverlayIpv6Test(Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario when multiple ENI and
    Outbound routing entries exist with the same CA IP prefixes
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def setUp(self):
        super(Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        CA: aaaa::10        -> bbbb::20
        tx_host_0 (vni 1)   -> rx_host_0 (vni 2)
        tx_host_1 (vni 10)  -> rx_host_1 (vni 20)
        tx_host_2 (vni 100) -> rx_host_2 (vni 200)
        """

        self.tx_host_0 = self.tx_host

        self.tx_host_1 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:03:00:00:05:16",
                                                      client_ip=self.tx_host_0.client.ip,
                                                      client_vni=10)

        self.tx_host_2 = self.define_neighbor_network(port=self.tx_host_0.port,
                                                      mac=self.tx_host_0.mac,
                                                      ip=self.tx_host_0.ip,
                                                      ip_prefix=self.tx_host_0.ip_prefix,
                                                      peer_port=self.tx_host_0.peer.port,
                                                      peer_mac=self.tx_host_0.peer.mac,
                                                      peer_ip=self.tx_host_0.peer.ip,
                                                      client_mac="00:04:00:00:06:17",
                                                      client_ip=self.tx_host_0.client.ip,
                                                      client_vni=100)

        self.rx_host_0 = self.rx_host

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip=self.rx_host.client.ip,
                                                      client_vni=20)

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:06:00:00:07:18",
                                                      client_ip=self.rx_host.client.ip,
                                                      client_vni=200)

        # Overlay routing
        self.vip_create(self.tx_host_0.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host_0.client.vni)
        self.direction_lookup_create(self.tx_host_1.client.vni)
        self.direction_lookup_create(self.tx_host_2.client.vni)

        src_vnet_0 = self.vnet_create(vni=self.tx_host_0.client.vni)
        src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)
        src_vnet_2 = self.vnet_create(vni=self.tx_host_2.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)
        dst_vnet_2 = self.vnet_create(vni=self.rx_host_2.client.vni)

        outbound_routing_group_id_0 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_1 = self.outbound_routing_group_create(disabled=False)
        outbound_routing_group_id_2 = self.outbound_routing_group_create(disabled=False)

        eni_id_0 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_0.ip),
                                   vm_vni=self.tx_host_0.client.vni,
                                   vnet_id=src_vnet_0,
                                   outbound_routing_group_id=outbound_routing_group_id_0)
        self.eni_mac_map_create(eni_id=eni_id_0, mac=self.tx_host_0.client.mac)

        eni_id_1 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_1.ip),
                                   vm_vni=self.tx_host_1.client.vni,
                                   vnet_id=src_vnet_1,
                                   outbound_routing_group_id=outbound_routing_group_id_1)
        self.eni_mac_map_create(eni_id=eni_id_1, mac=self.tx_host_1.client.mac)

        eni_id_2 = self.eni_create(admin_state=True,
                                   vm_underlay_dip=sai_ipaddress(self.tx_host_2.ip),
                                   vm_vni=self.tx_host_2.client.vni,
                                   vnet_id=src_vnet_2,
                                   outbound_routing_group_id=outbound_routing_group_id_2)
        self.eni_mac_map_create(eni_id=eni_id_2, mac=self.tx_host_2.client.mac)

        # Outbound routing and CA to PA entries creation
        # for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id_0, lpm="bbbb::0/64",
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id_1, lpm="bbbb::0/64",
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=False)

        self.outbound_routing_vnet_direct_create(outbound_routing_group_id=outbound_routing_group_id_2, lpm="bbbb::0/64",
                                                 dst_vnet_id=dst_vnet_2,
                                                 overlay_ip="bbbb::bc")
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_2,
                                      dip="bbbb::bc",
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultipleEniSameIpPrefixTwoPortsTest(Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario when multiple ENI and
    Outbound routing entries exist with the same CA IP prefixes
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, self.rx_host_0)

        self.outboundEni0Test(tx_equal_to_rx=False)
        self.outboundEni1Test(tx_equal_to_rx=False)
        self.outboundEni2Test(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultipleEniSameIpPrefixTwoPortsOverlayIpv6Test(Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario when multiple ENI and
    Outbound routing entries exist with the same CA IP prefixes
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host_0, self.rx_host_0)

        self.outboundEni0Test(tx_equal_to_rx=False)
        self.outboundEni1Test(tx_equal_to_rx=False)
        self.outboundEni2Test(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with single ENI and
    multiple Outbound routing entries with the overlapping CA IP prefixes
    with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.singleEniToOutboundVm1Test(tx_equal_to_rx=True)
        self.singleEniToOutboundVm2Test(tx_equal_to_rx=True)
        self.singleEniToOutboundVm3Test(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        CA:
        tx_host (vni 1) 9.0.0.1 -> 10.5.4.4/8  rx_host_0 (vni 2)
        tx_host (vni 1) 9.0.0.1 -> 10.0.1.2/24 rx_host_1 (vni 20)
        tx_host (vni 1) 9.0.0.1 -> 10.1.1.1/32 rx_host_2 (vni 200)
        """

        # Update VIP
        self.tx_host.peer.ip = "12.1.1.1"
        self.rx_host.peer.ip = "12.1.1.1"

        # Update some network parameters for ip prefixes overlapping
        self.tx_host.ip = "192.168.0.1"
        self.tx_host.ip_prefix = "192.168.0.0/24"
        self.tx_host.client.ip = "9.0.0.1"

        self.rx_host_0 = self.rx_host
        self.rx_host_0.ip = "192.168.1.1"
        self.rx_host_0.ip_prefix = "192.168.1.0/24"
        self.rx_host_0.client.ip = "10.5.4.4"
        rx_host_0_client_ip_prefix = "10.0.0.0/8"

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip="10.0.1.2",
                                                      client_vni=20)
        rx_host_1_client_ip_prefix = "10.0.1.0/24"

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:06:00:00:07:18",
                                                      client_ip="10.1.1.1",
                                                      client_vni=200)
        rx_host_2_client_ip_prefix = "10.1.1.1/32"

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)
        dst_vnet_2 = self.vnet_create(vni=self.rx_host_2.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_0_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_1_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_2_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_2)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_2,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)

    def singleEniToOutboundVm1Test(self, tx_equal_to_rx):
        """
        Packet sending:
            CA IP: 9.0.0.1 -> 10.5.4.4/8
            VNET: 1 -> 2
        """

        self.verify_traffic_scenario(client=self.tx_host,
                                     server=self.rx_host_0,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.singleEniToOutboundVm1Test.__name__, ' OK')

    def singleEniToOutboundVm2Test(self, tx_equal_to_rx):
        """
        Packet sending:
            CA IP: 9.0.0.1 -> 10.0.1.2/24
            VNET: 1 -> 20
        """

        self.verify_traffic_scenario(client=self.tx_host,
                                     server=self.rx_host_1,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.singleEniToOutboundVm2Test.__name__, ' OK')

    def singleEniToOutboundVm3Test(self, tx_equal_to_rx):
        """
        Packet sending:
            CA IP: 9.0.0.1 -> 10.1.1.1/32
            VNET: 1 -> 200
        """

        self.verify_traffic_scenario(client=self.tx_host,
                                     server=self.rx_host_2,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)

        print('\n', self.singleEniToOutboundVm3Test.__name__, ' OK')


@group("draft")
class Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortOverlayIpv6Test(Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortTest):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with single ENI and
    multiple Outbound routing entries with the overlapping CA IP prefixes
    with underlay config (neighbour + next hop) but without underlay routes
    """
    def setUp(self):
        super(Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortOverlayIpv6Test, self).setUp(overlay_ipv6=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose

        CA:
        tx_host (vni 1) aaaa::10 -> 2001:db8:cad::1/48     rx_host_0 (vni 2)
        tx_host (vni 1) aaaa::10 -> 2001:db8:cad:800::1/53 rx_host_1 (vni 20)
        tx_host (vni 1) aaaa::10 -> 2001:db8:cad:810::1/62 rx_host_2 (vni 200)
        """

        # Update some network parameters for ip prefixes overlapping
        self.tx_host.ip = "192.168.0.1"
        self.tx_host.ip_prefix = "192.168.0.0/24"

        self.rx_host_0 = self.rx_host
        self.rx_host_0.ip = "192.168.1.1"
        self.rx_host_0.ip_prefix = "192.168.1.0/24"
        self.rx_host_0.client.ip = "2001:db8:cad::1"
        rx_host_0_client_ip_prefix = "2001:db8:cad::0/48"

        self.rx_host_1 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:05:00:00:06:17",
                                                      client_ip="2001:db8:cad:800::1",
                                                      client_vni=20)
        rx_host_1_client_ip_prefix = "2001:db8:cad:800::0/53"

        self.rx_host_2 = self.define_neighbor_network(port=self.rx_host_0.port,
                                                      mac=self.rx_host_0.mac,
                                                      ip=self.rx_host_0.ip,
                                                      ip_prefix=self.rx_host_0.ip_prefix,
                                                      peer_port=self.rx_host_0.peer.port,
                                                      peer_mac=self.rx_host_0.peer.mac,
                                                      peer_ip=self.rx_host_0.peer.ip,
                                                      client_mac="00:06:00:00:07:18",
                                                      client_ip="2001:db8:cad:810::1",
                                                      client_vni=200)
        rx_host_2_client_ip_prefix = "2001:db8:cad:810::0/62"

        # Overlay routing
        self.vip_create(self.tx_host.peer.ip)  # Appliance VIP

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        dst_vnet_0 = self.vnet_create(vni=self.rx_host_0.client.vni)
        dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)
        dst_vnet_2 = self.vnet_create(vni=self.rx_host_2.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id=eni_id, mac=self.tx_host.client.mac)

        # Outbound routing and CA to PA entries creation
        #  for use_dst_vnet_vni=True
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_0_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_0)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_0,
                                      dip=self.rx_host_0.client.ip,
                                      underlay_dip=self.rx_host_0.ip,
                                      overlay_dmac=self.rx_host_0.client.mac,
                                      use_dst_vnet_vni=True)

        # for use_dst_vnet_vni=False
        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_1_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_1)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm=rx_host_2_client_ip_prefix,
                                          dst_vnet_id=dst_vnet_2)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet_2,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundSingleEniMultipleIpPrefixTwoPortsTest(Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with single ENI and
    multiple Outbound routing entries with the overlapping CA IP prefixes
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.singleEniToOutboundVm1Test(tx_equal_to_rx=False)
        self.singleEniToOutboundVm2Test(tx_equal_to_rx=False)
        self.singleEniToOutboundVm3Test(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundSingleEniMultipleIpPrefixTwoPortsOverlayIpv6Test(Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortOverlayIpv6Test):
    """
    Underlay IPv4 and Overlay IPv6 configs
    Outbound Vnet to Vnet test scenario with single ENI and
    multiple Outbound routing entries with the overlapping CA IP prefixes
    with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host_0)

        self.singleEniToOutboundVm1Test(tx_equal_to_rx=False)
        self.singleEniToOutboundVm2Test(tx_equal_to_rx=False)
        self.singleEniToOutboundVm3Test(tx_equal_to_rx=False)


@group("draft")
class Vnet2VnetOutboundSameCaPaIpPrefixesSinglePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Outbound Vnet to Vnet test scenario with the same
    CA and PA IP prefixes with underlay config (neighbour + next hop) but without underlay routes
    """

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configureTest()
        # self.configure_underlay(self.tx_host, add_routes=False)

        self.vnet2VnetOutboundRouteVnetTest(tx_equal_to_rx=True)

    def configureTest(self):
        """
        Setup DUT in accordance with test purpose
        """

        # Update network parameters with the same provider and client ip addresses
        self.tx_host.ip = self.tx_host.client.ip  # 192.168.0.1
        self.tx_host.ip_prefix = "192.168.0.0/24"

        self.rx_host.ip = self.rx_host.client.ip  # 192.168.1.1
        self.rx_host.ip_prefix = "192.168.1.0/24"

        # Configure overlay routing
        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        outbound_routing_group_id = self.outbound_routing_group_create(disabled=False)

        eni_id = self.eni_create(admin_state=True,
                                 vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
                                 vm_vni=self.tx_host.client.vni,
                                 vnet_id=src_vnet,
                                 outbound_routing_group_id=outbound_routing_group_id)
        self.eni_mac_map_create(eni_id, self.tx_host.client.mac)  # ENI MAC

        self.outbound_routing_vnet_create(outbound_routing_group_id=outbound_routing_group_id, lpm="192.168.1.0/24",
                                          dst_vnet_id=dst_vnet)
        self.outbound_ca_to_pa_create(dst_vnet_id=dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetOutboundRouteVnetTest(self, tx_equal_to_rx):
        """
        Packet sending:
            CA IP: 192.168.0.1/24  -> 192.168.1.1/24
            PA IP: 192.168.0.1/24  -> VIP -> 192.168.1.1/24
            VNET: 1 -> 2
        """

        self.verify_traffic_scenario(client=self.tx_host,
                                     server=self.rx_host,
                                     connection=self.connection,
                                     fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundSameCaPaIpPrefixesTwoPortsTest(Vnet2VnetOutboundSameCaPaIpPrefixesSinglePortTest):
    """
    Outbound Vnet to Vnet test scenario with the same
    CA and PA IP prefixes with full underlay config (2 neighbours, 2 next-hops, 2 routes)
    """

    def runTest(self):
        self.configureTest()
        # self.configure_underlay(self.tx_host, self.rx_host)

        self.vnet2VnetOutboundRouteVnetTest(tx_equal_to_rx=False)
