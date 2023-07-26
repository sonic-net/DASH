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
Thrift SAI interface VNET to VNET Metering tests
"""

from random import randint
from unittest import skipIf

from sai_dash_utils import *
from sai_thrift.sai_headers import *


# Outbound tests
@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMeterOnePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Verify outbound route VNET meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    One direction overlay IPv4
    """
    policy_meter_class = 0
    route_meter_class = randint(1, (1 << 15) - 1)
    map_meter_class = 0
    route_type = "vnet"  # vnet_direct, direct
    # Tx/Rx value "1" is replaced with packet length in bytes
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0},
                   "route": {"oid": 0, "tx": 1, "rx": 0},
                   "map": {"oid": 0, "tx": 0, "rx": 0},}

    def get_ipv4_v6_policy_meter(self, meter_policy_oid):
        if self.overlay_ipv6:
            return None, meter_policy_oid
        else:  # IPv4 family
            return meter_policy_oid, None

    def get_ip_lpm(self):
        if self.overlay_ipv6:
            return "bbbb::bc", "bbbb::0/64"
        else:
            return "192.168.1.10", "192.168.1.0/24"

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, add_routes=False)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=True)

    def configure_metering(self):
        """
        Configure meter entities
        """

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        m_policy_oid = self.meter_policy if self.policy_meter_class > 0 else 0
        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(m_policy_oid)
        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        mask = 'ffff:f000::' if self.overlay_ipv6 else "255.255.255.0"
        if self.policy_meter_class > 0:
            print(f"Create policy meter class {self.policy_meter_class}")
            self.meter_policy = self.dash_meter_policy_create()
            self.meter_rule = self.dash_meter_rule_create(
                self.meter_policy, dip=self.rx_host.client.ip,
                dip_mask=mask, priority=1,
                meter_class=self.policy_meter_class)
            self.meter_bucket_policy = self.dash_meter_bucket_create(
                self.eni_id_1, self.policy_meter_class)
            self.buckets_exp["policy"]["oid"] = self.meter_bucket_policy
        if self.route_meter_class > 0:
            print(f"Create router meter class {self.route_meter_class}")
            self.meter_bucket_route = self.dash_meter_bucket_create(
                self.eni_id_1, self.route_meter_class)
            self.buckets_exp["route"]["oid"] = self.meter_bucket_route
        if self.map_meter_class > 0:
            print(f"Create map meter class {self.map_meter_class}")
            self.meter_bucket_map = self.dash_meter_bucket_create(
                self.eni_id_1, self.map_meter_class)
            self.buckets_exp["map"]["oid"] = self.meter_bucket_map

    def configure_overlay(self):
        """
        Configure outbound overlay
        """
        self.vip_create(self.tx_host.peer.ip)
        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        self.dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        self.eni_mac_map_create(self.eni_id_1, self.tx_host.client.mac)  # ENI MAC

        overlay_ip, lpm = self.get_ip_lpm()
        mpolicy_en = True if self.route_meter_class > 0 else False
        if self.route_type == "vnet":
            self.outbound_routing_vnet_create(
                eni_id=self.eni_id_1, lpm=lpm,
                dst_vnet_id=self.dst_vnet, meter_policy_en=mpolicy_en,
                meter_class=self.route_meter_class)
        elif self.route_type == "vnet_direct":
            self.outbound_routing_vnet_direct_create(
                eni_id=self.eni_id_1, lpm=lpm,
                dst_vnet_id=self.dst_vnet, overlay_ip=overlay_ip,
                meter_policy_en=mpolicy_en, meter_class=self.route_meter_class)
        else:  # direct
            self.outbound_routing_direct_create(
                eni_id=self.eni_id_1, lpm=lpm,
                meter_policy_en=mpolicy_en, meter_class=self.route_meter_class)
            return  # No map for direct route

        dip = self.rx_host.client.ip if self.route_type == "vnet" else overlay_ip
        use_dst_vnet_vni = True if "vnet" in self.route_type else False
        mpolicy_en = True if self.map_meter_class > 0 else False
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet,
                                      dip=dip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=use_dst_vnet_vni,
                                      meter_class_override=mpolicy_en,
                                      meter_class=self.map_meter_class)

    def verify_metering(self, bucket_1, bucket_2, tx_bytes, rx_bytes):
        """
        Verify meter results with packet sent
        """
        out_bytes = bucket_2["outbound_bytes_counter"] - bucket_1["outbound_bytes_counter"]
        in_bytes = bucket_2["inbound_bytes_counter"] - bucket_1["inbound_bytes_counter"]
        print(f'out_bytes: bucket#2={bucket_2["outbound_bytes_counter"]}'
              f' bucket#1={bucket_1["outbound_bytes_counter"]}')
        print(f'in_bytes: bucket#2={bucket_2["inbound_bytes_counter"]}'
              f' bucket#1={bucket_1["inbound_bytes_counter"]}')
        print(f'Difference: out_bytes={out_bytes} in_bytes={in_bytes}')

        self.assertEqual(out_bytes, tx_bytes)
        self.assertEqual(in_bytes, rx_bytes)

    def vnet2VnetOutboundMeterTest(self, tx_equal_to_rx):
        """
        Verify default meter configuration, increment policy bucket
        """
        print(f"Running {self.__class__.__name__} ...")
        buckets_1 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)
        # Verify meter bucket
        buckets_2 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        for meter_name, meter_val in self.buckets_exp.items():
            if meter_name not in buckets_1 or meter_name not in buckets_2:
                continue
            meter_val["tx"] = len(self.send_pkt) if meter_val["tx"] > 0 else meter_val["tx"]
            meter_val["rx"] = len(self.send_pkt) if meter_val["rx"] > 0 else meter_val["rx"]
            print(f'Verify meter results for {meter_name}, expected:'
                  f' tx={meter_val["tx"]} rx={meter_val["rx"]}')
            self.verify_metering(buckets_1[meter_name], buckets_2[meter_name],
                                  meter_val["tx"], meter_val["rx"])


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound route VNET meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMeterTwoPortsTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound route VNET meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundVnetRouteMeterOnePortOverlayIpv6Test):
    """
    Verify outbound route VNET meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetDirectRouteMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound route VNET Direct meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    One direction overlay IPv4
    """

    route_type = "vnet_direct"


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetDirectRouteMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundVnetDirectRouteMeterOnePortTest):
    """
    Verify outbound route VNET Direct meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetDirectRouteMeterTwoPortsTest(Vnet2VnetOutboundVnetDirectRouteMeterOnePortTest):
    """
    Verify outbound route VNET Direct meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetDirectRouteMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundVnetDirectRouteMeterOnePortOverlayIpv6Test):
    """
    Verify outbound route VNET Direct meter bucket incremented when
    meter_policy_en=False and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMapMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    One direction overlay IPv4
    """

    policy_meter_class = 0
    route_meter_class = 0
    map_meter_class = randint(1, (1 << 15) - 1) 
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 0},
                   "map": {"oid": 0, "tx": 1, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMapMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundVnetRouteMapMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    One direction IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMapMeterTwoPortsTest(Vnet2VnetOutboundVnetRouteMapMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundVnetRouteMapMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundVnetRouteMapMeterOnePortOverlayIpv6Test):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMapOverPolicyMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented, policy map meter not incremented
    when meter_policy_en=True and meter_class_override=True
    One direction overlay IPv4
    """

    policy_meter_class = 101
    route_meter_class = 0
    map_meter_class = 122
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 0},
                   "map": {"oid": 0, "tx": 1, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMapOverPolicyMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundMapOverPolicyMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented, policy map meter not incremented
    when meter_policy_en=True and meter_class_override=True
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMapOverPolicyMeterTwoPortsTest(Vnet2VnetOutboundMapOverPolicyMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented, policy map meter not incremented
    when meter_policy_en=True and meter_class_override=True
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMapOverPolicyMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundMapOverPolicyMeterOnePortOverlayIpv6Test):
    """
    Verify outbound map meter bucket incremented, policy map meter not incremented
    when meter_policy_en=True and meter_class_override=True
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    policy_meter_class = 101
    route_meter_class = 0
    map_meter_class = 122
    buckets_exp = {"policy": {"oid": 0, "tx": 1, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 0},
                   "map": {"oid": 0, "tx": 0, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterTwoPortsTest(Vnet2VnetOutboundPolicyMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterVnetDirectOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    route_type = "vnet_direct"
    policy_meter_class = 101
    route_meter_class = 103
    map_meter_class = 102
    buckets_exp = {"policy": {"oid": 0, "tx": 1, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 0},
                   "map": {"oid": 0, "tx": 0, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterVnetDirectOnePortOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterVnetDirectOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterVnetDirectTwoPortsTest(Vnet2VnetOutboundPolicyMeterVnetDirectOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterVnetDirectTwoPortsOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterVnetDirectOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyPriorityMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for rule with higher priority when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    policy_meter_class_1 = 111
    policy_meter_class_2 = 122
    policy_meter_class_3 = 133
    buckets_exp = {"policy1": {"oid": 0, "tx": 0, "rx": 0},
                   "policy2": {"oid": 0, "tx": 0, "rx": 0},
                   "policy3": {"oid": 0, "tx": 1, "rx": 0},}

    def setUp(self):
        super().setUp()
        client_ip_1 = 'bbbb::30' if self.overlay_ipv6 else "192.168.1.10"
        client_ip_2 = 'bbbb::40' if self.overlay_ipv6 else "192.168.1.12"
        self.rx_host_1 = self.define_neighbor_network(
            port=self.rx_host.port,
            mac=self.rx_host.mac,
            ip=self.rx_host.ip,
            ip_prefix=self.rx_host.ip_prefix,
            peer_port=self.rx_host.peer.port,
            peer_mac=self.rx_host.peer.mac,
            peer_ip=self.rx_host.peer.ip,
            client_mac="00:03:00:00:01:16",
            client_ip=client_ip_1,
            client_vni=self.rx_host.client.vni)

        self.rx_host_2 = self.define_neighbor_network(
            port=self.rx_host.port,
            mac=self.rx_host.mac,
            ip=self.rx_host.ip,
            ip_prefix=self.rx_host.ip_prefix,
            peer_port=self.rx_host.peer.port,
            peer_mac=self.rx_host.peer.mac,
            peer_ip=self.rx_host.peer.ip,
            client_mac="00:03:00:00:02:18",
            client_ip=client_ip_2,
            client_vni=self.rx_host.client.vni)

    def configure_metering(self):
        """
        Configure meter entities
        """

        self.meter_policy = self.dash_meter_policy_create()

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy)
        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        print(f"Create policy meter class {self.policy_meter_class_1}")
        mask = 'ffff:f000::' if self.overlay_ipv6 else "255.255.255.0"
        self.meter_rule_1 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host.client.ip,
            dip_mask=mask, priority=randint(100, 500),
            meter_class=self.policy_meter_class_1)
        self.meter_bucket_policy_1 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_1)
        self.buckets_exp["policy1"]["oid"] = self.meter_bucket_policy_1

        print(f"Create policy meter class {self.policy_meter_class_2}")
        mask = 'ffff:f100::' if self.overlay_ipv6 else "255.255.255.240"
        self.meter_rule_2 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host_1.client.ip,
            dip_mask=mask, priority=1,
            meter_class=self.policy_meter_class_2)
        self.meter_bucket_policy_2 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_2)
        self.buckets_exp["policy2"]["oid"] = self.meter_bucket_policy_2

        print(f"Create policy meter class {self.policy_meter_class_3}")
        mask = 'ffff:f200::' if self.overlay_ipv6 else "255.255.255.224"
        self.meter_rule_3 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host_2.client.ip,
            dip_mask="255.255.255.224", priority=0,
            meter_class=self.policy_meter_class_3)
        self.meter_bucket_policy_3 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_3)
        self.buckets_exp["policy3"]["oid"] = self.meter_bucket_policy_3

    def configure_overlay(self):
        """
        Configure outbound overlay
        """

        self.vip_create(self.tx_host.peer.ip)
        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        self.dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        self.eni_mac_map_create(self.eni_id1, self.tx_host.client.mac)  # ENI MAC

        lpm = "bbbb::0/64" if self.overlay_ipv6 else "192.168.1.0/24"
        self.outbound_routing_vnet_create(
            eni_id=self.eni_id_1, lpm=lpm,
            dst_vnet_id=self.dst_vnet, meter_policy_en=True)

        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetOutboundMeterTest(self, tx_equal_to_rx):
        """
        Verify default meter configuration, increment policy bucket
        """
        print(f"Running {self.__class__.__name__} ...")
        msg = "Verify only meter bucket #{idx} (counter) with highest priority is incremented."
        msg = {0: msg.format(idx=3), 1: msg.format(idx=2), 2: msg.format(idx=3)}

        buckets_1 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        for idx in range(3):
            self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                        connection=self.connection, fake_mac=True, 
                                        tx_equal_to_rx=tx_equal_to_rx)
            self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_1,
                                        connection=self.connection, fake_mac=True, 
                                        tx_equal_to_rx=tx_equal_to_rx)
            self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host_2,
                                        connection=self.connection, fake_mac=True, 
                                        tx_equal_to_rx=tx_equal_to_rx)
            # Verify meter bucket
            buckets_2 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                        for meter_name, meter_val in self.buckets_exp.items()
                        if meter_val["oid"] != 0}
            print(f"{msg[idx]}")
            for meter_name, meter_val in self.buckets_exp.items():
                meter_val["tx"] = len(self.send_pkt) if meter_val["tx"] > 0 else meter_val["tx"]
                meter_val["rx"] = len(self.send_pkt) if meter_val["rx"] > 0 else meter_val["rx"]
                print(f'Verify meter results for {meter_name}, expected:'
                    f' tx={meter_val["tx"]} rx={meter_val["rx"]}')
                self.verify_metering(buckets_1[meter_name], buckets_2[meter_name],
                                    meter_val["tx"], meter_val["rx"])
            if idx == 0:
                # Delete meter rule #3 and send packets
                # Verify meter #1, #3 values not changed, meter #2 counted (higher priority)
                self.buckets_exp["policy2"]["tx"] = len(self.send_pkt)
                self.buckets_exp["policy3"]["tx"] = 0
                self.dash_meter_rule_remove(self.buckets_exp["policy3"]["oid"])  # meter exists
                self.assertEqual(self.status, SAI_STATUS_SUCCESS)
            elif idx == 1:
                # Add meter rule #3 with highest priority and send packets
                # Verify meter #1, #2 values not changed, meter #3 counted (higher priority)
                self.buckets_exp["policy2"]["tx"] = 0
                self.buckets_exp["policy3"]["tx"] = len(self.send_pkt)
                self.meter_rule_3 = self.dash_meter_rule_create(
                    self.meter_policy, dip=self.rx_host_2.client.ip,
                    dip_mask="255.255.255.224", priority=0,
                    meter_class=self.policy_meter_class_3)
            buckets_1 = buckets_2


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyPriorityMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundPolicyPriorityMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for rule with higher priority when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyPriorityMeterTwoPortsTest(Vnet2VnetOutboundPolicyPriorityMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for rule with higher priority when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyPriorityMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundPolicyPriorityMeterOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket incremented for rule with higher priority when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterNoHitOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket not incremented when no hit for rule
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    policy_meter_class = 110
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0}}

    def configure_metering(self):
        """
        Configure meter entities
        """

        self.meter_policy = self.dash_meter_policy_create()

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy)
        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        print(f"Create policy meter class {self.policy_meter_class}")
        mask = 'ffff:f000::' if self.overlay_ipv6 else "255.255.255.0"
        no_hit_ip = "bbcc::20" if self.overlay_ipv6 else "192.168.100.1"
        self.meter_rule = self.dash_meter_rule_create(
            self.meter_policy, dip=no_hit_ip,
            dip_mask=mask, priority=1,
            meter_class=self.policy_meter_class)
        self.meter_bucket_policy = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class)
        self.buckets_exp["policy"]["oid"] = self.meter_bucket_policy


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterNoHitOnePortOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterNoHitOnePortTest):
    """
    Verify outbound policy meter bucket not incremented when no hit for rule
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterNoHitTwoPortsTest(Vnet2VnetOutboundPolicyMeterNoHitOnePortTest):
    """
    Verify outbound policy meter bucket not incremented when no hit for rule
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyMeterNoHitTwoPortsOverlayIpv6Test(Vnet2VnetOutboundPolicyMeterNoHitOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket not incremented when no hit for rule
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyDiffRulesMeterOnePortTest(Vnet2VnetOutboundPolicyPriorityMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for different rules and priorities when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    policy_meter_class_1 = 99
    policy_meter_class_2 = 109
    policy_meter_class_3 = 119
    buckets_exp = {"policy1": {"oid": 0, "tx": 1, "rx": 0},
                   "policy2": {"oid": 0, "tx": 1, "rx": 0},
                   "policy3": {"oid": 0, "tx": 1, "rx": 0},}

    def setUp(self):
        super().setUp()
        client_ip_1 = 'bbbb:0400::30' if self.overlay_ipv6 else "192.168.1.65"
        client_ip_2 = 'bbbb:0800::40' if self.overlay_ipv6 else "192.168.1.129"

        self.rx_host_1 = self.define_neighbor_network(
            port=self.rx_host.port,
            mac=self.rx_host.mac,
            ip=self.rx_host.ip,
            ip_prefix=self.rx_host.ip_prefix,
            peer_port=self.rx_host.peer.port,
            peer_mac=self.rx_host.peer.mac,
            peer_ip=self.rx_host.peer.ip,
            client_mac="00:03:00:00:01:16",
            client_ip=client_ip_1,
            client_vni=self.rx_host.client.vni)

        self.rx_host_2 = self.define_neighbor_network(
            port=self.rx_host.port,
            mac=self.rx_host.mac,
            ip=self.rx_host.ip,
            ip_prefix=self.rx_host.ip_prefix,
            peer_port=self.rx_host.peer.port,
            peer_mac=self.rx_host.peer.mac,
            peer_ip=self.rx_host.peer.ip,
            client_mac="00:03:00:00:02:18",
            client_ip=client_ip_2,
            client_vni=self.rx_host.client.vni)

    def configure_metering(self):
        """
        Configure meter entities
        """
        self.meter_policy = self.dash_meter_policy_create()

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy)
        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        print(f"Create policy meter class {self.policy_meter_class_1}")
        mask = 'ffff:fc00::' if self.overlay_ipv6 else "255.255.255.192"
        self.meter_rule_1 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host.client.ip,
            dip_mask=mask, priority=randint(100, 500),
            meter_class=self.policy_meter_class_1)
        self.meter_bucket_policy_1 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_1)
        self.buckets_exp["policy1"]["oid"] = self.meter_bucket_policy_1

        print(f"Create policy meter class {self.policy_meter_class_2}")
        self.meter_rule_2 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host_1.client.ip,
            dip_mask=mask, priority=1,
            meter_class=self.policy_meter_class_2)
        self.meter_bucket_policy_2 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_2)
        self.buckets_exp["policy2"]["oid"] = self.meter_bucket_policy_2

        print(f"Create policy meter class {self.policy_meter_class_3}")
        self.meter_rule_3 = self.dash_meter_rule_create(
            self.meter_policy, dip=self.rx_host_2.client.ip,
            dip_mask=mask, priority=0,
            meter_class=self.policy_meter_class_3)
        self.meter_bucket_policy_3 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_3)
        self.buckets_exp["policy3"]["oid"] = self.meter_bucket_policy_3


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyDiffRulesMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundPolicyPriorityMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for different rules and priorities when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyDiffRulesMeterTwoPortsTest(Vnet2VnetOutboundPolicyDiffRulesMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for different rules and priorities when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundPolicyDiffRulesMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundPolicyDiffRulesMeterOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket incremented for different rules and priorities when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultiEniPolicyMeterOnePortTest(Vnet2VnetOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for multiple ENIs when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv4
    """

    policy_meter_class_1 = 1
    policy_meter_class_2 = 81
    policy_meter_class_3 = 96
    buckets_exp = {"policy1": {"oid": 0, "tx": 1, "rx": 0},
                   "policy2": {"oid": 0, "tx": 1, "rx": 0},
                   "policy3": {"oid": 0, "tx": 1, "rx": 0},}

    def setUp(self):
        super().setUp()
        self.tx_host_1 = self.tx_host

        self.tx_host_2 = self.define_neighbor_network(
            port=self.tx_host_1.port,
            mac=self.tx_host_1.mac,
            ip=self.tx_host_1.ip,
            ip_prefix=self.tx_host_1.ip_prefix,
            peer_port=self.tx_host_1.peer.port,
            peer_mac=self.tx_host_1.peer.mac,
            peer_ip=self.tx_host_1.peer.ip,
            client_mac="00:04:00:00:03:15",
            client_ip=self.tx_host_1.client.ip,
            client_vni=10)

        self.tx_host_3 = self.define_neighbor_network(
            port=self.tx_host_1.port,
            mac=self.tx_host_1.mac,
            ip=self.tx_host_1.ip,
            ip_prefix=self.tx_host_1.ip_prefix,
            peer_port=self.tx_host_1.peer.port,
            peer_mac=self.tx_host_1.peer.mac,
            peer_ip=self.tx_host_1.peer.ip,
            client_mac="00:04:00:00:03:17",
            client_ip=self.tx_host_1.client.ip,
            client_vni=100)

        self.rx_host_1 = self.rx_host

        self.rx_host_2 = self.define_neighbor_network(
            port=self.rx_host_1.port,
            mac=self.rx_host_1.mac,
            ip=self.rx_host_1.ip,
            ip_prefix=self.rx_host_1.ip_prefix,
            peer_port=self.rx_host_1.peer.port,
            peer_mac=self.rx_host_1.peer.mac,
            peer_ip=self.rx_host_1.peer.ip,
            client_mac="00:06:00:00:04:22",
            client_ip=self.rx_host_1.client.ip,
            client_vni=20)

        self.rx_host_3 = self.define_neighbor_network(
            port=self.rx_host_1.port,
            mac=self.rx_host_1.mac,
            ip=self.rx_host_1.ip,
            ip_prefix=self.rx_host_1.ip_prefix,
            peer_port=self.rx_host_1.peer.port,
            peer_mac=self.rx_host_1.peer.mac,
            peer_ip=self.rx_host_1.peer.ip,
            client_mac="00:06:00:00:04:24",
            client_ip=self.rx_host_1.client.ip,
            client_vni=200)

    def configure_metering(self):
        """
        Configure meter entities
        """

        self.meter_policy_1 = self.dash_meter_policy_create()
        self.meter_policy_2 = self.dash_meter_policy_create()
        self.meter_policy_3 = self.dash_meter_policy_create()

        self.src_vnet_1 = self.vnet_create(vni=self.tx_host_1.client.vni)
        self.src_vnet_2 = self.vnet_create(vni=self.tx_host_2.client.vni)
        self.src_vnet_3 = self.vnet_create(vni=self.tx_host_3.client.vni)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy_1)

        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host_1.ip),
            vm_vni=self.tx_host_1.client.vni,
            vnet_id=self.src_vnet_1,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy_2)

        self.eni_id_2 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host_2.ip),
            vm_vni=self.tx_host_2.client.vni,
            vnet_id=self.src_vnet_2,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(self.meter_policy_3)

        self.eni_id_3 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host_3.ip),
            vm_vni=self.tx_host_3.client.vni,
            vnet_id=self.src_vnet_3,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        print(f"Create policy meter class {self.policy_meter_class_1}")
        mask = 'ffff:f000::' if self.overlay_ipv6 else "255.255.255.0"
        self.dash_meter_rule_create(
            self.meter_policy_1, dip=self.rx_host_1.client.ip,
            dip_mask=mask, priority=20,
            meter_class=self.policy_meter_class_1)
        self.meter_bucket_policy_1 = self.dash_meter_bucket_create(
            self.eni_id_1, self.policy_meter_class_1)
        self.buckets_exp["policy1"]["oid"] = self.meter_bucket_policy_1

        print(f"Create policy meter class {self.policy_meter_class_2}")
        self.meter_policy_2 = self.dash_meter_policy_create()
        self.dash_meter_rule_create(
            self.meter_policy_2, dip=self.rx_host_2.client.ip,
            dip_mask=mask, priority=30,
            meter_class=self.policy_meter_class_2)
        self.meter_bucket_policy_2 = self.dash_meter_bucket_create(
            self.eni_id_2, self.policy_meter_class_2)
        self.buckets_exp["policy2"]["oid"] = self.meter_bucket_policy_2

        print(f"Create policy meter class {self.policy_meter_class_3}")
        self.meter_policy_3 = self.dash_meter_policy_create()
        self.dash_meter_rule_create(
            self.meter_policy_3, dip=self.rx_host_3.client.ip,
            dip_mask=mask, priority=40,
            meter_class=self.policy_meter_class_3)
        self.meter_bucket_policy_3 = self.dash_meter_bucket_create(
            self.eni_id_3, self.policy_meter_class_3)
        self.buckets_exp["policy3"]["oid"] = self.meter_bucket_policy_3

    def configure_overlay(self):
        """
        Configure outbound overlay
        """
        self.vip_create(self.tx_host.peer.ip)
        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host_1.client.vni)
        self.direction_lookup_create(self.tx_host_2.client.vni)
        self.direction_lookup_create(self.tx_host_3.client.vni)

        self.dst_vnet_1 = self.vnet_create(vni=self.rx_host_1.client.vni)
        self.dst_vnet_2 = self.vnet_create(vni=self.rx_host_2.client.vni)
        self.dst_vnet_3 = self.vnet_create(vni=self.rx_host_3.client.vni)

        self.eni_mac_map_create(self.eni_id_1, self.tx_host_1.client.mac)
        self.eni_mac_map_create(self.eni_id_2, self.tx_host_2.client.mac)
        self.eni_mac_map_create(self.eni_id_3, self.tx_host_3.client.mac)

        _, lpm = self.get_ip_lpm()
        self.outbound_routing_vnet_create(
            eni_id=self.eni_id_1, lpm=lpm,
            dst_vnet_id=self.dst_vnet_1)
        self.outbound_routing_vnet_create(
            eni_id=self.eni_id_2, lpm=lpm,
            dst_vnet_id=self.dst_vnet_2)
        self.outbound_routing_vnet_create(
            eni_id=self.eni_id_3, lpm=lpm,
            dst_vnet_id=self.dst_vnet_3)

        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet_1,
                                      dip=self.rx_host_1.client.ip,
                                      underlay_dip=self.rx_host_1.ip,
                                      overlay_dmac=self.rx_host_1.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet_2,
                                      dip=self.rx_host_2.client.ip,
                                      underlay_dip=self.rx_host_2.ip,
                                      overlay_dmac=self.rx_host_2.client.mac,
                                      use_dst_vnet_vni=True)
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet_3,
                                      dip=self.rx_host_3.client.ip,
                                      underlay_dip=self.rx_host_3.ip,
                                      overlay_dmac=self.rx_host_3.client.mac,
                                      use_dst_vnet_vni=True)

    def vnet2VnetOutboundMeterTest(self, tx_equal_to_rx):
        """
        Verify policy meter bucket is incremented
        """
        print(f"Running {self.__class__.__name__} ...")
        buckets_1 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        self.verify_traffic_scenario(client=self.tx_host_1, server=self.rx_host_1,
                                     connection=self.connection, fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)
        self.verify_traffic_scenario(client=self.tx_host_2, server=self.rx_host_2,
                                     connection=self.connection, fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)
        self.verify_traffic_scenario(client=self.tx_host_3, server=self.rx_host_3,
                                     connection=self.connection, fake_mac=True, 
                                     tx_equal_to_rx=tx_equal_to_rx)
        # Verify meter bucket
        buckets_2 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        for meter_name, meter_val in self.buckets_exp.items():
            meter_val["tx"] = len(self.send_pkt) if meter_val["tx"] > 0 else meter_val["tx"]
            meter_val["rx"] = len(self.send_pkt) if meter_val["rx"] > 0 else meter_val["rx"]
            print(f'Verify meter results for {meter_name}, expected:'
                  f' tx={meter_val["tx"]} rx={meter_val["rx"]}')
            self.verify_metering(buckets_1[meter_name], buckets_2[meter_name],
                                  meter_val["tx"], meter_val["rx"])

@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultiEniPolicyMeterOnePortOverlayIpv6Test(Vnet2VnetOutboundMultiEniPolicyMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for multiple ENIs when
    meter_policy_en=True and meter_class_override=False
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultiEniPolicyMeterTwoPortsTest(Vnet2VnetOutboundMultiEniPolicyMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented for multiple ENIs when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetOutboundMultiEniPolicyMeterTwoPortsOverlayIpv6Test(Vnet2VnetOutboundMultiEniPolicyMeterOnePortOverlayIpv6Test):
    """
    Verify outbound policy meter bucket incremented for multiple ENIs when
    meter_policy_en=True and meter_class_override=False
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetOutboundMeterTest(tx_equal_to_rx=False)


# Inbound tests
@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapMeterOnePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP
    One direction overlay IPv4
    """

    route_meter_class = randint(1, (1 << 15) - 1) 
    route_action = "decap"  # decap_validate
    # Tx/Rx value "1" is replaced with packet length in bytes
    buckets_exp = {"route": {"oid": 0, "tx": 0, "rx": 1}}

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, add_routes=False)
        self.vnet2VnetInboundMeterTest(tx_equal_to_rx=True)

    def configure_metering(self):
        """
        Configure meter entities
        """
        self.vip_create(self.tx_host.peer.ip)

        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.rx_host.client.vni)

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)
        self.dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.rx_host.ip),
            vm_vni=self.rx_host.client.vni,
            vnet_id=self.dst_vnet)

        print(f"Create router meter class {self.route_meter_class}")
        self.meter_bucket_route = self.dash_meter_bucket_create(
            self.eni_id_1, self.route_meter_class)
        self.buckets_exp["route"]["oid"] = self.meter_bucket_route

    def configure_overlay(self):
        """
        Configure outbound overlay
        """

        self.eni_mac_map_create(self.eni_id_1, self.rx_host.client.mac)  # ENI MAC

        if self.route_action == "decap":
            self.inbound_routing_decap_create(
                self.eni_id_1, vni=self.tx_host.client.vni,
                sip=self.tx_host.ip, sip_mask="255.255.255.0")
        else:  # self.route_action == "decap_validate":
            self.inbound_routing_decap_validate_create(
                self.eni_id_1, vni=self.tx_host.client.vni,
                sip=self.tx_host.ip, sip_mask="255.255.255.0",
                src_vnet_id=self.src_vnet)
            # PA validation entry with Permit action
            self.pa_validation_create(self.tx_host.ip, self.src_vnet)

    def verify_metering(self, bucket_1, bucket_2, tx_bytes, rx_bytes):
        """
        Verify meter results with packet sent
        """
        out_bytes = bucket_2["outbound_bytes_counter"] - bucket_1["outbound_bytes_counter"]
        in_bytes = bucket_2["inbound_bytes_counter"] - bucket_1["inbound_bytes_counter"]
        print(f'out_bytes: bucket#2={bucket_2["outbound_bytes_counter"]}'
              f' bucket#1={bucket_1["outbound_bytes_counter"]}')
        print(f'in_bytes: bucket#2={bucket_2["inbound_bytes_counter"]}'
              f' bucket#1={bucket_1["inbound_bytes_counter"]}')
        print(f'Difference: out_bytes={out_bytes} in_bytes={in_bytes}')

        self.assertEqual(out_bytes, tx_bytes)
        self.assertEqual(in_bytes, rx_bytes)

    def vnet2VnetInboundMeterTest(self, tx_equal_to_rx):
        """
        Verify default meter configuration
        """
        print(f"Running {self.__class__.__name__} ...")
        buckets_1 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=False,
                                     tx_equal_to_rx=tx_equal_to_rx)
        # Verify meter bucket
        buckets_2 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        for meter_name, meter_val in self.buckets_exp.items():
            if meter_name not in buckets_1 or meter_name not in buckets_2:
                continue
            meter_val["tx"] = len(self.send_pkt) if meter_val["tx"] > 0 else meter_val["tx"]
            meter_val["rx"] = len(self.send_pkt) if meter_val["rx"] > 0 else meter_val["rx"]
            print(f'Verify meter results for {meter_name}, expected:'
                  f' tx={meter_val["tx"]} rx={meter_val["rx"]}')
            self.verify_metering(buckets_1[meter_name], buckets_2[meter_name],
                                  meter_val["tx"], meter_val["rx"])


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapMeterOnePortIpv6Test(Vnet2VnetInboundRouteDecapMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapMeterTwoPortsTest(Vnet2VnetInboundRouteDecapMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapMeterTwoPortsIpv6Test(Vnet2VnetInboundRouteDecapMeterOnePortIpv6Test):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapValidateMeterOnePortTest(Vnet2VnetInboundRouteDecapMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP_VALIDATE
    One direction overlay IPv4
    """

    route_action = "decap_validate"


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapValidateMeterOnePortIpv6Test(Vnet2VnetInboundRouteDecapValidateMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP_VALIDATE
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapValidateMeterTwoPortsTest(Vnet2VnetInboundRouteDecapValidateMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP_VALIDATE
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteDecapValidatepMeterTwoPortsIpv6Test(Vnet2VnetInboundRouteDecapValidateMeterOnePortIpv6Test):
    """
    Verify inbound route meter bucket incremented when
    inbound routing action DECAP_VALIDATE
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundMeterTest(tx_equal_to_rx=False)


# Inbound/Outbound
@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortTest(VnetApiEndpoints, VnetTrafficMixin):
    """
    Verify inbound route meter bucket incremented when
    outbound meter_policy_en=False and meter_class_override=False
    One direction overlay IPv4
    """
    policy_meter_class = 0
    route_meter_class = randint(1, (1 << 15) - 1)
    map_meter_class = 0
    route_type = "vnet"  # vnet_direct, direct
    route_action = "decap"  # decap_validate
    # Tx/Rx value "1" is replaced with packet length in bytes
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0},
                   "route": {"oid": 0, "tx": 1, "rx": 1},
                   "map": {"oid": 0, "tx": 0, "rx": 0},}

    def get_ipv4_v6_policy_meter(self, meter_policy_oid):
        if self.overlay_ipv6:
            return None, meter_policy_oid
        else:  # IPv4 family
            return meter_policy_oid, None

    def get_ip_lpm(self):
        if self.overlay_ipv6:
            return "bbbb::bc", "bbbb::0/64"
        else:
            return "192.168.1.10", "192.168.1.0/24"

    def runTest(self):
        self.update_configuration_for_tx_equal_to_rx()
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, add_routes=False)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=True)

    def configure_metering(self):
        """
        Configure meter entities
        """

        self.src_vnet = self.vnet_create(vni=self.tx_host.client.vni)

        m_policy_oid = self.meter_policy if self.policy_meter_class > 0 else 0
        ipv4_m_policy, ipv6_m_policy = self.get_ipv4_v6_policy_meter(m_policy_oid)
        self.eni_id_1 = self.eni_create(
            admin_state=True,
            vm_underlay_dip=sai_ipaddress(self.tx_host.ip),
            vm_vni=self.tx_host.client.vni,
            vnet_id=self.src_vnet,
            v4_meter_policy_id=ipv4_m_policy,
            v6_meter_policy_id=ipv6_m_policy)

        mask = 'ffff:f000::' if self.overlay_ipv6 else "255.255.255.0"
        if self.policy_meter_class > 0:
            print(f"Create policy meter class {self.policy_meter_class}")
            self.meter_policy = self.dash_meter_policy_create()
            self.meter_rule = self.dash_meter_rule_create(
                self.meter_policy, dip=self.rx_host.client.ip,
                dip_mask=mask, priority=1,
                meter_class=self.policy_meter_class)
            self.meter_bucket_policy = self.dash_meter_bucket_create(
                self.eni_id_1, self.policy_meter_class)
            self.buckets_exp["policy"]["oid"] = self.meter_bucket_policy
        if self.route_meter_class > 0:
            print(f"Create router meter class {self.route_meter_class}")
            self.meter_bucket_route = self.dash_meter_bucket_create(
                self.eni_id_1, self.route_meter_class)
            self.buckets_exp["route"]["oid"] = self.meter_bucket_route
        if self.map_meter_class > 0:
            print(f"Create map meter class {self.map_meter_class}")
            self.meter_bucket_map = self.dash_meter_bucket_create(
                self.eni_id_1, self.map_meter_class)
            self.buckets_exp["map"]["oid"] = self.meter_bucket_map

    def configure_overlay(self):
        """
        Configure inbound/outbound overlay
        """
        self.vip_create(self.tx_host.peer.ip)
        # direction lookup VNI, reserved VNI assigned to the VM->Appliance
        self.direction_lookup_create(self.tx_host.client.vni)

        self.dst_vnet = self.vnet_create(vni=self.rx_host.client.vni)

        self.eni_mac_map_create(self.eni_id_1, self.tx_host.client.mac)  # ENI MAC

        overlay_ip, lpm = self.get_ip_lpm()
        mpolicy_en = True if self.route_meter_class > 0 else False
        if self.route_type == "vnet":
            self.outbound_routing_vnet_create(
                eni_id=self.eni_id_1, lpm=lpm,
                dst_vnet_id=self.dst_vnet, meter_policy_en=mpolicy_en,
                meter_class=self.route_meter_class)
        elif self.route_type == "vnet_direct":
            self.outbound_routing_vnet_direct_create(
                eni_id=self.eni_id_1, lpm=lpm,
                dst_vnet_id=self.dst_vnet, overlay_ip=overlay_ip,
                meter_policy_en=mpolicy_en, meter_class=self.route_meter_class)
        else:  # direct
            self.outbound_routing_direct_create(
                eni_id=self.eni_id_1, lpm=lpm,
                meter_policy_en=mpolicy_en, meter_class=self.route_meter_class)
            return  # No map for direct route

        use_dst_vnet_vni = True if self.route_type == "vnet" else False
        mpolicy_en = True if self.map_meter_class > 0 else False
        self.outbound_ca_to_pa_create(dst_vnet_id=self.dst_vnet,
                                      dip=self.rx_host.client.ip,
                                      underlay_dip=self.rx_host.ip,
                                      overlay_dmac=self.rx_host.client.mac,
                                      use_dst_vnet_vni=use_dst_vnet_vni,
                                      meter_class_override=mpolicy_en,
                                      meter_class=self.map_meter_class)

        if self.route_action == "decap":
            self.inbound_routing_decap_create(
                self.eni_id_1, vni=self.tx_host.client.vni,
                sip=self.tx_host.ip, sip_mask="255.255.255.0")
        else:  # self.route_action == "decap_validate":
            self.inbound_routing_decap_validate_create(
                self.eni_id_1, vni=self.tx_host.client.vni,
                sip=self.tx_host.ip, sip_mask="255.255.255.0",
                src_vnet_id=self.src_vnet)
            # PA validation entry with Permit action
            self.pa_validation_create(self.tx_host.ip, self.src_vnet)

    def verify_metering(self, bucket_1, bucket_2, tx_bytes, rx_bytes):
        """
        Verify meter results with packet sent
        """
        out_bytes = bucket_2["outbound_bytes_counter"] - bucket_1["outbound_bytes_counter"]
        in_bytes = bucket_2["inbound_bytes_counter"] - bucket_1["inbound_bytes_counter"]
        print(f'out_bytes: bucket#2={bucket_2["outbound_bytes_counter"]}'
              f' bucket#1={bucket_1["outbound_bytes_counter"]}')
        print(f'in_bytes: bucket#2={bucket_2["inbound_bytes_counter"]}'
              f' bucket#1={bucket_1["inbound_bytes_counter"]}')
        print(f'Difference: out_bytes={out_bytes} in_bytes={in_bytes}')

        self.assertEqual(out_bytes, tx_bytes)
        self.assertEqual(in_bytes, rx_bytes)

    def vnet2VnetInboundOutboundMeterTest(self, tx_equal_to_rx):
        """
        Verify default meter configuration, increment policy bucket
        """
        print(f"Running {self.__class__.__name__} ...")
        buckets_1 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        self.verify_traffic_scenario(client=self.tx_host, server=self.rx_host,
                                     connection=self.connection, fake_mac=True,
                                     tx_equal_to_rx=tx_equal_to_rx)
        # Verify meter bucket
        buckets_2 = {meter_name: self.dash_read_meter_bucket(meter_val["oid"])
                     for meter_name, meter_val in self.buckets_exp.items()
                     if meter_val["oid"] != 0}
        for meter_name, meter_val in self.buckets_exp.items():
            if meter_name not in buckets_1 or meter_name not in buckets_2:
                continue
            meter_val["tx"] = len(self.send_pkt) if meter_val["tx"] > 0 else meter_val["tx"]
            meter_val["rx"] = len(self.send_pkt) if meter_val["rx"] > 0 else meter_val["rx"]
            print(f'Verify meter results for {meter_name}, expected:'
                  f' tx={meter_val["tx"]} rx={meter_val["rx"]}')
            self.verify_metering(buckets_1[meter_name], buckets_2[meter_name],
                                  meter_val["tx"], meter_val["rx"])


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortIpv6Test(Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    outbound meter_policy_en=False and meter_class_override=False
    inbound routing action DECAP
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundVnetRouteMeterTwoPortsTest(Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortTest):
    """
    Verify inbound route meter bucket incremented when
    outbound meter_policy_en=False and meter_class_override=False
    inbound routing action DECAP
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundVnetRouteMeterTwoPortsIpv6Test(Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortIpv6Test):
    """
    Verify inbound route meter bucket incremented when
    outbound meter_policy_en=False and meter_class_override=False
    inbound routing action DECAP
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundMapMeterOnePortTest(Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    One direction overlay IPv4
    """

    policy_meter_class = 0
    route_meter_class = 0
    map_meter_class = randint(1, (1 << 15) - 1)
    buckets_exp = {"policy": {"oid": 0, "tx": 0, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 1},
                   "map": {"oid": 0, "tx": 1, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundMapMeterOnePortIpv6Test(Vnet2VnetInboundRouteOutboundMapMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundMapMeterTwoPortsTest(Vnet2VnetInboundRouteOutboundMapMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundMapMeterTwoPortsIpv6Test(Vnet2VnetInboundRouteOutboundMapMeterOnePortIpv6Test):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundPolicyMeterOnePortTest(Vnet2VnetInboundRouteOutboundVnetRouteMeterOnePortTest):
    """
    Verify outbound policy meter bucket incremented, map meter bucket not incremented when
    meter_policy_en=True and meter_class_override=False
    inbound routing action DECAP
    One direction overlay IPv4
    """

    policy_meter_class = 101
    route_meter_class = 0
    map_meter_class = 0
    buckets_exp = {"policy": {"oid": 0, "tx": 1, "rx": 0},
                   "route": {"oid": 0, "tx": 0, "rx": 1},
                   "map": {"oid": 0, "tx": 0, "rx": 0},}


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundPolicyMeterOnePortIpv6Test(Vnet2VnetInboundRouteOutboundPolicyMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    One direction overlay IPv6
    """

    def setUp(self):
        super().setUp(overlay_ipv6=True)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundPolicyMeterTwoPortsTest(Vnet2VnetInboundRouteOutboundPolicyMeterOnePortTest):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    Two directions overlay IPv4
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)


@group("draft")
@skipIf(test_param_get('target') == 'bmv2', "Blocked on BMv2 by Issue #236")
class Vnet2VnetInboundRouteOutboundPolicyMeterTwoPortsIpv6Test(Vnet2VnetInboundRouteOutboundPolicyMeterOnePortIpv6Test):
    """
    Verify outbound map meter bucket incremented when
    meter_policy_en=False and meter_class_override=True
    inbound routing action DECAP
    Two directions overlay IPv6
    """

    def runTest(self):
        self.configure_metering()
        self.configure_overlay()
        self.configure_underlay(self.tx_host, self.rx_host)
        self.vnet2VnetInboundOutboundMeterTest(tx_equal_to_rx=False)
