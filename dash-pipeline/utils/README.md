# DASH pipeline utils
## Overview
This package includes utils to configure DASH pipeline (bmv2) via p4runtime
directly. It is a supplementary of DASH SAI, which is not doable/proper to do
bmv2 specific configurations.

## Usage
1. internal configuration of bmv2 pipeline
```
    dut_mac = get_mac("veth0")
    neighbor_mac = get_mac("veth1")
    P4InternalConfigTable().set(neighbor_mac = mac_in_bytes(neighbor_mac), mac = mac_in_bytes(dut_mac))
```
2. underlay routing
```
    underlay_routing = P4UnderlayRoutingTable()
    underlay_routing.set(ip_prefix = '::10.0.1.0', ip_prefix_len = 120, next_hop_id = 1)
    underlay_routing.get(ip_prefix = '::10.0.1.0', ip_prefix_len = 120))
    underlay_routing.unset(ip_prefix = '::10.0.1.0', ip_prefix_len = 120))
```
3. flow
```
# decorator use_flow can be used to enable flow lookup of bmv2 pipeline for unittest class
@use_flow
class Test:
    def setUp(self):

# Verify flow entry is existing and customer packet can hit this flow
verify_flow(eni_mac, vnet_id, customer_packet)

# Verify flow entry is not existing and customer packet cannot hit this flow
verify_no_flow(eni_mac, vnet_id, customer_packet)
```
