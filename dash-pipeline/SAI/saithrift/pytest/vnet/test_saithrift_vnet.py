import pytest
import snappi

from sai_thrift import sai_headers
import sai_thrift.sai_adapter as adapter
from saithrift_rpc_client import SaithriftRpcClient

@pytest.mark.saithrift
@pytest.mark.bmv2
@pytest.mark.vnet
def test_sai_thrift_create_outbound_eni_to_vni_entry(saithrift_client):
    dle = sai_headers.sai_direction_lookup_entry_t(switch_id=0, vni=60)
    adapter.sai_thrift_create_direction_lookup_entry(saithrift_client, dle,
                        action=sai_headers.SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)  #SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION
    print ("test_sai_thrift_get_switch_attribute OK")
        

