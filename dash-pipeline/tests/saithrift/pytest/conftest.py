import pytest
from saithrift_rpc_client import SaithriftRpcClient

myclient = None
@pytest.fixture
def saithrift_client():   
    global myclient   
    print ("Called fixture saithrift_client()")
    if myclient is None: 
        myclient = SaithriftRpcClient().client
    return myclient


