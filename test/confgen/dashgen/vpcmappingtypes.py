from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    vpcmappingtypes = [
        "vpc",
        "privatelink",
        "privatelinknsg"
    ]

    return {"vpc-mappings-routing-types": vpcmappingtypes}
