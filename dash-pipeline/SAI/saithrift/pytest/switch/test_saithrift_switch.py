import pytest
import snappi

from sai_thrift import sai_headers
import sai_thrift.sai_adapter as adapter
from saithrift_rpc_client import SaithriftRpcClient
       
@pytest.mark.saithrift
@pytest.mark.bmv2
def test_sai_thrift_get_switch_attribute(saithrift_client):
    attr = adapter.sai_thrift_get_switch_attribute(
        saithrift_client, number_of_active_ports=True)
    print ("switch_attributes = %s" % attr)
    print ("test_sai_thrift_get_switch_attribute OK")


