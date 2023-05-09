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
Thrift SAI interface basic DASH utils.
"""

from sai_thrift.sai_headers import *
from sai_base_test import *

from random import randint
from copy import deepcopy
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class DutNetworkParameters:
    """
    Data class for storing basic network parameters of DUT
    """

    port: str
    mac: str
    ip: str


@dataclass
class ClientNetworkParameters:
    """
    Data class for storing basic VNET client network parameters
    """

    mac: str
    ip: str
    vni: int


@dataclass
class DutNeighborNetworkParameters:
    """
    Data class for storing basic network parameters of DUT Neighbors

    port: Neighbor port (Traffic generator port)
    mac: Neighbor port MAC address
    ip: Neighbor port IP address
    ip_prefix: Neighbor port IP prefix (e.g. 10.1.1.0/24)
    peer: DutNetworkParameters object
    client: ClientNetworkParameters object
    """

    port: object
    mac: str
    ip: str
    ip_prefix: str
    peer: DutNetworkParameters
    client: ClientNetworkParameters = None


class VnetObjects(SaiHelperSimplified):
    def setUp(self):
        super(VnetObjects, self).setUp()
        self.teardown_objects = list()

    def tearDown(self):
        super(VnetObjects, self).tearDown()

    def add_teardown_obj(self, func, *args):
        self.teardown_objects.insert(0, (func, *args))

    def destroy_teardown_obj(self):
        for obj_func, obj_args in self.teardown_objects:
            if isinstance(obj_args, (list, tuple)):
                obj_func(*obj_args)
            else:
                obj_func(obj_args)
            self.assertEqual(self.status(), SAI_STATUS_SUCCESS)


class VnetAPI(VnetObjects):
    def setUp(self):
        super(VnetAPI, self).setUp()

    def tearDown(self):
        self.destroy_teardown_obj()
        super(VnetAPI, self).tearDown()

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

    def dash_acl_group_create(self, ipv6=False):
        """
        Create Dash Acl group
        """

        ip_addr_family = SAI_IP_ADDR_FAMILY_IPV4
        if ipv6:
            ip_addr_family = SAI_IP_ADDR_FAMILY_IPV6

        dash_acl_group = sai_thrift_create_dash_acl_group(self.client,
                                                          ip_addr_family=ip_addr_family)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.assertNotEqual(dash_acl_group, SAI_NULL_OBJECT_ID)

        self.add_teardown_obj(self.dash_acl_group_remove, dash_acl_group)

        return dash_acl_group

    def dash_acl_group_remove(self, dash_acl_group_id):
        sai_thrift_remove_dash_acl_group(self.client, dash_acl_group_id)

    def eni_create(self, **kwargs):
        """
        Create ENI
        """

        default_kwargs = {
            "cps": 10000,
            "pps": 100000,
            "flows": 100000,
            "admin_state": True,
            "vm_underlay_dip": sai_ipaddress("0.0.0.0"),
            "vm_vni": 1,
            "vnet_id": 1,
            "v4_meter_policy_id": 0,
            "v6_meter_policy_id": 0,
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
    
    def eni_set_admin_state(self, eni_oid, state):
        sai_thrift_set_eni_attribute(self.client, eni_oid, admin_state=(state == "up"))
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)

        print(f"ENI oid: {eni_oid} setting admin state {state} - OK")

    def eni_remove(self, eni_id):
        sai_thrift_remove_eni(self.client, eni_id)

    def direction_lookup_create(self, vni):
        """
        Create direction lookup entry
        """

        act = SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION

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

    def outbound_routing_vnet_direct_create(self, eni_id, lpm, dst_vnet_id,
                                            overlay_ip, counter_id=None):
        """
        Create outband vnet direct routing entry
        """

        outbound_routing_entry = sai_thrift_outbound_routing_entry_t(
            switch_id=self.switch_id, eni_id=eni_id,
            destination=sai_ipprefix(lpm))
        sai_thrift_create_outbound_routing_entry(self.client,
                                                 outbound_routing_entry, dst_vnet_id=dst_vnet_id,
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT,
                                                 overlay_ip=sai_ipaddress(overlay_ip), counter_id=counter_id,
                                                 meter_policy_en=False, meter_class=0)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_routing_vnet_direct_remove, outbound_routing_entry)

    def outbound_routing_direct_create(self, eni_id, lpm, counter_id=None):
        """
        Create outband vnet direct routing entry
        """

        outbound_routing_entry = sai_thrift_outbound_routing_entry_t(
            switch_id=self.switch_id, eni_id=eni_id,
            destination=sai_ipprefix(lpm))
        sai_thrift_create_outbound_routing_entry(self.client, outbound_routing_entry, counter_id=counter_id,
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT,
                                                 meter_policy_en=False, meter_class=0)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_routing_vnet_direct_remove, outbound_routing_entry)

    def outbound_routing_vnet_create(self, eni_id, lpm, dst_vnet_id, counter_id=None):
        """
        Create outbound vnet routing entry
        """

        outbound_routing_entry = sai_thrift_outbound_routing_entry_t(
            switch_id=self.switch_id, eni_id=eni_id,
            destination=sai_ipprefix(lpm))
        sai_thrift_create_outbound_routing_entry(self.client,
                                                 outbound_routing_entry, dst_vnet_id=dst_vnet_id,
                                                 counter_id=counter_id,
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET,
                                                 meter_policy_en=False, meter_class=0)
        self.assertEqual(self.status(), SAI_STATUS_SUCCESS)
        self.add_teardown_obj(self.outbound_routing_vnet_direct_remove, outbound_routing_entry)

    def outbound_routing_vnet_direct_remove(self, entry):
        sai_thrift_remove_outbound_routing_entry(self.client, entry)

    def outbound_ca_to_pa_create(self, dst_vnet_id, dip, underlay_dip,
                                 use_dst_vnet_vni=True, overlay_dmac=None):
        """
        Create outband CA PA mapping
        """

        ca_to_pa_entry = sai_thrift_outbound_ca_to_pa_entry_t(switch_id=self.switch_id,
                                                              dst_vnet_id=dst_vnet_id,
                                                              dip=sai_ipaddress(dip))
        sai_thrift_create_outbound_ca_to_pa_entry(self.client, ca_to_pa_entry,
                                                  underlay_dip=sai_ipaddress(underlay_dip),
                                                  use_dst_vnet_vni=use_dst_vnet_vni,
                                                  overlay_dmac=overlay_dmac,
                                                  meter_class=0, meter_class_override=False)
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

    def configure_underlay(self, *neighbors, add_routes=True):
        """
        Configure L3 underlay network based on neighbors network configuration
        """

        for neighbor in neighbors:
            rif = self.router_interface_create(neighbor.peer.port,
                                               src_mac=neighbor.peer.mac)
            nhop = self.nexthop_create(rif, neighbor.ip)
            self.neighbor_create(rif, neighbor.ip, neighbor.mac)
            if add_routes is True:
                self.route_create(neighbor.ip_prefix, nhop)


class VnetApiEndpoints(VnetAPI):
    """
    Base class to define test network configuration
    Configuration types:
        - underlay and overlay IPv4
        - underlay and overlay IPv6
        - underlay IPv4 and overlay IPv6
        - underlay IPv6 and overlay IPv4
        Configuration:
           +--------------------------------------------------+
           |                        DUT                       |
           +--------------------------------------------------+
           |          VIP - 10.1.1.1 / 1000:cafe::10          |
           |       port0                         port1        |
           | 00:66:55:44:33:00             00:77:66:55:44:00  |
           +--------------------------------------------------+
                    /                                \
                   /                                  \
                  /                                    \
    +------------------------------+        +------------------------------+
    |         host1                |        |         host2                |
    | port: dev_port0              |        | port: dev_port1              |
    | mac: 10:22:33:aa:bb:cc       |        | mac: aa:bb:cc:11:22:33       |
    | ip: 10.10.1.10/2000:cafe::20 |        | ip: 10.10.2.10/3000:cafe::30 |
    | ip_prefix: 10.10.1.0/24 /    |        | ip_prefix: 10.10.2.0/24 /    |
    |            2000:cafe::0/112  |        |            3000:cafe::0/112  |
    +------------------------------+        +------------------------------+
    |      Peer (DUT)              |        |       Peer (DUT)             |
    | port: port0                  |        | port: port1                  |
    | mac: 00:66:55:44:33:00       |        | mac: 00:77:66:55:44:00       |
    | ip: 10.1.1.1/1000:cafe::10   |        | ip: 10.1.1.1/1000:cafe::10   |
    +------------------------------+        +------------------------------+
    |         Client               |        |         Client               |
    | mac: 00:01:00:00:03:14       |        | mac: 00:02:00:00:04:15       |
    | ip: 192.168.0.1/aaaa::10     |        | ip: 192.168.1.1/bbbb::20     |
    | VNI: 1                       |        | VNI: 2                       |
    +------------------------------+        +------------------------------+
    """

    def setUp(self, underlay_ipv6=False, overlay_ipv6=False):
        super(VnetApiEndpoints, self).setUp()

        # Set connection type for traffic verification methods
        self.assertTrue(test_param_get("connection").lower() in ["tcp", "udp", "icmp"],
                        "Unknown connection protocol! Supported protocols: tcp|udp|icmp")
        self.connection = test_param_get("connection").lower()
        print(f"{self.connection.upper()} protocol is used for traffic verification.")
        
        self.underlay_ipv6 = underlay_ipv6
        self.overlay_ipv6 = overlay_ipv6

        if self.underlay_ipv6 is True:
            vip = "1000:cafe::10"
            tx_host_ip = "2000:cafe::20"
            tx_host_ip_prefix = "2000:cafe::0/112"
            rx_host_ip = "3000:cafe::30"
            rx_host_ip_prefix = "3000:cafe::0/112"
        else:
            vip = "10.1.1.1"
            tx_host_ip = "10.10.1.10"
            tx_host_ip_prefix = "10.10.1.0/24"
            rx_host_ip = "10.10.2.10"
            rx_host_ip_prefix = "10.10.2.0/24"

        if self.overlay_ipv6 is True:
            tx_host_client_ip = "aaaa::10"
            rx_host_client_ip = "bbbb::20"
        else:
            tx_host_client_ip = "192.168.0.1"
            rx_host_client_ip = "192.168.1.1"

        self.tx_host = self.define_neighbor_network(port=self.dev_port0,
                                                    mac="10:22:33:aa:bb:cc",
                                                    ip=tx_host_ip,
                                                    ip_prefix=tx_host_ip_prefix,
                                                    peer_port=self.port0,
                                                    peer_mac="00:66:55:44:33:00",
                                                    peer_ip=vip,
                                                    client_mac="00:01:00:00:03:14",
                                                    client_ip=tx_host_client_ip,
                                                    client_vni=1)

        self.rx_host = self.define_neighbor_network(port=self.dev_port1,
                                                    mac="aa:bb:cc:11:22:33",
                                                    ip=rx_host_ip,
                                                    ip_prefix=rx_host_ip_prefix,
                                                    peer_port=self.port1,
                                                    peer_mac="00:77:66:55:44:00",
                                                    peer_ip=vip,
                                                    client_mac="00:02:00:00:04:15",
                                                    client_ip=rx_host_client_ip,
                                                    client_vni=2)

    def update_configuration_for_tx_equal_to_rx(self):
        """
        Update rx_host network info for use cases
        when the packet is expected to be received on the port from which it was sent
        (tx_equal_to_rx=True)
        """

        self.rx_host.port = self.tx_host.port
        self.rx_host.mac = self.tx_host.mac

        self.rx_host.peer.port = self.tx_host.peer.port
        self.rx_host.peer.mac = self.tx_host.peer.mac
        self.rx_host.peer.ip = self.tx_host.peer.ip

    @staticmethod
    def define_neighbor_network(port, mac, ip, ip_prefix,
                                peer_port, peer_mac, peer_ip,
                                client_mac=None, client_ip=None, client_vni=None):
        """
        Host (DUT neighbor) fields hierarchy
        ├── port
        ├── mac
        ├── ip
        ├── ip_prefix
        ├── peer [DUT]
        │   ├ port
        │   ├ mac
        │   └ ip
        └── client
            ├── mac
            ├── ip
            └── vni
        """

        dut = DutNetworkParameters(port=peer_port,
                                   mac=peer_mac,
                                   ip=peer_ip)

        client = None
        # checks only mac is not None and assume that ip and vni are not None
        if client_mac is not None:
            client = ClientNetworkParameters(mac=client_mac,
                                             ip=client_ip,
                                             vni=client_vni)

        host = DutNeighborNetworkParameters(port=port,
                                            mac=mac,
                                            ip=ip,
                                            ip_prefix=ip_prefix,
                                            peer=dut,
                                            client=client)

        return host


class VnetTrafficMixin:
    """
    Mixin class with methods dedicated for Vnet use cases traffic verification
    """

    # TCP flags
    SYN = "S"
    SYN_ACK = "SA"
    ACK = "A"
    FIN_ACK = "FA"

    ip_src_inner_pkt = 'ip_src'
    ip_dst_inner_pkt = 'ip_dst'
    ip_src_outer_pkt = 'ip_src'
    ip_dst_outer_pkt = 'ip_dst'

    def define_pkts_creation_func(self, connection):
        conn_type = connection.lower()

        if conn_type == 'tcp':
            inner_pkt = simple_tcp_packet
            inner_pkt_v6 = simple_tcpv6_packet
        elif conn_type == 'udp':
            inner_pkt = simple_udp_packet
            inner_pkt_v6 = simple_udpv6_packet
        elif conn_type == 'icmp':
            inner_pkt = simple_icmp_packet
            inner_pkt_v6 = simple_icmpv6_packet
        else:
            types = ['tcp', 'udp', 'icmp']
            raise AttributeError(f"Wrong connection type: {connection}.\n"
                                 f"Supported connection types: {types}")

        if self.overlay_ipv6 is True:
            create_inner_pkt = inner_pkt_v6
            self.ip_src_inner_pkt = 'ipv6_src'
            self.ip_dst_inner_pkt = 'ipv6_dst'
        else:
            create_inner_pkt = inner_pkt

        if self.underlay_ipv6 is True:
            create_outer_packet = simple_vxlanv6_packet
            self.ip_src_outer_pkt = 'ipv6_src'
            self.ip_dst_outer_pkt = 'ipv6_dst'
        else:
            create_outer_packet = simple_vxlan_packet

        return create_inner_pkt, create_outer_packet

    def verify_traffic_scenario(self,
                                client: DutNeighborNetworkParameters,
                                server: DutNeighborNetworkParameters,
                                connection: str,
                                fake_mac=True,
                                tx_equal_to_rx=True,
                                terminate_tcp_session=True,
                                route_direct=False,
                                pkt_drop=False):
        """
        Traffic check based on --test-params traffic_check parameter
        no - no traffic check
        monodir - mono-directional traffic verification
        bidir (default) - bidirectional traffic verification
        """

        if test_param_get('traffic_check') == 'no':
            pass
        elif test_param_get('traffic_check') == 'monodir':
            self.verify_oneway_connection(client=client,
                                          server=server,
                                          connection=connection,
                                          fake_mac=fake_mac,
                                          route_direct=route_direct,
                                          pkt_drop=pkt_drop)
        else:
            self.verify_bidirectional_connection(client=client,
                                                 server=server,
                                                 connection=connection,
                                                 fake_mac=fake_mac,
                                                 tx_equal_to_rx=tx_equal_to_rx,
                                                 terminate_tcp_session=terminate_tcp_session,
                                                 route_direct=route_direct)

    def verify_bidirectional_connection(self,
                                        client: DutNeighborNetworkParameters,
                                        server: DutNeighborNetworkParameters,
                                        connection: str,
                                        fake_mac=True,
                                        tx_equal_to_rx=True,
                                        terminate_tcp_session=True,
                                        route_direct=False):
        """
        Verify Inbound/Outbound overlay configuration with traffic.
        Traffic types: tcp, udp or icmp
        Notes:
            - The words "Client" and "Server" are used only for
              better understanding of the sequence of sending packets
            - Only one traffic type can be selected
        Parameters:
            client: DutNeighborNetworkParameters object with src network config
            server: DutNeighborNetworkParameters object with dst network config
            connection (str): connection type str (e.g. 'tcp', 'UDP', 'icmp')
            fake_mac (bool): If True requests for Inner client packets Ether Dst MAC (CA MAC) set to fake mac,
                             (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
            tx_equal_to_rx (bool): If True sends and verifies pkts on the same TG port
            terminate_tcp_session (bool): If True send and verify packets for tcp session termination
                                          else only send and verify pkts for tcp session start
            route_direct (bool): For scenarios when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT
                                 and decapsulated packets expected on the server side
        TCP scenario:
            Start session
            1) Client -> Server: SYN pkt
            2) Client <- Server: SYN_ACK pkt
            3) Client -> Server: ACK pkt
            Terminate session
            4) Client -> Server: FIN_ACK pkt
            5) Client <- Server: ACK ptk
            6) Client <- Server: FIN_ACK ptk
            7) Client -> Server: ACK pkt
        UDP scenario:
            Start session
            1) Client -> Server
            2) Client <- Server
        ICMP scenario:
            1) Client -> Server: echo request
            2) Client <- Server: echo reply
        """

        conn_type = connection.lower()

        if conn_type == 'tcp' and route_direct:
            send_packets, exp_client_packets, exp_server_packets = \
                self.create_vxlan_tcp_session_route_direct_packets(
                    client, server,
                    fake_mac=fake_mac,
                    terminate_tcp_session=terminate_tcp_session)

        elif conn_type == 'tcp':
            send_packets, exp_client_packets, exp_server_packets = \
                self.create_vxlan_tcp_session_packets(client, server,
                                                      fake_mac=fake_mac,
                                                      terminate_tcp_session=terminate_tcp_session)
        elif conn_type == 'udp':
            send_packets, exp_client_packets, exp_server_packets = \
                self.create_vxlan_udp_session_packets(client, server,
                                                      fake_mac=fake_mac)

        elif conn_type == 'icmp':
            send_packets, exp_client_packets, exp_server_packets = \
                self.create_vxlan_icmp_session_packets(client, server,
                                                       fake_mac=fake_mac)

        else:
            types = ['tcp', 'udp', 'icmp']
            raise AttributeError(f"Wrong connection type: {connection}.\n"
                                 f"Supported connection types: {types}")

        # packets sending
        for name, pkt in send_packets.items():
            src_port = client.port if "client" in name else server.port
            direction = "-->" if "client" in name else "<--"

            print(f"\nSending {name},", client.port, direction, server.port)
            send_packet(self, src_port, pkt)

        # packets verification
        if tx_equal_to_rx:
            exp_packets = {**exp_client_packets, **exp_server_packets}

            print(f"\nVerify that all packets are received on {server.port}:\n")
            for name, pkt in exp_packets.items():
                print(f"Verifying {name}")
                verify_packet(self, pkt, server.port)
                print(f"{name} - OK")
        else:
            print(f"\nVerify 'clients' packets are received on {server.port}:\n")
            for name, pkt in exp_client_packets.items():
                print(f"Verifying {name}")
                verify_packet(self, pkt, server.port)
                print(f"{name} - OK")

            print(f"\nVerify 'server' packets are received on {client.port}:\n")
            for name, pkt in exp_server_packets.items():
                print(f"Verifying {name}")
                verify_packet(self, pkt, client.port)
                print(f"{name} - OK")

    def verify_oneway_connection(self,
                                 client: DutNeighborNetworkParameters,
                                 server: DutNeighborNetworkParameters,
                                 connection: str,
                                 fake_mac=False,
                                 route_direct=False,
                                 pkt_drop=False):
        """
        Sends and verifies VxLAN encapsulated TCP, UDP or ICMP packet
        client: DutNeighborNetworkParameters object with src network config
        server: DutNeighborNetworkParameters object with dst network config
        connection (str): connection type str (e.g. 'tcp', 'UDP', 'icmp')
        fake_mac (bool): If True requests for Inner client packets Ether Dst MAC (CA MAC) set to fake mac,
                         (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
        route_direct (bool): For scenarios when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT
                             and decapsulated packets expected on the server side
        """

        send_pkt, exp_pkt = self.create_vxlan_oneway_pkts(client=client,
                                                          server=server,
                                                          connection=connection,
                                                          fake_mac=fake_mac,
                                                          route_direct=route_direct)

        print(f"\nSending VxLAN {connection.lower()} packet:", client.port, "-->", server.port)
        send_packet(self, client.port, send_pkt)

        if pkt_drop:
            verify_no_other_packets(self, timeout=1)

        else:
            print(f"Verifying VxLAN {connection.lower()} packet on {server.port}")
            verify_packet(self, exp_pkt, server.port)
            print(f"VxLAN {connection.lower()} packet - OK")

    def verify_negative_traffic_scenario(self,
                                         client: DutNeighborNetworkParameters,
                                         server: DutNeighborNetworkParameters,
                                         fake_mac=True,
                                         udp: bool = False,
                                         invalid_vni=None,
                                         invalid_vip=None,
                                         invalid_inner_src_mac=None,
                                         invalid_inner_dst_mac=None,
                                         invalid_inner_dst_ip=None,
                                         invalid_outer_src_ip=None,
                                         valid_pkt_drop=False):
        """
        Verifies packets drop
        By default uses TCP packets. If udp True uses UDP packets.
        """

        if udp:
            send_packets, exp_client_packets, _ = \
                self.create_vxlan_udp_session_packets(client=client,
                                                      server=server,
                                                      fake_mac=fake_mac)
            vxlan_pkt = send_packets["client_udp_vxlan_pkt"]
        else:
            send_packets, exp_client_packets, _ = \
                self.create_vxlan_tcp_session_packets(client=client,
                                                      server=server,
                                                      fake_mac=fake_mac)
            vxlan_pkt = send_packets["client_syn_pkt"]

        def send_verify(pkt):
            send_packet(self, client.port, pkt)
            verify_no_other_packets(self, timeout=1)

        if invalid_vni is not None:
            # Verify drop with invalid VNI
            vxlan_pkt_invalid_vni = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_vni.getlayer('VXLAN').vni = invalid_vni

            print("Sending VxLAN IPv4 packet with invalid VNI, expect drop")
            send_verify(vxlan_pkt_invalid_vni)
            print("\nInvalid VNI OK\n")

        if invalid_vip is not None:
            # Verify drop with invalid VIP
            vxlan_pkt_invalid_vip = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_vip.getlayer('IP').dst = invalid_vip

            print("Sending VxLAN IPv4 packet with invalid VIP, expect drop")
            send_verify(vxlan_pkt_invalid_vip)
            print("\nInvalid VIP OK\n")

        if invalid_inner_src_mac is not None:
            # Verify drop with invalid inner Src MAC
            vxlan_pkt_invalid_src_mac = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_src_mac.getlayer('VXLAN').getlayer('Ether').src = invalid_inner_src_mac

            print("Sending VxLAN IPv4 packet with invalid Inner Src MAC, expect drop")
            send_verify(vxlan_pkt_invalid_src_mac)
            print("\nInvalid Inner Src MAC OK\n")

        if invalid_inner_dst_mac is not None:
            # Verify drop with invalid inner Dst MAC
            vxlan_pkt_invalid_dst_mac = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_dst_mac.getlayer('VXLAN').getlayer('Ether').dst = invalid_inner_dst_mac

            print("Sending VxLAN IPv4 packet with invalid Inner Dst MAC, expect drop")
            send_verify(vxlan_pkt_invalid_dst_mac)
            print("\nInvalid Inner Dst MAC OK\n")

        if invalid_inner_dst_ip is not None:
            # Verify drop with invalid inner Dst IP
            vxlan_pkt_invalid_inner_dst_ip = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_inner_dst_ip.getlayer('VXLAN').getlayer('IP').dst = invalid_inner_dst_ip

            print("Sending VxLAN IPv4 packet with invalid Inner Dst MAC, expect drop")
            send_verify(vxlan_pkt_invalid_inner_dst_ip)
            print("\nInvalid Inner Dst IP OK\n")

        if invalid_outer_src_ip is not None:
            # Verify drop with invalid outer Src IP
            vxlan_pkt_invalid_outer_src_ip = deepcopy(vxlan_pkt)
            vxlan_pkt_invalid_outer_src_ip.getlayer('IP').src = invalid_outer_src_ip

            print("Sending VxLAN IPv4 packet with invalid Outer Src IP, expect drop")
            send_verify(vxlan_pkt_invalid_outer_src_ip)
            print("\nInvalid Outer Src IP OK\n")

        if valid_pkt_drop:
            print("Sending valid VxLAN IPv4 packet, expect drop")
            send_verify(vxlan_pkt)
            print("\nValid packet drop OK\n")

    def create_vxlan_tcp_session_packets(self,
                                         client: DutNeighborNetworkParameters,
                                         server: DutNeighborNetworkParameters,
                                         fake_mac: bool, terminate_tcp_session=True):
        """
        Creates TCP VxLAN encapsulated packets needed for TCP session establishment
        Parameters:
            client: DutNeighborNetworkParameters object with src network config
            server: DutNeighborNetworkParameters object with dst network config
            fake_mac (bool): If True sets in client Inner packets Ether Dst MAC (CA MAC) to fake mac,
                             (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
            terminate_tcp_session (bool): If True return packets for tcp session termination else
                                          return only packets for session start
        """

        client_tcp_port = randint(1024, 49151)
        http_port = 80

        fake_ca_dst_mac = "AA:12:44:69:05:AA"

        create_inner_pkt, create_outer_pkt = self.define_pkts_creation_func('tcp')

        # Client (host1) packets
        # create tcp SYN pkt encapsulated in VxLAN packet
        client_inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                            eth_src=client.client.mac,
                                            **{self.ip_dst_inner_pkt: server.client.ip},
                                            **{self.ip_src_inner_pkt: client.client.ip},
                                            tcp_sport=client_tcp_port,
                                            tcp_dport=http_port,
                                            tcp_flags=self.SYN)
        self.update_tcp_pkt(client_inner_pkt, seq=1, ack=0)

        exp_client_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                                eth_src=client.client.mac,
                                                **{self.ip_dst_inner_pkt: server.client.ip},
                                                **{self.ip_src_inner_pkt: client.client.ip},
                                                tcp_sport=client_tcp_port,
                                                tcp_dport=http_port,
                                                tcp_flags=self.SYN)
        self.update_tcp_pkt(exp_client_inner_pkt, seq=1, ack=0)

        client_tcp_syn_vxlan_pkt = create_outer_pkt(eth_dst=client.peer.mac,
                                                    eth_src=client.mac,
                                                    **{self.ip_dst_outer_pkt: client.peer.ip},  # VIP
                                                    **{self.ip_src_outer_pkt: client.ip},
                                                    with_udp_chksum=True,
                                                    vxlan_vni=client.client.vni,
                                                    inner_frame=client_inner_pkt)

        exp_client_tcp_syn_vxlan_pkt = create_outer_pkt(eth_dst=server.mac,
                                                        eth_src=server.peer.mac,
                                                        **{self.ip_dst_outer_pkt: server.ip},
                                                        **{self.ip_src_outer_pkt: server.peer.ip},  # VIP
                                                        with_udp_chksum=True,
                                                        vxlan_vni=server.client.vni,
                                                        inner_frame=exp_client_inner_pkt)

        # create tcp ACK pkt encapsulated in VxLAN packet
        client_tcp_ack_vxlan_pkt = deepcopy(client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=2, ack=11)

        exp_client_tcp_ack_vxlan_pkt = deepcopy(exp_client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(exp_client_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=2, ack=11)

        # create tcp FIN ACK pkt encapsulated in VxLAN packet
        client_tcp_fin_vxlan_pkt = deepcopy(client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_fin_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=2, ack=11)

        exp_client_tcp_fin_vxlan_pkt = deepcopy(exp_client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(exp_client_tcp_fin_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=2, ack=11)

        # create last client tcp ACK pkt encapsulated in VxLAN packet
        client_tcp_ack_vxlan_pkt_close = deepcopy(client_tcp_ack_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_ack_vxlan_pkt_close, seq=3, ack=12)

        exp_client_tcp_ack_vxlan_pkt_close = deepcopy(exp_client_tcp_ack_vxlan_pkt)
        self.update_tcp_pkt(exp_client_tcp_ack_vxlan_pkt_close, seq=3, ack=12)

        # Server (host2) packets
        # create tcp SYN ACK pkt encapsulated in VxLAN packet
        server_inner_pkt = create_inner_pkt(eth_dst=client.client.mac,
                                            eth_src=server.client.mac,
                                            **{self.ip_dst_inner_pkt: client.client.ip},
                                            **{self.ip_src_inner_pkt: server.client.ip},
                                            tcp_sport=http_port,
                                            tcp_dport=client_tcp_port,
                                            tcp_flags=self.SYN_ACK)
        self.update_tcp_pkt(server_inner_pkt, seq=10, ack=2)

        server_tcp_synack_vxlan_pkt = create_outer_pkt(eth_dst=server.peer.mac,
                                                       eth_src=server.mac,
                                                       **{self.ip_dst_outer_pkt: server.peer.ip},  # VIP
                                                       **{self.ip_src_outer_pkt: server.ip},
                                                       with_udp_chksum=True,
                                                       vxlan_vni=server.client.vni,
                                                       inner_frame=server_inner_pkt)

        exp_server_tcp_synack_vxlan_pkt = create_outer_pkt(eth_dst=client.mac,
                                                           eth_src=client.peer.mac,
                                                           **{self.ip_dst_outer_pkt: client.ip},
                                                           **{self.ip_src_outer_pkt: client.peer.ip},  # VIP
                                                           with_udp_chksum=True,
                                                           vxlan_vni=client.client.vni,
                                                           inner_frame=server_inner_pkt)

        # create tcp ACK pkt encapsulated in VxLAN packet
        server_tcp_ack_vxlan_pkt = deepcopy(server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(server_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=11, ack=3)

        exp_server_tcp_ack_vxlan_pkt = deepcopy(exp_server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(exp_server_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=11, ack=3)

        # create tcp FIN ACK pkt encapsulated in VxLAN packet
        server_tcp_finack_vxlan_pkt = deepcopy(server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(server_tcp_finack_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=11, ack=3)

        exp_server_tcp_finack_vxlan_pkt = deepcopy(exp_server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(exp_server_tcp_finack_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=11, ack=3)

        send_packets = OrderedDict()

        # packets for starting tcp session
        send_packets["client_syn_pkt"] = client_tcp_syn_vxlan_pkt
        send_packets["server_syn_ack_pkt"] = server_tcp_synack_vxlan_pkt
        send_packets["client_ack_pkt"] = client_tcp_ack_vxlan_pkt

        exp_client_packets = {"exp_client_syn_pkt": exp_client_tcp_syn_vxlan_pkt,
                              "exp_client_ack_pkt": exp_client_tcp_ack_vxlan_pkt}

        exp_server_packets = {"exp_server_syn_ack_pkt": exp_server_tcp_synack_vxlan_pkt}

        if terminate_tcp_session:
            # packets for termination tcp session
            send_packets["client_fin_ack_pkt"] = client_tcp_fin_vxlan_pkt
            send_packets["server_ack_pkt"] = server_tcp_ack_vxlan_pkt
            send_packets["server_fin_ack_pkt"] = server_tcp_finack_vxlan_pkt
            send_packets["client_ack_pkt_close"] = client_tcp_ack_vxlan_pkt_close

            exp_client_packets["exp_client_fin_ack_pkt"] = exp_client_tcp_fin_vxlan_pkt
            exp_client_packets["exp_client_ack_pkt_close"] = exp_client_tcp_ack_vxlan_pkt_close

            exp_server_packets["exp_server_ack_pkt"] = exp_server_tcp_ack_vxlan_pkt
            exp_server_packets["exp_server_fin_ack_pkt"] = exp_server_tcp_finack_vxlan_pkt

        return send_packets, exp_client_packets, exp_server_packets

    def create_vxlan_tcp_session_route_direct_packets(self,
                                                      client: DutNeighborNetworkParameters,
                                                      server: DutNeighborNetworkParameters,
                                                      fake_mac: bool, terminate_tcp_session=True):
        """
        Creates TCP VxLAN encapsulated packets needed for TCP session establishment
        when action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT
        Parameters:
            client: DutNeighborNetworkParameters object with src network config
            server: DutNeighborNetworkParameters object with dst network config
            fake_mac (bool): If True sets in client Inner packets Ether Dst MAC (CA MAC) to fake mac,
                             (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
            terminate_tcp_session (bool): If True return packets for tcp session termination else
                                          return only packets for session start
        """

        client_tcp_port = randint(1024, 49151)
        http_port = 80

        fake_ca_dst_mac = "AA:12:44:69:05:AA"

        create_inner_pkt, create_outer_pkt = self.define_pkts_creation_func('tcp')

        # Client (host1) packets
        # create tcp SYN pkt encapsulated in VxLAN packet
        client_inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                            eth_src=client.client.mac,
                                            **{self.ip_dst_inner_pkt: server.client.ip},
                                            **{self.ip_src_inner_pkt: client.client.ip},
                                            tcp_sport=client_tcp_port,
                                            tcp_dport=http_port,
                                            tcp_flags=self.SYN)
        self.update_tcp_pkt(client_inner_pkt, seq=1, ack=0)

        client_tcp_syn_vxlan_pkt = create_outer_pkt(eth_dst=client.peer.mac,
                                                    eth_src=client.mac,
                                                    **{self.ip_dst_outer_pkt: client.peer.ip},  # VIP
                                                    **{self.ip_src_outer_pkt: client.ip},
                                                    with_udp_chksum=True,
                                                    vxlan_vni=client.client.vni,
                                                    inner_frame=client_inner_pkt)

        exp_client_tcp_syn_pkt = create_inner_pkt(eth_dst=server.mac,
                                                  eth_src=server.peer.mac,
                                                  **{self.ip_dst_inner_pkt: server.client.ip},
                                                  **{self.ip_src_inner_pkt: client.peer.ip},
                                                  tcp_sport=client_tcp_port,
                                                  tcp_dport=http_port,
                                                  tcp_flags=self.SYN)
        self.update_tcp_pkt(exp_client_tcp_syn_pkt, seq=1, ack=0)

        # create tcp ACK pkt encapsulated in VxLAN packet
        client_tcp_ack_vxlan_pkt = deepcopy(client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=2, ack=11)

        exp_client_tcp_ack_pkt = deepcopy(exp_client_tcp_syn_pkt)
        self.update_tcp_pkt(exp_client_tcp_ack_pkt, tcp_flag=self.ACK,
                            seq=2, ack=11)

        # create tcp FIN ACK pkt encapsulated in VxLAN packet
        client_tcp_fin_vxlan_pkt = deepcopy(client_tcp_syn_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_fin_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=2, ack=11)

        exp_client_tcp_fin_pkt = deepcopy(exp_client_tcp_syn_pkt)
        self.update_tcp_pkt(exp_client_tcp_fin_pkt, tcp_flag=self.FIN_ACK,
                            seq=2, ack=11)

        # create last client tcp ACK pkt encapsulated in VxLAN packet
        client_tcp_ack_vxlan_pkt_close = deepcopy(client_tcp_ack_vxlan_pkt)
        self.update_tcp_pkt(client_tcp_ack_vxlan_pkt_close, seq=3, ack=12)

        exp_client_tcp_ack_pkt_close = deepcopy(exp_client_tcp_syn_pkt)
        self.update_tcp_pkt(exp_client_tcp_ack_pkt_close, seq=3, ack=12)

        # Server (host2) packets
        # create tcp SYN ACK pkt encapsulated in VxLAN packet
        server_tcp_synack_pkt = create_inner_pkt(eth_dst=client.peer.mac,
                                                 eth_src=server.client.mac,
                                                 **{self.ip_dst_inner_pkt: client.peer.ip},  # VIP
                                                 **{self.ip_src_inner_pkt: server.client.ip},
                                                 tcp_sport=http_port,
                                                 tcp_dport=client_tcp_port,
                                                 tcp_flags=self.SYN_ACK)
        self.update_tcp_pkt(server_tcp_synack_pkt, seq=10, ack=2)

        exp_server_inner_pkt = create_inner_pkt(eth_dst=client.client.mac,
                                                eth_src=server.client.mac,
                                                **{self.ip_dst_inner_pkt: client.client.ip},
                                                **{self.ip_src_inner_pkt: server.client.ip},
                                                tcp_sport=http_port,
                                                tcp_dport=client_tcp_port,
                                                tcp_flags=self.SYN_ACK)
        self.update_tcp_pkt(exp_server_inner_pkt, seq=10, ack=2)

        exp_server_tcp_synack_vxlan_pkt = create_outer_pkt(eth_dst=client.mac,
                                                           eth_src=client.peer.mac,
                                                           **{self.ip_dst_inner_pkt: client.ip},
                                                           **{self.ip_src_inner_pkt: client.peer.ip},  # VIP
                                                           with_udp_chksum=True,
                                                           vxlan_vni=client.client.vni,
                                                           inner_frame=exp_server_inner_pkt)

        # create tcp ACK pkt encapsulated in VxLAN packet
        server_tcp_ack_pkt = deepcopy(server_tcp_synack_pkt)
        self.update_tcp_pkt(server_tcp_ack_pkt, tcp_flag=self.ACK,
                            seq=11, ack=3)

        exp_server_tcp_ack_vxlan_pkt = deepcopy(exp_server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(exp_server_tcp_ack_vxlan_pkt, tcp_flag=self.ACK,
                            seq=11, ack=3)

        # create tcp FIN ACK pkt encapsulated in VxLAN packet
        server_tcp_finack_pkt = deepcopy(server_tcp_synack_pkt)
        self.update_tcp_pkt(server_tcp_finack_pkt, tcp_flag=self.FIN_ACK,
                            seq=11, ack=3)

        exp_server_tcp_finack_vxlan_pkt = deepcopy(exp_server_tcp_synack_vxlan_pkt)
        self.update_tcp_pkt(exp_server_tcp_finack_vxlan_pkt, tcp_flag=self.FIN_ACK,
                            seq=11, ack=3)

        send_packets = OrderedDict()

        # packets for starting tcp session
        send_packets["client_syn_pkt"] = client_tcp_syn_vxlan_pkt
        send_packets["server_syn_ack_pkt"] = server_tcp_synack_pkt
        send_packets["client_ack_pkt"] = client_tcp_ack_vxlan_pkt

        exp_client_packets = {"exp_client_syn_pkt": exp_client_tcp_syn_pkt,
                              "exp_client_ack_pkt": exp_client_tcp_ack_pkt}

        exp_server_packets = {"exp_server_syn_ack_pkt": exp_server_tcp_synack_vxlan_pkt}

        if terminate_tcp_session:
            # packets for termination tcp session
            send_packets["client_fin_ack_pkt"] = client_tcp_fin_vxlan_pkt
            send_packets["server_ack_pkt"] = server_tcp_ack_pkt
            send_packets["server_fin_ack_pkt"] = server_tcp_finack_pkt
            send_packets["client_ack_pkt_close"] = client_tcp_ack_vxlan_pkt_close

            exp_client_packets["exp_client_fin_ack_pkt"] = exp_client_tcp_fin_pkt
            exp_client_packets["exp_client_ack_pkt_close"] = exp_client_tcp_ack_pkt_close

            exp_server_packets["exp_server_ack_pkt"] = exp_server_tcp_ack_vxlan_pkt
            exp_server_packets["exp_server_fin_ack_pkt"] = exp_server_tcp_finack_vxlan_pkt

        return send_packets, exp_client_packets, exp_server_packets

    def create_vxlan_udp_session_packets(self,
                                         client: DutNeighborNetworkParameters,
                                         server: DutNeighborNetworkParameters,
                                         fake_mac: bool):
        """
        Creates UDP VxLAN encapsulated packets needed for UDP session establishment
        Parameters:
            client: DutNeighborNetworkParameters object with src network config
            server: DutNeighborNetworkParameters object with dst network config
            fake_mac (bool): If True sets in client Inner packets Ether Dst MAC (CA MAC) to fake mac,
                             (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
        """

        client_udp_port = randint(1024, 49151)
        http_port = 80

        fake_ca_dst_mac = "AA:12:44:69:05:AA"

        create_inner_pkt, create_outer_pkt = self.define_pkts_creation_func('udp')

        client_inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                            eth_src=client.client.mac,
                                            **{self.ip_dst_inner_pkt: server.client.ip},
                                            **{self.ip_src_inner_pkt: client.client.ip},
                                            udp_sport=client_udp_port,
                                            udp_dport=http_port)

        exp_client_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                                eth_src=client.client.mac,
                                                **{self.ip_dst_inner_pkt: server.client.ip},
                                                **{self.ip_src_inner_pkt: client.client.ip},
                                                udp_sport=client_udp_port,
                                                udp_dport=http_port)

        server_inner_pkt = create_inner_pkt(eth_dst=client.client.mac,
                                            eth_src=server.client.mac,
                                            **{self.ip_dst_inner_pkt: client.client.ip},
                                            **{self.ip_src_inner_pkt: server.client.ip},
                                            udp_sport=http_port,
                                            udp_dport=client_udp_port)

        client_vxlan_pkt = create_outer_pkt(eth_dst=client.peer.mac,
                                            eth_src=client.mac,
                                            **{self.ip_dst_outer_pkt: client.peer.ip},  # VIP
                                            **{self.ip_src_outer_pkt: client.ip},
                                            with_udp_chksum=True,
                                            vxlan_vni=client.client.vni,
                                            inner_frame=client_inner_pkt)

        exp_client_vxlan_pkt = create_outer_pkt(eth_dst=server.mac,
                                                eth_src=server.peer.mac,
                                                **{self.ip_dst_outer_pkt: server.ip},
                                                **{self.ip_src_outer_pkt: server.peer.ip},  # VIP
                                                with_udp_chksum=True,
                                                vxlan_vni=server.client.vni,
                                                inner_frame=exp_client_inner_pkt)

        server_vxlan_pkt = create_outer_pkt(eth_dst=server.peer.mac,
                                            eth_src=server.mac,
                                            **{self.ip_dst_outer_pkt: server.peer.ip},  # VIP
                                            **{self.ip_src_outer_pkt: server.ip},
                                            with_udp_chksum=True,
                                            vxlan_vni=server.client.vni,
                                            inner_frame=server_inner_pkt)

        exp_server_vxlan_pkt = create_outer_pkt(eth_dst=client.mac,
                                                eth_src=client.peer.mac,
                                                **{self.ip_dst_outer_pkt: client.ip},
                                                **{self.ip_src_outer_pkt: client.peer.ip},  # VIP
                                                with_udp_chksum=True,
                                                vxlan_vni=client.client.vni,
                                                inner_frame=server_inner_pkt)
        send_packets = OrderedDict()

        # packets for starting udp session
        send_packets["client_udp_vxlan_pkt"] = client_vxlan_pkt
        send_packets["server_udp_vxlan_pkt"] = server_vxlan_pkt

        exp_client_packets = {"exp_client_udp_vxlan_pkt": exp_client_vxlan_pkt}
        exp_server_packets = {"exp_server_udp_vxlan_pkt": exp_server_vxlan_pkt}

        return send_packets, exp_client_packets, exp_server_packets

    def create_vxlan_icmp_session_packets(self,
                                          client: DutNeighborNetworkParameters,
                                          server: DutNeighborNetworkParameters,
                                          fake_mac: bool):
        """
        Creates ICMP VxLAN encapsulated packets needed for
        echo request and reply
        Parameters:
            client: DutNeighborNetworkParameters object with src network config
            server: DutNeighborNetworkParameters object with dst network config
            fake_mac (bool): If True sets in client Inner packets Ether Dst MAC (CA MAC) to fake mac,
                             (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
        """

        fake_ca_dst_mac = "AA:12:44:69:05:AA"

        create_inner_pkt, create_outer_pkt = self.define_pkts_creation_func('icmp')

        client_inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                            eth_src=client.client.mac,
                                            **{self.ip_dst_inner_pkt: server.client.ip},
                                            **{self.ip_src_inner_pkt: client.client.ip},
                                            icmp_type=8)

        exp_client_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                                eth_src=client.client.mac,
                                                **{self.ip_dst_inner_pkt: server.client.ip},
                                                **{self.ip_src_inner_pkt: client.client.ip},
                                                icmp_type=8)

        server_inner_pkt = create_inner_pkt(eth_dst=client.client.mac,
                                            eth_src=server.client.mac,
                                            **{self.ip_dst_inner_pkt: client.client.ip},
                                            **{self.ip_src_inner_pkt: server.client.ip},
                                            icmp_type=0)

        client_vxlan_pkt = create_outer_pkt(eth_dst=client.peer.mac,
                                            eth_src=client.mac,
                                            **{self.ip_dst_outer_pkt: client.peer.ip},  # VIP
                                            **{self.ip_src_outer_pkt: client.ip},
                                            with_udp_chksum=True,
                                            vxlan_vni=client.client.vni,
                                            inner_frame=client_inner_pkt)

        exp_client_vxlan_pkt = create_outer_pkt(eth_dst=server.mac,
                                                eth_src=server.peer.mac,
                                                **{self.ip_dst_outer_pkt: server.ip},
                                                **{self.ip_src_outer_pkt: server.peer.ip},  # VIP
                                                with_udp_chksum=True,
                                                vxlan_vni=server.client.vni,
                                                inner_frame=exp_client_inner_pkt)

        server_vxlan_pkt = create_outer_pkt(eth_dst=server.peer.mac,
                                            eth_src=server.mac,
                                            **{self.ip_dst_outer_pkt: server.peer.ip},  # VIP
                                            **{self.ip_src_outer_pkt: server.ip},
                                            with_udp_chksum=True,
                                            vxlan_vni=server.client.vni,
                                            inner_frame=server_inner_pkt)

        exp_server_vxlan_pkt = create_outer_pkt(eth_dst=client.mac,
                                                eth_src=client.peer.mac,
                                                **{self.ip_dst_outer_pkt: client.ip},
                                                **{self.ip_src_outer_pkt: client.peer.ip},
                                                with_udp_chksum=True,
                                                vxlan_vni=client.client.vni,
                                                inner_frame=server_inner_pkt)
        send_packets = OrderedDict()

        # packets for starting udp session
        send_packets["client_echo_request_vxlan_pkt"] = client_vxlan_pkt
        send_packets["server_echo_reply_vxlan_pkt"] = server_vxlan_pkt

        exp_client_packets = {"exp_client_echo_request_pkt": exp_client_vxlan_pkt}
        exp_server_packets = {"exp_server_echo_reply_pkt": exp_server_vxlan_pkt}

        return send_packets, exp_client_packets, exp_server_packets

    def create_vxlan_oneway_pkts(self,
                                 client: DutNeighborNetworkParameters,
                                 server: DutNeighborNetworkParameters,
                                 connection: str,
                                 fake_mac=False,
                                 route_direct=False):
        """
        Creates VxLAN encapsulated TCP, UDP or ICMP packet
        client: DutNeighborNetworkParameters object with src network config
        server: DutNeighborNetworkParameters object with dst network config
        connection (str): connection type str (e.g. 'tcp', 'UDP', 'icmp')
        fake_mac (bool): If True requests for Inner client packets Ether Dst MAC (CA MAC) set to fake mac,
                         (default Outbound scenario) else to Dst CA MAC (Inbound scenario)
        TODO: route_direct (bool): For scenarios when routing action is SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT
                             and decapsulated packets expected on the server side
        """
        client_port = randint(1024, 49151)
        http_port = 80
        fake_ca_dst_mac = "AA:12:44:69:05:AA"

        conn_type = connection.lower()

        create_inner_pkt, create_outer_pkt = self.define_pkts_creation_func(conn_type)

        if conn_type == 'tcp':
            inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                         eth_src=client.client.mac,
                                         **{self.ip_dst_inner_pkt: server.client.ip},
                                         **{self.ip_src_inner_pkt: client.client.ip},
                                         tcp_sport=client_port,
                                         tcp_dport=http_port,
                                         tcp_flags=self.SYN)
            self.update_tcp_pkt(inner_pkt, seq=1, ack=0)

            exp_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                             eth_src=client.client.mac,
                                             **{self.ip_dst_inner_pkt: server.client.ip},
                                             **{self.ip_src_inner_pkt: client.client.ip},
                                             tcp_sport=client_port,
                                             tcp_dport=http_port,
                                             tcp_flags=self.SYN)
            self.update_tcp_pkt(exp_inner_pkt, seq=1, ack=0)

        elif conn_type == 'udp':
            inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                         eth_src=client.client.mac,
                                         **{self.ip_dst_inner_pkt: server.client.ip},
                                         **{self.ip_src_inner_pkt: client.client.ip},
                                         udp_sport=client_port,
                                         udp_dport=http_port)

            exp_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                             eth_src=client.client.mac,
                                             **{self.ip_dst_inner_pkt: server.client.ip},
                                             **{self.ip_src_inner_pkt: client.client.ip},
                                             udp_sport=client_port,
                                             udp_dport=http_port)

        elif conn_type == 'icmp':
            inner_pkt = create_inner_pkt(eth_dst=fake_ca_dst_mac if fake_mac else server.client.mac,
                                         eth_src=client.client.mac,
                                         **{self.ip_dst_inner_pkt: server.client.ip},
                                         **{self.ip_src_inner_pkt: client.client.ip},
                                         icmp_type=8)

            exp_inner_pkt = create_inner_pkt(eth_dst=server.client.mac,
                                             eth_src=client.client.mac,
                                             **{self.ip_dst_inner_pkt: server.client.ip},
                                             **{self.ip_src_inner_pkt: client.client.ip},
                                             icmp_type=8)

        vxlan_pkt = create_outer_pkt(eth_dst=client.peer.mac,
                                     eth_src=client.mac,
                                     **{self.ip_dst_outer_pkt: client.peer.ip},  # VIP
                                     **{self.ip_src_outer_pkt: client.ip},
                                     with_udp_chksum=True,
                                     vxlan_vni=client.client.vni,
                                     inner_frame=inner_pkt)

        exp_vxlan_pkt = create_outer_pkt(eth_dst=server.mac,
                                         eth_src=server.peer.mac,
                                         **{self.ip_dst_outer_pkt: server.ip},
                                         **{self.ip_src_outer_pkt: server.peer.ip},  # VIP
                                         with_udp_chksum=True,
                                         vxlan_vni=server.client.vni,
                                         inner_frame=exp_inner_pkt)

        return vxlan_pkt, exp_vxlan_pkt

    @staticmethod
    def update_tcp_pkt(pkt, seq, ack, tcp_flag=None):
        """
        Update Flag, Sequence and Acknowledgement fields in given TCP packet
        """
        if tcp_flag is not None:
            pkt.getlayer("TCP").flags = tcp_flag

        pkt.getlayer("TCP").seq = seq
        pkt.getlayer("TCP").ack = ack
