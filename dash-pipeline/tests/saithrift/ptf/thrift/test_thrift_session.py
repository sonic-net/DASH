from sai_thrift.sai_headers import *
from sai_base_test import *

class TestSaiThriftSession(SaiHelperSimplified):
    """ Test saithrift client connection only"""
    def setup(self):
        print ("setup()")

    def runTest(self):
        print ("TestSaiThriftSession OK")


    def teardown(self):
        print ("teardown()")

class TestSaiThriftSaiHelper(SaiHelperSimplified):
    """ Test saithrift client connection and basic SaiHelper intitialization"""
    def setup(self):
        print ("setup()")

    def runTest(self):
        print ("TestSaiThriftSaiHelper OK")

    def teardown(self):
        print ("teardown()")
