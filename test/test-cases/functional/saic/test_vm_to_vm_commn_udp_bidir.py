import json
from pathlib import Path
from pprint import pprint
import time
import pytest
from test-cases.utils.snappi_utils import *

current_file_dir = Path(__file__).parent

"""
This covers following scenario :

vnet to vnet communication with UDP traffic flow on bidirectional traffic :

Configure BMv2 as DPU 
Configure TGEN UDP traffic flow as one vnet to another vnet of two ixia-c ports
Verify Traffic flow between vnet to vnet through DPU  


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
TEST_TYPES = ["bidirection"]

SPEED = "SPEED_100_GBPS"
TOTALPACKETS = 5
PPS = 1
TRAFFIC_SLEEP_TIME = (TOTALPACKETS * PPS) + 2 
PACKET_LENGTH = 128
ENI_IP = "1.1.0.1"
NETWORK_IP1 = "1.128.0.1"
NETWORK_IP2 = "1.128.0.3"

DPU_VTEP_IP = "221.0.0.2"
ENI_VTEP_IP = "221.0.1.11"
NETWORK_VTEP_IP = "221.0.2.101"

OUTER_SRC_MAC = "80:09:02:01:00:01"
OUTER_DST_MAC = "c8:2c:2b:00:d1:30" #TODO learn MAC from DUT
INNER_SRC_MAC = "00:1A:C5:00:00:01"
INNER_DST_MAC = "00:1b:6e:00:00:01"
OUTER_SRC_MAC_F2 = "80:09:02:02:00:01"
OUTER_DST_MAC_F2 = "c8:2c:2b:00:d1:34"  

###############################################################
#                  Start of the testcase
###############################################################
@pytest.mark.parametrize('test_type',TEST_TYPES)       
def test_vm_to_vm_commn_udp_bidir(confgen, dpu, dataplane, test_type):
    # declare result 
    result = True 

    # STEP1 : Configure DPU
    with (current_file_dir / 'config_bidir_setup_commands.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)
    result = [*dpu.process_commands(setup_commands)]
    print("\n======= SAI commands RETURN values =======")
    pprint(result)

    # STEP2 : Configure TGEN
    # configure L1 properties on configured ports
    config_l1_properties(dataplane, SPEED)
    
    # Flow1 settings
    f1 = dataplane.configuration.flows.flow(name="ENI_TO_NETWORK")[-1]
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

    outer_eth1.src.value = OUTER_SRC_MAC
    outer_eth1.dst.value = OUTER_DST_MAC
    outer_eth1.ether_type.value = 2048

    ip1.src.value = ENI_VTEP_IP #ENI - VTEP
    ip1.dst.value = DPU_VTEP_IP #DPU - VTEP

    udp1.src_port.value = 11638
    udp1.dst_port.value = 4789

    #vxlan.flags.value = 
    vxlan1.vni.value = 11
    vxlan1.reserved0.value = 0
    vxlan1.reserved1.value = 0

    inner_eth1.src.value = INNER_SRC_MAC
    inner_eth1.dst.value = INNER_DST_MAC

    inner_ip1.src.value = ENI_IP   #ENI
    inner_ip1.dst.value = NETWORK_IP1  #world

    inner_udp1.src_port.value = 10000
    inner_udp1.dst_port.value = 20000

    # Flow2 settings
    f2 = dataplane.configuration.flows.flow(name="NETWORK_TO_ENI")[-1]
    f2.tx_rx.port.tx_name = dataplane.configuration.ports[1].name
    f2.tx_rx.port.rx_name = dataplane.configuration.ports[0].name
    f2.size.fixed = PACKET_LENGTH
    # send 1000 packets and stop
    f2.duration.fixed_packets.packets = TOTALPACKETS
    # send 1000 packets per second
    f2.rate.pps = PPS
    f2.metrics.enable = True

    outer_eth, ip, udp, vxlan, inner_eth, inner_ip , inner_udp= (
            f2.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
    )
    
    outer_eth.src.value = OUTER_SRC_MAC_F2
    outer_eth.dst.value = OUTER_DST_MAC_F2 #TODO learn MAC from DUT  
    outer_eth.ether_type.value = 2048

    ip.src.value = NETWORK_VTEP_IP
    ip.dst.value = DPU_VTEP_IP

    udp.src_port.value = 11638
    udp.dst_port.value = 4789

    #vxlan.flags.value = 
    vxlan.vni.value = 101
    vxlan.reserved0.value = 0
    vxlan.reserved1.value = 0

    inner_eth.src.value = INNER_DST_MAC
    inner_eth.dst.value = INNER_SRC_MAC

    inner_ip.src.value = NETWORK_IP1 #world
    inner_ip.dst.value = ENI_IP   # ENI

    inner_udp.src_port.value = 20000
    inner_udp.dst_port.value = 10000

    # Flow3 settings
    f3 = dataplane.configuration.flows.flow(name="ENI_TO_NETWORK2")[-1]
    f3.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
    f3.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
    f3.size.fixed = PACKET_LENGTH
    # send 1000 packets and stop
    f3.duration.fixed_packets.packets = TOTALPACKETS
    # send 1000 packets per second
    f3.rate.pps = PPS
    f3.metrics.enable = True

    outer_eth, ip, udp, vxlan, inner_eth, inner_ip , inner_udp= (
            f3.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
    )

    outer_eth.src.value = OUTER_SRC_MAC
    outer_eth.dst.value = OUTER_DST_MAC
    outer_eth.ether_type.value = 2048

    ip.src.value = ENI_VTEP_IP #ENI - VTEP
    ip.dst.value = DPU_VTEP_IP #DPU - VTEP

    udp.src_port.value = 11638
    udp.dst_port.value = 4789

    #vxlan.flags.value = 
    vxlan.vni.value = 11
    vxlan.reserved0.value = 0
    vxlan.reserved1.value = 0

    inner_eth.src.value = INNER_SRC_MAC
    inner_eth.dst.value = "00:1b:6e:00:00:03"

    
    inner_ip.src.value = ENI_IP    #ENI
    inner_ip.dst.value = NETWORK_IP2  #world

    inner_udp.src_port.value = 10000
    inner_udp.dst_port.value = 20000

    # Flow4 settings
    f4 = dataplane.configuration.flows.flow(name="NETWORK_TO_ENI2")[-1]
    f4.tx_rx.port.tx_name = dataplane.configuration.ports[1].name
    f4.tx_rx.port.rx_name = dataplane.configuration.ports[0].name
    f4.size.fixed = PACKET_LENGTH
    # send 1000 packets and stop
    f4.duration.fixed_packets.packets = TOTALPACKETS
    # send 100 packets per second
    f4.rate.pps = PPS
    f4.metrics.enable = True

    outer_eth, ip, udp, vxlan, inner_eth, inner_ip , inner_udp= (
            f4.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
    )
    
    outer_eth.src.value = OUTER_SRC_MAC_F2
    outer_eth.dst.value = OUTER_DST_MAC_F2 #TODO learn MAC from DUT  
    outer_eth.ether_type.value = 2048

    ip.src.value = NETWORK_VTEP_IP
    ip.dst.value = DPU_VTEP_IP

    udp.src_port.value = 11638
    udp.dst_port.value = 4789

    #vxlan.flags.value = 
    vxlan.vni.value = 101
    vxlan.reserved0.value = 0
    vxlan.reserved1.value = 0

    inner_eth.src.value = "00:1b:6e:00:00:03"
    inner_eth.dst.value = INNER_SRC_MAC

    inner_ip.src.value = NETWORK_IP2 #world
    inner_ip.dst.value = ENI_IP   # ENI

    inner_udp.src_port.value = 20000
    inner_udp.dst_port.value = 10000
    dataplane.set_config()

    # STEP3 : Verify Traffic
    start_traffic(dataplane, f1.name)
    start_traffic(dataplane, f3.name)
    time.sleep(0.5)
    start_traffic(dataplane, f2.name)
    start_traffic(dataplane, f4.name)
    time.sleep(TRAFFIC_SLEEP_TIME)            
    dataplane.stop_traffic()
    res1 = check_flow_tx_rx_frames_stats(dataplane, f1.name)
    res2 = check_flow_tx_rx_frames_stats(dataplane, f2.name)
    res3 = check_flow_tx_rx_frames_stats(dataplane, f3.name)
    res4 = check_flow_tx_rx_frames_stats(dataplane, f4.name)
    print("res1 and res2 and res3 and res4 is {} {} {} {}".format(res1, res2, res3, res4))
    if not (res1 and res2 and res3 and res4) :
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
    assert result == False, "Test Vm to Vm communication with UDP flow on {} flow traffic Failed!!".format(test_type)