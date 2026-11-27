#!/usr/bin/python3

import sys
from copy import deepcopy

from dashgen.confbase import *
from dashgen.confutils import *


class Vpcs(ConfBase):

    def __init__(self, params={}):
        super().__init__('vpc', params)

    def items(self):
        self.numYields = 0
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        IP_L_START = cp.IP_L_START
        IP_R_START = cp.IP_R_START
        IP_STEP4 = cp.IP_STEP4
        ENI_L2R_STEP = p.ENI_L2R_STEP
        ENI_COUNT = p.ENI_COUNT

        for eni_index in range(1, ENI_COUNT+1):
            IP_L = IP_L_START + (eni_index - 1) * IP_STEP4
            r_vpc = eni_index + ENI_L2R_STEP
            IP_R = IP_R_START + (eni_index - 1) * IP_STEP4
            self.numYields += 1
            yield {
                "VPC:%d" % eni_index: {
                    "vpc-id": "vpc-%d" % eni_index,
                    "vni-key": eni_index,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/32" % IP_L
                    ]
                },
            }

            self.numYields += 1
            yield {
                "VPC:%d" % r_vpc: {
                    "vpc-id": "vpc-%d" % r_vpc,
                    "vni-key": r_vpc,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/9" % IP_R
                    ]
                },
            }


if __name__ == "__main__":
    conf = Vpcs()
    common_main(conf)
