import inspect
from pprint import pprint as pp


class SkuTest:
    def __init__(self, *args, **kwargs):
        print("*"*20+"SkuTest"+"*"*20)
        self.ip = kwargs['stateless'][0]['dpu'][0]['interfaces'][0][0]
        self.user = kwargs["CR"][self.ip]['user']
        self.password = kwargs["CR"][self.ip]['password']
        print("SN Ip", self.ip)
        print("SN User", self.user)
        print("SN Password", self.password)

    def configure_target(self, test_data):
        print("Configuring Target with Test Data")
        pp(test_data)
