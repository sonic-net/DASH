import ipaddress
from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    prefixtag = []
    for eni_index in range(1, ENI_COUNT+1):
        IP_L = IP_L_START + (eni_index - 1) * IP_STEP4
        r_vpc = eni_index + ENI_L2R_STEP
        IP_R = IP_R_START + (eni_index - 1) * IP_STEP4
        prefixtag.append(
            {
                "PREFIX-TAG:VPC:%d" % eni_index: {
                    "prefix-tag-id": "%d" % eni_index,
                    "prefix-tag-number": eni_index,
                    "ip-prefixes-ipv4": [
                        "%s/32" % IP_L
                    ]
                },
            }
        )
        prefixtag.append(
            {
                "PREFIX-TAG:VPC:%d" % r_vpc: {
                    "prefix-tag-id": "%d" % r_vpc,
                    "prefix-tag-number": r_vpc,
                    "ip-prefixes-ipv4": [
                        "%s/9" % IP_R
                    ]
                },
            }
        )
    return {"prefix-tags": prefixtag}
