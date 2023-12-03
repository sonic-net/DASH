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

Test vnet to vnet communication with ACL on inbound direction:
1. Configure DUT on inbound routing direction to deny and allow traffic
2. Configure TGEN vxlan traffic flow as one vnet to another vnet of two OpenTrafficGenerator ports
3. Verify Traffic denied through deny IPs


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
class TestAclInbound:
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

    @pytest.mark.dependency(depends=['TestAclInbound::test_setup'])
    def test_vm_to_vm_commn_acl_inbound(self, dataplane):

        # configure Tgen properties
        
        # inbound Flow settings
        f2 = dataplane.configuration.flows.flow(name="INBOUND")[-1]
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
        
        outer_eth.src.value = "80:09:02:02:00:01"
        outer_eth.dst.value = "c8:2c:2b:00:d1:34"   
        outer_eth.ether_type.value = 2048

        ip.src.value = NETWORK_VTEP_IP
        ip.dst.value = DPU_VTEP_IP

        udp.src_port.value = 11638
        udp.dst_port.value = 4789

        #vxlan.flags.value = 
        vxlan.vni.value = 101
        vxlan.reserved0.value = 0
        vxlan.reserved1.value = 0

        inner_eth.dst.value = "00:1A:C5:00:00:01"
        inner_eth.src.value = "00:1b:6e:00:00:02"

        inner_ip.src.value = NETWORK_IP1 #world
        inner_ip.dst.value = ENI_IP   # ENI

        inner_udp.src_port.value = 20000
        inner_udp.dst_port.value = 10000

        dataplane.set_config()

        # Verify traffic
        print("\n======= Verify traffic with allowed packets passing =======")
        print("\n======= Start traffic =======")
        su.start_traffic(dataplane, f2.name)
        flow_names=[f2.name]
        while(True):
            if (dataplane.is_traffic_stopped(flow_names)):
                break
        print("\n======= Stop traffic =======")
        dataplane.stop_traffic()

        #Packets should be allowed now
        print("\n======= Verify packet TX and RX matching =======")
        acl_traffic_result1 = su.check_flow_tx_rx_frames_stats(dataplane, f2.name)
        # Print Result of the test
        print("Tx and Rx packet match result of flow {} is {}".format(f2.name, acl_traffic_result1))
        
        inner_ip.src.value = NETWORK_IP2 #world
        inner_ip.dst.value = ENI_IP   # ENI

        inner_udp.src_port.value = 20000
        inner_udp.dst_port.value = 10000

        dataplane.set_config()
        
        # Verify Traffic
        print("\n======= Verify traffic with denied packets failing =======")
        print("\n======= Start traffic =======")
        su.start_traffic(dataplane, f2.name)
        flow_names=[f1.name, f2.name, f3.name, f4.name]
        while(True):
            if (dataplane.is_traffic_stopped(flow_names)):
                break
        print("\n======= Stop traffic =======")
        dataplane.stop_traffic()
        
        #Packets should be denied
        print("\n======= Verify packet TX and RX not matching =======")
        acl_traffic_result2 = su.check_flow_tx_rx_frames_stats(dataplane, f2.name)
        # Print Result of the test
        print("Tx and Rx packet match result of flow {} is {}".format(f2.name, acl_traffic_result2))

        dataplane.teardown()

        # Validate test result
        assert acl_traffic_result1==True, "Traffic test packets Allow failure"
        assert acl_traffic_result2==False, "Traffic test packets Deny failure"

    @pytest.mark.skip(reason="TODO: validate acl drop from DPU stats when stats api becomes available")
    def test_check_dpu_drop_reason_is_acl():
        pass

    @pytest.mark.dependency(depends=['TestAclInbound::test_setup'])
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
