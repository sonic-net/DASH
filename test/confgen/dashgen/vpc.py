from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    vpcs = []
    for eni_index in range(1, ENI_COUNT+1):
        IP_L = IP_L_START + (eni_index - 1) * IP_STEP4
        r_vpc = eni_index + ENI_L2R_STEP
        IP_R = IP_R_START + (eni_index - 1) * IP_STEP4
        vpcs.append(
            {
                "VPC:%d" % eni_index: {
                    "vpc-id": "vpc-%d" % eni_index,
                    "vni-key": eni_index,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/32" % IP_L
                    ]
                },
            }
        )
        vpcs.append(
            {
                "VPC:%d" % r_vpc: {
                    "vpc-id": "vpc-%d" % r_vpc,
                    "vni-key": r_vpc,
                    "encap": "vxlan",
                    "address_spaces": [
                        "%s/9" % IP_R
                    ]
                },
            }
        )
    return {"vpc": vpcs}
