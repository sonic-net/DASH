#!/usr/bin/python3
#
# Pytest case which can be run as a normal pytest or as standalone executable, to dump generated configurations.
#
# PyTest:
# =======
# 
# Note, not all tests involve sending traffic, for example setup/teardown of DUT configurations,
# so PTF or snappi may not be relevant. Such cases are often marked for both dataplanes.
#
# run snappi-enabled tests using snappi dataplane (e.g. ixia-c pktgen):
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_snappi.json -m snappi <this-filename> 
# run PTF-enabled tests using snappi test fixture (e.g. ixia-c pktgen)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_snappi.json -m ptf <this-filename>
# run PTF-enabled tests using PTF dataplane (e.g. scapy)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_ptf.json -m ptf <this-filename>
#   
# NOT SUPPORTED: run snappi-capable tests using PTF dataplane (PTF can't support snappi at this writing)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_ptf.json -m snappi <this-filename>
#
# Standalone:
# <this-filename> -h  # Print help
# <this-filename> -a  # Dump create & remove SAI records as JSON to stdout
# <this-filename> -c  # Dump create SAI records as JSON to stdout
# <this-filename> -r  # Dump create SAI records as JSON to stdout
#
import json, argparse
from pathlib import Path
from pprint import pprint

import pytest
import saichallenger.common.sai_dataplane.snappi.snappi_traffic_utils as stu
import sys
sys.path.append("../utils")
import vnet2vnet_helper as dh

current_file_dir = Path(__file__).parent
import dpugen
from saigen.confbase import *
from saigen.confutils import *

# Constants for scale VNET outbound routing configuration
NUMBER_OF_VIP = 1
NUMBER_OF_DLE = 1
NUMBER_OF_ENI = 1
NUMBER_OF_EAM = NUMBER_OF_ENI
NUMBER_OF_ORE = 1  # Per ENI
NUMBER_OF_OCPE = 1  # Per ORE
NUMBER_OF_VNET = NUMBER_OF_ENI + (NUMBER_OF_ORE * NUMBER_OF_ENI)  # So far per ORE, but may be different
NUMBER_OF_IN_ACL_GROUP = 0
NUMBER_OF_OUT_ACL_GROUP = 0


# Scaled configuration
# Pay attention to the 'count', 'start', 'step' keywords.
# See README.md for details.
TEST_VNET_OUTBOUND_CONFIG_SCALE = {
    'DASH_VIP':                 {'vpe': {'count': NUMBER_OF_VIP,'SWITCH_ID': '$SWITCH_ID','IPV4': 	{'count': NUMBER_OF_VIP,'start': '221.0.0.2','step': '0.1.0.0'}}},
    'DASH_DIRECTION_LOOKUP':    {'dle': {'count': NUMBER_OF_DLE,'SWITCH_ID': '$SWITCH_ID','VNI': 	{'count': NUMBER_OF_DLE,'start': 5000,'step': 1000},'ACTION': 'SET_OUTBOUND_DIRECTION'}},
    'DASH_ACL_GROUP':           {'in_acl_group_id': {'count': NUMBER_OF_IN_ACL_GROUP,'ADDR_FAMILY': 'IPv4'},'out_acl_group_id': {'count': NUMBER_OF_OUT_ACL_GROUP,'ADDR_FAMILY': 'IPv4'}},
    'DASH_VNET':                {'vnet': {'VNI': {'count': NUMBER_OF_VNET,'start': 1000,'step': 1000}}},
    'DASH_ENI':            {
                                'name': 		{'substitution': {'base': 'eni#{0}','params': {0: {'start': 11,'step': 1,'count': NUMBER_OF_ENI,},},'count': NUMBER_OF_ENI,}},
                                'eni_id': 		{'increment': {'start': 11,'step': 1,'count': NUMBER_OF_ENI}},
                                'mac_address': 	{'increment': {'start': '00:1A:C5:00:00:01','step': '00:00:00:18:00:00','count': NUMBER_OF_ENI}},
                                'address': 		{'increment': {'start': '1.1.0.1','step': '1.0.0.0','count': NUMBER_OF_ENI}},
                                'underlay_ip': 	{'increment': {'start': '221.0.1.1','step': '0.0.1.0','count': NUMBER_OF_ENI}},
                                'vnet': 		{'substitution': {'base': 'vnet#{0}','params': {0: {'start': 1,'step': 1,'count': NUMBER_OF_ENI},},'count': NUMBER_OF_ENI}},
                                },
    'DASH_ENI_ETHER_ADDRESS_MAP': {'eam': {
                                             'count': NUMBER_OF_EAM,'SWITCH_ID': '$SWITCH_ID',
                                             'MAC': {'count': NUMBER_OF_EAM,'start': '00:1A:C5:00:00:01','step': "00:00:00:00:00:01"},
                                             'ENI_ID': {'count': NUMBER_OF_ENI,'start': '$eni_#{0}'}
                                }
                                },

    'DASH_OUTBOUND_ROUTING': {
        'ore': {
            'count': NUMBER_OF_ENI * NUMBER_OF_ORE,  # Full count: OREs per ENI and VNET
            'SWITCH_ID': '$SWITCH_ID',
            'ACTION': 'ROUTE_VNET',
            'DESTINATION': 	{'count': NUMBER_OF_ORE,'start': "1.128.0.1/9",'step': '0.0.0.2'},
            'ENI_ID': 		{'count': NUMBER_OF_ENI,'start': '$eni_#{0}','delay': NUMBER_OF_ORE},
            'DST_VNET_ID': 	{'count': NUMBER_OF_VNET,'start': '$vnet_#{0}','delay': NUMBER_OF_ORE}
        }
    },

    'DASH_OUTBOUND_CA_TO_PA': {
        'ocpe': {
            'count': (NUMBER_OF_ENI * NUMBER_OF_ORE) * NUMBER_OF_OCPE, 'SWITCH_ID': '$SWITCH_ID',  # 2 Per ORE
            'DIP': {'count': NUMBER_OF_ORE * NUMBER_OF_OCPE,'start': '1.128.0.1','step': '0.0.0.1'},
            'DST_VNET_ID': 	{'count': NUMBER_OF_VNET,'start': '$vnet_#{0}','delay': NUMBER_OF_ORE},
            'UNDERLAY_DIP': {'count': NUMBER_OF_ENI * NUMBER_OF_ORE,'start': '221.0.1.1','step': '0.0.1.0'},
            'OVERLAY_DMAC': {'count': NUMBER_OF_ENI * NUMBER_OF_ORE,'start': '00:1B:6E:00:00:01'},
            'USE_DST_VNET_VNI': True
        }
    }
}

