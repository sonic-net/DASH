import json
from pathlib import Path
from pprint import pprint
import time
import pytest
import sys
sys.path.append("../utils")
import snappi_utils as su

current_file_dir = Path(__file__).parent

#import global variables and dpu config
from config_bidir_setup_commands import *

"""
This covers following scenario :

vnet to vnet communication with UDP traffic flow on bidirectional traffic :

Configure DUT on bidirectional routing direction
Configure TGEN vxlan UDP traffic flow as one vnet to another vnet of two OpenTrafficGenerator ports
Verify Traffic flow between vnet to vnet through DPU  


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
#                  Start of the testcase
###############################################################


@pytest.mark.skip(reason="https://github.com/sonic-net/DASH/issues/345")
class TestUdpBidir:

    @pytest.fixture(scope="class")
    def setup_config(self):
        """
        Fixture returns the content of the file with SAI configuration commands.
        scope=class - The file is loaded once for the whole test class
        """
        return dpu_config

    @pytest.mark.dependency()
    def test_setup(self, dpu, setup_config):
        results = [*dpu.process_commands(setup_config)]
        print("\n======= SAI setup commands RETURN values =======")
        pprint(results)

    @pytest.mark.dependency(depends=['TestUdpBidir::test_setup'])
    def test_vm_to_vm_commn_udp_bidir(self, dataplane):

        # Configure TGEN

        print("\n======= Configure Flow1 from ENI to NETWORK =======")        
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

        print("\n======= Configure Flow2 from NETWORK to ENI =======")        
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

        print("\n======= Configure Flow3 from ENI to NETWORK2 =======")        

        # Flow3 settings
        f3 = dataplane.configuration.flows.flow(name="ENI_TO_NETWORK2")[-1]
        f3.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
        f3.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
        f3.size.fixed = PACKET_LENGTH
        # send n packets and stop
        f3.duration.fixed_packets.packets = TOTALPACKETS
        # send n packets per second
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
        inner_eth.dst.value = INNER_DST_MAC2

        
        inner_ip.src.value = ENI_IP    #ENI
        inner_ip.dst.value = NETWORK_IP2  #world

        inner_udp.src_port.value = 10000
        inner_udp.dst_port.value = 20000

        print("\n======= Configure Flow4 from NETWORK2 to ENI =======")        
        # Flow4 settings
        f4 = dataplane.configuration.flows.flow(name="NETWORK2_TO_ENI")[-1]
        f4.tx_rx.port.tx_name = dataplane.configuration.ports[1].name
        f4.tx_rx.port.rx_name = dataplane.configuration.ports[0].name
        f4.size.fixed = PACKET_LENGTH
        # send n packets and stop
        f4.duration.fixed_packets.packets = TOTALPACKETS
        # send n packets per second
        f4.rate.pps = PPS
        f4.metrics.enable = True

        outer_eth, ip, udp, vxlan, inner_eth, inner_ip , inner_udp= (
                f4.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
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

        inner_eth.src.value = INNER_DST_MAC2
        inner_eth.dst.value = INNER_SRC_MAC

        inner_ip.src.value = NETWORK_IP2 #world
        inner_ip.dst.value = ENI_IP   # ENI

        inner_udp.src_port.value = 20000
        inner_udp.dst_port.value = 10000
        dataplane.set_config()

        # Verify Traffic
        print("\n======= Start Traffic  =======")        
        su.start_traffic(dataplane, f1.name)
        su.start_traffic(dataplane, f3.name)
        time.sleep(0.5)
        su.start_traffic(dataplane, f2.name)
        su.start_traffic(dataplane, f4.name)
        flow_names=[f1.name, f2.name, f3.name, f4.name]
        while(True):
            if (dataplane.is_traffic_stopped(flow_names)):
                break
        print("\n======= Stop Traffic  =======")                    
        dataplane.stop_traffic()

        print("\n======= Verify Traffic flows   =======")        
        res1 = su.check_flow_tx_rx_frames_stats(dataplane, f1.name)
        res2 = su.check_flow_tx_rx_frames_stats(dataplane, f2.name)
        res3 = su.check_flow_tx_rx_frames_stats(dataplane, f3.name)
        res4 = su.check_flow_tx_rx_frames_stats(dataplane, f4.name)
        
        dataplane.teardown()

        # Validate test result  
        print("\n======= Print Test Results  =======")     
        print("Tx and Rx packet match result of flow {} is {}".format(f1.name, res1))
        print("Tx and Rx packet match result of flow {} is {}".format(f2.name, res2))
        print("Tx and Rx packet match result of flow {} is {}".format(f3.name, res3))
        print("Tx and Rx packet match result of flow {} is {}".format(f4.name, res4))
        assert res1, "Traffic test failure"
        assert res2, "Traffic test failure"
        assert res3, "Traffic test failure"
        assert res4, "Traffic test failure"

    @pytest.mark.dependency(depends=['TestUdpBidir::test_setup'])
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
                
