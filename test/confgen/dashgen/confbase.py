import ipaddress
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime

import macaddress
from munch import DefaultMunch

from dashgen.dflt_params import *

ipp = ipaddress.ip_address
macM = macaddress.MAC


class ConfBase(ABC):

    def __init__(self, name='base', params={}):
        self.dictname = name
        self.dflt_params = deepcopy(dflt_params)
        self.cooked_params = {}
        self.mergeParams(params)
        self.numYields = 0

    def mergeParams(self, params):
        # Merge provided params into/onto defaults
        self.params_dict = deepcopy(self.dflt_params)
        self.params_dict.update(params)

        # make scalar attributes for speed & brevity (compared to dict)
        # https://stackoverflow.com/questions/1305532/how-to-convert-a-nested-python-dict-to-object
        self.cookParams()
        self.params = DefaultMunch.fromDict(self.params_dict)
        # print ('%s: self.params=' % self.dictname, self.params)
        self.cooked_params = DefaultMunch.fromDict(self.cooked_params_dict)
        # print ("cooked_params = ", self.cooked_params)

    def cookParams(self):
        self.cooked_params_dict = {}
        for ip in [
            'IP_STEP1',
            'IP_STEP2',
            'IP_STEP3',
            'IP_STEP4',
            'IP_STEPE'
        ]:
            self.cooked_params_dict[ip] = int(ipp(self.params_dict[ip]))
        for ip in [
            'IP_L_START',
            'IP_R_START',
            'PAL',
            'PAR'
        ]:
            self.cooked_params_dict[ip] = ipp(self.params_dict[ip])
        for mac in [
            'MAC_L_START',
            'MAC_R_START'
        ]:
            self.cooked_params_dict[mac] = macM(self.params_dict[mac])

    @abstractmethod
    def items(self):
        pass

    # expensive - runs generator
    def itemCount(self):
        return len(self.items())

    def itemsGenerated(self):
        """ Last count of # yields, reset each time at begining"""
        return self.num_yields

    def dictName(self):
        return self.dictname

    def toDict(self):
        return {self.dictname: list(self.items())}

    def getParams(self):
        return self.params_dict

    def getMeta(self, message=''):
        """Generate metadata. FOr reference, could also add e.g. data to help drive tests"""
        return {'meta': {
            'tstamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'msg': message,
            'params': self.getParams()
        }
        }

    def pretty(self):
        pprint.pprint(self.toDict())
