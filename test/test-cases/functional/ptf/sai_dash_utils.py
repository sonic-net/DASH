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
                                                 overlay_ip=sai_ipaddress(overlay_ip), counter_id=counter_id)
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
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT)
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
                                                 action=SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET)
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
                                                  overlay_dmac=overlay_dmac)
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

    def configure_underlay(self, neighbor1, neighbor2=None, add_routes=True):
        """
        Configure L3 underlay network based on neighbors network configuration
        """

        rif0 = self.router_interface_create(neighbor1.peer.port,
                                            src_mac=neighbor1.peer.mac)
        nhop1 = self.nexthop_create(rif0, neighbor1.ip)
        self.neighbor_create(rif0, neighbor1.ip, neighbor1.mac)

        if neighbor2 is not None:
            rif1 = self.router_interface_create(neighbor2.peer.port,
                                                src_mac=neighbor2.peer.mac)
            nhop2 = self.nexthop_create(rif1, neighbor2.ip)
            self.neighbor_create(rif1, neighbor2.ip, neighbor2.mac)

        if add_routes is True:
            self.route_create(neighbor1.ip_prefix, nhop1)
            if neighbor2 is not None:
                self.route_create(neighbor2.ip_prefix, nhop2)
