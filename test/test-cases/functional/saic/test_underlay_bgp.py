import json
from pathlib import Path
from pprint import pprint
import time
import pytest
from test-cases.utils.snappi_utils import *

current_file_dir = Path(__file__).parent 

"""
This covers following scenario :

Test Underlay BGP Established between BMv2 and ixia-c

Topology Used :

       --------          -------          -------- 
      |        |        |       |        |        |
      |        |        |       |        |        |
      | IXIA-C |--------|  BMv2 |--------| IXIA-C |
      |        |        |       |        |        |
      |        |        |       |        |        |
       --------          -------          -------- 
       
"""

###############################################################
#                  Declaring Global variables
###############################################################

SPEED = "SPEED_100_GBPS"
BGP_TYPE = "ebgp"
NUMBER_OF_ROUTES = 10

###############################################################
#                  Start of the testcase
###############################################################
def test_underlay_bgp(confgen, dpu, dataplane):

    # declare result 
    result = True 

    # STEP1 : Configure DPU
    with (current_file_dir / 'config_underlay_bgp.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)
    result = [*dpu.process_commands(setup_commands)]
    print("\n======= SAI commands RETURN values =======")
    pprint(result)

    # STEP2 : Configure TGEN
    # configure L1 properties on configured ports
    dataplane.config_l1_properties(SPEED)
    
    ## Tx side 
    dataplane.configuration.devices.device(name='Topology 1')
    dataplane.configuration.devices.device(name='Topology 2')
    eth = dataplane.configuration.devices[0].ethernets.add()
    eth.port_name = dataplane.configuration.ports[0].name
    eth.name = 'Ethernet 1'
    eth.mac = "00:00:00:00:00:01"
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 1'
    ipv4.address = '220.0.1.2'
    ipv4.gateway = '220.0.1.1'
    ipv4.prefix = 24
    bgpv4 = dataplane.configuration.devices[0].bgp
    bgpv4.router_id = '220.0.1.1'
    bgpv4_int = bgpv4.ipv4_interfaces.add()
    bgpv4_int.ipv4_name = ipv4.name
    bgpv4_peer = bgpv4_int.peers.add()
    bgpv4_peer.name = 'BGP 1' 
    bgpv4_peer.as_type = BGP_TYPE
    bgpv4_peer.peer_address = '220.0.1.1'
    bgpv4_peer.as_number = 65001
    route_range = bgpv4_peer.v4_routes.add(name="Network_Group1") 
    route_range.addresses.add(address='221.0.1.1', prefix=32, count=NUMBER_OF_ROUTES)

    ## Rx side 
    eth = dataplane.configuration.devices[1].ethernets.add()
    eth.port_name = dataplane.configuration.ports[1].name
    eth.name = 'Ethernet 2'
    eth.mac = "00:00:00:00:00:02"
    ipv4 = eth.ipv4_addresses.add()
    ipv4.name = 'IPv4 2'
    ipv4.address = '220.0.2.2'
    ipv4.gateway = '220.0.2.1'
    ipv4.prefix = 24
    bgpv4 = dataplane.configuration.devices[1].bgp
    bgpv4.router_id = '220.0.1.1'
    bgpv4_int = bgpv4.ipv4_interfaces.add()
    bgpv4_int.ipv4_name = ipv4.name
    bgpv4_peer = bgpv4_int.peers.add()
    bgpv4_peer.name = 'BGP 2' 
    bgpv4_peer.as_type = BGP_TYPE
    bgpv4_peer.peer_address = '220.0.2.1'
    bgpv4_peer.as_number = 65002
    route_range = bgpv4_peer.v4_routes.add(name="Network_Group2") 
    route_range.addresses.add(address='221.0.2.1', prefix=32, count=NUMBER_OF_ROUTES)
    dataplane.set_config()

    # STEP3 : Verify BGP Neighbours Established 
    dataplane.start_protocols()
    result = check_bgp_neighborship_established(dataplane)
    
    # STEP4 : Cleanup DPU
    dataplane.tearDown()
    cleanup_commands = []
    for val in setup_commands:
        new_dict = {'name' : val['name'] ,'op': 'remove'}
        cleanup_commands.append(new_dict)

    result = [*dpu.process_commands(cleanup_commands)]
    print("\n======= SAI commands RETURN values =======")
    pprint(result)

    # STEP5 : Print Result of the test
    print("Final Result : {}".format(result))

    assert result == False, "Test underlay bgp FAILED!!"

