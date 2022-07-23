import pytest
import snappi
from scapy.all import *

from sai_thrift.sai_headers import *
from sai_thrift.sai_adapter import *
from sai_thrift.ttypes  import *

@pytest.mark.saithrift
@pytest.mark.bmv2
@pytest.mark.vnet

def test_sai_thrift_create_outbound_eni_to_vni_entry(saithrift_client):

    switch_id = 0
    eth_addr = '\xaa\xcc\xcc\xcc\xcc\xcc'
    vni = 60
    eni = 7

    try:
        dle = sai_thrift_direction_lookup_entry_t(switch_id=switch_id, vni=vni)
        eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=switch_id, address = eth_addr)
        e2v = sai_thrift_outbound_eni_to_vni_entry_t(switch_id=switch_id, eni_id=eni)

        status = sai_thrift_create_direction_lookup_entry(saithrift_client, dle,
                            action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
        assert(status == SAI_STATUS_SUCCESS)
        
        status = sai_thrift_create_eni_ether_address_map_entry(saithrift_client,
                                                    eni_ether_address_map_entry=eam,
                                                    eni_id=eni)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_create_outbound_eni_to_vni_entry(saithrift_client,
                                                                outbound_eni_to_vni_entry=e2v,
                                                                vni=vni)
        assert(status == SAI_STATUS_SUCCESS)     

        # TODO form a packet related to dataplane config

        # TODO this is using raw scapy; prefer to use snappi or a wrapper for scapy or snappi
        udp_pkt = Ether()/IP()/UDP()
        # TODO expected packet might be different
        udp_pkt_exp = udp_pkt
        print("\nSending packet...", udp_pkt.__repr__())
        sendp(udp_pkt, iface='veth0')

        # TODO need simple pkt verify for Pytest similar to PTF helper
        print("\nTODO: Verifying packet...", udp_pkt_exp.__repr__())
        # verify_packets(self, udp_pkt_exp, [0])
        print ("test_sai_thrift_create_outbound_eni_to_vni_entry OK")

        # Delete in reverse order

        status = sai_thrift_remove_outbound_eni_to_vni_entry(saithrift_client, e2v)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_eni_ether_address_map_entry(saithrift_client, eam)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_direction_lookup_entry(saithrift_client, dle)
        assert(status == SAI_STATUS_SUCCESS)                        
        
    except AssertionError as ae:
        # Delete entries which might be lingering from previous failures etc.; ignore failures here
        print ("Cleaning up after failure...")
        sai_thrift_remove_outbound_eni_to_vni_entry(saithrift_client, e2v)
        sai_thrift_remove_eni_ether_address_map_entry(saithrift_client, eam)
        sai_thrift_remove_direction_lookup_entry(saithrift_client, dle)
        raise ae

    print ("test_sai_thrift_create_outbound_eni_to_vni_entry OK")
    
