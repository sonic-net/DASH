import pytest
import snappi
import thrift
import sai_thrift

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from sai_thrift import sai_rpc
import sai_thrift.sai_adapter as adapter

THRIFT_PORT = 9092

class TestSaiThrift:

    def test_saithrift_session(self):
        self.transport = None
        self.createRpcClient()
        print ("test_saithrift_session")

    def createRpcClient(self):
        """
        Set up thrift client and contact RPC server
        """

        # if 'thrift_server' in self.test_params:
        #     server = self.test_params['thrift_server']
        # else:
        server = 'localhost'

        self.transport = TSocket.TSocket(server, THRIFT_PORT)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = sai_rpc.Client(self.protocol)
        self.transport.open()    
