import pytest
       
from saithrift_rpc_client import SaithriftRpcClient

@pytest.mark.saithrift
@pytest.mark.bmv2
def test_saithrift_session(saithrift_client):
    """ Test saithrift client connection only"""
    print ("test_saithrift_session OK")
        

