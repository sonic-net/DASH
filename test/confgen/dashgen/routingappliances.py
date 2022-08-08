from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    routing_appliances = []
    for eni_index in range(1, ENI_COUNT+1):
        IP_L = IP_L_START + (eni_index - 1) * IP_STEP4
        r_vpc = eni_index + ENI_L2R_STEP
        IP_R = IP_R_START + (eni_index - 1) * IP_STEP4
        routing_appliances.append(
            {
                "ROUTING-APPLIANCE:%d" % eni_index: {
                    "appliance-id": "appliance-%d" % eni_index,
                    "routing-appliance-id": eni_index,
                    "routing-appliance-addresses": [
                        "%s/32" % IP_L
                    ],
                    "encap-type": "vxlan",
                    "vni-key": eni_index
                },
            }
        )
        routing_appliances.append(
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
        )
    return {"routing-appliances": routing_appliances}
