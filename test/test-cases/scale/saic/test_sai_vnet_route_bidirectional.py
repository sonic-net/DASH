"""
Verify VNET Route scenario
"""

import json
from pathlib import Path
from pprint import pprint
import time
import pytest
from saichallenger.common.sai_dataplane.utils.ptf_testutils import (send_packet,
                                                                    simple_udp_packet,
                                                                    simple_vxlan_packet,
                                                                    verify_packet,
                                                                    verify_no_other_packets)

import sys
sys.path.append("../utils")
current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5

# Simple, non-scaled configuration.
# See README.md for details.

@pytest.mark.ptf
@pytest.mark.snappi
class TestSaiVnetRoute:

    # @pytest.fixture(scope="module", autouse=True)
    # def discovery(dpu):
    #     dpu.objects_discovery()
        
    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_route_bidirectional_create(self, dpu):
        """Generate and apply configuration"""

        with (current_file_dir / 'vnet_route_setup_commands_bidirectional.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        results = [*dpu.process_commands(setup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(results)
        assert all(results), 'Create error'


    @pytest.mark.snappi
    def test_vnet_route_packet_bidirectional_forwarding_with_route_match(self, dpu, dataplane):
        """Verify packet forwarding with route match"""

        dataplane.set_config()

        # Route match, send packets from each port and drop packets on both ports.
        # Send packet one
        inner_pkt_one = simple_udp_packet(eth_dst = "02:02:02:02:02:02",
                                      eth_src = "00:cc:cc:cc:00:00",
                                      ip_dst  = "12.1.2.50",
                                      ip_src  = "10.1.1.10")
        vxlan_pkt_one = simple_vxlan_packet(eth_dst         = "00:00:02:03:04:05",
                                        eth_src         = "00:00:05:06:06:06",
                                        ip_dst          = "170.16.1.100",
                                        ip_src          = "170.16.1.1",
                                        udp_sport       = 11638,
                                        with_udp_chksum = False,
                                        vxlan_vni       = 100,
                                        inner_frame     = inner_pkt_one)
        
        # Expected received packet one
        inner_exp_pkt_one = simple_udp_packet(eth_dst = "00:DD:DD:DD:00:00",
                                          eth_src = "00:cc:cc:cc:00:00",
                                          ip_dst  = "12.1.2.50",
                                          ip_src  = "10.1.1.10")
        vxlan_exp_pkt_one = simple_vxlan_packet(eth_dst         = "00:00:00:00:00:00",
                                            eth_src         = "00:00:00:00:00:00",
                                            ip_dst          = "170.16.1.20",
                                            ip_src          = "170.16.1.100",
                                            udp_sport       = 0,
                                            with_udp_chksum = False,
                                            vxlan_vni       = 100,
                                            vxlan_flags     = 0x8,
                                            inner_frame     = inner_exp_pkt_one)
        # Send packet two
        inner_pkt_two = simple_udp_packet(eth_dst = "00:00:00:09:03:14",
                                      eth_src = "00:0a:04:06:06:06",
                                      ip_dst  = "171.18.1.100",
                                      ip_src  = "171.18.1.1")
        vxlan_pkt_two = simple_vxlan_packet(eth_dst         = "00:0b:05:06:06:06",
                                        eth_src         = "00:0a:05:06:06:06",
                                        ip_dst          = "10.11.1.20",
                                        ip_src          = "10.11.1.10",
                                        udp_sport       = 11639,
                                        with_udp_chksum = False,
                                        vxlan_vni       = 100,
                                        inner_frame     = inner_pkt_two)
        
        # Expected received packet two
        inner_exp_pkt_two = simple_udp_packet(eth_dst = "00:BB:BB:BB:00:00",
                                          eth_src = "00:0a:04:06:06:06",
                                          ip_dst  = "171.18.1.100",
                                          ip_src  = "171.18.1.1")
        vxlan_exp_pkt_two = simple_vxlan_packet(eth_dst         = "00:00:00:00:00:00",
                                            eth_src         = "00:00:00:00:00:00",
                                            ip_dst          = "10.11.1.15",
                                            ip_src          = "10.11.1.20",
                                            udp_sport       = 0,
                                            with_udp_chksum = False,
                                            vxlan_vni       = 100,
                                            vxlan_flags     = 0x8,
                                            inner_frame     = inner_exp_pkt_two)

        # Send packets from both ports 
        send_packet(dataplane, 0, vxlan_pkt_one, 10)
        # time.sleep(0.5)
        send_packet(dataplane, 1, vxlan_pkt_two, 20)

        # Verify no packets received
        print("\nVerifying drop...\n")
        assert verify_no_other_packets(dataplane), "Packet are received"

        # Route match. send packets from each port, forward and receive packets on opposite ports
        # Send packet one
        inner_pkt_one = simple_udp_packet(eth_dst = "02:02:02:02:02:02",
                                      eth_src = "00:cc:cc:cc:00:00",
                                      ip_dst  = "10.1.2.50",
                                      ip_src  = "10.1.1.10")
        vxlan_pkt_one = simple_vxlan_packet(eth_dst         = "00:00:02:03:04:05",
                                        eth_src         = "00:00:05:06:06:06",
                                        ip_dst          = "172.16.1.100",
                                        ip_src          = "172.16.1.1",
                                        udp_sport       = 11638,
                                        with_udp_chksum = False,
                                        vxlan_vni       = 100,
                                        inner_frame     = inner_pkt_one)
        
        # Expected received packet one
        inner_exp_pkt_one = simple_udp_packet(eth_dst = "00:DD:DD:DD:00:00",
                                          eth_src = "00:cc:cc:cc:00:00",
                                          ip_dst  = "10.1.2.50",
                                          ip_src  = "10.1.1.10")
        vxlan_exp_pkt_one = simple_vxlan_packet(eth_dst         = "00:00:00:00:00:00",
                                            eth_src         = "00:00:00:00:00:00",
                                            ip_dst          = "172.16.1.20",
                                            ip_src          = "172.16.1.100",
                                            udp_sport       = 0,
                                            with_udp_chksum = False,
                                            vxlan_vni       = 100,
                                            vxlan_flags     = 0x8,
                                            inner_frame     = inner_exp_pkt_one)
        # Send packet two
        inner_pkt_two = simple_udp_packet(eth_dst = "00:00:00:09:03:14",
                                      eth_src = "00:0a:04:06:06:06",
                                      ip_dst  = "172.19.1.100",
                                      ip_src  = "172.19.1.1")
        vxlan_pkt_two = simple_vxlan_packet(eth_dst         = "00:0b:05:06:06:06",
                                        eth_src         = "00:0a:05:06:06:06",
                                        ip_dst          = "10.10.2.20",
                                        ip_src          = "10.10.2.10",
                                        udp_sport       = 11639,
                                        with_udp_chksum = False,
                                        vxlan_vni       = 60,
                                        inner_frame     = inner_pkt_two)
        
        # Expected received packet two
        inner_exp_pkt_two = simple_udp_packet(eth_dst = "00:BB:BB:BB:00:00",
                                          eth_src = "00:0a:04:06:06:06",
                                          ip_dst  = "172.19.1.100",
                                          ip_src  = "172.19.1.1")
        vxlan_exp_pkt_two = simple_vxlan_packet(eth_dst         = "00:00:00:00:00:00",
                                            eth_src         = "00:00:00:00:00:00",
                                            ip_dst          = "10.10.2.15",
                                            ip_src          = "10.10.2.20",
                                            udp_sport       = 0,
                                            with_udp_chksum = False,
                                            vxlan_vni       = 100,
                                            vxlan_flags     = 0x8,
                                            inner_frame     = inner_exp_pkt_two)
        # Send packets from both ports 
        send_packet(dataplane, 0, vxlan_pkt_one, 10)
        time.sleep(0.5)
        send_packet(dataplane, 1, vxlan_pkt_two, 20)

        # Verify received packets on specific ports
        print("\nVerifying packets on both ports...\n")
        assert verify_packet(dataplane, vxlan_exp_pkt_one, 1), "Packet not received on port 1"
        assert verify_packet(dataplane, vxlan_exp_pkt_two, 0), "Packet not received on port 0"

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_route_bidirectional_remove(self, dpu):
        """Verify configuration removal"""

        with (current_file_dir / 'vnet_route_setup_commands_bidirectional.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        cleanup_commands = []
        for cmd in reversed(setup_commands):
            cleanup_commands.append({'name': cmd['name'], 'op': 'remove'})

        results = [*dpu.process_commands(cleanup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(results)
        assert all(
            [result == 'SAI_STATUS_SUCCESS' for result in results]
        ), 'Remove error'