def add_meter_attrs(attr_type, attrs, ext):
    i = 0
    for item in attrs:
        if item['type'] == attr_type:
            attrs[i]['attributes'].extend(ext)
        i += 1
    return attrs
class TestSaiVnetOutbound:
    def make_create_vnet_config(self):
        """ Generate a configuration
            returns iterator (generator) of SAI records
        """
        conf = dpugen.sai.SaiConfig()
        conf.mergeParams(TEST_VNET_OUTBOUND_CONFIG_SCALE)
        conf.generate()
        ret = add_meter_attrs('SAI_OBJECT_TYPE_ENI', conf.items(), ["SAI_ENI_ATTR_V4_METER_POLICY_ID", "0", "SAI_ENI_ATTR_V6_METER_POLICY_ID", "0"])

        ret = add_meter_attrs('SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY', ret, [ 'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS', '0',
                              'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS_OVERRIDE', 'True' ])

        ret = add_meter_attrs('SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY', ret, [ 'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_POLICY_EN', 'True',
                              'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS', '0' ])
        return ret

    def make_remove_vnet_config(self):
        """ Generate a configuration to remove entries
            returns iterator (generator) of SAI records
        """
        cleanup_commands = [{'name': cmd['name'], 'op': 'remove'} for cmd in self.make_create_vnet_config()]
        cleanup_commands = reversed(cleanup_commands)
        for cmd in cleanup_commands:
            yield cmd
        return

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_create_vnet_config(self, dpu):
        """Generate and apply configuration"""
        results = [*dpu.process_commands( (self.make_create_vnet_config()) )]

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

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_remove_vnet_config(self, dpu, dataplane):
        """
        Generate and remove configuration
        We generate configuration on remove stage as well to avoid storing giant objects in memory.
        """
        results = [*dpu.process_commands( (self.make_remove_vnet_config()) )]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DASH SAI Config Generator for vnet outbound')
    parser.add_argument('-a', action='store_true', help='Generate all SAI records as JSON to stdout')
    parser.add_argument('-c', action='store_true', help='Generate "create" SAI records as JSON to stdout')
    parser.add_argument('-r', action='store_true', help='Generate "remove"" SAI records as JSON to stdout')

    args = parser.parse_args()

    if not args.a and not args.c and not args.r:
        # must provide at least one flag
        print ("\n*** Please specify at least one option flag from [acr] to generate output ***\n", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.a or args.c:
        print(json.dumps([cmd for cmd in (TestSaiVnetOutbound().make_create_vnet_config())],
                         indent=2))

    if args.a or args.r:
        print(json.dumps([cmd for cmd in (TestSaiVnetOutbound().make_remove_vnet_config())],
                         indent=2))

