#!/usr/bin/env python3
"""
Test SAI Baby Hero.
Baby Hero test scale is 1% of the Hero test scale.
This is achieved by having only one prefix per ACL instead of 100 prefixes per ACL.
scale:
    SAI_OBJECT_TYPE_VIP_ENTRY = 1
    SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY = 32
    SAI_OBJECT_TYPE_VNET = 32
    SAI_OBJECT_TYPE_DASH_ACL_GROUP = 320
    SAI_OBJECT_TYPE_ENI = 32
    SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY = 32
    SAI_OBJECT_TYPE_OUTBOUND_CA_TO_PA_ENTRY = 80.000 + 320
    SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY = 80.000 (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET) + 80.000 (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT)
    SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY = 32
run time:
    configure BMv2: 15 min
    run traffic:     3 min
    clear config:    6 min
TO DO:
    add back ACLs once BMv2 issue solved
    add traffic for SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT ips
    add traffic for all SAI_OBJECT_TYPE_DASH_ACL_GROUP (curently only first one for each ENI is exercised)
    use dpugen and remove the duplicate code
"""


import ipaddress
import json
import socket
import struct
from copy import deepcopy
from pathlib import Path
from pprint import pprint

import macaddress
import pytest
from munch import DefaultMunch

import dpugen

# utils
socket_inet_ntoa = socket.inet_ntoa
struct_pack = struct.pack


class MAC(macaddress.MAC):
    formats = ('xx:xx:xx:xx:xx:xx',) + macaddress.MAC.formats
maca = MAC       # optimization so the . does not get executed multiple times

baby_hero_params = {                    # CONFIG VALUE             # DEFAULT VALUE
    'DPUS':                             1,                         # 8
    'ENI_COUNT':                        32,                        # 256
    'ENI_L2R_STEP':                     1000,                      # 1000
    'IP_PER_ACL_RULE':                  1,                         # 100
}


