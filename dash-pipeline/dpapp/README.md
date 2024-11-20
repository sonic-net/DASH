# DPAPP - Data Plane Application
## Overview
DPAPP fulfills [VPP](https://fd.io/) plugin mechanism to implement the slow (exception) path of
packet processing. It works with [DASH pipeline BMv2](https://github.com/sonic-net/DASH/tree/main/dash-pipeline/bmv2),
serving fast path, to consist of a complete DASH data plane. Refer to the doc
[bmv2 data plane app](https://github.com/sonic-net/DASH/blob/main/documentation/dataplane/dash-bmv2-data-plane-app.md)
for design details.

## Usage
1. build dpapp
```
DASH/dash-pipeline$ make dpapp
```
2. Run dpapp
```
DASH/dash-pipeline$ make run-dpapp
```

## Debug
VPP CLI `vppctl` provides lots of commands for debugging. Use the command `docker exec -it dash-dpapp-${USER} vppctl`
to launch it.

- Check dpapp interfaces and the counters
```
vpp# show interface
              Name               Idx    State  MTU (L3/IP4/IP6/MPLS)     Counter          Count
host-veth5                        1      up          9000/0/0/0     rx packets                    39
                                                                    rx bytes                   10764
                                                                    tx packets                    39
                                                                    tx bytes                    7628
local0                            0     down          0/0/0/0

vpp# show hardware-interfaces
              Name                Idx   Link  Hardware
host-veth5                         1     up   host-veth5
  Link speed: unknown
  RX Queues:
    queue thread         mode
    0     vpp_wk_0 (1)   interrupt
  TX Queues:
    TX Hash: [name: hash-eth-l34 priority: 50 description: Hash ethernet L34 headers]
    queue shared thread(s)
    0     yes    0-1
  Ethernet address 02:fe:23:f0:88:99
  Linux PACKET socket interface v3
  FEATURES:
    qdisc-bpass-enabled
    cksum-gso-enabled
  RX Queue 0:
    block size:65536 nr:160  frame size:2048 nr:5120 next block:39
  TX Queue 0:
    block size:69206016 nr:1  frame size:67584 nr:1024 next frame:39
    available:1024 request:0 sending:0 wrong:0 total:1024
local0                             0    down  local0
  Link speed: unknown
  local

```

- Check flow table in dpapp
```
vpp# show dash flow
     1: eni 00:cc:cc:cc:cc:cc, vnet_id 343, proto 17, 10.1.1.10 1234 -> 10.1.2.50 80
        common data - version 0, direction 1, actions 0x9, timeout 28

vpp# clear dash flow 1
```

- Check packet processing trace in dpapp
```
vpp# trace add af-packet-input 100
vpp# show trace
```

On behalf of BMv2 switch, script `tools/send_p2a_pkt.py` can send packet with dash header to verify basic flow
functionality of dpapp.

## Test
By default, flow lookup is not enabled in DASH pipeline. The decorator `@use_flow` will enable it and then involve dpapp
for slow path. If test cases are verified to support flow, aka stateful packet processing, use the decorator to mark
the test class.

PTF test script [saidashdpapp_sanity.py](https://github.com/sonic-net/DASH/blob/main/test/test-cases/functional/ptf/saidashdpapp_sanity.py)
provides sanity check for dpapp. Refer to it as a sample for new flow tests.
