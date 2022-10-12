import snappi
import saichallenger.dataplane.traffic_utils as tu
from collections import namedtuple


def configure_vnet_outbound_packet_flows(sai_dp, vip, dir_lookup, ca_smac, ca_dip):
    """
    Define VNET Outbound routing flows
    """

    print("\nTest config:")
    print(f"{vip}\n{dir_lookup}\n{ca_smac}\n{ca_dip}\n")

    print("Adding flows {} > {}:".format(sai_dp.configuration.ports[0].name, sai_dp.configuration.ports[1].name))
    vip_val = vip.start
    for vip_number in range(0, vip.count):
        dir_lookup_val = dir_lookup.start
        print(f"\tVIP {vip_val}")

        ca_smac_portion = ca_smac.count // dir_lookup.count
        for dir_lookup_number in range(0, dir_lookup.count):
            print(f"\t\tDIR_LOOKUP VNI {dir_lookup_val}")
            ca_smac_val = ca_smac.start

            ca_smac_start_index = dir_lookup_number * ca_smac_portion
            for ca_smac_number in range(ca_smac_start_index, ca_smac_start_index + ca_smac_portion):
                print(f"\t\t\tCA SMAC: {tu.get_next_mac(ca_smac_val, step=ca_smac.step, number=ca_smac_number)}")
                print(f"\t\t\t\tCA DIP {ca_dip.start}, count: {ca_dip.count}, step: {ca_dip.step}")

                # Check that ca_mac differs on each iteration
                flow = sai_dp.add_flow("flow {} > {} |vip#{}|dir_lookup#{}|ca_mac#{}|ca_dip#{}".format(
                                            sai_dp.configuration.ports[0].name, sai_dp.configuration.ports[1].name,
                                            vip_number, dir_lookup_number, ca_smac_number, ca_dip.start),
                                       packet_count=ca_dip.count)

                sai_dp.add_ethernet_header(flow, dst_mac="00:00:02:03:04:05", src_mac="00:00:05:06:06:06")
                sai_dp.add_ipv4_header(flow, dst_ip=vip_val, src_ip="172.16.1.1")
                sai_dp.add_udp_header(flow, dst_port=80, src_port=11638)
                sai_dp.add_vxlan_header(flow, vni=dir_lookup_val)
                # sai_dp.add_ethernet_header(flow, dst_mac="02:02:02:02:02:02", src_mac=ca_smac_val)
                sai_dp.add_ethernet_header(flow, dst_mac="02:02:02:02:02:02",
                                           src_mac=tu.get_next_mac(ca_smac_val, step=ca_smac.step, number=ca_smac_number))

                sai_dp.add_ipv4_header(flow, dst_ip=ca_dip.start, src_ip="10.1.1.10",
                                       dst_step=ca_dip.step, dst_count=ca_dip.count,
                                    dst_choice=snappi.PatternFlowIpv4Dst.INCREMENT)
                sai_dp.add_udp_header(flow)

            dir_lookup_val += dir_lookup.step

        vip_val = tu.get_next_ip(vip_val, vip.step)

    print(f">>> FLOWS: {len(sai_dp.flows)}")
    for flow in sai_dp.flows:
        print(f">>>: {flow.name}")


def scale_vnet_outbound_flows(sai_dp, test_conf: dict):
    """
    Get scale options and define VNET Outbound routing flows
    """

    vip_tup = namedtuple('VIP', 'count start step')
    dir_lookup_tup = namedtuple('DIRECTION_LOOKUP', 'count start step')
    ca_smac_tup = namedtuple('CA_SMAC', 'count start step')
    ca_dip_tup = namedtuple('CA_DIP', 'count start step')

    def dict_helper(named_tup, conf, def_step):
        if type(conf) != dict:
            return named_tup(1, conf, def_step)
        else:
            return named_tup(conf.get('count', 1), conf.get('start', def_step), conf.get('step', def_step))

    vip = dict_helper(vip_tup, test_conf['DASH_VIP']['vpe']['IPV4'], "0.0.0.1")
    dir_lookup = dict_helper(dir_lookup_tup, test_conf['DASH_DIRECTION_LOOKUP']['dle']['VNI'], 1)
    ca_smac = dict_helper(ca_smac_tup, test_conf['DASH_ENI_ETHER_ADDRESS_MAP']['eam']['MAC'], "00:00:00:00:00:01")
    ca_dip = dict_helper(ca_dip_tup, test_conf['DASH_OUTBOUND_CA_TO_PA']['ocpe']['DIP'], "0.0.0.1")

    configure_vnet_outbound_packet_flows(sai_dp, vip, dir_lookup, ca_smac, ca_dip)


def check_flows_all_packets_metrics(sai_dp, flows=[], name="Flow group", exp_tx=None, exp_rx=None, show=False):
    if not flows:
        print("Flows None or empty")
        return False, None
    if not exp_tx:
        # check if all flows are fixed_packets
        # sum of bool list == count of True in this list
        if sum([flow.duration.choice == snappi.FlowDuration.FIXED_PACKETS for flow in flows]) == len(flows):
            exp_tx = sum([flow.duration.fixed_packets.packets for flow in flows])
        else:
            print("{}: some flow in flow group doesn't configured to {}.".format( \
                    name, snappi.FlowDuration.FIXED_PACKETS))
            return False, None
    if not exp_rx:
        exp_rx = exp_tx

    act_tx = 0
    act_rx = 0
    success = 0

    for flow in flows:
        tmp = check_flow_packets_metrics(sai_dp, flow)
        success += tmp[0]
        act_tx += tmp[1]['TX']
        act_rx += tmp[1]['RX']

    success = success == len(flows)

    if show:
        # flow group name | exp tx | act tx | exp rx | act rx
        print(f"{name} | exp tx:{exp_tx} - tx:{act_tx} | exp rx:{exp_rx} - rx:{act_rx}")

    return success, { 'TX': act_tx, 'RX': act_rx }


