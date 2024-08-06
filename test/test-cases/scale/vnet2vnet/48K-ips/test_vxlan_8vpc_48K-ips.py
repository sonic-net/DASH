import inspect
import json
import sys
import time
from copy import deepcopy

import ipaddress
import macaddress
import pytest
import requests
from ixload import IxLoadUtils as IxLoadUtils
from ixnetwork_restpy import SessionAssistant
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from tabulate import tabulate
from testdata_baby_hero import testdata,ip_type
from datetime import datetime
from future.utils import iteritems

data = []
final_result_data=[]
setup_information=None
ixnetwork=None
config_elements_sets=[]
val_map={}
tiNo = 16
captions = ["Test","PPS", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %","PossibleBoundary"]


@pytest.fixture(scope="class")
def setup(smartnics, tbinfo,utils):
    """Gather all required test information from DUT and tbinfo.
        A Dictionary with required test information.
    """
    print ("*"*50+"SETUP"+"*"*50)
    setup_information = {"nics": smartnics, "tbinfo": tbinfo, }
    smartnics.configure_target(testdata)
    yield setup_information

def find_boundary(utils):
    global data, final_result_data
    hls = ixnetwork.Traffic.TrafficItem.find()[0].HighLevelStream.find()

    def boundary_check(test_boundary_val):
        for hl in hls:
            hl.FrameRate.update(Type='framesPerSecond', Rate=test_boundary_val)

        utils.start_traffic(ixnetwork)
        utils.ss("\t\t\tLet Traffic run for  ", 10)
        utils.ss("\t\t\tPrint Stats Before issuing Clear Stats  ", 2)
        utils.printStats(ixnetwork, "Traffic Item Statistics", {"Traffic Item Statistics": {'transpose': False, 'toprint': ["Traffic Item", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]}})
        utils.ss("\t\t\tLet Clear Stats  ", 2)
        ixnetwork.ClearStats()
        utils.ss("\t\t\tLet Traffic run for another ", 90)
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

    poss_val, step, tolerance, pass_val, fail_val = int(20000000 / tiNo), int(20000000 / tiNo), 100000, None, None
    #poss_val, step, tolerance, pass_val, fail_val = int(20000000 / tiNo), int(20000000 / tiNo), 50000, None, None

    while True:
        print("="*50)
        print(f"Test running for {utils.human_format(poss_val * tiNo)} framesPerSecond")
        print(" POSSPASS|FAIL|PASS=", poss_val, fail_val, pass_val)
        print("="*50)
        result = boundary_check(poss_val)
        row = utils.printStats(ixnetwork, "Traffic Item Statistics", {"Traffic Item Statistics": {'transpose': False, 'toprint': ["Traffic Item", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]}})
        utils.printStats(ixnetwork, "Flow Statistics", {"Flow Statistics": {'transpose': False, 'toprint': ["Traffic Item", "Source/Dest Endpoint Pair", "Tx Frames", "Rx Frames", "Frames Delta", "Loss %"]}})
        data.append([sys._getframe().f_back.f_code.co_name,utils.human_format(poss_val * tiNo)]+row[1:])

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
                if pass_val==None:
                    print ("Not able to find Boundary Tolerance (%d) is Less than last fail value (%d)" % (tolerance,fail_val))
                    pass_val="NA"
                else:
                    pass_val = utils.human_format(pass_val * tiNo)
                    print("Final Possible Boundary is ", pass_val)
                print(" X POSSPASS|FAIL|PASS=", poss_val, fail_val, pass_val)
                break
    data.append([sys._getframe().f_back.f_code.co_name]+["***"]*5+[pass_val])
    print(tabulate(data, headers=captions, tablefmt="psql"))
    
    final_result_data.append([sys._getframe().f_back.f_code.co_name,pass_val])



@pytest.fixture(scope="class")
def pps_config(setup,tbinfo,utils):
    """
        Description: Verify ip address can be configured in SVI.
        Topo: DUT02 ============ DUT01
        Dev. status: DONE
    """
    global ixnetwork,config_elements_sets,val_map
    testbed = setup["tbinfo"]
    snic = setup["nics"]
    def createTI(name, endpoints):
        trafficItem = ixnetwork.Traffic.TrafficItem.find(Name="^%s$" % name)
        if len(trafficItem) == 0:
            trafficItem = ixnetwork.Traffic.TrafficItem.add(Name=name, TrafficType='ipv4', BiDirectional=False)  # BiDirectional=True
        for indx,srcdst in enumerate(endpoints):
            print ("ENP UP",indx+1)
            src,dst = srcdst
            endpoint_set_up = trafficItem.EndpointSet.add(Name="%s-ENI_UP-%s" % (name,str(indx+1)),ScalableSources=src, ScalableDestinations=dst)
            ce = trafficItem.ConfigElement.find()[-1]
            ce.FrameRate.update(Type='framesPerSecond', Rate=50000)
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
            ce_up = ce
            print ("ENP Down",indx+1)
            #DOWN
            endpoint_set_down = trafficItem.EndpointSet.add(Name="%s-ENI_DOWN-%s" % (name,str(indx+1)),ScalableSources=dst, ScalableDestinations=src)
            ce = trafficItem.ConfigElement.find()[-1]
            ce.FrameRate.update(Type='framesPerSecond', Rate=50000)
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
            ce_down=ce
            
            if name=="Allow":
                config_elements_sets.append((ce_up,ce_down))

        print ("Done")
        #trafficItem.Generate()
        print (datetime.now(),"*"*80)
        return trafficItem


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
    

    portList = [{'xpath': '/vport[%s]' % str(indx+1), 'name': 'VTEP_0%d' % (indx+1), 'location': p['location']} for indx, p in enumerate(tb['tgen'][0]['interfaces'])]
    ixnetwork.ResourceManager.ImportConfig(json.dumps(portList), False)

    vports = list(ixnetwork.Vport.find())
    l1data = tb['tgen'][0]['interfaces']
    tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "ieeeL1Defaults": l1data[indx]['ieee'] } for indx, vp in enumerate(vports)]
    ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)
    tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "enableAutoNegotiation": l1data[indx]['an']} for indx, vp in enumerate(vports)]
    ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)
    
    tmp = [{'xpath': '/vport[%d]/l1Config/%s' % (vp.InternalId, vp.Type), "enableRsFec": l1data[indx]['fec'], "autoInstrumentation": "floating"} for indx, vp in enumerate(vports)]
    ixnetwork.ResourceManager.ImportConfig(json.dumps(tmp), False)
    for ed in [1, 2]:
        # OUTER DG
        obj_map[ed]["oeth"] = ixnetwork.Topology.add(Ports=vports[ed-1], Name="TG_%d" % ed).DeviceGroup.add(Name="O_DG_%d" % ed, Multiplier=1).Ethernet.add(Name='ETH_%d' % ed)
        if ip_type=="v4":
            obj_map[ed]["oipv4"] = obj_map[ed]["oeth"].Ipv4.add(Name="IPv4%d" % ed)
        elif ip_type=="v6":
            obj_map[ed]["oipv4"] = obj_map[ed]["oeth"].Ipv6.add(Name="IPv6%d" % ed)

        if val_map[ed]['underlay_routing']=="BGP":
            if ip_type=="v4":
                obj_map[ed]["obgp"] = obj_map[ed]["oipv4"].BgpIpv4Peer.add(Name="BGP_%d" % ed)
            elif ip_type=="v6":
                obj_map[ed]["obgp"] = obj_map[ed]["oipv4"].BgpIpv6Peer.add(Name="BGP_%d" % ed)
                
        # OUTER NG
        ng = ixnetwork.Topology.find().DeviceGroup.find(Name="O_DG_%d" % ed).NetworkGroup.add(Name="NG_%d" % ed, Multiplier=val_map[ed]["oipv4pool"]["multiplier"])
        if ip_type=="v4":
            obj_map[ed]["oipv4pool"] = ng.Ipv4PrefixPools.add(NumberOfAddresses='1')
        elif ip_type=="v6":
            obj_map[ed]["oipv4pool"] = ng.Ipv6PrefixPools.add(NumberOfAddresses='1')

        # DG Behing Outer NG
        obj_map[ed]["dg_b_ong"] = ng.DeviceGroup.add(Name="DG_B_ONG_%d" % ed, Multiplier=1)
        obj_map[ed]["dg_b_ong_eth"] = obj_map[ed]["dg_b_ong"].Ethernet.add(Name='ETH_%d' % ed)
        if ip_type=="v4":
            obj_map[ed]["dg_b_ong_ipv4"] = obj_map[ed]["dg_b_ong_eth"].Ipv4.add(Name='IPv4_%d' % ed)
            obj_map[ed]["vxlan"] = obj_map[ed]["dg_b_ong_ipv4"].Vxlan.add(Name="VXLAN_%d" % ed)
        elif ip_type=="v6":
            obj_map[ed]["dg_b_ong_ipv4"] = obj_map[ed]["dg_b_ong_eth"].Ipv6.add(Name='IPv6_%d' % ed)
            obj_map[ed]["vxlan"] = obj_map[ed]["dg_b_ong_ipv4"].Vxlanv6.add(Name="VXLAN_%d" % ed)
        
        

        # ALLOW & DENY
        if ed==1:
            if ip_type=="v4":
                obj_map[ed]["iipv4_local"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Local',Multiplier=1).Ethernet.add().Ipv4.add()
            elif ip_type=="v6":
                obj_map[ed]["iipv4_local"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Local',Multiplier=1).Ethernet.add().Ipv6.add()
                
            obj_map[ed]["ieth_local"] = obj_map[ed]["iipv4_local"].parent
        else:
            if ip_type=="v4":
                obj_map[ed]["iipv4_allow"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Allow',Multiplier=val_map[ed]["iipv4_allow"]["multiplier"]).Ethernet.add().Ipv4.add()
            elif ip_type=="v6":
                obj_map[ed]["iipv4_allow"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Allow',Multiplier=val_map[ed]["iipv4_allow"]["multiplier"]).Ethernet.add().Ipv6.add()
                
            obj_map[ed]["ieth_allow"] = obj_map[ed]["iipv4_allow"].parent

            if ip_type=="v4":
                obj_map[ed]["iipv4_deny"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Deny',Multiplier=val_map[ed]["iipv4_deny"]["multiplier"]).Ethernet.add().Ipv4.add()
            elif ip_type=="v6":
                obj_map[ed]["iipv4_deny"] = obj_map[ed]["dg_b_ong"].DeviceGroup.add(Name='Deny',Multiplier=val_map[ed]["iipv4_deny"]["multiplier"]).Ethernet.add().Ipv6.add()
            obj_map[ed]["ieth_deny"] = obj_map[ed]["iipv4_deny"].parent


    for ed in [1, 2]:
        # OUTER DG
        obj_map[ed]["oeth"].Mac.Increment(start_value=val_map[ed]["oeth"]["mac"],  step_value='00:00:00:00:00:01')
        obj_map[ed]["oipv4"].Address.Increment(start_value=val_map[ed]["oipv4"]["ip"],  step_value=val_map[ed]["oipv4"]["ip_step"])
        obj_map[ed]["oipv4"].GatewayIp.Increment(start_value=val_map[ed]["oipv4"]["gip"], step_value=val_map[ed]["oipv4"]["gip_step"])
        
        
        resolve_gateway = False
        if val_map[ed]['underlay_routing']=="STATIC":
            resolve_gateway = True
            
        obj_map[ed]["oipv4"].ResolveGateway.Single(resolve_gateway)
        obj_map[ed]["oipv4"].ManualGatewayMac.Single(val_map[ed]["oipv4"]["mac"])

        # BGP
        if val_map[ed]['underlay_routing']=="BGP":
            obj_map[ed]["obgp"].DutIp.Single(val_map[ed]["obgp"]["dip"])
            obj_map[ed]["obgp"].LocalAs2Bytes.Single(val_map[ed]["obgp"]["las"])
            if ip_type=="v4":
                obj_map[ed]["obgp"].EnableBgpIdSameasRouterId.Single(True)
                obj_map[ed]["obgp"].FilterIpV4Unicast.Single(True)
            elif ip_type=="v6":
                #obj_map[ed]["obgp"].EnableBgpIdSameasRouterId.Single(True)----------------------------> This gives an error
                obj_map[ed]["obgp"].FilterIpV6Unicast.Single(True)
            
            obj_map[ed]["obgp"].FilterEvpn.Single(True)

            #obj_map[ed]["bgp"].IpVrfToIpVrfType = 'interfacefullWithUnnumberedCorefacingIRB'
            #obj_map[ed]["bgp"].EthernetSegmentsCountV4 = 128

            obj_map[ed]["obgp"].BgpId.Single(val_map[ed]["obgp"]["bid"])
            obj_map[ed]["obgp"].Type.Single('external')

        # OUTER NG
        obj_map[ed]["oipv4pool"].NetworkAddress.Increment(start_value=val_map[ed]["oipv4pool"]["ip"], step_value=val_map[ed]["oipv4pool"]["ip_step"])
        obj_map[ed]["oipv4pool"].PrefixLength.Single(32)
        ipv4_behindvxlan = obj_map[ed]["vxlan"].parent
        ipv4_behindvxlan.Address.Increment(start_value=val_map[ed]["oipv4pool"]["ip"],  step_value=val_map[ed]["oipv4pool"]["ip_step"])
        ipv4_behindvxlan.ResolveGateway.Single(False)

        # DG Behing Outer NG
        # DG Behind Outer NG Ethernet
        eth = obj_map[ed]["dg_b_ong_ipv4"].parent
        eth.Mac.Increment(start_value=val_map[ed]["dg_b_ong_eth"]["mac"], step_value='00:00:00:00:00:01')

        # DG Behind Outer NG IPv4
        for s in obj_map[ed]["dg_b_ong_ipv4"].Address.Steps:
            s.Enabled = False
        obj_map[ed]["dg_b_ong_ipv4"].Address.Increment(start_value=val_map[ed]["dg_b_ong_ipv4"]["ip"],  step_value=val_map[ed]["dg_b_ong_ipv4"]["ip_step"])
        obj_map[ed]["dg_b_ong_ipv4"].GatewayIp.Increment(start_value=val_map[ed]["dg_b_ong_ipv4"]["gip"], step_value=val_map[ed]["dg_b_ong_ipv4"]["gip_step"])
        obj_map[ed]["dg_b_ong_ipv4"].Prefix.Single(32)
            
        # VXLAN
        obj_map[ed]["vxlan"].EnableStaticInfo = True

        if ip_type=="v4":
            vxlan_sinfo=obj_map[ed]["vxlan"].VxlanStaticInfo
            vxlan_sinfo.MacStaticConfig.Single(True)
            remote_vtep_ip_obj = vxlan_sinfo.RemoteVtepIpv4
            remote_vm_mac = vxlan_sinfo.RemoteVmStaticMac
        elif ip_type=="v6":
            vxlan_sinfo=obj_map[ed]["vxlan"].VxlanIPv6StaticInfo
            vxlan_sinfo.EnableManualRemoteVMMac.Single(True)
            remote_vtep_ip_obj = vxlan_sinfo.RemoteVtepUnicastIpv6
            remote_vm_mac = vxlan_sinfo.RemoteVMMacAddress
        
        

        remote_vtep_ip_obj.Single(val_map[ed]["vxlan"]["RemoteVtepIpv4"])
        obj_map[ed]["vxlan"].Vni.Increment(start_value=val_map[ed]["vxlan"]["Vni"], step_value=1)
        vxlan_sinfo.SuppressArp.Single(True)
        obj_map[ed]["vxlan"].StaticInfoCount = val_map[ed]["vxlan"]["StaticInfoCount"]


        # LOCAL | ALLOW & DENY
        if ed==1:

            remote_vm_mac.Custom(
                                        start_value=val_map[ed]["vxlan"]["RemoteVmStaticMac"]["start_value"],
                                        step_value=val_map[ed]["vxlan"]["RemoteVmStaticMac"]["step_value"],
                                        increments=val_map[ed]["vxlan"]["RemoteVmStaticMac"]["increments"]
                                        )
            remote_vm_mac.Steps[0].Enabled = True
            remote_vm_mac.Steps[0].Step = val_map[ed]["vxlan"]["RemoteVmStaticMac"]["ng_step"]

            vxlan_sinfo.RemoteVmStaticIpv4.Custom(
                                        start_value=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["start_value"],
                                        step_value=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["step_value"],
                                        increments=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["increments"]
                                        )
            vxlan_sinfo.RemoteVmStaticIpv4.Steps[0].Enabled = True
            vxlan_sinfo.RemoteVmStaticIpv4.Steps[0].Step = val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["ng_step"]
            
            
            obj_map[ed]["ieth_local"].Mac.Increment(start_value=val_map[ed]["ieth_local"]["mac"],  step_value=val_map[ed]["ieth_local"]["step"],)
            obj_map[ed]["ieth_local"].Mac.Steps[1].Enabled=True
            obj_map[ed]["ieth_local"].Mac.Steps[1].Step = '00:00:00:08:00:00'
                
            obj_map[ed]["iipv4_local"].Prefix.Single(8)
                
            obj_map[ed]["iipv4_local"].Address.Increment(  start_value=val_map[ed]["iipv4_local"]["ip"],  step_value=val_map[ed]["iipv4_local"]["ip_step"])
            obj_map[ed]["iipv4_local"].Address.Steps[1].Enabled=True
            obj_map[ed]["iipv4_local"].Address.Steps[1].Step = val_map[ed]["iipv4_local"]["ip_ng1_step"]
                
            obj_map[ed]["iipv4_local"].GatewayIp.Increment(start_value=val_map[ed]["iipv4_local"]["gip"], step_value=val_map[ed]["iipv4_local"]["gip_step"])
            obj_map[ed]["iipv4_local"].GatewayIp.Steps[1].Enabled=True
            obj_map[ed]["iipv4_local"].GatewayIp.Steps[1].Step = val_map[ed]["iipv4_local"]["gip_ng1_step"]

                
        else:

            remote_vm_mac.Increment(start_value=val_map[ed]["vxlan"]["RemoteVmStaticMac"],step_value='00:00:00:00:00:01')
            remote_vm_mac.Steps[0].Enabled =True
            remote_vm_mac.Steps[0].Step = '00:00:00:08:00:00'
                
            #vxlan_sinfo.RemoteVmStaticIpv4.Increment(start_value=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"],step_value='0.0.0.1')
            vxlan_sinfo.RemoteVmStaticIpv4.Custom(
                                        start_value=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["start_value"],
                                        step_value=val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["step_value"],
                                        )
            
            vxlan_sinfo.RemoteVmStaticIpv4.Steps[0].Enabled =True
            vxlan_sinfo.RemoteVmStaticIpv4.Steps[0].Step = val_map[ed]["vxlan"]["RemoteVmStaticIpv4"]["ng_step"]

            eth_allow   = obj_map[ed]["ieth_allow"]
            ip_allow    = obj_map[ed]["iipv4_allow"]
            eth_deny    = obj_map[ed]["ieth_deny"]
            ip_deny     = obj_map[ed]["iipv4_deny"]


            eth_allow.Mac.Custom(
                                    start_value=val_map[ed]["ieth_allow"]["mac"]["start_value"],
                                    step_value =val_map[ed]["ieth_allow"]["mac"]["step_value"],
                                    increments =val_map[ed]["ieth_allow"]["mac"]["increments"]
                                    )
                                    
            eth_allow.Mac.Steps[1].Enabled = True
            eth_allow.Mac.Steps[1].Step = val_map[ed]["ieth_allow"]["mac"]["ng_step"]

            ip_allow.Address.Custom(
                                    start_value=val_map[ed]["iipv4_allow"]["ip"]["start_value"],
                                    step_value =val_map[ed]["iipv4_allow"]["ip"]["step_value"],
                                    increments =val_map[ed]["iipv4_allow"]["ip"]["increments"]
                                    )
            ip_allow.Address.Steps[1].Enabled = True
            ip_allow.Address.Steps[1].Step = val_map[ed]["iipv4_allow"]["ip"]["ng_step"]

            ip_allow.Prefix.Single(8)
            
            ip_allow.GatewayIp.Increment(start_value=val_map[ed]["iipv4_allow"]["gip"], step_value=val_map[ed]["iipv4_allow"]["gip_step"])         #Fix Increments
            ip_allow.GatewayIp.Steps[1].Enabled=True
            ip_allow.GatewayIp.Steps[1].Step = val_map[ed]["iipv4_allow"]["gip_ng_step"]
                

            eth_deny.Mac.Custom(
                                    start_value=val_map[ed]["ieth_deny"]["mac"]["start_value"],
                                    step_value =val_map[ed]["ieth_deny"]["mac"]["step_value"],
                                    increments =val_map[ed]["ieth_deny"]["mac"]["increments"]
                                    )
            eth_deny.Mac.Steps[1].Enabled = True
            eth_deny.Mac.Steps[1].Step = val_map[ed]["ieth_deny"]["mac"]["ng_step"]

            ip_deny.Address.Custom(
                                    start_value=val_map[ed]["iipv4_deny"]["ip"]["start_value"],
                                    step_value =val_map[ed]["iipv4_deny"]["ip"]["step_value"],
                                    increments =val_map[ed]["iipv4_deny"]["ip"]["increments"]
                                    )
                                    
            ip_deny.Address.Steps[1].Enabled = True
            ip_deny.Address.Steps[1].Step = val_map[ed]["iipv4_deny"]["ip"]["ng_step"]

            ip_deny.Prefix.Single(8)


            ip_deny.GatewayIp.Increment(start_value=val_map[ed]["iipv4_deny"]["gip"], step_value=val_map[ed]["iipv4_deny"]["gip_step"])           #Fix Increments
            ip_deny.GatewayIp.Steps[1].Enabled=True
            ip_deny.GatewayIp.Steps[1].Step = val_map[ed]["iipv4_deny"]["gip_ng_step"]

    print("Create Traffic OneIPOneVPC")
    if ip_type=="v4":
        ipv4_local = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Local").Ethernet.find().Ipv4.find()
        ipv4_allow = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Allow").Ethernet.find().Ipv4.find()
        ipv4_deny  = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Deny").Ethernet.find().Ipv4.find()
    elif ip_type=="v6":    
        ipv4_local = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Local").Ethernet.find().Ipv6.find()
        ipv4_allow = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Allow").Ethernet.find().Ipv6.find()
        ipv4_deny  = ixnetwork.Topology.find().DeviceGroup.find().NetworkGroup.find().DeviceGroup.find().DeviceGroup.find(Name="Deny").Ethernet.find().Ipv6.find()
    print("Create Traffic OneIPOneVPC")
    
    vpcs, ips = val_map[1]["oipv4pool"]["multiplier"], int(val_map[1]["vxlan"]["StaticInfoCount"]/2)
    endpoints_allow,endpoints_deny=[], []
    
    for vpc in range(vpcs):
        endpoints_allow.append(
                            (
                            deepcopy([{"arg1": ipv4_local.href,"arg2": 1,"arg3": 1,"arg4": vpc+1,"arg5": 1  }]),
                            deepcopy([{"arg1": ipv4_allow.href,"arg2": 1,"arg3": 1,"arg4": vpc*ips+1,"arg5": ips  }])
                            )
                          )
        endpoints_deny.append(
                            (
                            deepcopy([{"arg1": ipv4_local.href,"arg2": 1,    "arg3": 1,    "arg4": vpc+1,    "arg5": 1  }]),
                            deepcopy([{"arg1": ipv4_deny.href ,"arg2": 1,    "arg3": 1,    "arg4": vpc*ips+1,    "arg5": ips  }])
                            )
                          )

    ti_allow = createTI("Allow", endpoints_allow)
    ti_deny = createTI("Deny",  endpoints_deny)


#@pytest.mark.usefixtures("pps_config")
class Test_Dpu:

    def teardown_method(self, method):
        print("Clean up configuration")

    def test_pps_001(self, setup, utils):
        print('Start All Protocols test_pps_001')
        ixnetwork.StartAllProtocols(Arg1='sync')

        try:
            print('Verify protocol sessions')
            protocolsSummary = StatViewAssistant(ixnetwork, 'Protocols Summary')
            protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
            protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
        except Exception as e:
            raise Exception(str(e))
        time.sleep(90)

        ti_allow = ixnetwork.Traffic.TrafficItem.find(Name="Allow")
        ti_deny  = ixnetwork.Traffic.TrafficItem.find(Name="Deny")
        ti_allow.Generate()
        ti_deny.Generate()
        ixnetwork.Traffic.Apply()
        utils.start_traffic(ixnetwork)
        time.sleep(30)
        utils.stop_traffic(ixnetwork)
        
        find_boundary(utils)
        print(tabulate(final_result_data, headers=["Test","Max Possible PPS"], tablefmt="psql"))

    def test_pps_increment_udp(self, setup, utils):

        print('Start All Protocols test_pps_random_udp_src_dst')
        ixnetwork.StartAllProtocols(Arg1='sync')
        try:
            print('Verify protocol sessions')
            protocolsSummary = StatViewAssistant(ixnetwork, 'Protocols Summary')
            protocolsSummary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
            protocolsSummary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
        except Exception as e:
            raise Exception(str(e))

        trafficItem = ixnetwork.Traffic.TrafficItem.find(Name="Deny")
        if len(trafficItem)==1:
            trafficItem.Enabled=False
        ti_allow =  ixnetwork.Traffic.TrafficItem.find(Name="Allow")
        vm_start_value=9000
        host_start_value=10000
        host_step = 5000
        endpoint_sets = ti_allow.EndpointSet.find()
        #for ep_up,ep_down in endpoint_sets:
        for ce_up,ce_down in config_elements_sets:
            print (ce_up,ce_down)
            inner_udp = ce_up.Stack.find(TemplateName="udp-template.xml")[-1]
            inn_sp = inner_udp.Field.find(DisplayName='^UDP-Source-Port')
            inn_dp = inner_udp.Field.find(DisplayName='^UDP-Dest-Port')
            inn_sp.ValueType = "singleValue"
            inn_dp.ValueType = "increment"
            inn_sp.SingleValue = vm_start_value
            inn_dp.StartValue = host_start_value
            inn_dp.StepValue = 1
            inn_dp.CountValue = int(val_map[1]["vxlan"]["StaticInfoCount"]/2)


            inner_udp = ce_down.Stack.find(TemplateName="udp-template.xml")[-1]
            inn_sp = inner_udp.Field.find(DisplayName='^UDP-Source-Port')
            inn_dp = inner_udp.Field.find(DisplayName='^UDP-Dest-Port')
            inn_sp.ValueType = "increment"
            inn_dp.ValueType = "singleValue"
            inn_dp.SingleValue = vm_start_value
            inn_sp.StartValue = host_start_value
            inn_sp.StepValue = 1
            inn_sp.CountValue = int(val_map[1]["vxlan"]["StaticInfoCount"]/2)

            
            
            vm_start_value+=1
            host_start_value=host_start_value+host_step

        ti_allow.Generate()
        ixnetwork.Traffic.Apply()
        utils.start_traffic(ixnetwork)
        time.sleep(30)
        utils.stop_traffic(ixnetwork)

        find_boundary(utils)
        print(tabulate(final_result_data, headers=["Test","Max Possible PPS"], tablefmt="psql"))

    def test_cps_001(self, setup, create_ixload_session_url):
        """
            Description: Verify ip address can be configured in SVI.
            Topo: DUT02 ============ DUT01
            Dev. status: DONE
        """
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
            stat_columns = ["It", "Obtained CPS", "HTTP Requests Failed", "TCP Retries",
                            "TCP Resets TX", "TCP Resets RX"]
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

        def _get_testrun_results(stats_dict, url_patch_dict):

            stats_global = _get_stats_global(stats_dict)

            failures_dict = {"http_requests_failed": 0, "tcp_retries": 0, "tcp_resets_tx": 0,
                             "tcp_resets_rx": 0, "total": 0}

            # get and compare stats
            http_requests_failed_l = [[x[0], x[5]] for x in stats_global]
            http_requests_failed = max([x[1] for x in http_requests_failed_l])
            failures_dict["http_requests_failed"] = http_requests_failed
            #http_requests_dict = _check_for_error_stats(http_requests_failed_l, "http_requests_failed")

            tcp_retries_l = [[x[0], x[6]] for x in stats_global]
            tcp_retries = max([x[1] for x in tcp_retries_l])
            failures_dict["tcp_retries"] = tcp_retries
            #tcp_retries_dict = _check_for_error_stats(tcp_retries_l, "tcp_retries")

            tcp_resets_tx_l = [[x[0], x[7]] for x in stats_global]
            tcp_resets_tx = max([x[1] for x in tcp_resets_tx_l])
            failures_dict["tcp_resets_tx"] = tcp_resets_tx
            #tcp_resets_tx_dict = _check_for_error_stats(tcp_resets_tx_l, "tcp_resets_tx")

            tcp_resets_rx_l = [[x[0], x[8]] for x in stats_global]
            tcp_resets_rx = max([x[1] for x in tcp_resets_rx_l])
            failures_dict["tcp_resets_rx"] = tcp_resets_rx
            #tcp_resets_rx_dict = _check_for_error_stats(tcp_resets_rx_l, "tcp_resets_rx")

            failures = http_requests_failed + tcp_retries + tcp_resets_tx + tcp_resets_rx
            failures_dict["total"] = failures

            steady_time_start = url_patch_dict['timeline_settings']['advancedIteration']['d0'] * 1000
            cps_stats = [[x[0], x[3]] for x in stats_global if x[0] >= steady_time_start]
            cps_max_w_ts = _get_max_cps(stats_global, cps_stats)
            cps_max = cps_max_w_ts[1]
            #effective_cps, effective_cps_ts = _get_effective_cps(cps_stats, http_requests_dict, tcp_retries_dict,
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
                [latency_ranges["latency_min"], latency_ranges["latency_max"], latency_ranges["latency_avg"]]
            )
            lat_stat_columns = ["Connect Time min (us)", "Connect Time max (us)", "Connect Time avg (us)"]

            print("\n%s" % tabulate(stat_table, headers=stat_columns, tablefmt='psql'))
            print("\n%s" % tabulate(stat_f_table, headers=stat_f_columns, tablefmt='psql'))
            print("\n%s" % tabulate(lat_table, headers=lat_stat_columns, tablefmt='psql'))

        def _run_cc_test(connection, session_url, url_patch_dict, MAX_CPS, MIN_CPS,
                            threshold, target_failures, test_settings, start_value=0):

            test_run_results = []
            test_value = start_value
            test_iteration = 1

            test_result = ""
            IxLoadUtils.log(
                "----Test Iteration %d------------------------------------------------------------------"
                % test_iteration)
            old_value = test_value
            IxLoadUtils.log("Testing CC Objective = %d" % test_value)
            kActivityOptionsToChange = {
                # format: { activityName : { option : value } }
                "HTTPClient1": {
                    "userIpMapping": "1:ALL",
                    "enableConstraint": False,
                    "userObjectiveType": "concurrentConnections",
                    "userObjectiveValue": int(test_value),
                }
            }
            IxLoadUtils.log("Updating CPS objective value settings...")
            IxLoadUtils.changeActivityOptions(connection, session_url, kActivityOptionsToChange)
            IxLoadUtils.changeActivityOptions(connection, session_url, kActivityOptionsToChange)
            IxLoadUtils.log("CPS objective value updated.")

            IxLoadUtils.log("Saving rxf")
            IxLoadUtils.saveRxf(connection, session_url, "C:\\automation\\24k_8VPC_CC_{}.rxf".format(test_iteration))

            IxLoadUtils.log("Applying config...")
            IxLoadUtils.applyConfiguration(connection, session_url)

            IxLoadUtils.log("Starting the test...")
            IxLoadUtils.runTest(connection, session_url)
            IxLoadUtils.log("Test started.")

            IxLoadUtils.log("Test running and extracting stats...")
            stats_dict = _poll_stats(connection, session_url, stats_test_settings)
            IxLoadUtils.log("Test finished.")

            failures_dict, cps_max, cps_max_w_ts, latency_ranges = _get_testrun_results(stats_dict, url_patch_dict)

            _print_stat_table(cps_max_w_ts, failures_dict, latency_ranges)

            test_run_results.append(
                [test_iteration, cps_max, failures_dict["http_requests_failed"],
                 failures_dict["tcp_retries"], failures_dict["tcp_resets_tx"],
                 failures_dict["tcp_resets_rx"]]
            )

            return cps_max_w_ts, failures_dict, test_run_results, latency_ranges

        def _create_ip_ranges(connection, session_url, traffic_network, plugin_name):

            IxLoadUtils.HttpUtils.addIpRange(connection, session_url, traffic_network,
                                             plugin_name, {"ipType": "IPv4"})

        def _get_ip_range_names(connection, session_url, traffic_network, plugin_names, url_patch_dict):

            ip_range_names = []
            range_string = IxLoadUtils.HttpUtils.getRangeListUrl(connection, session_url, traffic_network, plugin_names,
                                                              "rangeList")
            string_split = range_string.split("/")
            range_url = "/" + "/".join(string_split[2:])
            url = url_patch_dict["base_url"] + range_url

            response = requests.get(url, params=None)
            range_list_info = response.json()

            for elem in range_list_info:
                ip_range_names.append(elem['name'])

            return ip_range_names, range_list_info

        def _create_traffic_map(connection, url_patch_dict, nsgs, enis, ip_ranges_per_vpc):
            # Make Traffic Map Settings

            portMapPolicy_json = {'portMapPolicy': 'customMesh'}
            destinations_url = url_patch_dict['base_url'] + url_patch_dict['traffic_maps']['destinations_url']
            response = requests.patch(destinations_url, json=portMapPolicy_json)

            # meshType
            submapsIPv4_url = url_patch_dict['base_url'] + url_patch_dict['traffic_maps']['subMapsIPv4_url']
            meshType_json = url_patch_dict['traffic_maps']['meshType_setting']
            response = requests.patch(submapsIPv4_url, json=meshType_json)

            # map source-to-destination
            sourceRanges_url = submapsIPv4_url + "/sourceRanges/%s"
            destId = 1
            if url_patch_dict['traffic_maps']['meshType_setting']['meshType'] == 'ipRangePairs':
                ip_count = 0
                for i in range(nsgs):
                    destinationId_json = {'destinationId': destId}
                    url = sourceRanges_url % (i)
                    response = requests.patch(url, json=destinationId_json)
                    ip_count += 1
                    if ip_count == ip_ranges_per_vpc:
                        destId += 1
                        ip_count = 0
            else:
                # vlanRangePairs meshType
                for i in range(enis):
                    destinationId_json = {'destinationId': destId}
                    url = sourceRanges_url % (i)
                    response = requests.patch(url, json=destinationId_json)
                    destId += 1

            # destinationRanges
            destRanges_json = {'enable': False}
            destinationRanges_url = url_patch_dict['base_url'] + "/destinationRanges/%s"
            for i in range(enis):
                url = destinationRanges_url % (i)
                if i == 0:
                    response = requests.patch(url, json=destRanges_json)

            return

        def _build_node_ips(count, vpc, nodetype="client"):
            IP_STEP1 = int(ipaddress.ip_address(u'0.0.0.1'))
            IP_STEP2 = int(ipaddress.ip_address(u'0.0.1.0'))
            IP_STEP3 = int(ipaddress.ip_address(u'0.1.0.0'))
            IP_STEP4 = int(ipaddress.ip_address(u'1.0.0.0'))
            IP_STEPE = int(ipaddress.ip_address(u'0.0.0.2'))
            IP_C_START = ipaddress.ip_address(u'1.128.0.1')
            IP_S_START = ipaddress.ip_address(u'1.1.0.1')

            if nodetype in "client":
                ip = ipaddress.ip_address(int(IP_C_START) + (IP_STEP3 * count * 4) + (IP_STEP4 * (vpc - 1)))

            if nodetype in "server":
                ip = ipaddress.ip_address(int(IP_S_START) + (IP_STEP4 * (vpc - 1)))

            return ip

        def _set_ip_range_options(ip_count, eni_index, nodetype):

            if nodetype in "client":
                host_count = 500
                incrementBy = "0.0.2.0"
            else:
                host_count = 1
                incrementBy = "0.0.0.2"

            ip = str(_build_node_ips(ip_count, eni_index, nodetype))

            IpOptionsToChange = {'count': host_count, 'ipAddress': ip, 'prefix': 8, 'incrementBy': incrementBy,
                                'gatewayAddress': "0.0.0.0", 'gatewayIncrement': '0.0.0.0'}


            return IpOptionsToChange

        def _build_node_macs(count, vpc, nodetype="client"):
            ENI_MAC_STEP = '00:00:00:08:00:00'
            mac_start_client = macaddress.MAC('00:1B:6E:80:00:01')
            mac_start_server = macaddress.MAC('00:1B:6E:00:00:01')
            mac_incr1 = macaddress.MAC('00:00:00:01:00:00')
            mac_incr3 = macaddress.MAC('00:00:00:03:00:00')

            if nodetype in "client":
                m = macaddress.MAC(int(mac_start_client) + int(macaddress.MAC(ENI_MAC_STEP)) * (vpc - 1) + (int(mac_incr1) * count))

            if nodetype in "server":
                m = macaddress.MAC(int(mac_start_server) + int(macaddress.MAC(ENI_MAC_STEP)) * (vpc - 1))

            return m

        def _set_mac_range_options(ip_count=0, eni_index=0, nodetype="client"):

            if nodetype in "client":
                mac_increment = "00:00:00:00:00:80"
            else:
                mac_increment = "00:00:00:00:00:02"

            mac_address = str(_build_node_macs(ip_count, eni_index, nodetype))
            mac_address = mac_address.replace("-", ":")

            macOptionsToChange = {"mac": mac_address, "incrementBy": mac_increment}

            return macOptionsToChange

        def _set_vlan_range_options(url_patch_dict, index, nodetype="client"):

            if nodetype == 'client':
                firstId = url_patch_dict['client_vlan_settings']['json']['firstId'] + index
                uniqueCount = url_patch_dict['client_vlan_settings']['json']['uniqueCount']
            else:
                firstId = url_patch_dict['server_vlan_settings']['json']['firstId'] + index
                uniqueCount = url_patch_dict['server_vlan_settings']['json']['uniqueCount']

            vlan_settings = {'firstId': firstId, 'uniqueCount': uniqueCount}

            return vlan_settings

        def _get_url_ip(nodetype, node_ip_range_names, index):

            if nodetype == "client":
                range_url = url_patch_dict['client_range_setting']['url']
            else:
                range_url = url_patch_dict['server_range_setting']['url']

            r_index = node_ip_range_names[index].split("-")[1][1:]
            url_ip = url_patch_dict['base_url'] + range_url % (r_index)

            return url_ip

        # MAIN
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

        session = create_ixload_session_url
        connection = session['connection']
        test_settings = session['test_settings']

        headers = {'Accept': 'application/json'}
        session_url = IxLoadUtils.createNewSession(connection, test_settings.ixLoadVersion)
        base_url = 'http://' + test_settings.gatewayServer + ":{}".format(test_settings.gatewayPort) + \
                   '/api/v1/' + session_url

        url_patch_dict = {
            'base_url': base_url,
            'traffic_maps': {
                'meshType_setting': {'meshType': "vlanRangePairs"},
                #'meshType_setting': {'meshType': "ipRangePairs"},
                'subMapsIPv4_url': "/ixload/test/activeTest/communityList/0/activityList/0/destinations/0/customPortMap/submapsIPv4/0",
                'destinations_url': "/ixload/test/activeTest/communityList/0/activityList/0/destinations/0"
            },
            'allow_routes': {
                'json': {"allowRouteConflicts": True},
                'url': "/ixload/preferences"
            },
            'auto_mac_setting': {
                "autoMacGeneration": False
            },
            'timeline_settings': {
                'timelineType': 1,
                'url': "/ixload/test/activetest/communitylist/0/activitylist/0/timeline",
                'advanced': {
                    'rampUpValue': 1000000,
                    'sustainTime': 240,
                },
                'advancedIteration': {
                    'd0': 120,
                    'd1': 150,
                    'd2': 10,
                    'd3': 10,
                }
            },
            'client_range_setting': {
                'json': {},
                'url': "/ixload/test/activeTest/communityList/0/network/stack/childrenList/2/childrenList/3/rangeList/%s"
            },
            'server_range_setting': {
                'json': {},
                'url': "/ixload/test/activeTest/communityList/1/network/stack/childrenList/5/childrenList/6/rangeList/%s"
            },
            'client_vlan_settings': {
                'json': {"firstId": 101, "uniqueCount": 1},
                'url': "/ixload/test/activeTest/communityList/0/network/stack/childrenList/2/childrenList/3/rangeList/%s/vlanRange"
            },
            'server_vlan_settings': {
                'json': {"firstId": 1, "uniqueCount": 1},
                'url': "/ixload/test/activeTest/communityList/1/network/stack/childrenList/5/childrenList/6/rangeList/%s/vlanRange"
            },
            'http_version': {
                'json': {"httpVersion": 1},
                'url': "/ixload/test/activeTest/communityList/0/activityList/0/agent"
            },
            'http_tcp_conns_per_user': {
                'json': {"maxSessions": 48},
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
            'stats_configured': {
                'url': '/ixload/stats/HTTPClient/configuredStats'
            },
            'cps_aggregation_type': {
                'json': {"aggregationType": "kRate"},
                'url': ""
            },
            'cps_stat_caption': {
                'json': {"caption": "TCP CPS"},
                'url': ""
            }
        }

        enis = 8
        ip_ranges_per_vpc = 6
        num_ranges = enis
        nsgs = enis * ip_ranges_per_vpc

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
        # Create Client and Server IP Ranges
        for _ in range(nsgs):
            _create_ip_ranges(connection, session_url, "Traffic1@Network1", "IP-1")

        for _ in range(enis):
            _create_ip_ranges(connection, session_url, "Traffic2@Network2", "IP-2")

        # Get Client/Server IP range info
        client_ip_range_names, client_range_list_info = _get_ip_range_names(connection, session_url,
                                                    "Traffic1@Network1", "IP-1", url_patch_dict)
        server_ip_range_names, server_range_list_info = _get_ip_range_names(connection, session_url,
                                                    "Traffic2@Network2", "IP-2", url_patch_dict)

        IxLoadUtils.log("Disabling autoMacGeneration ...")
        for i in range(nsgs):
            url_ip = _get_url_ip("client", client_ip_range_names, i)
            response = requests.patch(url_ip, json=url_patch_dict['auto_mac_setting'])
            #response = self.make_request('PATCH', url_ip, url_patch_dict['auto_mac_setting'])

        for i in range(enis):
            url_ip = _get_url_ip("server", server_ip_range_names, i)
            response = requests.patch(url_ip, json=url_patch_dict['auto_mac_setting'])
            #response = self.make_request('PATCH', url_ip, url_patch_dict['auto_mac_setting'])

        vlan_enabled = {"enabled": True}

        IxLoadUtils.log("Creating Client IPs, MACs, and VLANIDs")
        client_ip_range_settings = []
        client_mac_range_settings = []
        client_vlan_range_settings = []
        eni_index = 1
        ip_count = 0
        nodetype = "client"
        # Build Client IPs and MACs
        for i in range(nsgs + 1 + ip_ranges_per_vpc):
            if ip_count < ip_ranges_per_vpc and eni_index <= enis:
                # --- ixNet objects need to be added in the list before they are configured.
                client_ip_range_settings.append(_set_ip_range_options(ip_count, eni_index, nodetype))
                client_mac_range_settings.append(_set_mac_range_options(ip_count, eni_index, nodetype))
                client_vlan_range_settings.append(_set_vlan_range_options(url_patch_dict, eni_index-1, nodetype))
                ip_count += 1
            else:
                eni_index += 1
                ip_count = 0

        IxLoadUtils.log("Setting Client Ranges: IPs, MACs, VLANs")
        for i in range(nsgs):
            # Enable VLAN settings
            range_url = url_patch_dict['client_range_setting']['url']
            r_index = client_ip_range_names[i].split("-")[1][1:]

            url_ip = url_patch_dict['base_url'] + range_url % (r_index)
            url_mac = url_patch_dict['base_url'] + range_url % (r_index) + "/macRange"
            url_vlan = url_patch_dict['base_url'] + range_url % (r_index) + "/vlanRange"

            response = requests.patch(url_ip, json=client_ip_range_settings[i])
            response = requests.patch(url_mac, json=client_mac_range_settings[i])
            response = requests.patch(url_vlan, json=vlan_enabled)
            response = requests.patch(url_vlan, json=client_vlan_range_settings[i])

        IxLoadUtils.log("Creating Server IPs, MACs, and VLANIDs")
        nodetype = "server"
        server_ip_range_settings = []
        server_mac_range_settings = []
        server_vlan_range_settings = []
        # Build Server IPs and MACs
        for i in range(enis):
            server_ip_range_settings.append(_set_ip_range_options(0, i + 1, nodetype))
            server_mac_range_settings.append(_set_mac_range_options(0, i+1, nodetype))
            server_vlan_range_settings.append(_set_vlan_range_options(url_patch_dict, i, nodetype))

        IxLoadUtils.log("Setting Server Ranges: IPs, MACs, VLANs")
        for i in range(enis):
            range_url = url_patch_dict['server_range_setting']['url']
            r_index = server_ip_range_names[i].split("-")[1][1:]

            url_ip = url_patch_dict['base_url'] + range_url % (r_index)
            url_mac = url_patch_dict['base_url'] + range_url % (r_index) + "/macRange"
            url_vlan = url_patch_dict['base_url'] + range_url % (r_index) + "/vlanRange"

            response = requests.patch(url_ip, json=server_ip_range_settings[i])
            response = requests.patch(url_mac, json=server_mac_range_settings[i])
            response = requests.patch(url_vlan, json=vlan_enabled)
            response = requests.patch(url_vlan, json=server_vlan_range_settings[i])

        IxLoadUtils.log("Disabling Unused IP ranges ...")
        kIpOptionsToChange = {
            # format : { IP Range name : { optionName : optionValue } }
            client_ip_range_names[-1]: {
                'count': 1,
                'enabled': False,
            },
            server_ip_range_names[-1]: {
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
        if url_patch_dict['timeline_settings']['timelineType'] == 0:
            rampDownTime = 10
            sustainTime = 180
            _set_timeline_settings(test_settings, rampDownTime, sustainTime)
        else:
            url_timeline = url_patch_dict['base_url'] + url_patch_dict['timeline_settings']['url']
            timelineType_json = {'timelineType': url_patch_dict['timeline_settings']['timelineType']}
            response = requests.patch(url_timeline, json=timelineType_json)

            timeline_json = url_patch_dict['timeline_settings']['advanced']
            response = requests.patch(url_timeline, json=timeline_json)

            advanced_url = url_timeline + "/advancedIteration/segmentList/%s"
            for i in range(4):
                url = advanced_url % (i)
                d_json = {'duration': url_patch_dict['timeline_settings']['advancedIteration']['d{}'.format(i)]}
                response = requests.patch(url, json=d_json)

        #  Change TCP Connections Established to CPS caption name and to use kRate aggregationType
        stats_configured_url = url_patch_dict['base_url'] + url_patch_dict['stats_configured']['url']
        response = requests.get(stats_configured_url, params=None)
        stat_url_list = response.json()
        for stat in stat_url_list:
            if stat['caption'] == 'TCP Connections Established':
                objectID = stat['objectID']

        cps_url = url_patch_dict['stats_configured']['url'] + '/' + str(objectID)
        url_patch_dict['cps_aggregation_type']['url'] = cps_url
        url_patch_dict['cps_stat_caption']['url'] = cps_url

        response = _patch_test_setting(url_patch_dict, 'cps_aggregation_type')
        response = _patch_test_setting(url_patch_dict, 'cps_stat_caption')

        IxLoadUtils.log("Adding new commands %s..." % (list(kNewCommands)))
        IxLoadUtils.addCommands(connection, session_url, kNewCommands)
        IxLoadUtils.log("Commands added.")

        IxLoadUtils.log("Creating custom traffic maps")
        _create_traffic_map(connection, url_patch_dict, nsgs, enis, ip_ranges_per_vpc)
        IxLoadUtils.log("Traffic Maps completed")

        IxLoadUtils.log("Clearing chassis list...")
        IxLoadUtils.clearChassisList(connection, session_url)
        IxLoadUtils.log("Chassis list cleared.")

        IxLoadUtils.log("Adding chassis %s..." % (test_settings.chassisList))
        IxLoadUtils.addChassisList(connection, session_url, test_settings.chassisList)
        IxLoadUtils.log("Chassis added.")

        IxLoadUtils.log("Assigning new ports...")
        IxLoadUtils.assignPorts(connection, session_url, test_settings.portListPerCommunity)
        IxLoadUtils.log("Ports assigned.")

        initial_objective = 6000000
        threshold = 100000
        target_failures = 1000
        MAX_CPS = 9000000
        MIN_CPS = 0
        cps_max_w_ts, failures_dict, test_run_results, latency_ranges = _run_cc_test(connection, session_url,
                                                                                        url_patch_dict,
                                                                                        MAX_CPS,
                                                                                        MIN_CPS, threshold,
                                                                                        target_failures, test_settings,
                                                                                        initial_objective)

        IxLoadUtils.log("Test Complete Final Values")
        _print_final_table(test_run_results)

        IxLoadUtils.deleteAllSessions(connection)

