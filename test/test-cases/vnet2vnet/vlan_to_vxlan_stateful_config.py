import json
import requests
from testdata_vxlan_1vpc_1ip import testdata as TD

import sys
sys.path.append("../.")
from testbed import TESTBED as TB

url = "http://{}:30180/srp4/api/v1/config".format(TB["stateful"][0]["vxlan"][0]["tgen"][0][0])
headers = {'Accept': 'application/json'}

conf = r"""
{
    "config": {
        "port_pairs": [
            {
                "vlan_port": {
                    "front_panel_port": 9,
                    "l1_profile": "autoneg",
                    "arp_to_port": 10,
                    "arp_to_port_offset": 100
                },
                "vxlan_port": {
                    "front_panel_port": 17,
                    "l1_profile": "manual_RS",
                    "gw_mac": "c82c2b00cf70",
                    "gw_ip": "%s",
                    "gw_router_id": "old",
                    "rustic_port": "srp4-rustic-vlan1",
                    "src_mac": "01:02:03:04:05:01",
                    "src_ip_start": "%s"
                },
                "vid_vni_profile": "stateful"
            },
            {
                "vlan_port": {
                    "front_panel_port": 10,
                    "l1_profile": "autoneg",
                    "arp_to_port": 9,
                    "arp_to_port_offset": -100
                },
                "vxlan_port": {
                    "front_panel_port": 18,
                    "l1_profile": "manual_RS",
                    "gw_mac": "c82c2b00cf74",
                    "gw_ip": "%s",
                    "gw_router_id": "old2",
                    "rustic_port": "srp4-rustic-vlan2",
                    "src_mac": "01:02:03:04:05:02",
                    "src_ip_start": "%s"
                },
                "vid_vni_profile": "stateful"
            }
        ],
        "layer1_settings" : {
            "default_profile": "manual_NONE",
            "profiles": [
                {
                    "name": "manual_RS",
                    "autoneg": false,
                    "fec_mode": "RS"
                },
                {
                    "name": "manual_NONE",
                    "autoneg": false,
                    "fec_mode": "NONE"
                },
                {
                    "name": "autoneg",
                    "autoneg": true,
                    "fec_mode": "RS"
                }
            ]

        }
    }
}"""

ip_split = TD["val_map"][2]["oipv4pool"]['ip'].split('.')
ip_split[3] = str(int(ip_split[3])+100)
converted_ip = '.'.join(ip_split)

conf_string = conf % (TD["val_map"][1]["vxlan"]["RemoteVtepIpv4"], TD["val_map"][1]["oipv4pool"]["ip"],
                      TD["val_map"][1]["vxlan"]["RemoteVtepIpv4"], converted_ip)

data = json.loads(conf_string)

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print(response.headers)
else:
    print("Error while making request, status code = {}, message {}".format(response.status_code, response.text))
