import json
from pathlib import Path
from pprint import pprint

import pytest
import saichallenger.dataplane.snappi.snappi_traffic_utils as stu
from saichallenger.dataplane.ptf_testutils import (send_packet,
                                                   simple_udp_packet,
                                                   simple_vxlan_packet,
                                                   verify_no_other_packets,
                                                   verify_packet)

import dash_helper.vnet2vnet_helper as dh

current_file_dir = Path(__file__).parent

# Constants for scale VNET outbound routing configuration
NUMBER_OF_VIP = 1
NUMBER_OF_DLE = 2
NUMBER_OF_ENI = 2
NUMBER_OF_EAM = NUMBER_OF_ENI
NUMBER_OF_ORE = 2  # Per ENI
NUMBER_OF_OCPE = 2  # Per ORE
NUMBER_OF_VNET = NUMBER_OF_ENI + (NUMBER_OF_ORE * NUMBER_OF_ENI)  # So far per ORE, but may be different
NUMBER_OF_IN_ACL_GROUP = 10
NUMBER_OF_OUT_ACL_GROUP = 10


# Scaled configuration
# Pay attention to the 'count', 'start', 'step' keywords.
# See README.md for details.
TEST_VNET_OUTBOUND_CONFIG_SCALE = {

    'DASH_VIP': {
        'vpe': {
            'count': NUMBER_OF_VIP,
            'SWITCH_ID': '$SWITCH_ID',
            'IPV4': {
                'count': NUMBER_OF_VIP,
                'start': '172.16.1.100',
                'step': '0.1.0.0'
            }
        }
    },

    'DASH_DIRECTION_LOOKUP': {
        'dle': {
            'count': NUMBER_OF_DLE,
            'SWITCH_ID': '$SWITCH_ID',
            'VNI': {
                'count': NUMBER_OF_DLE,
                'start': 5000,
                'step': 1000
            },
            'ACTION': 'SET_OUTBOUND_DIRECTION'
        }
    },

    'DASH_ACL_GROUP': {
        'in_acl_group_id': {
            'count': NUMBER_OF_IN_ACL_GROUP,
            'ADDR_FAMILY': 'IPv4'
        },
        'out_acl_group_id': {
            'count': NUMBER_OF_OUT_ACL_GROUP,
            'ADDR_FAMILY': 'IPv4'
        }
    },

    'DASH_VNET': {
        'vnet': {
            'VNI': {
                'count': NUMBER_OF_VNET,
                'start': 1000,
                'step': 1000
            }
        }
    },

    'DASH_ENI': {
        'eni': {
            'count': NUMBER_OF_ENI,
            'ACL_GROUP': {
                'INBOUND': {
                    'STAGE1': {
                        'list': 'DASH_ACL_GROUP#in_acl_group_id#0'
                    },
                    'STAGE2': {
                        'list': 'DASH_ACL_GROUP#in_acl_group_id#0'
                    },
                    'STAGE3': {
                        'list': 'DASH_ACL_GROUP#in_acl_group_id#0'
                    },
                    'STAGE4': {
                        'list': 'DASH_ACL_GROUP#in_acl_group_id#0'
                    },
                    'STAGE5': {
                        'list': 'DASH_ACL_GROUP#in_acl_group_id#0'
                    }
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
            'VM_UNDERLAY_DIP': {
                'count': NUMBER_OF_ENI,
                'start': '172.16.1.1',
                'step': '0.0.1.0'
            },
            'VM_VNI': {
                'count': NUMBER_OF_ENI,
                'start': 9
            },
            'VNET_ID': {
                'count': NUMBER_OF_ENI,
                'start': '$vnet_#{4}'
            }
        }
    },

    'DASH_ENI_ETHER_ADDRESS_MAP': {
        'eam': {
            'count': NUMBER_OF_EAM,
            'SWITCH_ID': '$SWITCH_ID',
            'MAC': {
                'count': NUMBER_OF_EAM,
                'start': '00:CC:CC:CC:00:00',
                'step': "00:00:00:00:00:01"
            },
            'ENI_ID': {
                'count': NUMBER_OF_ENI,
                'start': '$eni_#{0}'
            }
        }
    },

    'DASH_OUTBOUND_ROUTING': {
        'ore': {
            'count': NUMBER_OF_ENI * NUMBER_OF_ORE,  # Full count: OREs per ENI and VNET
            'SWITCH_ID': '$SWITCH_ID',
            'ACTION': 'ROUTE_VNET',
            'DESTINATION': {
                'count': NUMBER_OF_ORE,
                'start': '10.1.1.0/31',
                'step': '0.0.0.2'
            },
            'ENI_ID': {
                'count': NUMBER_OF_ENI,
                'start': '$eni_#{0}',
                'delay': NUMBER_OF_ORE
            },
            'DST_VNET_ID': {
                'count': NUMBER_OF_VNET,
                'start': '$vnet_#{0}',
                'delay': NUMBER_OF_ORE
            }
        }
    },

    'DASH_OUTBOUND_CA_TO_PA': {
        'ocpe': {
            'count': (NUMBER_OF_ENI * NUMBER_OF_ORE) * NUMBER_OF_OCPE,  # 2 Per ORE
            'SWITCH_ID': '$SWITCH_ID',
            'DIP': {
                'count': NUMBER_OF_ORE * NUMBER_OF_OCPE,
                'start': '10.1.1.0',
                'step': '0.0.0.1'
            },
            'DST_VNET_ID': {
                'count': NUMBER_OF_VNET,
                'start': '$vnet_#{0}',
                'delay': NUMBER_OF_ORE
            },
            'UNDERLAY_DIP': {
                'count': NUMBER_OF_ENI * NUMBER_OF_ORE,
                'start': '172.16.1.20',
                'step': '0.0.1.0'
            },
            'OVERLAY_DMAC': {
                'count': NUMBER_OF_ENI * NUMBER_OF_ORE,
                'start': '00:DD:DD:DD:00:00'
            },
            'USE_DST_VNET_VNI': True
        }
    }
}


class TestSaiVnetOutbound:

    def test_create_vnet_config(self, confgen, dpu):
        """Generate and apply configuration"""

        # confgen.mergeParams(TEST_VNET_OUTBOUND_CONFIG_SCALE)
        # confgen.generate()
        # results = []
        # for item in confgen.items():
        #     pprint(item)
        #     results.append(dpu.command_processor.process_command(item))

        with (current_file_dir / 'vnet_outbound_setup_commands_scale.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        result = [*dpu.process_commands(setup_commands)]
        # print("\n======= SAI commands RETURN values =======")
        # for cmd, res in zip(setup_commands, result):
        #     print(cmd['name'], cmd['type'], res)

    @pytest.mark.snappi
    def test_run_traffic_check_fixed_packets(self, dpu, dataplane):
        """
        Test with the fixed number of packets to send.
        packets_per_flow=1 means that each possible packet path will be verified using a single packet.
        NOTE: This test does not verify the correctness of the packets transformation.
        """

        #Generate traffic configuration, apply it and run.
        dh.scale_vnet_outbound_flows(dataplane, TEST_VNET_OUTBOUND_CONFIG_SCALE,
                                     packets_per_flow=1, flow_duration=0, pps_per_flow=10)
        dataplane.set_config()
        dataplane.start_traffic()

        # The following function waits for expected counters and fail if no success during time out.
        stu.wait_for(lambda: dh.check_flows_all_packets_metrics(dataplane, dataplane.flows,
                                                                name="Custom flow group", show=True)[0],
                    "Test", timeout_seconds=5)

    @pytest.mark.snappi
    def test_run_traffic_check_fixed_duration(self, dpu, dataplane):
        """
        Test with the fixed traffic duration to send.
        flow_duration sets the total duration of traffic. Number of packets is limited by PPS.
        For the HW PPS may be omitted and then it will send traffic on a line rate.
        NOTE: This test does not verify the correctness of the packets transformation.
        """
        test_duration = 5
        dh.scale_vnet_outbound_flows(dataplane, TEST_VNET_OUTBOUND_CONFIG_SCALE,
                                     packets_per_flow=0, flow_duration=test_duration, pps_per_flow=5)
        dataplane.set_config()
        dataplane.start_traffic()
        stu.wait_for(lambda: dh.check_flows_all_seconds_metrics(dataplane, dataplane.flows,
                                                                name="Custom flow group", show=True)[0],
                    "Test", timeout_seconds=test_duration + 1)

    def test_remove_vnet_config(self, confgen, dpu, dataplane):
        """
        Generate and remove configuration
        We generate configuration on remove stage as well to avoid storing giant objects in memory.
        """

        # confgen.mergeParams(TEST_VNET_OUTBOUND_CONFIG_SCALE)
        # confgen.generate()
        # results = []
        # for item in confgen.items():
        #     item['op'] = 'remove'
        #     pprint(item)
        #     results.append(dpu.command_processor.process_command(item))

        with (current_file_dir / 'vnet_outbound_setup_commands_scale.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        cleanup_commands = []
        for cmd in reversed(setup_commands):
            cleanup_commands.append({'name': cmd['name'], 'op': 'remove'})

        result = [*dpu.process_commands(cleanup_commands)]
        # print("\n======= SAI commands RETURN values =======")
        # for cmd, res in zip(cleanup_commands, result):
        #     print(cmd['name'], res)
