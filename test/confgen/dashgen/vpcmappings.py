from dashgen.variables import *
from copy import deepcopy


def generate():
    print('    ' + os.path.basename(__file__))
    vpc_mappings = []
    PAL = ipp("221.0.1.0")
    PAR = ipp("221.0.2.100")
    for eni_index in range(1, ENI_COUNT + 1):
        PAL = PAL + IP_STEP1
        PAR = PAR + IP_STEP1

        local_ip = IP_L_START + (eni_index - 1) * IP_STEP4
        local_mac = str(
            macaddress.MAC(
                int(MAC_L_START) +
                (eni_index - 1) * int(macaddress.MAC(ENI_MAC_STEP))
            )
        ).replace('-', ':')

        l_vpc_mapping = deepcopy(
            {
                "MAPPINGS:VPC:%d" % eni_index: {
                    "vpc-id": "vpc-%d" % eni_index,
                    "mappings": [
                        {
                            "routing-type": "vpc-direct",
                            "overlay-ip-address": "%s" % local_ip,
                            "underlay-ip-address": "%s" % PAL,
                            "mac": local_mac
                        }
                    ]
                },
            }
        )
        vpc_mappings.append(l_vpc_mapping)

        r_mappings = []
        r_mappings_append = r_mappings.append
        r_vpc = eni_index + ENI_L2R_STEP
        for table_index in range(1, (ACL_TABLE_COUNT*2+1)):
            for ip_index in range(1, (ACL_RULES_NSG+1)):
                remote_ip = IP_R_START + (eni_index - 1) * IP_STEP4 + (table_index - 1) * 4 * IP_STEP3 + (ip_index - 1) * IP_STEP2
                remote_mac = str(
                    macaddress.MAC(
                        int(macaddress.MAC('00:1B:6E:80:00:01')) +
                        (eni_index - 1) * int(macaddress.MAC(ENI_MAC_STEP)) +
                        (table_index - 1) * int(macaddress.MAC(ACL_TABLE_MAC_STEP)) +
                        (ip_index - 1) * int(macaddress.MAC(ACL_POLICY_MAC_STEP))
                    )
                ).replace('-', ':')

                for i in range(IP_MAPPED_PER_ACL_RULE):
                    remote_expanded_ip = remote_ip + i
                    remote_expanded_mac = str(
                        macaddress.MAC(
                            int(macaddress.MAC(remote_mac)) + i
                        )
                    ).replace('-', ':')
                    r_mappings_append(
                        {
                            "routing-type": "vpc-direct",
                            "overlay-ip-address": "%s" % remote_expanded_ip,
                            "underlay-ip-address": "%s" % PAR,
                            "mac": remote_expanded_mac
                        }
                    )

        r_vpc_mapping = deepcopy(
            {
                "MAPPINGS:VPC:%d" % r_vpc: {
                    "vpc-id": "vpc-%d" % r_vpc,
                    "mappings": r_mappings
                },
            }
        )

        vpc_mappings.append(r_vpc_mapping)
    return {'vpc-mappings': vpc_mappings}
