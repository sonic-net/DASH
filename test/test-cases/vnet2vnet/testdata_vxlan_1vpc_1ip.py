testdata = {
    "val_map": {
        1: {
            "oeth": {"mac": "80:09:02:01:00:01", },
            "oipv4": {"ip": "220.0.1.2", "gip": "220.0.1.1", "mac": "00:ae:cd:10:7e:c6", },
            "obgp": {"ip": "220.0.1.2", "dip": "220.0.1.1", "bid": "194.0.0.1", "type": "External", "las": 200, },
            "oipv4pool": {"ip": "221.0.1.1", "multiplier": 1},
            "dg_b_ong_eth": {"mac": '00:12:01:00:00:01', },
            "dg_b_ong_ipv4": {"ip": "221.0.1.1", "gip": "101.1.0.1"},
            "vxlan": {"RemoteVmStaticMac": '00:1b:6e:80:00:01', "RemoteVtepIpv4": '221.0.0.2', "StaticInfoCount": 1, "Vni": 1, "RemoteVmStaticIpv4": ["222.0.0.2"]},
            "ieth": {"mac": "00:1b:6e:00:00:01"},
            "iipv4": {"ip": "222.0.0.1", "gip": "222.0.0.2"},
            "iipv4L": {"ip": "193.0.0.1", "gip": "193.0.0.9"},
        },
        2: {
            "oeth": {"mac": "80:09:02:02:00:01", },
            "oipv4": {"ip": "220.0.2.2", "gip": "220.0.2.1", "mac": "00:ae:cd:10:7e:c6", },
            "obgp": {"ip": "220.0.2.2", "dip": "220.0.2.1", "bid": "194.0.0.1", "type": "External", "las": 200, },
            "oipv4pool": {"ip": "221.0.2.1", "multiplier": 1},
            "dg_b_ong_eth": {"mac": '00:15:01:00:00:01', },
            "dg_b_ong_ipv4": {"ip": "221.0.2.1", "gip": "104.1.0.1"},
            "vxlan": {"RemoteVmStaticMac": '00:1b:6e:00:00:01', "RemoteVtepIpv4": '221.0.0.2', "StaticInfoCount": 1, "Vni": 1, "RemoteVmStaticIpv4": ["222.0.0.1"]},
            "ieth": {"mac": "00:1b:6e:80:00:01"},
            "iipv4": {"ip": "222.0.0.2", "gip": "222.0.0.1"},
            "iipv4L": {"ip": "193.0.0.9", "gip": "193.0.0.1"},
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
