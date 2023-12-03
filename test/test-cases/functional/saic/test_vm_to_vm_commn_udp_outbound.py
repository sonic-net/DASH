import json
from pathlib import Path
from pprint import pprint
import time
import pytest
import sys
sys.path.append("../utils")
import snappi_utils as su

current_file_dir = Path(__file__).parent

"""
This covers following scenario :

vnet to vnet communication with UDP traffic flow :

Configure DUT 
Configure TGEN UDP traffic flow as one vnet to another vnet of two OpenTrafficGenerator ports
Verify Traffic flow between vnet to vnet through DUT  


Topology Used :

       --------          -------          -------- 
      |        |        |       |        |        |
      |        |        |       |        |        |
      |  TGEN  |--------|  DUT  |--------|  TGEN  |
      |        |        |       |        |        |
      |        |        |       |        |        |
       --------          -------          -------- 
       
"""

###############################################################
#                  Declaring Global variables
###############################################################

TOTALPACKETS = 1000
PPS = 100
TRAFFIC_SLEEP_TIME = (TOTALPACKETS / PPS) + 2 
PACKET_LENGTH = 128
ENI_IP = "1.1.0.1"
NETWORK_IP1 = "1.128.0.1"
NETWORK_IP2 = "1.128.0.3"
DPU_VTEP_IP = "221.0.0.2"
ENI_VTEP_IP = "221.0.1.11"
NETWORK_VTEP_IP = "221.0.2.101"

OUTER_SRC_MAC = "80:09:02:01:00:01"
OUTER_DST_MAC = "c8:2c:2b:00:d1:30" 
INNER_SRC_MAC = "00:1A:C5:00:00:01"
INNER_DST_MAC = "00:1b:6e:00:00:01"
OUTER_SRC_MAC_F2 = "80:09:02:02:00:01"
OUTER_DST_MAC_F2 = "c8:2c:2b:00:d1:34"  

###############################################################
#                  Start of the testcase
###############################################################

class TestUdpOutbound:

    @pytest.fixture(scope="class")
    def setup_config(self):
        """
        Fixture returns the content of the file with SAI configuration commands.
        scope=class - The file is loaded once for the whole test class
        """
        current_file_dir = Path(__file__).parent
        with (current_file_dir / 'config_outbound_setup_commands.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        return setup_commands

    @pytest.mark.dependency()
    def test_setup(self, dpu, setup_config):
        results = [*dpu.process_commands(setup_config)]
        print("\n======= SAI setup commands RETURN values =======")
        pprint(results)
               
    @pytest.mark.dependency(depends=['TestUdpOutbound::test_setup'])
    @pytest.mark.xfail(reason="https://github.com/sonic-net/DASH/issues/236")
    def test_vm_to_vm_commn_udp_outbound(self, dataplane):
        # Configure TGEN
        
        # Flow1 settings
        f1 = dataplane.configuration.flows.flow(name="ENI_TO_NETWORK")[-1]
        f1.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
        f1.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
        f1.size.fixed = PACKET_LENGTH
        # send n packets and stop
        f1.duration.fixed_packets.packets = TOTALPACKETS
        # send n packets per second
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
        # send n packets and stop
        f2.duration.fixed_packets.packets = TOTALPACKETS
        # send n packets per second
        f2.rate.pps = PPS
        f2.metrics.enable = True

        outer_eth, ip, udp, vxlan, inner_eth, inner_ip , inner_udp= (
                f2.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
        )
        
        outer_eth.src.value = OUTER_SRC_MAC_F2
        outer_eth.dst.value = OUTER_DST_MAC_F2  
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

        dataplane.set_config()

        # Verify Traffic flow
        print("\n======= Start traffic =======")
        su.start_traffic(dataplane, f1.name)
        time.sleep(0.5)
        su.start_traffic(dataplane, f2.name)
        time.sleep(TRAFFIC_SLEEP_TIME) 
        print("\n======= Stop traffic =======")           
        dataplane.stop_traffic()
      
        print("\n======= Verify traffic TX and RX packets matching =======")
        res1 = su.check_flow_tx_rx_frames_stats(dataplane, f1.name)
        res2 = su.check_flow_tx_rx_frames_stats(dataplane, f2.name)

        dataplane.teardown()

        # Validate test result  
        print("\n======= Assert if traffic fails =======")
        assert res1, "Traffic test failure"
        assert res2, "Traffic test failure"

    @pytest.mark.dependency(depends=['TestUdpOutbound::test_setup'])
    def test_cleanup(self, dpu, setup_config):

        cleanup_commands = []
        for command in reversed(setup_config):
            command['op'] = 'remove'
            cleanup_commands.append(command)

        results = []
        for command in cleanup_commands:
            results.append(dpu.command_processor.process_command(command))
        print (results)
        print("\n======= SAI teardown commands RETURN values =======")
