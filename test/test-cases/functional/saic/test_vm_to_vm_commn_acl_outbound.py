import json
from pathlib import Path
from pprint import pprint
import time
import pytest
from test-cases.utils.snappi_utils import *

current_file_dir = Path(__file__).parent

"""
This covers following scenario :

Test vnet to vnet communication with ACL on outbound direction:
1. Configure DPU to deny and allow traffic
2. Configure TGEN traffic flow as one vnet to another vnet of two ixia-c ports
3. Verify Traffic denied through deny traffic IPs

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
TEST_TYPES = ["outbound"]

SPEED = "SPEED_100_GBPS"
TOTALPACKETS = 5
PPS = 1
TRAFFIC_SLEEP_TIME = (TOTALPACKETS * PPS) + 2 
PACKET_LENGTH = 128
ENI_IP = "1.1.0.1"
NETWORK_IP2 = "1.128.0.2"
NETWORK_IP1 = "1.140.0.2"

DPU_VTEP_IP = "221.0.0.2"
ENI_VTEP_IP = "221.0.1.11"
NETWORK_VTEP_IP = "221.0.2.101"

###############################################################
#                  Start of the testcase
###############################################################

@pytest.mark.parametrize('test_type',TEST_TYPES)       
def test_vm_to_vm_commn_acl_outbound(confgen, dpu, dataplane, test_type):
    # declare result 
    result = True 

    # STEP1 : Configure DPU
    with (current_file_dir / 'config_outbound_setup_commands.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)
    result = [*dpu.process_commands(setup_commands)]
    print("\n======= SAI commands RETURN values =======")
    pprint(result)


    # STEP2 : Configure TGEN
    # configure L1 properties on configured ports
    config_l1_properties(dataplane, SPEED)
    
    # Flow1 settings
    f1 = dataplane.configuration.flows.flow(name="OUTBOUND")[-1]
    f1.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
    f1.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
    f1.size.fixed = PACKET_LENGTH
    # send 1000 packets and stop
    f1.duration.fixed_packets.packets = TOTALPACKETS
    # send 1000 packets per second
    f1.rate.pps = PPS
    f1.metrics.enable = True

    outer_eth1, ip1, udp1, vxlan1, inner_eth1, inner_ip1, inner_udp1= (
            f1.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
    )

    outer_eth1.src.value = "80:09:02:01:00:01"
    outer_eth1.dst.value = "c8:2c:2b:00:d1:30"
    outer_eth1.ether_type.value = 2048

    ip1.src.value = ENI_VTEP_IP #ENI - VTEP
    ip1.dst.value = DPU_VTEP_IP #DPU - VTEP

    udp1.src_port.value = 11638
    udp1.dst_port.value = 4789

    #vxlan.flags.value = 
    vxlan1.vni.value = 11
    vxlan1.reserved0.value = 0
    vxlan1.reserved1.value = 0

    inner_eth1.src.value = "00:1A:C5:00:00:01"
    #inner_eth1.dst.value = "00:1b:6e:00:00:02"
    inner_eth1.dst.value = "00:1b:6e:14:00:02"
    inner_ip1.src.value = ENI_IP   #ENI
    inner_ip1.dst.value = NETWORK_IP1  #world

    inner_udp1.src_port.value = 10000
    inner_udp1.dst_port.value = 20000

    dataplane.set_config()

    # STEP3 : Verify traffic
    start_traffic(dataplane, f1.name)
    time.sleep(10)            
    dataplane.stop_traffic()
    res1 = check_flow_tx_rx_frames_stats(dataplane, f1.name)
    print("res1 {}".format(res1))
    if (res1) :
        result = False        

    # STEP4 : Cleanup
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
    assert result == False, "Test Vm to Vm communication with ACL on {} flow traffic Failed!!".format(test_type)