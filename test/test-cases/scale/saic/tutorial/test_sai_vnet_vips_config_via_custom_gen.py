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

def vip_generate(vip_start=1, a1=192, a2=192, b1=168, b2=168, c1=0, c2=0, d1=1, d2=1):
    """
    Return an sequence of vip dictionary entries with incrementing IP addresses.
    Uses generator (yield) technique. Only one element exists in memory at a time.
    A sequence is generated with least-significant IP address octets incrementing first,
    followed by successive outer octets. So, for the IP adddress A.B.C.D, D counts the quickest,
    A counts the slowest.
    vip_start - starting VIP number, successive entries will increment this by 1
    a1, a2 - starting, ending values (inclusive) for address octet "A" in the sequence A.B.C.D
    b1, b2 - starting, ending values (inclusive) for address octet "B" in the sequence A.B.C.D
    c1, c2 - starting, ending values (inclusive) for address octet "C" in the sequence A.B.C.D
    d1, d2 - starting, ending values (inclusive) for address octet "D" in the sequence A.B.C.D
    """
    v = vip_start
    for a in range (a1,a2+1):
        for b in range(b1, b2+1):
            for c in range(c1,c2+1):
                for d in range(d1,d2+1):
                    yield \
                    {
                        "name": "vip_entry#%d" % v,
                        "op": "create",
                        "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
                        "key": {
                        "switch_id": "$SWITCH_ID",
                        "vip": "%d.%d.%d.%d" % (a,b,c,d)
                        },
                        "attributes": [
                        "SAI_VIP_ENTRY_ATTR_ACTION",
                        "SAI_VIP_ENTRY_ACTION_ACCEPT"
                        ]
                    }
                    v+= 1
    return

# create 2x2x2x32 = 256 vips
def make_create_cmds(vip_start=1,a1=192, a2=193, b1=168, b2=169, c1=1,c2=2,d1=1,d2=32):
    """ Return a generator (iterable) of create commands
        Entries generated on the fly.
        vip_start - starting VIP number, successive entries will increment this by 1
        a1, a2 - starting, ending values (inclusive) for address octet "A" in the sequence A.B.C.D
        b1, b2 - starting, ending values (inclusive) for address octet "B" in the sequence A.B.C.D
        c1, c2 - starting, ending values (inclusive) for address octet "C" in the sequence A.B.C.D
        d1, d2 - starting, ending values (inclusive) for address octet "D" in the sequence A.B.C.D
    """
    return vip_generate(vip_start, a1, a2, b1, b2, c1,c2,d1,d2)

# remove 2x2x2x32 = 256 vips
def make_remove_cmds(vip_start=1,a1=192, a2=193, b1=168, b2=169, c1=1,c2=2,d1=1,d2=32):
    """ Return an array of remove commands
        Entries generated and modifed on the fly; added to array in memory; reversed; then returned.
        vip_start - starting VIP number, successive entries will increment this by 1
        a1, a2 - starting, ending values (inclusive) for address octet "A" in the sequence A.B.C.D
        b1, b2 - starting, ending values (inclusive) for address octet "B" in the sequence A.B.C.D
        c1, c2 - starting, ending values (inclusive) for address octet "C" in the sequence A.B.C.D
        d1, d2 - starting, ending values (inclusive) for address octet "D" in the sequence A.B.C.D
    """
    cleanup_commands = [{'name': cmd['name'], 'op': 'remove'} for cmd in make_create_cmds(vip_start, a1, a2, b1, b2, c1,c2,d1,d2)]
    for cmd in reversed(cleanup_commands):
        yield cmd
    return


class TestSaiDashVipsGenerator:
    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_many_vips_create_via_generator(self, dpu):
        """Verify VIP configuration create
        """
        results = [*dpu.process_commands( (make_create_cmds()) )]
        print("\n======= SAI commands RETURN values =======")
        pprint(results)
        assert (all(results), "Create error")

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_many_vips_remove_via_generator(self, dpu):
        """Verify VIP configuration removal
        """
        results = [*dpu.process_commands(make_remove_cmds())]
        print("\n======= SAI commands RETURN values =======")
        assert (all( [result == 0 for result in results]), "Remove error")
        pprint(results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DASH SAI Config Generator for vip table entries')
    parser.add_argument('-a', action='store_true', help='Generate ALL commands as JSON to stdout')
    parser.add_argument('-c', action='store_true', help='Generate CREATE commands as JSON to stdout')
    parser.add_argument('-r', action='store_true', help='Generate REMOVE commands as JSON to stdout')
    parser.add_argument('--vip-start', type=int, default=1, help='Starting vip number')
    parser.add_argument('-a1', type=int, default=192, help='Starting value for A in VIP ip address sequence A.B.C.D')
    parser.add_argument('-a2', type=int, default=192, help='Ending value for A in VIP ip address sequence A.B.C.D')
    parser.add_argument('-b1', type=int, default=168, help='Starting value for B in VIP ip address sequence A.B.C.D')
    parser.add_argument('-b2', type=int, default=168, help='Ending value for B in VIP ip address sequence A.B.C.D')
    parser.add_argument('-c1', type=int, default=0, help='Starting value for C in VIP ip address sequence A.B.C.D')
    parser.add_argument('-c2', type=int, default=0, help='Ending value for C in VIP ip address sequence A.B.C.D')
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
                                                            args.a1, args.a2,\
                                                            args.b1,args.b2,\
                                                            args.c1,args.c2,
                                                            args.d1,args.d2)],
                         indent=2))

    if args.a or args.r:
        print (json.dumps([item for item in make_remove_cmds(args.vip_start, \
                                                            args.a1, args.a2,\
                                                            args.b1,args.b2,\
                                                            args.c1,args.c2,
                                                            args.d1,args.d2)],
                         indent=2)) 

