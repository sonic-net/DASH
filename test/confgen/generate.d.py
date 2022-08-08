import io
import orjson
import dashgen


print('generating config')
enis = dashgen.enis.generate()
aclgroups = dashgen.aclgroups.generate()
vpc = dashgen.vpc.generate()
vpcmappingtypes = dashgen.vpcmappingtypes.generate()
vpcmappings = dashgen.vpcmappings.generate()
routingappliances = dashgen.routingappliances.generate()
routetables = dashgen.routetables.generate()
prefixtags = dashgen.prefixtags.generate()
config = {}
config.update(enis)
config.update(aclgroups)
config.update(vpc)
config.update(vpcmappingtypes)
config.update(vpcmappings)
config.update(routingappliances)
config.update(routetables)
config.update(prefixtags)

print('writing the config to file')
with io.open(r'dash_conf.json', 'wb') as jsonfile:
    jsonfile.write(orjson.dumps(config, option=orjson.OPT_INDENT_2))

print('done')
