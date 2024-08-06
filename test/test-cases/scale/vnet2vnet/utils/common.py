import json
import os
import sys
import time
from math import floor, log
#import yaml
from pprint import pprint as pp

from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from tabulate import tabulate

if sys.version_info[0] >= 3:
    unicode = str       # alias str as unicode for python3 and above
TESTBED_FILE = "testbed.py"                     # path to settings.json relative root dir

opd, opj, opj = os.path.dirname, os.path.join, os.path.join


def ss(mssg, st):
    for remaining in range(st, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(mssg + " {:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    print("\n")


def human_format(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])


def byteify(val):
    if isinstance(val, dict):
        return {byteify(key): byteify(value) for key, value in val.item()}
    elif isinstance(val, list):
        return [byteify(element) for element in val]
    # change u'string' to 'string' only for python2
    elif isinstance(val, unicode) and sys.version_info[0] == 2:
        return val.encode("utf-8")
    else:
        return val


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printStats(api, vName, printoptions={}):
    transpose = True
    try:
        transpose = printoptions[vName]["transpose"]
    except:
        pass
    view = StatViewAssistant(api, vName)
    data = view.Rows.RawData
    columnCaptions = view.ColumnHeaders
    cheader = columnCaptions[:]
    if vName in printoptions and "toprint" in printoptions[vName]:
        cheader = printoptions[vName]["toprint"]
    if vName in printoptions and 'nottoprint' in printoptions[vName]:
        [cheader.remove(st) for st in printoptions[vName]['nottoprint']]
    rows = []
    for row in data:
        tmp = [row[columnCaptions.index(col)] for col in cheader]
        rows.append(tmp[:])
    if transpose:
        rows.insert(0, cheader)
        rows = list(zip(*rows))
        cheader = []
    print(tabulate(rows, headers=cheader, tablefmt="psql"))
    return rows[0]


def print_stats_acl(api, vName, printoptions={}):
    if isinstance(vName, list):
        [print_stats_acl(api, view, printoptions) for view in vName]
    else:
        transpose = True
        try:
            transpose = printoptions[vName]["transpose"]
        except:
            pass
        view = StatViewAssistant(api, vName)
        data = view.Rows.RawData
        columnCaptions = view.ColumnHeaders
        cheader = columnCaptions[:]

        if vName in printoptions and "toprint" in printoptions[vName]:
            cheader = printoptions[vName]["toprint"]
        if vName in printoptions and 'nottoprint' in printoptions[vName]:
            [cheader.remove(st) for st in printoptions[vName]['nottoprint']]
        rows = []
        for row in data:
            tmp = [row[columnCaptions.index(col)] for col in cheader]
            pf = f"{bcolors.FAIL}FAIL{bcolors.ENDC}"
            if row[columnCaptions.index("Traffic Item")] in ["Priority 2", "Priority 8", "Priority 5"]:
                if int(float(row[columnCaptions.index("Loss %")])) == 100:
                    pf = f"{bcolors.OKGREEN}%s{bcolors.ENDC}" % "PASS"
            else:
                if int(float(row[columnCaptions.index("Loss %")])) == 0:
                    pf = f"{bcolors.OKGREEN}%s{bcolors.ENDC}" % "PASS"
            tmp.append(pf)
            rows.append(tmp[:])
        cheader.append("PASS/FAIL")
        if transpose:
            rows.insert(0, cheader)
            rows = list(zip(*rows))
            cheader = []
        print('\n"%s"\n' % (vName,)+tabulate(rows, headers=cheader, tablefmt="psql"))


def start_portocols(api):
    print('Starting All protocols', len(api.Vport.find(Name="^Tx"))+len(api.Vport.find(Name="^Rx")))
    api.StartAllProtocols()

    try:
        print('Verify protocol sessions')
        protocolsSummary = StatViewAssistant(api, 'Protocols Summary')
        protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
        protocolsSummary.CheckCondition('Sessions Up', StatViewAssistant.EQUAL, len(api.Vport.find(Name="^Tx"))+len(api.Vport.find(Name="^Rx")))
    except Exception as e:
        raise Exception(str(e))


def start_traffic(api):
    print('\t\t\tstarting traffic from ixia')
    api.Traffic.StartStatelessTrafficBlocking()
    ti = StatViewAssistant(api, 'Traffic Item Statistics')
    try:
        ti.CheckCondition('Tx Frames', StatViewAssistant.GREATER_THAN, 0)
    except Exception as ex:
        raise Exception("Stats Missing")


def stop_traffic(api, blocking=True):
    print('\t\t\tStopping traffic')
    api.Traffic.StopStatelessTrafficBlocking()
    attempts = 0
    while api.Traffic.IsTrafficRunning and attempts < 18:
        print("\t\t\tTraffic is Still Running")
        time.sleep(5)
        attempts += 1
    if attempts > 18:
        raise Exception("Traffic not stopped after 90 Seconds")
    print("\t\t\tTraffic stopped")
    ti = StatViewAssistant(api, 'Traffic Item Statistics')
    try:
        ti.CheckCondition('Tx Frames', StatViewAssistant.GREATER_THAN, 0)
    except Exception as ex:
        raise Exception("Stats Missing")


def seconds_elapsed(start_seconds):
    return int(round(time.time() - start_seconds))


def timed_out(start_seconds, timeout):
    return seconds_elapsed(start_seconds) > timeout


def wait_for(func, condition_str, interval_seconds=None, timeout_seconds=None):
    """
    Keeps calling the `func` until it returns true or `timeout_seconds` occurs
    every `interval_seconds`. `condition_str` should be a constant string
    implying the actual condition being tested.
    Usage
    -----
    If we wanted to poll for current seconds to be divisible by `n`, we would
    implement something similar to following:
    ```
    import time
    def wait_for_seconds(n, **kwargs):
        condition_str = 'seconds to be divisible by %d' % n
        def condition_satisfied():
            return int(time.time()) % n == 0
        poll_until(condition_satisfied, condition_str, **kwargs)
    ```
    """
    if interval_seconds is None:
        interval_seconds = settings.interval_seconds
    if timeout_seconds is None:
        timeout_seconds = settings.timeout_seconds
    start_seconds = int(time.time())

    print("\n\nWaiting for %s ..." % condition_str)
    while True:
        res = func()
        if res:
            print("Done waiting for %s" % condition_str)
            break
        if res is None:
            raise Exception("Wait aborted for %s" % condition_str)
        if timed_out(start_seconds, timeout_seconds):
            msg = "Time out occurred while waiting for %s" % condition_str
            raise Exception(msg)

        time.sleep(interval_seconds)


def get_all_stats(api, print_output=True):
    """
    Returns all port and flow stats
    """
    print("Fetching all port stats ...")
    request = api.metrics_request()
    request.port.port_names = []
    port_results = api.get_metrics(request).port_metrics
    if port_results is None:
        port_results = []

    print("Fetching all flow stats ...")
    request = api.metrics_request()
    request.flow.flow_names = []
    flow_results = api.get_metrics(request).flow_metrics
    if flow_results is None:
        flow_results = []

    if print_output:
        print_stats(port_stats=port_results, flow_stats=flow_results)

    return port_results, flow_results


def total_frames_ok(port_results, flow_results, expected):
    port_tx = sum([p.frames_tx for p in port_results])
    port_rx = sum([p.frames_rx for p in port_results])
    flow_rx = sum([f.frames_rx for f in flow_results])

    return port_tx == port_rx == flow_rx == expected


def total_bytes_ok(port_results, flow_results, expected):
    port_tx = sum([p.bytes_tx for p in port_results])
    port_rx = sum([p.bytes_rx for p in port_results])
    flow_rx = sum([f.bytes_rx for f in flow_results])

    return port_tx == port_rx == flow_rx == expected


def print_stats(port_stats=None, flow_stats=None, clear_screen=None):
    if clear_screen is None:
        clear_screen = settings.dynamic_stats_output

    if clear_screen:
        os.system("clear")

    if port_stats is not None:
        row_format = "{:>15}" * 6
        border = "-" * (15 * 6 + 5)
        print("\nPort Stats")
        print(border)
        print(
            row_format.format(
                "Port",
                "Tx Frames",
                "Tx Bytes",
                "Rx Frames",
                "Rx Bytes",
                "Tx FPS",
            )
        )
        for stat in port_stats:
            print(
                row_format.format(
                    stat.name,
                    stat.frames_tx,
                    stat.bytes_tx,
                    stat.frames_rx,
                    stat.bytes_rx,
                    stat.frames_tx_rate,
                )
            )
        print(border)
        print("")
        print("")

    if flow_stats is not None:
        row_format = "{:>15}" * 3
        border = "-" * (15 * 3 + 5)
        print("Flow Stats")
        print(border)
        print(row_format.format("Flow", "Rx Frames", "Rx Bytes"))
        for stat in flow_stats:
            print(row_format.format(stat.name, stat.frames_rx, stat.bytes_rx))
        print(border)
        print("")
        print("")


def check_warnings(response):
    if response.warnings:
        print("Warning: %s" % str(response.warnings))


def get_all_captures(api, cfg):
    """
    Returns a dictionary where port name is the key and value is a list of
    frames where each frame is represented as a list of bytes.
    """
    cap_dict = {}
    for name in get_capture_port_names(cfg):
        print("Fetching captures from port %s" % name)
        request = api.capture_request()
        request.port_name = name
        pcap_bytes = api.get_capture(request)

        cap_dict[name] = []
        for ts, pkt in dpkt.pcap.Reader(pcap_bytes):
            if sys.version_info[0] == 2:
                cap_dict[name].append([ord(b) for b in pkt])
            else:
                cap_dict[name].append(list(pkt))

    return cap_dict


def get_capture_port_names(cfg):
    """
    Returns name of ports for which capture is enabled.
    """
    names = []
    for cap in cfg.captures:
        if cap._properties.get("port_names"):
            for name in cap.port_names:
                if name not in names:
                    names.append(name)

    return names


def mac_or_ip_to_num(mac_or_ip_addr, mac=True):
    """
    Example:
    mac_or_ip_to_num('00:0C:29:E3:53:EA')
    returns: 52242371562
    mac_or_ip_to_num('10.1.1.1', False)
    returns: 167837953
    """
    sep = ":" if mac else "."
    addr = []
    if mac:
        addr = mac_or_ip_addr.split(sep)
    else:
        addr = ["{:02x}".format(int(i)) for i in mac_or_ip_addr.split(sep)]
    return int("".join(addr), 16)


def num_to_mac_or_ip(mac_or_ip_addr, mac=True):
    """
    Example:
    num_to_mac_or_ip(52242371562)
    returns: '00:0C:29:E3:53:EA'
    num_to_mac_or_ip(167837953, False)
    returns: '10.1.1.1'
    """
    sep = ":" if mac else "."
    fmt = "{:012x}" if mac else "{:08x}"
    rng = 12 if mac else 8
    mac_or_ip = fmt.format(mac_or_ip_addr)
    addr = []
    for i in range(0, rng, 2):
        if mac:
            addr.append(mac_or_ip[i] + mac_or_ip[i + 1])
        else:
            addr.append(str(int(mac_or_ip[i] + mac_or_ip[i + 1], 16)))
    return sep.join(addr)


def mac_or_ip_addr_from_counter_pattern(start_addr, step, count, up, mac=True):
    """
    Example:
    mac_or_ip_addr_from_counter_pattern('10.1.1.1', '0.0.1.1', 2, True, False)
    returns: ['00:0C:29:E3:53:EA', '00:0C:29:E3:54:EA']
    mac_or_ip_addr_from_counter_pattern('10.1.1.1', '0.0.1.1', 2, True, False)
    teturns: ['10.1.1.1', '10.1.2.2']
    """
    addr_list = []
    for num in range(count):
        addr_list.append(start_addr)
        if up:
            start_addr = mac_or_ip_to_num(start_addr, mac) + mac_or_ip_to_num(
                step, mac
            )
        else:
            start_addr = mac_or_ip_to_num(start_addr, mac) - mac_or_ip_to_num(
                step, mac
            )
        start_addr = num_to_mac_or_ip(start_addr, mac)
    return addr_list


def flow_transmit_matches(flow_results, state):
    return len(flow_results) == all(
        [f.transmit == state for f in flow_results]
    )


def to_hex(lst):
    """
    Takes lst of data from packet capture and converts to hex
    Ex: [11,184] is converted to 0xbb8
        [0,30] is converted to 0x1e
    """
    from functools import reduce

    value = reduce(lambda x, y: hex(x) + hex(y), lst)
    value = value[0:2] + value[2:].replace("0x", "").lstrip("0")
    return value
