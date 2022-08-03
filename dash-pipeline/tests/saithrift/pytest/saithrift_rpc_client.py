import pytest

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from sai_thrift import sai_rpc

THRIFT_PORT = 9092

class SaithriftRpcClient:
    def __init__(self, port=THRIFT_PORT, server = 'localhost'):
        self.transport = None
        self.port = port
        self.server = server
        self.createRpcClient()

    def createRpcClient(self):
        """
        Set up thrift client and contact RPC server
        """

        print ("making thrift connection to %s:%d" % (self.server, self.port))
        self.transport = TSocket.TSocket(self.server, THRIFT_PORT)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = sai_rpc.Client(self.protocol)
        self.transport.open()    
        print ("sai-thrift connection established with %s:%d" % (self.server, self.port))
       
