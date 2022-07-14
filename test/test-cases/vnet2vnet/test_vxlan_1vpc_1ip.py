import inspect
import json
import sys
import time
from copy import deepcopy

import pytest
import requests
from ixload import IxLoadUtils as IxLoadUtils
from ixnetwork_restpy import SessionAssistant
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from tabulate import tabulate
from testdata_vxlan_1vpc_1ip import testdata
from future.utils import iteritems

data = []


@pytest.fixture(scope="session")
def setup(smartnics, tbinfo):
    """Gather all required test information from DUT and tbinfo.
        A Dictionary with required test information.
    """
    setup_information = {"nics": smartnics, "tbinfo": tbinfo, }
    smartnics.configure_target(testdata)
    yield setup_information


class Test_Dpu:

    def teardown_method(self, method):
        print("Clean up configuration")

    def test_pps_001(self, setup, utils):
        """
            Description: Verify ip address can be configured in SVI.
            Topo: DUT02 ============ DUT01
            Dev. status: DONE
        """
        captions = ["PPS", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]
        tiNo = 2
        testbed = setup["tbinfo"]
        snic = setup["nics"]

        def createTI(name, src, dst, scalable=False):
            trafficItem = ixnetwork.Traffic.TrafficItem.find(Name="^%s$" % name)
            if len(trafficItem) == 0:
                trafficItem = ixnetwork.Traffic.TrafficItem.add(Name=name, TrafficType='ipv4', BiDirectional=True)  # BiDirectional=True

            if scalable:
                endpoint_set = trafficItem.EndpointSet.add(ScalableSources=src, ScalableDestinations=dst)
            else:
                endpoint_set = trafficItem.EndpointSet.add(Sources=src, Destinations=dst)
            ce = trafficItem.ConfigElement.find()[-1]

            ce.FrameRate.update(Type='framesPerSecond', Rate=500000)
            ce.TransmissionControl.Type = 'continuous'
            ce.FrameRateDistribution.PortDistribution = 'applyRateToAll'
            ce.FrameSize.FixedSize = 128
            udp_srcport = ce.Stack.find(StackTypeId="udp").Field.find(FieldTypeId="udp.header.srcPort")
            udp_srcport.Auto = False
            udp_srcport.SingleValue = 50687
            udp_len = ce.Stack.find(StackTypeId="udp").Field.find(FieldTypeId="udp.header.length")
            udp_len.Auto = False
            udp_len.SingleValue = 80

            udp_template = ixnetwork.Traffic.ProtocolTemplate.find(StackTypeId='^udp$')
            ipv4_template = ce.Stack.find(TemplateName="ipv4-template.xml")[-1]
            inner_udp = ce.Stack.read(ipv4_template.AppendProtocol(udp_template))
            trafficItem.Tracking.find()[0].TrackBy = ['trackingenabled0', 'sourceDestEndpointPair0']
            inn_sp = inner_udp.Field.find(DisplayName='^UDP-Source-Port')
            inn_dp = inner_udp.Field.find(DisplayName='^UDP-Dest-Port')
            inn_sp.Auto = False
            inn_dp.Auto = False
            inn_sp.SingleValue = 10000
            inn_dp.SingleValue = 10000
            trafficItem.Generate()
            return trafficItem

        def find_boundary():
            global data
            hls = trafficItem.HighLevelStream.find()

            def boundary_check(test_boundary_val):
                for hl in hls:
                    hl.FrameRate.update(Type='framesPerSecond', Rate=test_boundary_val)

                utils.start_traffic(ixnetwork)
                utils.ss("\t\t\tLet Traffic run for  ", 20)
                utils.stop_traffic(ixnetwork)
                utils.ss("\t\t\tLets wait for stats to settle down for ", 10)
                #print("\tVerify Traffic stats")
                ti = StatViewAssistant(ixnetwork, 'Traffic Item Statistics')
                if float(ti.Rows[0]['Frames Delta']) == float(0):
                    ixnetwork.ClearStats()
                    return False
                else:
                    ixnetwork.ClearStats()
                    return True

            poss_val, step, tolerance, pass_val, fail_val = int(20000000 / tiNo), int(20000000 / tiNo), 1000000, None, None

            while True:
                print("="*50)
                print(f"Test running for {utils.human_format(poss_val * tiNo)} framesPerSecond")
                print(" POSSPASS|FAIL|PASS=", poss_val, fail_val, pass_val)
                print("="*50)
                result = boundary_check(poss_val)
                row = utils.printStats(ixnetwork, "Traffic Item Statistics", {"Traffic Item Statistics": {'transpose': False, 'toprint': ["Traffic Item", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]}})
                utils.printStats(ixnetwork, "Flow Statistics", {"Flow Statistics": {'transpose': False, 'toprint': ["Traffic Item", "Source/Dest Endpoint Pair", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]}})
                data.append([utils.human_format(poss_val * tiNo)]+row[1:])

                if result:
                    fail_val = poss_val
                    if pass_val:
                        poss_val = int((pass_val+fail_val)/2)
                    else:
                        poss_val = int(poss_val/2)
                else:  # we need to continue
                    pass_val = poss_val
                    if not fail_val:
                        poss_val = pass_val+step
                    else:
                        poss_val = int((pass_val+fail_val)/2)
                if fail_val:
                    if abs(fail_val-poss_val) <= tolerance:
                        print("Final Possible Boundry is ", pass_val * tiNo)
                        break
        obj_map = {}
        for k in testdata["val_map"].keys():
            obj_map[k] = deepcopy({})
        val_map = testdata["val_map"]

        print('connect to a test tool platform')
        tb=testbed['stateless'][0]
        session_assistant = SessionAssistant(
            IpAddress=tb['server'][0]['addr'],
            RestPort=tb['server'][0]['rest'],
            UserName=testbed["CR"][tb['server'][0]['addr']]['user'],
            Password=testbed["CR"][tb['server'][0]['addr']]['password'],
            SessionName="MIRTest",
            ClearConfig=True
        )

        ixnetwork = session_assistant.Ixnetwork
        portList = [{'xpath': '/vport[%s]' % str(indx+1), 'name': 'VTEP_0%d' % (indx+1), 'location': '%s;%s;%s' % tuple(p)} for indx, p in enumerate(tb['tgen'][0]['interfaces'])]
        ixnetwork.ResourceManager.ImportConfig(json.dumps(portList), False)
        vports = list(ixnetwork.Vport.find())
        tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "ieeeL1Defaults": False} for vp in vports]
        ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)
        tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "enableAutoNegotiation": False} for vp in vports]
        ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)
        tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "enableRsFec": False, "autoInstrumentation": "floating"} for vp in vports]
        ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)

        for ed in [1, 2]:
            # OUTER DG
            obj_map[ed]["oeth"] = ixnetwork.Topology.add(Ports=vports[ed-1], Name="TG_%d" % ed).DeviceGroup.add(Name="O_DG_%d" % ed, Multiplier=1).Ethernet.add(Name='ETH_%d' % ed)
            obj_map[ed]["oipv4"] = obj_map[ed]["oeth"].Ipv4.add(Name="IPv4%d" % ed)
            obj_map[ed]["obgp"] = obj_map[ed]["oipv4"].BgpIpv4Peer.add(Name="BGP_%d" % ed)

            # OUTER NG
            ng = ixnetwork.Topology.find().DeviceGroup.find(Name="O_DG_%d" % ed).NetworkGroup.add(Name="NG_%d" % ed, Multiplier=val_map[ed]["oipv4pool"]["multiplier"])
            obj_map[ed]["oipv4pool"] = ng.Ipv4PrefixPools.add(NumberOfAddresses='1')

            # DG Behing Outer NG
            obj_map[ed]["dg_b_ong"] = ng.DeviceGroup.add(Name="DG_B_ONG_%d" % ed, Multiplier=1)
            obj_map[ed]["dg_b_ong_eth"] = obj_map[ed]["dg_b_ong"].Ethernet.add(Name='ETH_%d' % ed)
            obj_map[ed]["dg_b_ong_ipv4"] = obj_map[ed]["dg_b_ong_eth"].Ipv4.add(Name='IPv4_%d' % ed)
            obj_map[ed]["vxlan"] = obj_map[ed]["dg_b_ong_ipv4"].Vxlan.add(Name="VXLAN_%d" % ed)

            # INNER DG
            obj_map[ed]["iipv4"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Multiplier=1).Ethernet.add().Ipv4.add()
            obj_map[ed]["ieth"] = obj_map[ed]["iipv4"].parent

        for ed in [1, 2]:
            # OUTER DG
            obj_map[ed]["oeth"].Mac.Increment(start_value=val_map[ed]["oeth"]["mac"],  step_value='00:00:00:00:00:01')
            obj_map[ed]["oipv4"].Address.Increment(start_value=val_map[ed]["oipv4"]["ip"],  step_value='0.0.0.1')
            obj_map[ed]["oipv4"].GatewayIp.Increment(start_value=val_map[ed]["oipv4"]["gip"], step_value='0.0.0.1')
            obj_map[ed]["oipv4"].ResolveGateway.Single(False)
            obj_map[ed]["oipv4"].ManualGatewayMac.Single(val_map[ed]["oipv4"]["mac"])

            # BGP
            obj_map[ed]["obgp"].DutIp.Single(val_map[ed]["obgp"]["dip"])
            obj_map[ed]["obgp"].LocalAs2Bytes.Single(val_map[ed]["obgp"]["las"])
            obj_map[ed]["obgp"].EnableBgpIdSameasRouterId.Single(True)
            obj_map[ed]["obgp"].FilterIpV4Unicast.Single(True)
            obj_map[ed]["obgp"].FilterEvpn.Single(True)

            #obj_map[ed]["bgp"].IpVrfToIpVrfType = 'interfacefullWithUnnumberedCorefacingIRB'
            #obj_map[ed]["bgp"].EthernetSegmentsCountV4 = 128
            obj_map[ed]["obgp"].BgpId.Single(val_map[ed]["obgp"]["bid"])
            obj_map[ed]["obgp"].Type.Single('external')

            # OUTER NG
            obj_map[ed]["oipv4pool"].NetworkAddress.Increment(start_value=val_map[ed]["oipv4pool"]["ip"], step_value='0.0.0.1')
            obj_map[ed]["oipv4pool"].PrefixLength.Single(32)
            ipv4_behindvxlan = obj_map[ed]["vxlan"].parent
            ipv4_behindvxlan.Address.Increment(start_value=val_map[ed]["oipv4pool"]["ip"],  step_value='0.0.0.1')
            ipv4_behindvxlan.ResolveGateway.Single(False)

            # DG Behing Outer NG
            # DG Behind Outer NG Ethernet
            eth = obj_map[ed]["dg_b_ong_ipv4"].parent
            eth.Mac.Increment(start_value=val_map[ed]["dg_b_ong_eth"]["mac"], step_value='00:00:00:00:00:01')

            # DG Behind Outer NG IPv4
            for s in obj_map[ed]["dg_b_ong_ipv4"].Address.Steps:
                s.Enabled = False
            obj_map[ed]["dg_b_ong_ipv4"].Address.Increment(start_value=val_map[ed]["dg_b_ong_ipv4"]["ip"],  step_value='0.0.0.1')
            obj_map[ed]["dg_b_ong_ipv4"].GatewayIp.Increment(start_value=val_map[ed]["dg_b_ong_ipv4"]["gip"], step_value='0.0.0.1')
            obj_map[ed]["dg_b_ong_ipv4"].Prefix.Single(32)

            # VXLAN
            obj_map[ed]["vxlan"].EnableStaticInfo = True
            obj_map[ed]["vxlan"].VxlanStaticInfo.MacStaticConfig.Single(True)
            obj_map[ed]["vxlan"].VxlanStaticInfo.RemoteVmStaticIpv4.ValueList(val_map[ed]["vxlan"]["RemoteVmStaticIpv4"])
            obj_map[ed]["vxlan"].VxlanStaticInfo.RemoteVmStaticMac.Increment(start_value=val_map[ed]["vxlan"]["RemoteVmStaticMac"], step_value='00:00:00:00:00:00')  # This need to based OuterNG mutiplier
            obj_map[ed]["vxlan"].VxlanStaticInfo.RemoteVmStaticMac.Steps[0].Enabled = True
            obj_map[ed]["vxlan"].VxlanStaticInfo.RemoteVmStaticMac.Steps[0].Step = '00:00:00:00:00:01'

            obj_map[ed]["vxlan"].VxlanStaticInfo.RemoteVtepIpv4.Single(val_map[ed]["vxlan"]["RemoteVtepIpv4"])
            obj_map[ed]["vxlan"].Vni.Increment(start_value=val_map[ed]["vxlan"]["Vni"], step_value=1)
            obj_map[ed]["vxlan"].VxlanStaticInfo.SuppressArp.Single(True)
            obj_map[ed]["vxlan"].StaticInfoCount = val_map[ed]["vxlan"]["StaticInfoCount"]

            # Inner Inner IPv4
            obj_map[ed]["ieth"].Mac.Increment(start_value=val_map[ed]["ieth"]["mac"],  step_value='00:00:00:00:00:01')
            obj_map[ed]["iipv4"].Address.Increment(start_value=val_map[ed]["iipv4"]["ip"],  step_value='0.0.1.0')
            obj_map[ed]["iipv4"].GatewayIp.Increment(start_value=val_map[ed]["iipv4"]["gip"], step_value='0.0.1.0')

        print('Start All Protocols')
        ixnetwork.StartAllProtocols(Arg1='sync')
        try:
            print('Verify protocol sessions')
            protocolsSummary = StatViewAssistant(ixnetwork, 'Protocols Summary')
            protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
            protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
        except Exception as e:
            raise Exception(str(e))

        print("Create Traffic OneIPOneVPC")
        trafficItem = createTI("OneIPOneVPC", obj_map[1]["iipv4"], obj_map[2]["iipv4"])

        trafficItem.Generate()
        ixnetwork.Traffic.Apply()
        utils.start_traffic(ixnetwork)
        time.sleep(30)
        utils.stop_traffic(ixnetwork)

        find_boundary()
        print(tabulate(data, headers=captions, tablefmt="psql"))

    def test_cps_001(self, setup, create_ixload_session_url):
        """
            Description: Verify ip address can be configured in SVI.
            Topo: DUT02 ============ DUT01
            Dev. status: DONE
        """
        session = create_ixload_session_url
        connection = session['connection']
        test_settings = session['test_settings']

        def _patch_test_setting(url_patch_dict, setting):

            url = url_patch_dict['base_url'] + url_patch_dict[setting]['url']

            return requests.patch(url, json=url_patch_dict[setting]['json'])

        def _get_timeline_link(timelines, timeline_key):

            link = ""
            link_test = ""

            for elem in timelines:
                if elem['name'] in timeline_key:
                    link_init = elem['links'][0]['href']
                    link_init_list = link_init.split("/")
                    link_init_list.pop(len(link_init_list) - 1)
                    link_test = '/'.join(link_init_list)

            shaved = link_test.split("/")
            for i in range(5):
                shaved.pop(0)
            shaved.insert(0, "")
            link = "/".join(shaved)

            return link

        def _set_timeline_settings(test_settings, rampDownTime, sustainTime):

            timeline_url = 'http://' + test_settings.gatewayServer + ":{}".format(
                test_settings.gatewayPort) + '/api/v1/' + session_url + '/ixload/test/activeTest/timelineList'
            response = requests.get(timeline_url, headers=headers)
            timelines = response.json()

            timeline1_url = 'http://' + test_settings.gatewayServer + ":{}".format(
                test_settings.gatewayPort) + '/api/v1/' + session_url + \
                            _get_timeline_link(timelines, "Timeline1")
            timeline1_settings = {"rampDownTime": rampDownTime, "sustainTime": sustainTime}
            requests.patch(timeline1_url, json=timeline1_settings)

            timeline2_url = 'http://' + test_settings.gatewayServer + ":{}".format(
                test_settings.gatewayPort) + '/api/v1/' + session_url + \
                            _get_timeline_link(timelines, "Timeline2")
            timeline2_settings = {"rampDownTime": rampDownTime, "sustainTime": sustainTime}
            requests.patch(timeline2_url, json=timeline2_settings)

            timeline_matchLongest_url = 'http://' + test_settings.gatewayServer + ":{}".format(
                test_settings.gatewayPort) + '/api/v1/' + session_url + \
                                        _get_timeline_link(timelines, "<Match Longest>")
            matchLongest_settings = {"sustainTime": sustainTime}
            requests.patch(timeline_matchLongest_url, json=matchLongest_settings)

            return

        def _getTestCurrentState(connection, sessionUrl):

            activeTestUrl = "%s/ixload/test/activeTest" % (sessionUrl)
            testObj = connection.httpGet(activeTestUrl)

            return testObj.currentState

        def _print_final_table(test_run_results):
            stat_table = []
            stat_columns = ["It", "Objective CPS", "Obtained CPS", "HTTP Requests Failed", "TCP Retries",
                            "TCP Resets TX", "TCP Resets RX", "Pass/Fail"]
            for iter in test_run_results:
                stat_table.append(iter)
            print("\n%s" % tabulate(stat_table, headers=stat_columns, tablefmt='psql', floatfmt=".2f"))

        def _poll_stats(connection, sessionUrl, watchedStatsDict, pollingInterval=4):

            statSourceList = list(watchedStatsDict)

            # retrieve stats for a given stat dict
            # all the stats will be saved in the dictionary below

            # statsDict format:
            # {
            #   statSourceName: {
            #                       timestamp:  {
            #                                       statCaption : value
            #                                   }
            #                   }
            # }
            stats_dict = {}

            # remember the timstamps that were already collected - will be ignored in future
            collectedTimestamps = {}  # format { statSource : [2000, 4000, ...] }
            testIsRunning = True

            # check stat sources
            for statSource in statSourceList[:]:
                statSourceUrl = "%s/ixload/stats/%s/values" % (sessionUrl, statSource)
                statSourceReply = connection.httpRequest("GET", statSourceUrl)
                if statSourceReply.status_code != 200:
                    statSourceList.remove(statSource)

            # check the test state, and poll stats while the test is still running
            while testIsRunning:

                # the polling interval is configurable. by default, it's set to 4 seconds
                time.sleep(pollingInterval)

                for statSource in statSourceList:
                    valuesUrl = "%s/ixload/stats/%s/values" % (sessionUrl, statSource)

                    valuesObj = connection.httpGet(valuesUrl)
                    valuesDict = valuesObj.getOptions()

                    # get just the new timestamps - that were not previously retrieved in another stats polling iteration
                    newTimestamps = [int(timestamp) for timestamp in list(valuesDict) if
                                     timestamp not in collectedTimestamps.get(statSource, [])]
                    newTimestamps.sort()

                    for timestamp in newTimestamps:
                        timeStampStr = str(timestamp)

                        collectedTimestamps.setdefault(statSource, []).append(timeStampStr)

                        timestampDict = stats_dict.setdefault(statSource, {}).setdefault(timestamp, {})

                        # save the values for the current timestamp, and later print them
                        for caption, value in iteritems(valuesDict[timeStampStr].getOptions()):
                            if caption in watchedStatsDict[statSource]:
                                timestampDict[caption] = value
                                stat_table_row = []
                                for table_row in timestampDict.keys():
                                    stat_table_row.append(table_row)
                                table = []
                                columns = ['Stat Source', 'Time Stamp', 'Stat Name', 'Value']
                                for i, stat in enumerate(stat_table_row):
                                    table.append([statSource, timeStampStr, stat, timestampDict[stat]])
                                # print("\n%s" % tabulate(table, headers=columns, tablefmt='psql'))

                testIsRunning = _getTestCurrentState(connection, sessionUrl) == "Running"

            print("Stopped receiving stats.")
            return stats_dict

        def _get_stats_global(stats_dict):
            stats_global = []

            for key in stats_dict['HTTPClient'].keys():
                if key in stats_dict['HTTPClient'] and key in stats_dict['HTTPServer']:
                    stats_global.append([key, stats_dict['HTTPClient'][key]['HTTP Simulated Users'],
                                         stats_dict['HTTPClient'][key]['HTTP Concurrent Connections'],
                                         stats_dict['HTTPClient'][key]['TCP CPS'],
                                         stats_dict['HTTPClient'][key]['HTTP Connect Time (us)'],
                                         stats_dict['HTTPServer'][key]['HTTP Requests Failed'],
                                         stats_dict['HTTPServer'][key]['TCP Retries'],
                                         stats_dict['HTTPServer'][key]['TCP Resets Sent'],
                                         stats_dict['HTTPServer'][key]['TCP Resets Received']])

            return stats_global

        def _check_for_error_stats(test_stats, error_type):

            error_dict = {
                error_type: {
                    "first_time": 0,
                    "last_time": 0,
                    "num_of_seq_timestamps": 0
                }
            }

            timestamps_l = [i[0] for i in test_stats]
            errors_l = [i[1] for i in test_stats]
            seen = set()
            dupes = {}

            first_time = 0
            for i, x in enumerate(errors_l):
                if x in seen:
                    dupes.setdefault(x, []).append(i)
                else:
                    seen.add(x)

            # insert timestamp index location at beginning of list
            for key in dupes.keys():
                dupes[key].insert(0, dupes[key][0] - 1)

            # make list of lens of each duplicates, then remove and remove rest of error entries from dupes dict
            errors_l = [len(dupes[x]) for x in dupes.keys()]
            max_index = errors_l.index(max(errors_l))
            errors_l.pop(max_index)

            # keep only the highest number of stable
            for i, key in enumerate(list(dupes)):
                if i != max_index:
                    dupes.pop(key, None)

            for key in dupes.keys():
                error_dict[error_type]["first_time"] = dupes[key][0]
                error_dict[error_type]["last_time"] = dupes[key][-1]

                if list(dupes.keys())[0] != 0:
                    error_dict[error_type]["num_of_seq_timestamps"] = len(dupes[key])
                else:
                    error_dict[error_type]["num_of_seq_timestamps"] = 0

            return error_dict

        def _get_max_cps(test_stats, cps_stats):

            cps_list = []
            for cps in cps_stats:
                cps_list.append(cps[1])

            stats = deepcopy(cps_list)
            for i, elem in enumerate(stats):
                if elem == '""':
                    stats[i] = 0

            stats.sort()
            max_cps = stats[-1]
            cps_max_w_ts = cps_stats[cps_list.index(max_cps)]

            return cps_max_w_ts

        def _get_effective_cps(cps_stats, http_requests_dict, tcp_retries_dict, tcp_resets_tx_dict, tcp_resets_rx_dict):

            error_list = [http_requests_dict, tcp_retries_dict, tcp_resets_tx_dict, tcp_resets_rx_dict]
            num_of_timestamps = len(cps_stats)

            seq_l = [list(x.values())[0]["num_of_seq_timestamps"] for x in error_list]
            error_list[seq_l.index(max(seq_l))]
            key = list(error_list[seq_l.index(max(seq_l))].keys())[0]
            first_time = error_list[seq_l.index(max(seq_l))][key]["first_time"]
            last_time = error_list[seq_l.index(max(seq_l))][key]["last_time"]

            effective_cps_ts = {
                "first_time": cps_stats[first_time][0],
                "last_time": cps_stats[last_time][0]
            }

            if max(seq_l) != 0:
                avg = 0
                effective_cps_l = []
                for i, cps in enumerate(cps_stats):
                    if i >= first_time and i <= last_time:
                        effective_cps_l.append(cps)
                        avg += cps[1]
                effective_cps = avg / error_list[seq_l.index(max(seq_l))][key]["num_of_seq_timestamps"]
            else:
                effective_cps = 0
                effective_cps_ts = {"first_time": 0, "last_time": cps_stats[last_time][0]}

            return effective_cps, effective_cps_ts

        def _get_latency_ranges(test_stats):

            latency_stats = {
                "latency_min": 0,
                "latency_max": 0,
                "latency_avg": 0
            }

            only_lat_stats = []
            for lat_stat in test_stats:
                if lat_stat[4] == '""':
                    lat_stat[4] = 0
                only_lat_stats.append(lat_stat[4])

            latency_stats["latency_min"] = min(only_lat_stats)
            latency_stats["latency_max"] = max(only_lat_stats)

            lat_addr = 0
            for elem in only_lat_stats:
                lat_addr += elem

            latency_stats["latency_avg"] = lat_addr / len(only_lat_stats)

            return latency_stats

        def _get_testrun_results(stats_dict):

            stats_global = _get_stats_global(stats_dict)

            failures_dict = {"http_requests_failed": 0, "tcp_retries": 0, "tcp_resets_tx": 0,
                             "tcp_resets_rx": 0, "total": 0}

            # get and compare stats
            http_requests_failed_l = [[x[0], x[5]] for x in stats_global]
            http_requests_failed = max([x[1] for x in http_requests_failed_l])
            failures_dict["http_requests_failed"] = http_requests_failed
            # http_requests_dict = _check_for_error_stats(http_requests_failed_l, "http_requests_failed")

            tcp_retries_l = [[x[0], x[6]] for x in stats_global]
            tcp_retries = max([x[1] for x in tcp_retries_l])
            failures_dict["tcp_retries"] = tcp_retries
            # tcp_retries_dict = _check_for_error_stats(tcp_retries_l, "tcp_retries")

            tcp_resets_tx_l = [[x[0], x[7]] for x in stats_global]
            tcp_resets_tx = max([x[1] for x in tcp_resets_tx_l])
            failures_dict["tcp_resets_tx"] = tcp_resets_tx
            # tcp_resets_tx_dict = _check_for_error_stats(tcp_resets_tx_l, "tcp_resets_tx")

            tcp_resets_rx_l = [[x[0], x[8]] for x in stats_global]
            tcp_resets_rx = max([x[1] for x in tcp_resets_rx_l])
            failures_dict["tcp_resets_rx"] = tcp_resets_rx
            # tcp_resets_rx_dict = _check_for_error_stats(tcp_resets_rx_l, "tcp_resets_rx")

            failures = http_requests_failed + tcp_retries + tcp_resets_tx + tcp_resets_rx
            failures_dict["total"] = failures

            cps_stats = [[x[0], x[3]] for x in stats_global]
            cps_max_w_ts = _get_max_cps(stats_global, cps_stats)
            cps_max = cps_max_w_ts[1]
            # effective_cps, effective_cps_ts = _get_effective_cps(cps_stats, http_requests_dict, tcp_retries_dict,
            #                                                     tcp_resets_tx_dict, tcp_resets_rx_dict)

            latency_ranges = _get_latency_ranges(stats_global)

            return failures_dict, cps_max, cps_max_w_ts, latency_ranges

        def _print_stat_table(cps_max_w_ts, failures_dict, latency_ranges):

            stat_table = []
            stat_columns = ["Timestamp (s)", "TCP Max CPS", "Total Failures"]
            stat_table.append([int(cps_max_w_ts[0]) / 1000, int(cps_max_w_ts[1]), failures_dict["total"]])

            stat_f_table = []
            stat_f_columns = ["HTTP Requests Failed", "TCP Retries", "TCP Resets TX", "TCP Resets RX"]
            stat_f_table.append([failures_dict["http_requests_failed"], failures_dict["tcp_retries"],
                                 failures_dict["tcp_resets_tx"], failures_dict["tcp_resets_rx"]])

            lat_table = []
            lat_table.append(
                [latency_ranges["latency_min"], latency_ranges["latency_max"], latency_ranges["latency_avg"]])
            lat_stat_columns = ["Connect Time min (us)", "Connect Time max (us)", "Connect Time avg (us)"]

            print("\n%s" % tabulate(stat_table, headers=stat_columns, tablefmt='psql'))
            print("\n%s" % tabulate(stat_f_table, headers=stat_f_columns, tablefmt='psql'))
            print("\n%s" % tabulate(lat_table, headers=lat_stat_columns, tablefmt='psql'))

        def _run_cps_search(connection, session_url, MAX_CPS, MIN_CPS,
                            threshold, target_failures, test_settings, start_value=0):

            test_run_results = []
            test_value = start_value
            test_iteration = 1
            while ((MAX_CPS - MIN_CPS) > threshold):
                test_result = ""
                IxLoadUtils.log(
                    "----Test Iteration %d------------------------------------------------------------------"
                    % test_iteration)
                old_value = test_value
                IxLoadUtils.log("Testing CPS Objective = %d" % test_value)
                kActivityOptionsToChange = {
                    # format: { activityName : { option : value } }
                    "HTTPClient1": {
                        "enableConstraint": False,
                        "userObjectiveType": "connectionRate",
                        "userObjectiveValue": int(test_value),
                    }
                }
                IxLoadUtils.log("Updating CPS objective value settings...")
                IxLoadUtils.changeActivityOptions(connection, session_url, kActivityOptionsToChange)
                IxLoadUtils.log("CPS objective value updated.")

                IxLoadUtils.log("Applying config...")
                IxLoadUtils.applyConfiguration(connection, session_url)

                # IxLoadUtils.log("Saving rxf")
                # IxLoadUtils.saveRxf(connection, session_url, "C:\\automation\\1ip_test.rxf")

                IxLoadUtils.log("Starting the test...")
                IxLoadUtils.runTest(connection, session_url)
                IxLoadUtils.log("Test started.")

                IxLoadUtils.log("Test running and extracting stats...")
                stats_dict = _poll_stats(connection, session_url, stats_test_settings)
                IxLoadUtils.log("Test finished.")

                failures_dict, cps_max, cps_max_w_ts, latency_ranges = _get_testrun_results(stats_dict)

                _print_stat_table(cps_max_w_ts, failures_dict, latency_ranges)

                if cps_max < test_value:
                    test = False
                else:
                    test = True

                if test:
                    IxLoadUtils.log('Test Iteration Pass')
                    test_result = "Pass"
                    MIN_CPS = test_value
                    test_value = (MAX_CPS + MIN_CPS) / 2
                else:
                    IxLoadUtils.log('Test Iteration Fail')
                    test_result = "Fail"
                    MAX_CPS = test_value
                    test_value = (MAX_CPS + MIN_CPS) / 2
                objective_cps = old_value
                obtained_cps = cps_max_w_ts[1]
                test_run_results.append(
                    [test_iteration, objective_cps, obtained_cps, failures_dict["http_requests_failed"],
                     failures_dict["tcp_retries"], failures_dict["tcp_resets_tx"],
                     failures_dict["tcp_resets_rx"], test_result])
                IxLoadUtils.log("Iteration Ended...")
                IxLoadUtils.log('MIN_CPS = %d' % MIN_CPS)
                IxLoadUtils.log('Current MAX_CPS = %d' % MAX_CPS)
                IxLoadUtils.log('Previous CPS Objective value = %d' % old_value)
                print(' ')
                test_iteration += 1
                IxLoadUtils.releaseConfiguration(connection, session_url)

            cps_max_w_ts[1] = MIN_CPS

            return cps_max_w_ts, failures_dict, test_run_results, latency_ranges

        # Beginning of testcase
        kCommunities = [
            # format: {option1: value1, option2: value2}
            {},  # default community with no options
            {"tcpAccelerationAllowedFlag": True},  # community with tcpAccelerationAllowedFlag set to True
        ]

        kActivities = {
            'Traffic1@Network1': ['HTTP Client'],
            'Traffic2@Network2': ['HTTP Server']
        }

        kNewCommands = {
            # format: { agent name : [ { field : value } ] }
            "HTTPClient1": [
                {
                    "commandType": "GET",
                    "destination": "Traffic2_HTTPServer1:80",
                    "pageObject": "/1b.html",
                },
            ],
        }

        stats_test_settings = {
            'HTTPClient': ['HTTP Simulated Users',
                           'HTTP Concurrent Connections',
                           'TCP CPS',
                           'HTTP Connect Time (us)',
                           ],
            'HTTPServer': ['HTTP Requests Failed',
                           'TCP Retries',
                           'TCP Resets Sent',
                           'TCP Resets Received',
                           ],
        }

        stats_dict = {}

        location = inspect.getfile(inspect.currentframe())

        headers = {'Accept': 'application/json'}
        session_url = IxLoadUtils.createNewSession(connection, test_settings.ixLoadVersion)
        base_url = 'http://' + test_settings.gatewayServer + ":{}".format(test_settings.gatewayPort) + \
                   '/api/v1/' + session_url

        url_patch_dict = {
            'base_url': base_url,
            'allow_routes': {
                'json': {"allowRouteConflicts": True},
                'url': "/ixload/preferences"
            },
            'client_vlan_settings': {
                'json': {"firstId": 101},
                'url': "/ixload/test/activeTest/communityList/0/network/stack/childrenList/2/vlanRangeList/1"
            },
            'http_version': {
                'json': {"httpVersion": 1},
                'url': "/ixload/test/activeTest/communityList/0/activityList/0/agent"
            },
            'http_tcp_conns_per_user': {
                'json': {"maxSessions": 1},
                'url': "/ixload/test/activeTest/communityList/0/activityList/0/agent"
            },
            'client_disable_tcp_tw_recycle': {
                'json': {"tcp_tw_recycle": False},
                'url': "/ixload/test/activeTest/communityList/0/network/globalPlugins/2"
            },
            'server_disable_tcp_tw_recycle': {
                'json': {"tcp_tw_recycle": False},
                'url': "/ixload/test/activeTest/communityList/1/network/globalPlugins/5"
            },
            'cps_aggregation_type': {
                'json': {"aggregationType": "kRate"},
                'url': "/ixload/stats/HTTPClient/configuredStats/229"
            },
            'cps_stat_caption': {
                'json': {"caption": "TCP CPS"},
                'url': "/ixload/stats/HTTPClient/configuredStats/229"
            }
        }

        IxLoadUtils.log('Creating communities...')
        IxLoadUtils.addCommunities(connection, session_url, kCommunities)
        IxLoadUtils.log('Communities created.')

        IxLoadUtils.log('Creating activities..')
        IxLoadUtils.addActivities(connection, session_url, kActivities)
        IxLoadUtils.log('Activities created..')

        IxLoadUtils.log("Enabling Forceful Ownership of Ports")
        IxLoadUtils.enableForcefullyTakeOwnershipAndResetPorts(connection, session_url)
        IxLoadUtils.log("Forceful Ownership Complete")

        response = _patch_test_setting(url_patch_dict, 'allow_routes')

        IxLoadUtils.log("Clearing commands %s..." % (list(kNewCommands)))
        IxLoadUtils.clearAgentsCommandList(connection, session_url, list(kNewCommands))
        IxLoadUtils.log("Command lists cleared.")

        IxLoadUtils.log("Adding IPv4 ranges ...")
        IxLoadUtils.HttpUtils.addIpRange(connection, session_url, "Traffic1@Network1", "IP-1", {"ipType": "IPv4"})
        IxLoadUtils.HttpUtils.addIpRange(connection, session_url, "Traffic2@Network2", "IP-2", {"ipType": "IPv4"})

        IxLoadUtils.log("Changing IPv4 ranges for test run ...")
        IxLoadUtils.log("Setting Client IPv4 ranges ...")
        clientIpOptionsToChange = {'count': 2, 'ipAddress': testdata['val_map'][2]['iipv4']['ip'],
                                   'prefix': testdata['val_map'][2]['iipv4']['prefix'], 'incrementBy': '1.0.0.0',
                                   'gatewayAddress': testdata['val_map'][2]['iipv4']['gip'],
                                   'gatewayIncrement': '1.0.0.0'}
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic1@Network1", "IP-1", "rangeList",
                                                 "IP-R1", clientIpOptionsToChange)

        IxLoadUtils.log("Setting Server IPv4 ranges ...")
        serverIpOptionsToChange = {'count': 2, 'ipAddress': testdata['val_map'][1]['iipv4']['ip'],
                                   'prefix': testdata['val_map'][1]['iipv4']['prefix'], 'incrementBy': '1.0.0.0',
                                   'gatewayAddress': testdata['val_map'][1]['iipv4']['gip'],
                                   'gatewayIncrement': '1.0.0.0'}
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic2@Network2", "IP-2", "rangeList",
                                                 "IP-R2", serverIpOptionsToChange)

        IxLoadUtils.log("Disabling autoMacGeneration ...")
        automac = {"autoMacGeneration": False}
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic1@Network1", "IP-1", "rangeList",
                                                 "IP-R1", automac)
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic2@Network2", "IP-2", "rangeList",
                                                 "IP-R2", automac)

        IxLoadUtils.log("Setting Client MAC and VLAN settings ...")
        vlan_enabled = {"enabled": True}
        clientMacOptionsToChange = {"mac": testdata['val_map'][2]['ieth']['mac'], "incrementBy": '00:00:00:08:00:00'}
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic1@Network1", "MAC/VLAN-1",
                                                 "macRangeList", "MAC-R1", clientMacOptionsToChange)

        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic1@Network1", "MAC/VLAN-1",
                                                 "vlanRangeList", "VLAN-R1", vlan_enabled)

        # Sku2 vlan ID
        response = _patch_test_setting(url_patch_dict, 'client_vlan_settings')

        IxLoadUtils.log("Setting Server MAC and VLAN settings ...")
        serverMacOptionsToChange = {"mac": testdata['val_map'][1]['ieth']['mac'], "incrementBy": '00:00:00:08:00:00'}
        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic2@Network2", "MAC/VLAN-2",
                                                 "macRangeList", "MAC-R2", serverMacOptionsToChange)

        IxLoadUtils.HttpUtils.changeRangeOptions(connection, session_url, "Traffic2@Network2", "MAC/VLAN-2",
                                                 "vlanRangeList", "VLAN-R3", vlan_enabled)

        IxLoadUtils.log("Disabling Unused IP ranges ...")
        kIpOptionsToChange = {
            # format : { IP Range name : { optionName : optionValue } }
            'IP-R3': {
                'count': 1,
                'enabled': False,
            },
            'IP-R4': {
                'count': 1,
                'enabled': False,
            }
        }
        IxLoadUtils.changeIpRangesParams(connection, session_url, kIpOptionsToChange)

        # Turn off TCP settings
        IxLoadUtils.log("Adjusting Test Settings, TCP, HTTP ...")
        response = _patch_test_setting(url_patch_dict, 'http_version')
        response = _patch_test_setting(url_patch_dict, 'http_tcp_conns_per_user')

        response = _patch_test_setting(url_patch_dict, 'client_disable_tcp_tw_recycle')
        response = _patch_test_setting(url_patch_dict, 'server_disable_tcp_tw_recycle')

        IxLoadUtils.log("Adjusting Test Timeline settings ...")
        rampDownTime = 10
        sustainTime = 180
        _set_timeline_settings(test_settings, rampDownTime, sustainTime)

        #  Change TCP Connections Established to CPS caption name and to use kRate aggregationType
        response = _patch_test_setting(url_patch_dict, 'cps_aggregation_type')
        response = _patch_test_setting(url_patch_dict, 'cps_stat_caption')

        IxLoadUtils.log("Adding new commands %s..." % (list(kNewCommands)))
        IxLoadUtils.addCommands(connection, session_url, kNewCommands)
        IxLoadUtils.log("Commands added.")

        IxLoadUtils.log("Clearing chassis list...")
        IxLoadUtils.clearChassisList(connection, session_url)
        IxLoadUtils.log("Chassis list cleared.")

        IxLoadUtils.log("Adding chassis %s..." % (test_settings.chassisList))
        IxLoadUtils.addChassisList(connection, session_url, test_settings.chassisList)
        IxLoadUtils.log("Chassis added.")

        IxLoadUtils.log("Assigning new ports...")
        IxLoadUtils.assignPorts(connection, session_url, test_settings.portListPerCommunity)
        IxLoadUtils.log("Ports assigned.")

        initial_objective = 3000000
        threshold = 100000
        target_failures = 1000
        MAX_CPS = 9000000
        MIN_CPS = 0
        cps_max_w_ts, failures_dict, test_run_results, latency_ranges = _run_cps_search(connection, session_url,
                                                                                        MAX_CPS,
                                                                                        MIN_CPS, threshold,
                                                                                        target_failures, test_settings,
                                                                                        initial_objective)

        IxLoadUtils.log("Test Complete Final Values")
        _print_final_table(test_run_results)

        IxLoadUtils.deleteAllSessions(connection)

