import pytest
import snappi

from sai_thrift.sai_headers import *
from sai_thrift.sai_adapter import *
from sai_thrift.ttypes  import *

@pytest.mark.saithrift
@pytest.mark.bmv2
@pytest.mark.vnet
def test_sai_thrift_create_outbound_eni_to_vni_entry(saithrift_client):
    dle = sai_thrift_direction_lookup_entry_t(switch_id=0, vni=60)
    sai_thrift_create_direction_lookup_entry(saithrift_client, dle,
                        action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
    print ("test_sai_thrift_create_outbound_eni_to_vni_entry OK")
        

