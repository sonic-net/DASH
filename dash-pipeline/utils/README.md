# DASH pipeline utils

## Overview

This package includes utils to configure DASH pipeline (bmv2) via p4runtime
directly. It is a supplementary of DASH SAI, which is not doable/proper to do
bmv2 specific configurations.

## Usage

### internal configuration of bmv2 pipeline

```python
    neighbor_mac = "xx:xx:xx:xx:xx:xx"
    dut_mac = "xx:xx:xx:xx:xx:xx"
    internal_config = P4InternalConfigTable(target = "localhost:9559")
    internal_config.set(neighbor_mac = neighbor_mac, mac = dut_mac)
    internal_config.set(flow_enabled = 1)
    internal_config.get()
    internal_config.unset()
```

### underlay routing

```python
    underlay_routing = P4UnderlayRoutingTable(target = "localhost:9559")
    underlay_routing.set(ip_prefix = '::10.0.1.0', ip_prefix_len = 120, next_hop_id = 1)
    underlay_routing.get(ip_prefix = '::10.0.1.0', ip_prefix_len = 120))
    underlay_routing.unset(ip_prefix = '::10.0.1.0', ip_prefix_len = 120))
```
