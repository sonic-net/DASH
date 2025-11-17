#!/usr/bin/python3

import sys
from copy import deepcopy

from dashgen.confbase import *
from dashgen.confutils import *


class RoutingAppliances(ConfBase):

    def __init__(self, params={}):
        super().__init__('routing-appliances', params)

    def items(self):
        self.numYields = 0
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        # optimizations:
        IP_STEP4 = cp.IP_STEP4
        IP_R_START = cp.IP_R_START
        IP_L_START = cp.IP_L_START
        ENI_COUNT = p.ENI_COUNT
        ENI_L2R_STEP = p.ENI_L2R_STEP

        for eni_index in range(1, ENI_COUNT+1):
            IP_L = IP_L_START + (eni_index - 1) * IP_STEP4
            r_vpc = eni_index + ENI_L2R_STEP
            IP_R = IP_R_START + (eni_index - 1) * IP_STEP4
            self.numYields += 1
            yield \
                {
                    "ROUTING-APPLIANCE:%d" % eni_index: {
                        "appliance-id": "appliance-%d" % eni_index,
                        "routing-appliance-id": eni_index,
                        "routing-appliance-addresses": [
                            "%s/32" % IP_L
                        ],
                        "encap-type": "vxlan",
                        "vni-key": eni_index
                    }
                }

            self.numYields += 1
            yield \
                {
                    "ROUTING-APPLIANCE:%d" % r_vpc: {
                        "appliance-id": "appliance-%d" % r_vpc,
                        "routing-appliance-id": r_vpc,
                        "routing-appliance-addresses": [
                            "%s/9" % IP_R
                        ],
                        "encap-type": "vxlan",
                        "vni-key": r_vpc
                    },
                }


if __name__ == "__main__":
    conf = RoutingAppliances()
    common_main(conf)