# exp = expected
# act = actual
# (bool, {'TX': int, 'RX': int})
def check_flow_packets_metrics(sai_dp, flow: snappi.Flow, exp_tx=None, exp_rx=None, show=False):
    if not exp_tx:
        if flow.duration.choice == snappi.FlowDuration.FIXED_PACKETS:
            exp_tx = flow.duration.fixed_packets.packets
        else:
            print("{}: check for packet count failed. Flow configured to {} instead of {}".format( \
                    flow.name, flow.duration.choice, snappi.FlowDuration.FIXED_PACKETS))
            return False, None
    if not exp_rx:
        exp_rx = exp_tx

    req = sai_dp.api.metrics_request()
    req.flow.flow_names = [ flow.name ]
    req.flow.metric_names = [ snappi.FlowMetricsRequest.FRAMES_TX, snappi.FlowMetricsRequest.FRAMES_RX ]
    res = sai_dp.api.get_metrics(req)

    act_tx = res.flow_metrics[0].frames_tx
    act_rx = res.flow_metrics[0].frames_rx

    if show:
        # flow name | exp tx | act tx | exp rx | act rx
        print("{} | {} | {} | {} | {}".format(flow.name, exp_tx, act_tx, exp_rx, act_rx))

    if exp_tx == act_tx and exp_rx == act_rx and \
        res.flow_metrics[0].transmit == snappi.FlowMetric.STOPPED:
        return True, { 'TX': act_tx, 'RX': act_rx }

    return False, { 'TX': act_tx, 'RX': act_rx }


# TODO
def check_flows_all_seconds_metrics(sai_dp):
    pass


def check_flow_seconds_metrics(sai_dp, flow: snappi.Flow, seconds=None, exp_tx=None, exp_rx=None, delta=None, show=False):
    if not seconds:
        if flow.duration.choice == snappi.FlowDuration.FIXED_SECONDS:
            seconds = flow.duration.fixed_seconds.seconds
        else:
            print("{}: check for packet count failed. Flow configured to {} instead of {}".format( \
                    flow.name, flow.duration.choice, snappi.FlowDuration.FIXED_SECONDS))
            return False, None
    if not exp_tx:
        exp_tx = flow.rate.pps * seconds
    if not exp_rx:
        exp_rx = exp_tx
    if not delta:
        # default delta is 10% of exp_tx. If it 0 (seconds < 10) then delta == pps
        tmp_delta = int(exp_tx / 10)
        delta = tmp_delta if tmp_delta > 0 else flow.rate.pps

    req = sai_dp.api.metrics_request()
    req.flow.flow_names = [ flow.name ]
    req.flow.metric_names = [ snappi.FlowMetricsRequest.FRAMES_TX, snappi.FlowMetricsRequest.FRAMES_RX ]
    res = sai_dp.api.get_metrics(req)

    act_tx = res.flow_metrics[0].frames_tx
    act_rx = res.flow_metrics[0].frames_rx

    if show:
        # flow name | [exp tx - delta, ext_tx + delta] | act tx | [exp rx - delta, exp_rx + delta] | act rx
        print("{} | [{}, {}] | {} | [{}, {}] | {}".format(flow.name, exp_tx - delta, exp_tx + delta, act_tx, \
                                                            exp_rx - delta, exp_rx + delta, act_rx))

    if act_tx in range(exp_tx - delta, exp_tx + delta) and \
        act_rx in range(exp_rx - delta, exp_rx + delta) and \
        res.flow_metrics[0].transmit == snappi.FlowMetric.STOPPED:
        return True, { 'TX': act_tx, 'RX': act_rx }

    return False, { 'TX': act_tx, 'RX': act_rx }


# TODO
def check_flows_all_continuous_metrics(sai_dp):
    pass


# TODO
def check_flow_continuous_metrics(sai_dp, flow: snappi.Flow):
    pass


def add_simple_vxlan_packet(sai_dp,
                            flow: snappi.Flow,
                            outer_dst_mac,
                            outer_src_mac,
                            outer_dst_ip,
                            outer_src_ip,
                            dst_udp_port,
                            src_udp_port,
                            vni,
                            inner_dst_mac,
                            inner_src_mac,
                            inner_dst_ip,
                            inner_src_ip
                            ):
    if flow == None:
        print("flow is None")
        return

    if flow.packet:
        print("packet in flow")
        return

    sai_dp.add_ethernet_header(flow, outer_dst_mac, outer_src_mac)
    sai_dp.add_ipv4_header(flow, outer_dst_ip, outer_src_ip)
    u = sai_dp.add_udp_header(flow, dst_udp_port, src_udp_port)
    # TODO: report ixia bug (udp checksum still generated)
    # u.checksum.choice = u.checksum.CUSTOM
    # u.checksum.custom = 0
    sai_dp.add_vxlan_header(flow, vni)
    sai_dp.add_ethernet_header(flow, inner_dst_mac, inner_src_mac)
    sai_dp.add_ipv4_header(flow, inner_dst_ip, inner_src_ip)
    sai_dp.add_udp_header(flow)
