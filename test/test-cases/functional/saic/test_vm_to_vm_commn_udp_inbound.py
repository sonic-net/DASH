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
from config_inbound_setup_commands import *

"""
This covers following scenario :
vnet to vnet communication with UDP traffic flow with inbound direction :
Configure DUT on inbound routing direction
Configure TGEN vxlan UDP traffic flow as one vnet to another vnet of two OpenTrafficGenerator ports
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
#                  Start of the testcase
###############################################################


@pytest.mark.skip(reason="https://github.com/sonic-net/DASH/issues/345")
class TestUdpInbound:
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

    @pytest.mark.dependency(depends=['TestUdpInbound::test_setup'])
    def test_vm_to_vm_commn_udp_inbound(self, dataplane):
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

        # Verify Traffic
        su.start_traffic(dataplane, f2.name)
        time.sleep(0.5)
        su.start_traffic(dataplane, f1.name)
        flow_names=[f1.name, f2.name]
        while(True):
            if (dataplane.is_traffic_stopped(flow_names)):
                break 
        dataplane.stop_traffic()
        
        res1 = su.check_flow_tx_rx_frames_stats(dataplane, f1.name)
        res2 = su.check_flow_tx_rx_frames_stats(dataplane, f2.name)
        print("Tx and Rx packet match result of flow {} is {}".format(f1.name, res1))
        print("Tx and Rx packet match result of flow {} is {}".format(f2.name, res2))
        
        dataplane.teardown()
        
        # Validate test result
        assert res1, "Traffic test failure"
        assert res2, "Traffic test failure"

    @pytest.mark.dependency(depends=['TestUdpInbound::test_setup'])
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

