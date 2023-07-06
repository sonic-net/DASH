import pytest
import snappi
from scapy.all import *

from sai_thrift.sai_headers import *
from sai_thrift.sai_adapter import *
from sai_thrift.ttypes  import *

@pytest.mark.saithrift
@pytest.mark.bmv2
@pytest.mark.vnet

def test_sai_thrift_create_eni(saithrift_client):
    
    switch_id = 0
    eth_addr = '\xaa\xcc\xcc\xcc\xcc\xcc'
    vni = 60
    eni = 7

    try:
        dle = sai_thrift_direction_lookup_entry_t(switch_id=switch_id, vni=vni)
        status = sai_thrift_create_direction_lookup_entry(saithrift_client, dle,
                            action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
        assert(status == SAI_STATUS_SUCCESS)
        
        in_acl_group_id = sai_thrift_create_dash_acl_group(saithrift_client,
                                                           ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        assert (in_acl_group_id != SAI_NULL_OBJECT_ID);
        out_acl_group_id = sai_thrift_create_dash_acl_group(saithrift_client,
                                                            ip_addr_family=SAI_IP_ADDR_FAMILY_IPV4)
        assert (out_acl_group_id != SAI_NULL_OBJECT_ID);

        vnet = sai_thrift_create_vnet(saithrift_client, vni=60)
        assert (vnet != SAI_NULL_OBJECT_ID);

        vm_underlay_dip = sai_thrift_ip_address_t(addr_family=SAI_IP_ADDR_FAMILY_IPV4,
                                                  addr=sai_thrift_ip_addr_t(ip4="172.16.3.1"))
        eni = sai_thrift_create_eni(saithrift_client, cps=10000,
                                    pps=100000, flows=100000,
                                    admin_state=True,
                                    vm_underlay_dip=vm_underlay_dip,
                                    vm_vni=9,
                                    vnet_id=vnet,
                                    v4_meter_policy_id = 0,
                                    v6_meter_policy_id = 0,
                                    inbound_v4_stage1_dash_acl_group_id = in_acl_group_id,
                                    inbound_v4_stage2_dash_acl_group_id = in_acl_group_id,
                                    inbound_v4_stage3_dash_acl_group_id = in_acl_group_id,
                                    inbound_v4_stage4_dash_acl_group_id = in_acl_group_id,
                                    inbound_v4_stage5_dash_acl_group_id = in_acl_group_id,
                                    outbound_v4_stage1_dash_acl_group_id = out_acl_group_id,
                                    outbound_v4_stage2_dash_acl_group_id = out_acl_group_id,
                                    outbound_v4_stage3_dash_acl_group_id = out_acl_group_id,
                                    outbound_v4_stage4_dash_acl_group_id = out_acl_group_id,
                                    outbound_v4_stage5_dash_acl_group_id = out_acl_group_id,
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
        assert (eni != SAI_NULL_OBJECT_ID);

        eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=switch_id, address = eth_addr)
        status = sai_thrift_create_eni_ether_address_map_entry(saithrift_client,
                                                    eni_ether_address_map_entry=eam,
                                                    eni_id=eni)
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
        print ("test_sai_thrift_create_eni OK")

        # Delete in reverse order
        status = sai_thrift_remove_eni_ether_address_map_entry(saithrift_client, eam)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_eni(saithrift_client, eni)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_vnet(saithrift_client, vnet)
        assert(status == SAI_STATUS_SUCCESS)                        

        status = sai_thrift_remove_dash_acl_group(saithrift_client, out_acl_group_id)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_dash_acl_group(saithrift_client, in_acl_group_id)
        assert(status == SAI_STATUS_SUCCESS)

        status = sai_thrift_remove_direction_lookup_entry(saithrift_client, dle)
        assert(status == SAI_STATUS_SUCCESS)                        
        
    except AssertionError as ae:
        # Delete entries which might be lingering from previous failures etc.; ignore failures here
        print ("Cleaning up after failure...")
        if "eam" in locals():
            sai_thrift_remove_eni_ether_address_map_entry(saithrift_client, eam)
        if "eni" in locals():
            sai_thrift_remove_eni(saithrift_client, eni)
        if "vnet" in locals():
            sai_thrift_remove_vnet(saithrift_client, vnet)
        if "out_acl_group_id" in locals():
            sai_thrift_remove_dash_acl_group(saithrift_client, out_acl_group_id)
        if "in_acl_group_id" in locals():
            sai_thrift_remove_dash_acl_group(saithrift_client, in_acl_group_id)
        if "dle" in locals():
            sai_thrift_remove_direction_lookup_entry(saithrift_client, dle)
        raise ae

    print ("test_sai_thrift_create_eni OK")
    
