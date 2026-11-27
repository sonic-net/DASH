#!/usr/bin/python3

import sys

from dashgen.confbase import *
from dashgen.confutils import *


class Enis(ConfBase):

    def __init__(self, params={}):
        super().__init__('enis', params)

    def items(self):
        self.numYields = 0
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p = self.params
        cp = self.cooked_params
        for eni_index in range(1, p.ENI_COUNT+1):
            local_mac = str(macaddress.MAC(int(cp.MAC_L_START)+(eni_index - 1)*int(macaddress.MAC(p.ENI_MAC_STEP)))).replace('-', ':')

            acl_tables_in = []
            acl_tables_out = []

            for table_index in range(1, (p.ACL_TABLE_COUNT*2+1)):
                table_id = eni_index * 1000 + table_index

                stage = (table_index - 1) % 3 + 1
                if table_index < 4:
                    acl_tables_in.append(
                        {
                            "acl-group-id": "acl-group-%d" % table_id,
                            "stage": stage
                        }
                    )
                else:
                    acl_tables_out.append(
                        {
                            "acl-group-id": "acl-group-%d" % table_id,
                            "stage": stage
                        }
                    )

            self.numYields += 1
            yield {
                'ENI:%d' % eni_index: {
                    'eni-id': 'eni-%d' % eni_index,
                    'mac': local_mac,
                    'vpcs': [
                        eni_index
                    ],
                    "acls-v4-in": acl_tables_in,
                    "acls-v4-out": acl_tables_out,
                    "route-table-v4": "route-table-%d" % eni_index
                },
            }


if __name__ == "__main__":
    conf = Enis()
    common_main(conf)
