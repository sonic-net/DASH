import pandas as pd
import os


ip_type = "v6"

testdata = {
    "val_map": {
        1: {
            "underlay_routing":"BGP",#"BGP"
            "oeth": {"mac": "80:09:02:01:00:01", },
            "oipv4": {
                        "ip": "220.0.1.2", 
                        "ip_step":"0.0.0.1",
                        "gip": "220.0.1.1", 
                        "gip_step":"0.0.0.1",
                        "mac": "00:ae:cd:10:7e:c6", 
                        },
            "obgp": {"ip": "220.0.1.2", "dip": "220.0.1.1", "bid": "194.0.0.1", "type": "External", "las": 200, },
            "oipv4pool": {"ip": "221.0.1.1", "ip_step":"0.0.0.1","multiplier": 8},
            "dg_b_ong_eth": {"mac": '00:12:01:00:00:01', },
            "dg_b_ong_ipv4": {
                            "ip": "221.0.1.1", 
                            "ip_step":"0.0.0.1",
                            "gip": "101.1.0.1",
                            "gip_step":"0.0.0.1",
                            },
            "vxlan": {
                    "RemoteVmStaticMac": {
                                            "start_value":'00:1b:6e:80:00:01',
                                            "step_value":"00:00:00:01:00:00",
                                            "increments":[("00:00:00:00:00:40", 1000,[])],
                                            "ng_step":'00:00:00:08:00:00'
                                            }, 
                    "RemoteVtepIpv4": '221.0.0.2', 
                    "StaticInfoCount": 6000, 
                    "Vni": 1, 
                    "RemoteVmStaticIpv4": {
                                            "start_value":"1.128.0.1",
                                            "step_value":"0.4.0.0",
                                            "increments":[("0.0.1.0", 1000,[])],"ng_step":"1.0.0.0"
                                            }
                    },
                    
            "ieth_local": {"mac": "00:1b:6e:00:00:01",'step':'00:00:00:00:00:01'},
            "iipv4_local": {"ip": "1.1.0.1", "gip": "1.128.0.1","prefix":9,'ip_step':'0.0.0.1','ip_ng1_step':'1.0.0.0','gip_step':'0.0.0.0','gip_ng1_step':'1.0.0.0'},
        },
        2: {
            "underlay_routing":"BGP",#"BGP"
            "oeth": {"mac": "80:09:02:02:00:01", },
            "oipv4": {
                        "ip": "220.0.2.2", 
                        "ip_step":"0.0.0.1",
                        "gip": "220.0.2.1", 
                        "gip_step":"0.0.0.1",
                        "mac": "00:ae:cd:10:7e:c6", 
                        },
            "obgp": {"ip": "220.0.2.2", "dip": "220.0.2.1", "bid": "194.0.0.1", "type": "External", "las": 200, },
            "oipv4pool": {"ip": "221.0.2.101","ip_step":"0.0.0.1", "multiplier": 8},
            "dg_b_ong_eth": {"mac": '00:15:01:00:00:01', },
            "dg_b_ong_ipv4": {
                                "ip": "221.0.2.101", 
                                "ip_step":"0.0.0.1",
                                "gip": "104.1.0.1",
                                "gip_step":"0.0.0.1",
                                
                                },
            "vxlan": {
                        "RemoteVmStaticMac": '00:1b:6e:00:00:01', 
                        "RemoteVtepIpv4": '221.0.0.2', 
                        "StaticInfoCount": 1, 
                        "Vni": 101, 
                        "RemoteVmStaticIpv4": "1.1.0.1",
                        "RemoteVmStaticIpv4": {
                                                "start_value":"1.1.0.1",
                                                "step_value":"0.0.0.1",
                                                "increments":[],"ng_step":"1.0.0.0"
                                                }                        
                        },
            "ieth_allow": {
                            "mac": {
                                        "start_value":'00:1b:6e:80:00:01',
                                        "step_value":"00:00:00:01:00:00",
                                        "increments":[("00:00:00:00:00:80", 500,[])],
                                        "ng_step":'00:00:00:08:00:00'
                                        },
                            
                            },
            "iipv4_allow": {
                            "ip": {
                                    "start_value":'1.128.0.1',
                                    "step_value":"0.4.0.0",
                                    "increments":[("0.0.2.0", 500,[])],
                                    "ng_step":"1.0.0.0"
                            },
                            "gip": "1.1.0.1",
                            "gip_step": "0.0.0.0",
                            "gip_ng_step": "1.0.0.0",
                            "prefix":9,
                            "multiplier": 3000
                            },
            "ieth_deny": {
                            "mac": {
                                        "start_value":'00:1b:6e:80:00:01',
                                        "step_value":"00:00:00:01:00:00",
                                        "increments":[("00:00:00:00:00:40", 500,[])],
                                        "ng_step":'00:00:00:08:00:00'
                                        },

                        },
            "iipv4_deny": {
                            "ip": {
                                    "start_value":'1.128.1.1',
                                    "step_value":"0.4.0.0",
                                    "increments":[("0.0.2.0", 500,[])],
                                    "ng_step":"1.0.0.0"
                            },
                            "gip": "1.1.0.1",
                            "gip_step": "0.0.0.0",
                            "gip_ng_step": "1.0.0.0",
                            "prefix":9,
                            "multiplier": 3000
                            },

        }
    },
    "acl_policies": [
        {
            'src_ip': ['222.0.0.2/32', '222.0.0.2/32'],
            'dst_ip':['222.0.0.1/32', '222.0.0.1/32'],
            'priority':0,
            'action':'allow',
        },
    ]
}
#VNI need increment

