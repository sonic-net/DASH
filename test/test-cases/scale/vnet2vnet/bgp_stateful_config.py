import snappi, logging
from testdata_vxlan_1vpc_1ip import testdata as TD

import sys
sys.path.append("../.")

from testbed import TESTBED as TB

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%m/%d %H:%M:%S', level=logging.DEBUG)

# obtain via "kubectl get services|grep controller"
API_CONTROLLER_PORT = 30080
# kubectl describe pod srp4-rustic-6d6bd4fbcc-g56zx |grep "IP:"
R_BGP_IP1 = "srp4-rustic-vlan1.default"
R_BGP_IP2 = "srp4-rustic-vlan2.default"

api = snappi.api(location="https://{}:{}".format(TB["stateful"][0]["vxlan"][0]["tgen"][0][0], API_CONTROLLER_PORT))

config = api.config()

#### PORT 1

p1 = config.ports.add(name='BGP Port 1')
# Magic format: <traffic-engine-ip:port>+<rustic-ip>:50071
p1.location = f"10.32.0.1:5555;1+{R_BGP_IP1}:50071"
device1 = config.devices.add(name='Dev1')

d1_eth = device1.ethernets.add(port_name=p1.name)
d1_eth.name = f"Eth {p1.name}"
d1_eth.mac = "01:02:03:04:05:06"
#d1_eth.mac = "00:ae:cd:11:36:ce"
d1_ipv4 = d1_eth.ipv4_addresses.add()
d1_ipv4.name = f"IPv4 {p1.name}"
d1_ipv4.address = TD["val_map"][1]["oipv4"]["ip"]
d1_ipv4.prefix = 32
d1_ipv4.gateway = TD["val_map"][1]["oipv4"]["gip"]

bgp_router1 = device1.bgp
bgp_router1.router_id = d1_ipv4.address
bgp_if1 = bgp_router1.ipv4_interfaces.add(ipv4_name=d1_ipv4.name)
bgp_peer1 = bgp_if1.peers.add()
bgp_peer1.peer_address = d1_ipv4.gateway
bgp_peer1.name = f"BGP Peer {p1.name}"
bgp_peer1.as_type = "ebgp"
bgp_peer1.as_number = TD["val_map"][1]["obgp"]["las"]
bgp_rr1 = bgp_peer1.v4_routes.add()
bgp_rr1.name = "rr1"
bgp_rr1.addresses.add(address=TD["val_map"][1]["dg_b_ong_ipv4"]["ip"], prefix=32, count=128, step=1)


##### PORT 2

p2 = config.ports.add(name='BGP Port 2')
# Magic format: <traffic-engine-ip:port>+<rustic-ip>:50071
p2.location = f"10.32.0.1:5555;1+{R_BGP_IP2}:50071"
device2 = config.devices.add(name='Dev2')

d2_eth = device2.ethernets.add(port_name=p2.name)
d2_eth.name = f"Eth {p2.name}"
d2_eth.mac = "02:02:03:04:05:06"
#d2_eth.mac = "00:ae:cd:11:36:cd"
d2_ipv4 = d2_eth.ipv4_addresses.add()
d2_ipv4.name = f"IPv4 {p2.name}"
d2_ipv4.address = TD["val_map"][2]["oipv4"]["ip"]
d2_ipv4.prefix = 32
d2_ipv4.gateway = TD["val_map"][2]["oipv4"]["gip"]

bgp_router2 = device2.bgp
bgp_router2.router_id = d2_ipv4.address
bgp_if2 = bgp_router2.ipv4_interfaces.add(ipv4_name=d2_ipv4.name)
bgp_peer2 = bgp_if2.peers.add()
bgp_peer2.peer_address = d2_ipv4.gateway
bgp_peer2.name = f"BGP Peer {p2.name}"
bgp_peer2.as_type = "ebgp"
bgp_peer2.as_number = TD["val_map"][2]["obgp"]["las"]
bgp_rr2 = bgp_peer2.v4_routes.add()
bgp_rr2.name = "rr2"
bgp_rr2.addresses.add(address=TD["val_map"][2]["oipv4pool"]["ip"], prefix=32, count=128, step=1)


serialized = config.serialize()
# logging.info(f"TAM: {serialized}")

try:
    resp = api.set_config(serialized)
    logging.info(f"TAM: set_config {resp}")

    start = api.protocol_state()
    start.state = start.START
    serialized_start = start.serialize()
    resp2 = api.set_protocol_state(serialized_start)
    logging.info(f"TAM: set_protocol_state {resp2}")
except Exception as e:
    if e.args and len(e.args) >= 4:
        logging.critical(e.args[3].buffer)
    else:
        logging.critical(e)


