import pytest
import snappi
import thrift

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from sai_thrift import sai_rpc
import sai_thrift.sai_adapter as adapter

THRIFT_PORT = 9092

class SaithriftClient:
    def __init__(self):
        self.transport = None
        self.createRpcClient()

    def createRpcClient(self):
        """
        Set up thrift client and contact RPC server
        """

        # if 'thrift_server' in self.test_params:
        #     server = self.test_params['thrift_server']
        # else:
        server = 'localhost'

        print ("making thrift connection to %s:%d" % (server, THRIFT_PORT))
        self.transport = TSocket.TSocket(server, THRIFT_PORT)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = sai_rpc.Client(self.protocol)
        self.transport.open()    
        print ("sai-thrift connection established")
       
class TestSaiThrift():
    def test_saithrift_session(self):
        client = SaithriftClient().client
        print ("test_saithrift_session OK")

    def test_sai_thrift_get_switch_attribute(self):
        client = SaithriftClient().client
        attr = adapter.sai_thrift_get_switch_attribute(
            client, number_of_active_ports=True)