class TestSaiBabyHero:

    def create_baby_hero_config(self):
        current_file_dir = Path(__file__).parent
        with (current_file_dir / 'config_baby_hero.json').open(mode='r') as config_file:
            baby_hero_commands = json.load(config_file)
        return baby_hero_commands

    @pytest.mark.snappi
    def test_create_vnet_config(self, dpu):
        print("\n======= SAI commands RETURN values =======")
        results = [*dpu.process_commands((self.create_baby_hero_config()))]
        pprint(results)

    @pytest.mark.snappi
    def test_baby_hero_traffic(self, dataplane):

        conf = dpugen.sai.SaiConfig()
        conf.mergeParams(baby_hero_params)

        dflt_params = {                        # CONFIG VALUE             # DEFAULT VALUE
            'SCHEMA_VER':                      '0.0.4',

            'DC_START':                        '220.0.1.1',                # '220.0.1.2'
            'DC_STEP':                         '0.0.1.0',                  # '0.0.1.0'

            'LOOPBACK':                        '221.0.0.1',                # '221.0.0.1'
            'PAL':                             '221.1.0.0',                # '221.1.0.1'
            'PAR':                             '221.2.0.0',                # '221.2.0.1'
            'GATEWAY':                         '222.0.0.1',                # '222.0.0.1'

            'DPUS':                             8,                         # 1

            'ENI_START':                        1,                         # 1
            'ENI_COUNT':                        256,                       # 32
            'ENI_STEP':                         1,                         # 1
            'ENI_L2R_STEP':                     0,                      # 1000

            'VNET_PER_ENI':                     1,                         # 16 TODO: partialy implemented

            'ACL_NSG_COUNT':                    5,                         # 5 (per direction per ENI)
            'ACL_RULES_NSG':                    1000,                    # 1000
            'IP_PER_ACL_RULE':                  1,                       # 100
            'ACL_MAPPED_PER_NSG':               500,                     # 500, efective is 250 because denny are skiped

            'MAC_L_START':                      '00:1A:C5:00:00:01',
            'MAC_R_START':                      '00:1B:6E:00:00:01',

            'MAC_STEP_ENI':                     '00:00:00:18:00:00',       # '00:00:00:18:00:00'
            'MAC_STEP_NSG':                     '00:00:00:02:00:00',
            'MAC_STEP_ACL':                     '00:00:00:00:01:00',

            'IP_L_START':                       '1.1.0.1',                 # local, eni
            'IP_R_START':                       '1.4.0.1',                 # remote, the world

            'IP_STEP1':                         '0.0.0.1',
            'IP_STEP_ENI':                      '0.64.0.0',
            'IP_STEP_NSG':                      '0.2.0.0',
            'IP_STEP_ACL':                      '0.0.1.0',
            'IP_STEPE':                         '0.0.0.2',

            'TOTAL_OUTBOUND_ROUTES':            25600000                  # ENI_COUNT * 100K
        }

        params_dict = deepcopy(dflt_params)

        cooked_params_dict = {}
        for ip in [
            'IP_STEP1',
            'IP_STEP_ENI',
            'IP_STEP_NSG',
            'IP_STEP_ACL',
            'IP_STEPE',
            'IP_L_START',
            'IP_R_START',
            'PAL',
            'PAR',
            'GATEWAY'
        ]:
            cooked_params_dict[ip] = int(ipaddress.ip_address((params_dict[ip])))
        for mac in [
            'MAC_L_START',
            'MAC_R_START',
            'MAC_STEP_ENI',
            'MAC_STEP_NSG',
            'MAC_STEP_ACL'
        ]:
            cooked_params_dict[mac] = int(maca(params_dict[mac]))

        params = DefaultMunch.fromDict(params_dict)
        cooked_params = DefaultMunch.fromDict(cooked_params_dict)

        p = params
        ip_int = cooked_params

        print('Configuring traffic ...')
        flows = []
        for eni_index, eni in enumerate(range(1, 33, 1)):

            # test values computation

            underlay_src_mac = '00:00:00:00:00:00'
            underlay_dst_mac = '00:00:00:00:00:00'

            underlay_src_ip = socket_inet_ntoa(struct_pack('>L', ip_int.PAL + eni_index * ip_int.IP_STEP1))
            underlay_dst_ip = '221.0.0.1'

            overlay_src_mac = str(maca(ip_int.MAC_L_START + eni_index * ip_int.MAC_STEP_ENI))
            # overlay_dst_mac = str(maca(ip_int.MAC_R_START + eni_index * ip_int.MAC_STEP_ENI))
            overlay_dst_mac = '00:00:00:00:00:00'  # TODO: https://github.com/sonic-net/DASH/issues/583

            overlay_src_ip = socket_inet_ntoa(struct_pack('>L', ip_int.IP_L_START + eni_index * ip_int.IP_STEP_ENI))
            overlay_dst_ip = socket_inet_ntoa(struct_pack('>L', ip_int.IP_R_START + eni_index * ip_int.IP_STEP_ENI))

            # SNAPPI flow creation

            outbound = dataplane.configuration.flows.flow(name="ENI%d_OUTBOUND" % eni)[-1]
            outbound.tx_rx.port.tx_name = dataplane.configuration.ports[0].name
            outbound.tx_rx.port.rx_name = dataplane.configuration.ports[1].name
            outbound.size.fixed = 256
            outbound.duration.fixed_packets.packets = 250
            outbound.rate.pps = 2  # unable to send more than 400 pps
            outbound.metrics.enable = True

            underlay_eth, underlay_ip, underlay_udp, vxlan, overlay_eth, overlay_ip, overlay_udp = (
                    outbound.packet.ethernet().ipv4().udp().vxlan().ethernet().ipv4().udp()
            )

            underlay_eth.src.value = underlay_src_mac  # test gear interface mac
            underlay_eth.dst.value = underlay_dst_mac  # DPU interface mac
            underlay_eth.ether_type.value = 2048

            underlay_ip.src.value = underlay_src_ip  # ENI_VTEP_IP
            underlay_ip.dst.value = underlay_dst_ip  # DPU_VTEP_IP

            underlay_udp.src_port.value = 11638
            underlay_udp.dst_port.value = 4789  # VXLAN_PORT

            vxlan.vni.value = eni  # VNI
            vxlan.reserved0.value = 0
            vxlan.reserved1.value = 0

            overlay_eth.src.value = overlay_src_mac  # ENI MAC
            overlay_eth.dst.increment.start = overlay_dst_mac
            overlay_eth.dst.increment.count = 250
            overlay_eth.dst.increment.step  = '00:00:00:00:00:02'

            overlay_ip.src.value = overlay_src_ip  # ENI IP
            overlay_ip.dst.increment.start = overlay_dst_ip
            overlay_ip.dst.increment.count = 250
            overlay_ip.dst.increment.step  = '0.0.0.2'

            overlay_udp.src_port.value = 10000
            overlay_udp.dst_port.value = 20000

            flows.append(outbound)

        dataplane.set_config()

        flow_names = [f.name for f in flows]

        print('start traffic')
        ts = dataplane.api.transmit_state()
        ts.state = ts.START
        if len(flow_names) > 0:
            ts.flow_names = flow_names
        dataplane.api.set_transmit_state(ts)

        print('Checking metrics on all configured ports ...')
        print('Expected\tTotal Tx\tTotal Rx')
        assert self.wait_for(lambda: self.metrics_ok(dataplane.api)), 'Metrics validation failed!'

        print('stop traffic')
        while (True):
            if (dataplane.is_traffic_stopped(flow_names)):
                break
        dataplane.stop_traffic()
        dataplane.teardown()

    def metrics_ok(self, api):
        # create a port metrics request and filter based on port names
        cfg = api.get_config()

        req = api.metrics_request()
        req.port.port_names = [p.name for p in cfg.ports]
        # include only sent and received packet counts
        req.port.column_names = [req.port.FRAMES_TX, req.port.FRAMES_RX]
        # fetch port metrics
        res = api.get_metrics(req)
        # calculate total frames sent and received across all configured ports
        total_tx = sum([m.frames_tx for m in res.port_metrics])
        total_rx = sum([m.frames_rx for m in res.port_metrics])
        expected = sum([f.duration.fixed_packets.packets for f in cfg.flows])

        print('%d\t\t%d\t\t%d' % (expected, total_tx, total_rx))

        return expected == total_tx and total_rx >= expected

    def wait_for(self, func, timeout=1000, interval=0.2):
        '''
        Keeps calling the `func` until it returns true or `timeout` occurs
        every `interval` seconds.
        '''
        import time

        start = time.time()

        while time.time() - start <= timeout:
            if func():
                return True
            time.sleep(interval)

        print('Timeout occurred !')
        return False

    @pytest.mark.snappi
    def test_remove_vnet_config(self, dpu, dataplane):
        cleanup_commands = []
        for cmd in reversed(self.create_baby_hero_config()):
            cleanup_commands.append({'name': cmd['name'], 'op': 'remove'})
        print("\n======= SAI commands RETURN values =======")
        for cleanup_command in cleanup_commands:
            try:
                print(cleanup_command)
                result = [*dpu.process_commands([cleanup_command])]
                pprint(result)
            except Exception as e:
                print(f"Error during cleanup: {e}")
