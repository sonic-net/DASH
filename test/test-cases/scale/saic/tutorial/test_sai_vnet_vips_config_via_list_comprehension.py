#!/usr/bin/python3
# Demonstration of how to generate many config objects with simple generator expressions
# Run as pytest or standalone script:
# - as a Pytest, run using the appropriate SAI Challenger setup file, e.g:
#      pytest -sv --setup ../sai_dpu_client_server_snappi.json .
#
# - in standalone mode, use to generate JSON to stdout, which can be saved to a file or pasted as literal
#    content into a test-case. Example:
#    python3 <this-filename> [options]  (use -h for help)

import json
import sys
from pprint import pprint
import argparse

import pytest

# Constants
SWITCH_ID = 5

# The array is expanded in-place by Python interpreter
# using "list comprehension." The entire array sits in memory.
# This is OK for smaller configs and simple loop expressions.
def vip_inflate(vip_start=1,d1=1,d2=1):
    """
    Return a populated array of vip dictionary entries 
    with IP address 192.168.0.[d1..d2] and incrementing vip sdtarting at vip_start
    """
    return [
        {
            "name": "vip_entry#%02d" % (x-d1+1),
            "op": "create",
            "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
            "key": {
            "switch_id": "$SWITCH_ID",
            "vip": "192.168.0.%d" % x
            },
            "attributes": [
            "SAI_VIP_ENTRY_ATTR_ACTION",
            "SAI_VIP_ENTRY_ACTION_ACCEPT"
            ]
        } for x in range (d1,d2+1)]


# create 16 vips
def make_create_cmds(vip_start=1,d1=1,d2=1):
    """ Return a generator (iterable) of create commands
        Entries generated on the fly.
        vip_start - starting VIP number, successive entries will increment this by 1
        d1, d2 - starting, ending values (inclusive) for address octet "D" in the sequence A.B.C.D
    """
    return vip_inflate(vip_start, d1,d2)

# remove 16 vips
def make_remove_cmds(vip_start=1,d1=1,d2=1):
    """ Return an array of remove commands
        Entries generated via list comprehension; added to array in memory; reversed; then returned.
        vip_start - starting VIP number, successive entries will increment this by 1
        d1, d2 - starting, ending values (inclusive) for address octet "D" in the sequence A.B.C.D
    """
    cleanup_commands = [{'name': vip['name'], 'op': 'remove'} for vip in make_create_cmds(vip_start, d1,d2)]
    return reversed(cleanup_commands)

class TestSaiDashVipsListComprehension:
    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_many_vips_create_via_list_comprehension(self, dpu):
        """Verify VIP configuration create
        """
        result = [*dpu.process_commands( (make_create_cmds()) )]
        print("\n======= SAI commands RETURN values =======")
        pprint(result)

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_many_vips_remove_via_list_comprehension(self, dpu):
        """Verify VIP configuration removal
        """
        result = [*dpu.process_commands(make_remove_cmds())]
        # print("\n======= SAI commands RETURN values =======")
        # pprint(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DASH SAI Config Generator for vip table entries')
    parser.add_argument('-a', action='store_true', help='Generate ALL commands as JSON to stdout')
    parser.add_argument('-c', action='store_true', help='Generate CREATE commands as JSON to stdout')
    parser.add_argument('-r', action='store_true', help='Generate REMOVE commands as JSON to stdout')
    parser.add_argument('--vip-start', type=int, default=1, help='Starting vip number')
    parser.add_argument('-d1', type=int, default=1, help='Starting value for D in VIP ip address sequence A.B.C.D')
    parser.add_argument('-d2', type=int, default=1, help='Ending value for D in VIP ip address sequence A.B.C.D')

    args = parser.parse_args()

    if not args.a and not args.c and not args.r:
        # must provide at least one flag
        print ("\n*** Please specify at least one option flag from [acr] to generate output ***\n", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.a or args.c:
        print(json.dumps([item for item in make_create_cmds(args.vip_start, \
                                                            args.d1,args.d2)],
                         indent=2))

    if args.a or args.r:
        print (json.dumps([item for item in make_remove_cmds(args.vip_start, \
                                                            args.d1,args.d2)],
                         indent=2)) 

