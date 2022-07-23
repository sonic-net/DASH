import pytest
import snappi
import scapy

from sai_thrift.sai_headers import *
from sai_base_test import *
# TODO - when switch APIs implemented:
# class TestSaiThrift_create_outbound_eni_to_vni_entry(SaiHelper):

class TestSaiThrift_create_outbound_eni_to_vni_entry(ThriftInterfaceDataPlane):
    """ Test saithrift vnet outbound"""
    def setUp(self):
        super(TestSaiThrift_create_outbound_eni_to_vni_entry, self).setUp()
        self.switch_id = 0
        self.eth_addr = '\xaa\xcc\xcc\xcc\xcc\xcc'
        self.vni = 60
        self.eni = 7
        self.dle = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=self.vni)
        self.eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=self.switch_id, address = self.eth_addr)
        self.e2v = sai_thrift_outbound_eni_to_vni_entry_t(switch_id=self.switch_id, eni_id=self.eni)

        try:

            status = sai_thrift_create_direction_lookup_entry(self.client, self.dle,
                                action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
            assert(status == SAI_STATUS_SUCCESS)
            
            status = sai_thrift_create_eni_ether_address_map_entry(self.client,
                                                        eni_ether_address_map_entry=self.eam,
                                                        eni_id=self.eni)
            assert(status == SAI_STATUS_SUCCESS)

            status = sai_thrift_create_outbound_eni_to_vni_entry(self.client,
                                                                    outbound_eni_to_vni_entry=self.e2v,
                                                                    vni=self.vni)
            assert(status == SAI_STATUS_SUCCESS)     

        except AssertionError as ae:
            # Delete entries which might be lingering from previous failures etc.; ignore failures here
            print ("Cleaning up after failure...")
            sai_thrift_remove_outbound_eni_to_vni_entry(self.client, self.e2v)
            sai_thrift_remove_eni_ether_address_map_entry(self.client, self.eam)
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
        verify_packets(self, self.udp_pkt_exp, [0])
        print ("test_sai_thrift_create_outbound_eni_to_vni_entry OK")

    def tearDown(self):

        # Delete in reverse order
        status = sai_thrift_remove_outbound_eni_to_vni_entry(self.client, self.e2v)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_eni_ether_address_map_entry(self.client, self.eam)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_direction_lookup_entry(self.client, self.dle)
        assert(status == SAI_STATUS_SUCCESS)                        


    
