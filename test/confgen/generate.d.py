#!/usr/bin/python3

import dashgen
from dashgen.confbase import *
from dashgen.confutils import *

print('generating config')

parser = commonArgParser()
args = parser.parse_args()


class DashConfig(ConfBase):

    def __init__(self, params={}):
        super().__init__('dash-config', params)

    def generate(self):
        # Pass top-level params to sub-generrators.
        self.configs = [
            dashgen.enis.Enis(self.params_dict),
            dashgen.aclgroups.AclGroups(self.params_dict),
            dashgen.vpcs.Vpcs(self.params_dict),
            dashgen.vpcmappingtypes.VpcMappingTypes(self.params_dict),
            dashgen.vpcmappings.VpcMappings(self.params_dict),
            dashgen.routingappliances.RoutingAppliances(self.params_dict),
            dashgen.routetables.RouteTables(self.params_dict),
            dashgen.prefixtags.PrefixTags(self.params_dict),
        ]

    def toDict(self):
        return {x.dictName(): x.items() for x in self.configs}

    def items(self):
        return (c.items() for c in self.configs)


if __name__ == "__main__":
    conf = DashConfig()
    common_parse_args(conf)
    conf.generate()
    common_output(conf)
    print('done')
