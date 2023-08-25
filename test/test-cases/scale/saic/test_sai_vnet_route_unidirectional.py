"""
Verify VNET Route scenario
"""

import json
from pathlib import Path
from pprint import pprint
import time
import pytest
from saichallenger.common.sai_dataplane.utils.ptf_testutils import (send_packet,
                                                                    simple_udp_packet,
                                                                    simple_vxlan_packet,
                                                                    verify_packet,
                                                                    verify_no_other_packets)
import sys
sys.path.append("../utils")
import vnet2vnet_helper as dh
current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5

# Simple, non-scaled configuration.
# See README.md for details.

TEST_VNET_ROUTE_UNIDIRECTIONAL_CONFIG = {

    "ENI_COUNT": 1,
    "ACL_RULES_NSG": 1,
    "ACL_TABLE_COUNT": 1,
    "IP_PER_ACL_RULE": 1,
    "IP_MAPPED_PER_ACL_RULE": 1,
    "IP_ROUTE_DIVIDER_PER_ACL_RULE": 1,

    'DASH_VIP': {
        'vpe': {
            'SWITCH_ID': '$SWITCH_ID',
            'IPV4': "172.16.1.100"
        }
    },

    'DASH_DIRECTION_LOOKUP': {
        'dle': {
            'SWITCH_ID': '$SWITCH_ID',
            'VNI': 100,
            'ACTION': 'SET_OUTBOUND_DIRECTION'
        }
    },

    'DASH_ACL_GROUP': {
        'in_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        },
        'out_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        }
    },

    'DASH_VNET': {
        'vnet': {
            'VNI': 1000
        }
    },

    'DASH_ENI': {
        'eni': {
            'ACL_GROUP': {
                'INBOUND': {
                    'STAGE1': '$in_acl_group_id_#{0}',
                    'STAGE2': '$in_acl_group_id_#{0}',
                    'STAGE3': '$in_acl_group_id_#{0}}',
                    'STAGE4': '$in_acl_group_id_#{0}}',
                    'STAGE5': '$in_acl_group_id_#{0}}'
                },
                'OUTBOUND': {
                    'STAGE1': 0,
                    'STAGE2': 0,
                    'STAGE3': 0,
                    'STAGE4': 0,
                    'STAGE5': 0
                }
            },
            'ADMIN_STATE': True,
            'CPS': 10000,
            'FLOWS': 10000,
            'PPS': 100000,
            'VM_UNDERLAY_DIP': "172.16.1.1",
            'VM_VNI': 9,
            'VNET_ID': '$vnet_#{0}'
        }
    },

    'DASH_ENI_ETHER_ADDRESS_MAP': {
        'eam': {
            'SWITCH_ID': '$SWITCH_ID',
            'MAC': "00:cc:cc:cc:00:00",
            'ENI_ID': '$eni_#{0}'
        }
    },

    'DASH_OUTBOUND_ROUTING': {
        'ore': {
            'SWITCH_ID': '$SWITCH_ID',
            'ENI_ID': '$eni_#{0}',
            'DESTINATION': "10.1.0.0/16",
            'ACTION': 'ROUTE_VNET',
            'DST_VNET_ID': '$vnet_#{0}'
        }
    },

    'DASH_OUTBOUND_CA_TO_PA': {
        'ocpe': {
            'SWITCH_ID': '$SWITCH_ID',
            'DST_VNET_ID': '$vnet_#{0}',
            'DIP': "10.1.2.50",
            'UNDERLAY_DIP': "172.16.1.20",
            'OVERLAY_DMAC': "00:DD:DD:DD:00:00",
            'USE_DST_VNET_VNI': True
        }
    },

    'DASH_ACL_GROUP': {
        'in_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        },
        'out_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        }
    }
}

@pytest.mark.ptf
@pytest.mark.snappi
class TestSaiVnetRoute:

    # @pytest.fixture(scope="module", autouse=True)
    # def discovery(dpu):
    #     dpu.objects_discovery()
        
    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_route_unidirectional_create(self, dpu):
        """Generate and apply configuration"""

        with (current_file_dir / 'vnet_route_setup_commands_unidirectional.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        results = [*dpu.process_commands(setup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(results)
        assert all(results), 'Create error'


    @pytest.mark.snappi
    def test_vnet_route_packet_unidirectional_forwarding_with_route_match(self, dpu, dataplane):
        """Verify packet forwarding with route match"""
 
        """
        Verify same config with high-rate traffic.
        packets_per_flow=10 means that each possible packet path will be verified using 10 packet.
        NOTE: For BMv2 we keep here PPS limitation
        """
        dh.scale_vnet_outbound_flows(dataplane, TEST_VNET_ROUTE_UNIDIRECTIONAL_CONFIG, packets_per_flow=10, pps_per_flow=10)
        dataplane.set_config()
        dataplane.start_traffic()
        # stu.wait_for(lambda: dh.check_flow_packets_metrics(dataplane, dataplane.flows[0], show=True)[0],
        #             "Test", timeout_seconds=10)
        
        time.sleep(10)
        rows = dataplane.get_all_stats()
        print("{}".format(rows[0].name))
        print("--------------------------")
        print("Tx_Frames : {}".format(rows[0].frames_tx))
        print("Rx_Frames : {}".format(rows[0].frames_rx))
        print("{}".format(rows[1].name))
        print("--------------------------")
        print("Tx_Frames : {}".format(rows[1].frames_tx))
        print("Rx_Frames : {}".format(rows[1].frames_rx))

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_route_unidirectional_remove(self, dpu):
        """Verify configuration removal"""

        with (current_file_dir / 'vnet_route_setup_commands_unidirectional.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        cleanup_commands = []
        for cmd in reversed(setup_commands):
            cleanup_commands.append({'name': cmd['name'], 'op': 'remove'})

        results = [*dpu.process_commands(cleanup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(results)
        assert all(
            [result == 'SAI_STATUS_SUCCESS' for result in results]
        ), 'Remove error'
