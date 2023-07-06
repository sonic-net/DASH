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
import dpugen
from saigen.confbase import *
from saigen.confutils import *

current_file_dir = Path(__file__).parent

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

def add_meter_attrs(attr_type, attrs, ext):
    i = 0
    for item in attrs:
        if item['type'] == attr_type:
            attrs[i]['attributes'].extend(ext)
        i += 1
    return attrs
class TestSaiVnetOutbound:
    def make_create_commands(self):
        """ Generate a configuration
            returns iterator (generator) of SAI records
        """
        conf = dpugen.sai.SaiConfig()
        conf.generate()
        ret = add_meter_attrs('SAI_OBJECT_TYPE_ENI', conf.items(), ["SAI_ENI_ATTR_V4_METER_POLICY_ID", "0", "SAI_ENI_ATTR_V6_METER_POLICY_ID", "0"])

        ret = add_meter_attrs('SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY', ret, [ 'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS', '0',
                              'SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS_OVERRIDE', 'True' ])

        ret = add_meter_attrs('SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY', ret, [ 'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_POLICY_EN', 'True',
                              'SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS', '0' ])
        return ret

    def make_remove_commands(self):
        """ Generate a configuration to remove entries
            returns iterator (generator) of SAI records
        """
        cleanup_commands = [{'name': cmd['name'], 'op': 'remove'} for cmd in self.make_create_commands()]
        cleanup_commands = reversed(cleanup_commands)
        for cmd in cleanup_commands:
            yield cmd
        return

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_create_vnet_scale_config_generated(self, dpu):
        """Generate and apply configuration"""
        results = [*dpu.process_commands( (self.make_create_commands()) )]
        print("\n======= SAI commands RETURN values =======")
        pprint.pprint(results)


    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_remove_vnet_scale_config_generated(self, dpu):
        """
        Generate and remove configuration
        We generate configuration on remove stage as well to avoid storing giant objects in memory.
        """
        results = [*dpu.process_commands( (self.make_remove_commands()) )]
        print("\n======= SAI commands RETURN values =======")
        print(results)


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
        print(json.dumps([cmd for cmd in (TestSaiVnetOutbound().make_create_commands())],
                         indent=2))

    if args.a or args.r:
        print(json.dumps([cmd for cmd in (TestSaiVnetOutbound().make_remove_commands())],
                         indent=2))

