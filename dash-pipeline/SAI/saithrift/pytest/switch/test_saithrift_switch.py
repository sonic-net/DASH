import pytest

from sai_thrift.sai_headers import *
from sai_thrift.sai_adapter import *
from sai_thrift.ttypes  import *
       
@pytest.mark.saithrift
@pytest.mark.bmv2
def test_sai_thrift_get_switch_attribute(saithrift_client):
    attr = sai_thrift_get_switch_attribute(
        saithrift_client, number_of_active_ports=True)
    print ("switch_attributes = %s" % attr)
    print ("test_sai_thrift_get_switch_attribute OK")


