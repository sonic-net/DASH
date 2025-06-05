#!/usr/bin/python3

from dashgen.confbase import *
from dashgen.confutils import *
from copy import deepcopy
import sys
class AclGroups(ConfBase):

    def __init__(self, params={}):
        super().__init__('acl-groups', params)
    
    def items(self):
        self.numYields = 0
        print('  Generating %s...' % self.dictname, file=sys.stderr)
        p=self.params
        cp=self.cooked_params
        IP_STEP1=cp.IP_STEP1
        IP_STEP2=cp.IP_STEP2
        IP_STEP3=cp.IP_STEP3
        IP_STEP4=cp.IP_STEP4
        IP_STEPE=cp.IP_STEPE
        IP_R_START=cp.IP_R_START
        IP_L_START=cp.IP_L_START
        ACL_TABLE_COUNT=p.ACL_TABLE_COUNT
        ACL_RULES_NSG=p.ACL_RULES_NSG
        IP_PER_ACL_RULE=p.IP_PER_ACL_RULE
        
        for eni_index in range(1, p.ENI_COUNT + 1):
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
                    rule_id_a = table_id * 10 *ACL_RULES_NSG + ip_index
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
                self.numYields+=1
                yield acl_group

if __name__ == "__main__":
    conf=AclGroups()
    common_main(conf)