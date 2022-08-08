from copy import deepcopy
from dashgen.variables import *


def generate():
    print('    ' + os.path.basename(__file__))
    acl_groups = []
    for eni_index in range(1, ENI_COUNT + 1):
        local_ip = IP_L_START + (eni_index - 1) * IP_STEP4
        l_ip_ac = deepcopy(str(local_ip)+"/32")

        for table_index in range(1, (ACL_TABLE_COUNT*2+1)):
            table_id = eni_index * 1000 + table_index

            rules = []
            rappend = rules.append
            for ip_index in range(1, (ACL_RULES_NSG+1), 2):
                rule_id_a = table_id * 10 * ACL_RULES_NSG + ip_index
                remote_ip_a = IP_R_START + (eni_index - 1) * IP_STEP4 + (
                    table_index - 1) * 4 * IP_STEP3 + (ip_index - 1) * IP_STEP2

                ip_list_a = [str(remote_ip_a + expanded_index * IP_STEPE)+"/32" for expanded_index in range(0, IP_PER_ACL_RULE)]
                ip_list_a.append(l_ip_ac)

                rule_a = {
                    "priority": ip_index,
                    "action": "allow",
                    "terminating": False,
                    "src_addrs": ip_list_a[:],
                    "dst_addrs":  ip_list_a[:],
                }
                rappend(rule_a)
                rule_id_d = rule_id_a + 1
                remote_ip_d = remote_ip_a + IP_STEP1

                ip_list_d = [str(remote_ip_d + expanded_index * IP_STEPE)+"/32" for expanded_index in range(0, IP_PER_ACL_RULE)]
                ip_list_d.append(l_ip_ac)

                rule_d = {
                    "priority": ip_index+1,
                    "action": "deny",
                    "terminating": True,
                    "src_addrs": ip_list_d[:],
                    "dst_addrs":  ip_list_d[:],
                }
                rappend(rule_d)

            # add as last rule in last table from ingress and egress an allow rule for all the ip's from egress and ingress
            if ((table_index - 1) % 3) == 2:
                rule_id_a = table_id * 10 * ACL_RULES_NSG + ip_index
                all_ipsA = IP_R_START + (eni_index - 1) * IP_STEP4 + (table_index % 6) * 4 * IP_STEP3
                all_ipsB = all_ipsA + 1 * 4 * IP_STEP3
                all_ipsC = all_ipsA + 2 * 4 * IP_STEP3

                ip_list_all = [
                    l_ip_ac,
                    str(all_ipsA)+"/14",
                    str(all_ipsB)+"/14",
                    str(all_ipsC)+"/14",
                ]

                rule_allow_all = {
                    "priority": ip_index+2,
                    "action": "allow",
                    "terminating": "true",
                    "src_addrs": ip_list_all[:],
                    "dst_addrs":  ip_list_all[:],
                }
                rappend(rule_allow_all)

            acl_group = deepcopy(
                {
                    "ACL-GROUP:ENI:%d:TABLE:%d" % (eni_index, table_id): {
                        "acl-group-id": "acl-group-%d" % table_id,
                        "ip_version": "IPv4",
                        "rules": rules
                    }
                }
            )
            acl_groups.append(acl_group)

    return {"acl-groups": acl_groups}
