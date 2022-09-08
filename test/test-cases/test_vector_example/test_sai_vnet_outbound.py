import json
from pathlib import Path
from pprint import pprint

import pytest
from saichallenger.dataplane.ptf_testutils import (send_packet,
                                                   simple_udp_packet,
                                                   simple_vxlan_packet,
                                                   verify_packet)

current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5
OUTBOUND_VNI = 60
VNET_VNI = 100
VM_VNI = 9
ENI_MAC = "00:CC:CC:CC:CC:CC"
OUR_MAC = "00:00:02:03:04:05"
DST_CA_MAC = "00:DD:DD:DD:DD:DD"
VIP = "172.16.1.100"
OUTBOUND_VNI = 100
DST_CA_IP = "10.1.2.50"
DST_PA_IP = "172.16.1.20"
SRC_VM_PA_IP = "172.16.1.1"
CA_PREFIX = "10.1.0.0/16"

# Test Vector
TEST_VNET_OUTBOUND_CONFIG = {
    'DASH_VIP': [
        { 'vpe':
            { 'SWITCH_ID': '$SWITCH_ID',
              'IPv4': VIP }
        }
    ],

    'DASH_DIRECTION_LOOKUP': [
        { 'dle':
            { 'SWITCH_ID': '$SWITCH_ID',
              'VNI': OUTBOUND_VNI,
              'ACTION': 'SET_OUTBOUND_DIRECTION' }
        }
    ],

    'DASH_ACL_GROUP': [
        { 'in_acl_group_id':
            { 'ADDR_FAMILY': 'IPv4' }
        },
        { 'out_acl_group_id':
            { 'ADDR_FAMILY': 'IPv4' }
        }
    ],

    'DASH_VNET': [
        { 'vnet':
            { 'VNI': VNET_VNI }
        }
    ],

    'DASH_ENI': [
        { 'eni':
            {'ACL_GROUP': {
                'INBOUND': [{ 'STAGE1': 0 },
                            { 'STAGE2': 0 },
                            { 'STAGE3': 0 },
                            { 'STAGE4': 0 },
                            { 'STAGE5': 0 }
                            ],
                'OUTBOUND': [{ 'STAGE1': 0 },
                             { 'STAGE2': 0 },
                             { 'STAGE3': 0 },
                             { 'STAGE4': 0 },
                             { 'STAGE5': 0 }
                             ]
                            },
            'ADMIN_STATE': True,
            'CPS': 10000,
            'FLOWS': 10000,
            'PPS': 100000,
            'VM_UNDERLAY_DIP': SRC_VM_PA_IP,
            'VM_VNI': VM_VNI,
            'VNET_ID': '$vnet'}
        }
    ],

#    'DASH_ACL_RULE': [
#        { 'out_acl_rule_id':
#            { 'ACTION': 'PERMIT',
#              'DIP': DST_CA_IP,
#              'GID': '$out_acl_group_id',
#              'PRIORITY': 10 }
#        }
#    ],

    'DASH_ENI_ETHER_ADDRESS_MAP': [
        { 'eam':
            { 'SWITCH_ID': '$SWITCH_ID',
              'MAC': ENI_MAC,
              'ENI_ID': '$eni' }
        }
    ],

    'DASH_OUTBOUND_ROUTING': [
        { 'ore':
            { 'SWITCH_ID': '$SWITCH_ID',
              'ENI_ID': '$eni',
              'DESTINATION': CA_PREFIX,
              'ACTION': 'ROUTE_VNET',
              'DST_VNET_ID': '$vnet' }
        }
    ],

    'DASH_OUTBOUND_CA_TO_PA': [
        { 'ocpe':
            { 'SWITCH_ID': '$SWITCH_ID',
              'DST_VNET_ID': '$vnet',
              'DIP': DST_PA_IP,
              'UNDERLAY_DIP': DST_PA_IP,
              'OVERLAY_DMAC': DST_CA_MAC,
              'USE_DST_VNET_VNI': True }
        }
    ]
}


class TestSaiVnetOutbound:

    def test_create_vnet_config(self, confgen, dpu, dataplane):

        confgen.mergeParams(TEST_VNET_OUTBOUND_CONFIG)
        confgen.generate()
        for item in confgen.items():
            pprint(item)

        with (current_file_dir / 'test_vnet_outbound_setup_commands.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        result = [*dpu.process_commands(setup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(result)

    def test_run_traffic_check(self, dpu, dataplane):

        src_vm_ip = "10.1.1.10"
        outer_smac = "00:00:05:06:06:06"
        inner_smac = "00:00:04:06:06:06"

        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=ENI_MAC,
                                      ip_dst=DST_CA_IP,
                                      ip_src=src_vm_ip)
        vxlan_pkt = simple_vxlan_packet(eth_dst=OUR_MAC,
                                        eth_src=outer_smac,
                                        ip_dst=VIP,
                                        ip_src=SRC_VM_PA_IP,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=OUTBOUND_VNI,
                                        inner_frame=inner_pkt)

        inner_exp_pkt = simple_udp_packet(eth_dst=DST_CA_MAC,
                                      eth_src=ENI_MAC,
                                      ip_dst=DST_CA_IP,
                                      ip_src=src_vm_ip)
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst="00:00:00:00:00:00",
                                        eth_src="00:00:00:00:00:00",
                                        ip_dst=DST_PA_IP,
                                        ip_src=VIP,
                                        udp_sport=0, # TODO: Fix sport in pipeline
                                        with_udp_chksum=False,
                                        vxlan_vni=VNET_VNI,
                                        inner_frame=inner_exp_pkt)
        # TODO: Fix IP chksum
        vxlan_exp_pkt['IP'].chksum = 0
        # TODO: Fix UDP length
        vxlan_exp_pkt['IP']['UDP']['VXLAN'].flags = 0
        self.pkt_exp = vxlan_exp_pkt

        print("\nSending outbound packet...\n\n", vxlan_pkt.__repr__())
        send_packet(dataplane, 0, vxlan_pkt)

        print("\nVerifying packet...\n", self.pkt_exp.__repr__())
        verify_packet(dataplane, self.pkt_exp, 0)

        print ("test_sai_vnet_outbound OK")

    def test_remove_vnet_config(self, confgen, dpu, dataplane):

        confgen.mergeParams(TEST_VNET_OUTBOUND_CONFIG)
        confgen.generate()

        for item in confgen.items():
            item['OP'] = 'remove'
            pprint(item)

        with (current_file_dir / 'test_vnet_outbound_cleanup_commands.json').open(mode='r') as config_file:
            cleanup_commands = json.load(config_file)

        result = [*dpu.process_commands(cleanup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(result)
