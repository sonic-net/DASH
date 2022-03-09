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
        session_assistant = SessionAssistant(
            IpAddress=testbed['novus'][0]['server'][0]['addr'],
            RestPort=testbed['novus'][0]['server'][0]['rest'],
            UserName=testbed["CR"][testbed['novus'][0]['server'][0]['addr']]['user'],
            Password=testbed["CR"][testbed['novus'][0]['server'][0]['addr']]['password'],
            SessionName="MIRTest",
            ClearConfig=True
        )

        ixnetwork = session_assistant.Ixnetwork
        portList = [{'xpath': '/vport[%s]' % str(indx+1), 'name': 'VTEP_0%d' % (indx+1), 'location': '%s;%s;%s' % tuple(p)} for indx, p in enumerate(testbed['novus'][0]['tgen'][0]['interfaces'])]
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
        #session_url = session['session_url']
        connection = session['connection']
        test_settings = session['test_settings']

        kCommunities = [
            # format: {option1: value1, option2: value2}
            {},  # default community with no options
            {"tcpAccelerationAllowedFlag": True},  # community with tcpAccelerationAllowedFlag set to True
        ]

        kActivities = {
            'Traffic1@Network1': ['HTTP Client'],
            'Traffic2@Network2': ['HTTP Server']
        }

        kIpOptionsToChange = {
            'IP-R1': {
                'count': 1,
                'ipAddress': '193.0.0.1',
                'prefix': 8,
                'incrementBy': "0.0.0.1",
                'gatewayAddress': '193.0.0.9'
            },
            'IP-R2': {
                'count': 1,
                'ipAddress': '193.0.0.9',
                'prefix': 8,
                'incrementBy': '0.0.0.1',
                'gatewayAddress': '193.0.0.1'
            }
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

        stats_dict = {
            'HTTPClient': ['TCP Connections Established',
                           'HTTP Simulated Users',
                           'HTTP Connections',
                           'HTTP Transactions',
                           'HTTP Connection Attempts'
                           ],
            'HTTPServer': ['TCP Connections Established',
                           'TCP Connection Requests Failed'
                           ]
        }

        kActivityOptionsToChange = {
            # format: { activityName : { option : value } }
            "HTTPClient1": {
                "enableConstraint": True,
                "constraintValue": 200,
                "userObjectiveType": "connectionRate",
                "userObjectiveValue": 3000000
            }
        }

        location = inspect.getfile(inspect.currentframe())

        # Added
        session_url = IxLoadUtils.createNewSession(connection, test_settings.ixLoadVersion)

        IxLoadUtils.log('Creating communities...')

        IxLoadUtils.addCommunities(connection, session_url, kCommunities)
        IxLoadUtils.log('Communities created.')

        IxLoadUtils.log("Clearing chassis list...")
        IxLoadUtils.clearChassisList(connection, session_url)
        IxLoadUtils.log("Chassis list cleared.")

        IxLoadUtils.log("Adding chassis %s..." % (test_settings.chassisList))
        IxLoadUtils.addChassisList(connection, session_url, test_settings.chassisList)
        IxLoadUtils.log("Chassis added.")

        IxLoadUtils.log("Enabling Forceful Ownership of Ports")
        IxLoadUtils.enableForcefullyTakeOwnershipAndResetPorts(connection, session_url)
        IxLoadUtils.log("Forceful Ownership Complete")

        IxLoadUtils.log('Creating activities..')
        IxLoadUtils.addActivities(connection, session_url, kActivities)
        IxLoadUtils.log('Activities created..')

        IxLoadUtils.log("Clearing commands %s..." % (list(kNewCommands)))
        IxLoadUtils.clearAgentsCommandList(connection, session_url, list(kNewCommands))
        IxLoadUtils.log("Command lists cleared.")

        IxLoadUtils.log("Updating activity options...")
        IxLoadUtils.changeActivityOptions(connection, session_url, kActivityOptionsToChange)
        IxLoadUtils.log("Updated activity options.")

        new_sustain = {'sustainTime': 30}
        new_sustain2 = {'sustainTime': 0}
        url = 'http://' + test_settings.gatewayServer + ':8080' + '/api/v1/' + session_url + \
            '/ixload/test/activeTest/timelineList'
        response = requests.get(url)
        if response.status_code == 200:
            timelineList = response.json()
            for i, elem in enumerate(timelineList):
                url2 = url + '/{}'.format(i)
                if elem['name'] == '<Match Longest>':
                    requests.patch(url2, json=new_sustain)
                else:
                    requests.patch(url2, json=new_sustain2)

        IxLoadUtils.log("Adding new commands %s..." % (list(kNewCommands)))
        IxLoadUtils.addCommands(connection, session_url, kNewCommands)
        IxLoadUtils.log("Commands added.")

        IxLoadUtils.log("Assigning new ports...")
        IxLoadUtils.assignPorts(connection, session_url, test_settings.portListPerCommunity)
        IxLoadUtils.log("Ports assigned.")

        IxLoadUtils.log("Starting the test...")
        IxLoadUtils.runTest(connection, session_url)
        IxLoadUtils.log("Test started.")

        IxLoadUtils.log("Polling values for stats %s..." % (stats_dict))
        IxLoadUtils.pollStats(connection, session_url, stats_dict)

        IxLoadUtils.log("Test finished.")
