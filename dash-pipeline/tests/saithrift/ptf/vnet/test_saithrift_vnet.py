import pytest
import snappi
import scapy

from sai_thrift.sai_headers import *
from sai_base_test import *
# TODO - when switch APIs implemented:
# class TestSaiThrift_create_eni(SaiHelper):

class TestSaiThrift_create_eni(ThriftInterfaceDataPlane):
    """ Test saithrift vnet outbound"""
    def setUp(self):
        super(TestSaiThrift_create_eni, self).setUp()
        self.switch_id = 0
        self.eth_addr = '\xaa\xcc\xcc\xcc\xcc\xcc'
        self.vni = 60
        self.eni = 7

        try:
            self.dle = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=self.vni)
            
            status = sai_thrift_create_direction_lookup_entry(self.client, self.dle,
                                action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
            assert(status == SAI_STATUS_SUCCESS)

            self.in_acl_group_id = sai_thrift_create_dash_acl_group(self.client,
                                                                    ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
            assert (self.in_acl_group_id != SAI_NULL_OBJECT_ID)
            self.out_acl_group_id = sai_thrift_create_dash_acl_group(self.client,
                                                                     ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
            assert (self.in_acl_group_id != SAI_NULL_OBJECT_ID)

            self.vnet = sai_thrift_create_vnet(self.client, vni=self.vni)
            assert (self.vnet != SAI_NULL_OBJECT_ID)

            vm_underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                                      addr=sai_thrift_ip_addr_t(ip4="172.16.3.1"))
            self.eni = sai_thrift_create_eni(self.client, cps=10000,
                                             pps=100000, flows=100000,
                                             admin_state=True,
                                             vm_underlay_dip=vm_underlay_dip,
                                             vm_vni=9,
                                             vnet_id=self.vnet,
                                             inbound_v4_stage1_dash_acl_group_id = self.in_acl_group_id,
                                             inbound_v4_stage2_dash_acl_group_id = self.in_acl_group_id,
                                             inbound_v4_stage3_dash_acl_group_id = self.in_acl_group_id,
                                             inbound_v4_stage4_dash_acl_group_id = self.in_acl_group_id,
                                             inbound_v4_stage5_dash_acl_group_id = self.in_acl_group_id,
                                             outbound_v4_stage1_dash_acl_group_id = self.out_acl_group_id,
                                             outbound_v4_stage2_dash_acl_group_id = self.out_acl_group_id,
                                             outbound_v4_stage3_dash_acl_group_id = self.out_acl_group_id,
                                             outbound_v4_stage4_dash_acl_group_id = self.out_acl_group_id,
                                             outbound_v4_stage5_dash_acl_group_id = self.out_acl_group_id,
                                             inbound_v6_stage1_dash_acl_group_id = 0,
                                             inbound_v6_stage2_dash_acl_group_id = 0,
                                             inbound_v6_stage3_dash_acl_group_id = 0,
                                             inbound_v6_stage4_dash_acl_group_id = 0,
                                             inbound_v6_stage5_dash_acl_group_id = 0,
                                             outbound_v6_stage1_dash_acl_group_id = 0,
                                             outbound_v6_stage2_dash_acl_group_id = 0,
                                             outbound_v6_stage3_dash_acl_group_id = 0,
                                             outbound_v6_stage4_dash_acl_group_id = 0,
                                             outbound_v6_stage5_dash_acl_group_id = 0)

            self.eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=self.switch_id, address = self.eth_addr)
            status = sai_thrift_create_eni_ether_address_map_entry(self.client,
                                                        eni_ether_address_map_entry=self.eam,
                                                        eni_id=self.eni)
            assert(status == SAI_STATUS_SUCCESS)

        except AssertionError as ae:
            # Delete entries which might be lingering from previous failures etc.; ignore failures here
            print ("Cleaning up after failure...")
            if hasattr(self, "eam"):
                sai_thrift_remove_eni_ether_address_map_entry(self.client, self.eam)
            if hasattr(self, "eni"):
                sai_thrift_remove_eni(self.client, self.eni)
            if hasattr(self, "vnet"):
                sai_thrift_remove_vnet(self.client, self.vnet)
            if hasattr(self, "out_acl_group_id") and self.out_acl_group_id != SAI_NULL_OBJECT_ID:
                sai_thrift_remove_dash_acl_group(self.client, self.out_acl_group_id)
            if hasattr(self, "in_acl_group_id") and self.in_acl_group_id != SAI_NULL_OBJECT_ID:
                sai_thrift_remove_dash_acl_group(self.client, self.in_acl_group_id)
            if hasattr(self, "dle"):
                sai_thrift_remove_direction_lookup_entry(self.client, self.dle)
            raise ae


    def runTest(self):
        # TODO form a packet related to dataplane config
        self.udp_pkt = simple_udp_packet()
        # TODO expected packet might be different
        self.udp_pkt_exp = self.udp_pkt
        print("\nSending packet...", self.udp_pkt.__repr__())
        send_packet(self, 0, self.udp_pkt)
        print("\nVerifying packet...", self.udp_pkt_exp.__repr__())
        verify_packet(self, self.udp_pkt_exp, 0)
        print ("test_sai_thrift_create_eni OK")

    def tearDown(self):

        # Delete in reverse order
        status = sai_thrift_remove_eni_ether_address_map_entry(self.client, self.eam)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_eni(self.client, self.eni)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_vnet(self.client, self.vnet)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_dash_acl_group(self.client, self.out_acl_group_id)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_dash_acl_group(self.client, self.in_acl_group_id)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_direction_lookup_entry(self.client, self.dle)
        assert(status == SAI_STATUS_SUCCESS)                        
    
