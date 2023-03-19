import json
import time
from pathlib import Path
from pprint import pprint

import pytest
import saichallenger.common.sai_dataplane.snappi.snappi_traffic_utils as stu
from saichallenger.common.sai_dataplane.utils.ptf_testutils import (send_packet,
                                                                    simple_udp_packet,
                                                                    simple_vxlan_packet,
                                                                    verify_no_other_packets,
                                                                    verify_packet)

import sys
sys.path.append("../utils")
import vnet2vnet_helper as dh

current_file_dir = Path(__file__).parent

# Constants
SWITCH_ID = 5

# Simple, non-scaled configuration.
# See README.md for details.
TEST_VNET_OUTBOUND_CONFIG = {

    "ENI_COUNT": 1,
    "ACL_RULES_NSG": 1,
    "ACL_TABLE_COUNT": 1,
    "IP_PER_ACL_RULE": 1,
    "IP_MAPPED_PER_ACL_RULE": 1,
    "IP_ROUTE_DIVIDER_PER_ACL_RULE": 1,

    'DASH_VIP': {
        'vpe': {
            'SWITCH_ID': '$SWITCH_ID',
            'IPV4': "172.16.1.100"
        }
    },

    'DASH_DIRECTION_LOOKUP': {
        'dle': {
            'SWITCH_ID': '$SWITCH_ID',
            'VNI': 100,
            'ACTION': 'SET_OUTBOUND_DIRECTION'
        }
    },

    'DASH_ACL_GROUP': {
        'in_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        },
        'out_acl_group_id': {
            'ADDR_FAMILY': 'IPv4'
        }
    },

    'DASH_VNET': {
        'vnet': {
            'VNI': 1000
        }
    },

    'DASH_ENI': {
        'eni': {
            'ACL_GROUP': {
                'INBOUND': {
                    'STAGE1': '$in_acl_group_id_#{0}',
                    'STAGE2': '$in_acl_group_id_#{0}',
                    'STAGE3': '$in_acl_group_id_#{0}}',
                    'STAGE4': '$in_acl_group_id_#{0}}',
                    'STAGE5': '$in_acl_group_id_#{0}}'
                },
                'OUTBOUND': {
                    'STAGE1': 0,
                    'STAGE2': 0,
                    'STAGE3': 0,
                    'STAGE4': 0,
                    'STAGE5': 0
                }
            },
            'ADMIN_STATE': True,
            'CPS': 10000,
            'FLOWS': 10000,
            'PPS': 100000,
            'VM_UNDERLAY_DIP': "172.16.1.1",
            'VM_VNI': 9,
            'VNET_ID': '$vnet_#{0}'
        }
    },

    'DASH_ENI_ETHER_ADDRESS_MAP': {
        'eam': {
            'SWITCH_ID': '$SWITCH_ID',
            'MAC': "00:cc:cc:cc:00:00",
            'ENI_ID': '$eni_#{0}'
        }
    },

    'DASH_OUTBOUND_ROUTING': {
        'ore': {
            'SWITCH_ID': '$SWITCH_ID',
            'ENI_ID': '$eni_#{0}',
            'DESTINATION': "10.1.0.0/16",
            'ACTION': 'ROUTE_VNET',
            'DST_VNET_ID': '$vnet_#{0}'
        }
    },

    'DASH_OUTBOUND_CA_TO_PA': {
        'ocpe': {
            'SWITCH_ID': '$SWITCH_ID',
            'DST_VNET_ID': '$vnet_#{0}',
            'DIP': "10.1.2.50",
            'UNDERLAY_DIP': "172.16.1.20",
            'OVERLAY_DMAC': "00:DD:DD:DD:00:00",
            'USE_DST_VNET_VNI': True
        }
    }
}


@pytest.mark.ptf
@pytest.mark.snappi
class TestSaiVnetOutbound:

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_inbound_simple_create(self, dpu):
        """Generate and apply configuration"""

        with (current_file_dir / 'vnet_outbound_setup_commands_simple.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        result = [*dpu.process_commands(setup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(result)

    @pytest.mark.ptf
    def test_vnet_inbound_simple_packet_modification(self, dpu, dataplane):
        """Verify proper packet transformation."""

        dataplane.set_config()

        SRC_VM_IP = "10.1.1.10"
        OUTER_SMAC = "00:00:05:06:06:06"
        OUR_MAC = "00:00:02:03:04:05"

        VIP = TEST_VNET_OUTBOUND_CONFIG['DASH_VIP']['vpe']['IPV4']
        VNET_VNI = TEST_VNET_OUTBOUND_CONFIG['DASH_VNET']['vnet']['VNI']
        DIR_LOOKUP_VNI = TEST_VNET_OUTBOUND_CONFIG['DASH_DIRECTION_LOOKUP']['dle']['VNI']
        SRC_VM_PA_IP = TEST_VNET_OUTBOUND_CONFIG['DASH_ENI']['eni']['VM_UNDERLAY_DIP']
        ENI_MAC = TEST_VNET_OUTBOUND_CONFIG['DASH_ENI_ETHER_ADDRESS_MAP']['eam']['MAC']
        DST_CA_IP = TEST_VNET_OUTBOUND_CONFIG['DASH_OUTBOUND_CA_TO_PA']['ocpe']['DIP']
        DST_PA_IP = TEST_VNET_OUTBOUND_CONFIG['DASH_OUTBOUND_CA_TO_PA']['ocpe']["UNDERLAY_DIP"]
        DST_CA_MAC = TEST_VNET_OUTBOUND_CONFIG['DASH_OUTBOUND_CA_TO_PA']['ocpe']["OVERLAY_DMAC"]

        # # check VIP drop
        WRONG_VIP = "172.16.100.100"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=ENI_MAC,
                                      ip_dst=DST_CA_IP,
                                      ip_src=SRC_VM_IP)
        vxlan_pkt = simple_vxlan_packet(eth_dst=OUR_MAC,
                                        eth_src=OUTER_SMAC,
                                        ip_dst=WRONG_VIP,
                                        ip_src=SRC_VM_PA_IP,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=VNET_VNI,
                                        inner_frame=inner_pkt)
        print("\n\nSending packet with wrong vip...\n\n", vxlan_pkt.__repr__())
        send_packet(dataplane, 0, vxlan_pkt)
        print("\nVerifying drop...")
        verify_no_other_packets(dataplane)

        # check routing drop
        WRONG_DST_CA = "10.200.2.50"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=ENI_MAC,
                                      ip_dst=WRONG_DST_CA,
                                      ip_src=SRC_VM_IP)
        vxlan_pkt = simple_vxlan_packet(eth_dst=OUR_MAC,
                                        eth_src=OUTER_SMAC,
                                        ip_dst=VIP,
                                        ip_src=SRC_VM_PA_IP,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=VNET_VNI,
                                        inner_frame=inner_pkt)
        print("\nSending packet with wrong dst CA IP to verify routing drop...\n\n", vxlan_pkt.__repr__())
        send_packet(dataplane, 0, vxlan_pkt)
        print("\nVerifying drop...")
        verify_no_other_packets(dataplane)

        # check mapping drop
        WRONG_DST_CA = "10.1.211.211"
        inner_pkt = simple_udp_packet(eth_dst="02:02:02:02:02:02",
                                      eth_src=ENI_MAC,
                                      ip_dst=WRONG_DST_CA,
                                      ip_src=SRC_VM_IP)
        vxlan_pkt = simple_vxlan_packet(eth_dst=OUR_MAC,
                                        eth_src=OUTER_SMAC,
                                        ip_dst=VIP,
                                        ip_src=SRC_VM_PA_IP,
                                        udp_sport=11638,
                                        with_udp_chksum=False,
                                        vxlan_vni=VNET_VNI,
                                        inner_frame=inner_pkt)
        print("\nSending packet with wrong dst CA IP to verify mapping drop...\n\n", vxlan_pkt.__repr__())
        send_packet(dataplane, 0, vxlan_pkt)
        print("\nVerifying drop...")
        verify_no_other_packets(dataplane)

        # check forwarding
        inner_pkt = simple_udp_packet(eth_dst = "02:02:02:02:02:02",
                                      eth_src = ENI_MAC,
                                      ip_dst  = DST_CA_IP,
                                      ip_src  = SRC_VM_IP)
        vxlan_pkt = simple_vxlan_packet(eth_dst         = OUR_MAC,
                                        eth_src         = OUTER_SMAC,
                                        ip_dst          = VIP,
                                        ip_src          = SRC_VM_PA_IP,
                                        udp_sport       = 11638,
                                        with_udp_chksum = False,
                                        vxlan_vni       = DIR_LOOKUP_VNI,
                                        inner_frame     = inner_pkt)

        inner_exp_pkt = simple_udp_packet(eth_dst = DST_CA_MAC,
                                          eth_src = ENI_MAC,
                                          ip_dst  = DST_CA_IP,
                                          ip_src  = SRC_VM_IP)
        vxlan_exp_pkt = simple_vxlan_packet(eth_dst         = "00:00:00:00:00:00",
                                            eth_src         = "00:00:00:00:00:00",
                                            ip_dst          = DST_PA_IP,
                                            ip_src          = VIP,
                                            udp_sport       = 0, # TODO: Fix sport in pipeline
                                            with_udp_chksum = False,
                                            vxlan_vni       = VNET_VNI,
                                            vxlan_flags     = 0,
                                            inner_frame     = inner_exp_pkt)
        vxlan_exp_pkt['IP'].chksum = 0

        print("\nSending outbound packet...\n\n", vxlan_pkt.__repr__())
        send_packet(dataplane, 0, vxlan_pkt)
        time.sleep(0.5)
        print("\nVerifying packet...\n", vxlan_exp_pkt.__repr__())
        verify_packet(dataplane, vxlan_exp_pkt, 0)

    @pytest.mark.snappi
    def test_vnet_inbound_simple_traffic_fixed_packets(self, dpu, dataplane):
        """
        Verify same config with high-rate traffic.
        packets_per_flow=10 means that each possible packet path will be verified using 10 packet.
        NOTE: For BMv2 we keep here PPS limitation
        """
        dh.scale_vnet_outbound_flows(dataplane, TEST_VNET_OUTBOUND_CONFIG, packets_per_flow=10, pps_per_flow=10)
        dataplane.set_config()
        dataplane.start_traffic()
        stu.wait_for(lambda: dh.check_flow_packets_metrics(dataplane, dataplane.flows[0], show=True)[0],
                    "Test", timeout_seconds=10)

    @pytest.mark.snappi
    def test_vnet_inbound_simple_traffic_fixed_duration(self, dpu, dataplane):
        """
        Test with the fixed traffic duration to send.
        flow_duration sets the total duration of traffic. Number of packets is limited by PPS.
        For the HW PPS may be omitted and then it will send traffic on a line rate.
        NOTE: This test does not verify the correctness of the packets transformation.
        """
        test_duration = 5
        dh.scale_vnet_outbound_flows(dataplane, TEST_VNET_OUTBOUND_CONFIG,
                                     packets_per_flow=0, flow_duration=test_duration, pps_per_flow=5)
        dataplane.set_config()
        dataplane.start_traffic()
        stu.wait_for(lambda: dh.check_flows_all_seconds_metrics(dataplane, dataplane.flows,
                                                                name="Custom flow group", show=True)[0],
                    "Test", timeout_seconds=test_duration + 1)

    @pytest.mark.ptf
    @pytest.mark.snappi
    def test_vnet_inbound_simple_remove(self, dpu):
        """Verify configuration removal"""

        with (current_file_dir / 'vnet_outbound_setup_commands_simple.json').open(mode='r') as config_file:
            setup_commands = json.load(config_file)
        cleanup_commands = []
        for cmd in reversed(setup_commands):
            cleanup_commands.append({'name': cmd['name'], 'op': 'remove'})

        result = [*dpu.process_commands(cleanup_commands)]
        print("\n======= SAI commands RETURN values =======")
        pprint(result)
