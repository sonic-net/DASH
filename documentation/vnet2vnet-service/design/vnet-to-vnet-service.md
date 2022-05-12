---
Note: Work in progress
Last update: 05/12/2022
---

[[<< Back to parent directory](../README.md)]

[[<< Back to DASH top-level Documents](../../README.md#contents)]

# VNET to VNET scenario

- [Overview](#overview)
- [Moving packets from source to destination VM](#moving-packets-from-source-to-destination-vm)
- [Packet transforms](#packet-transforms)
  - [V-Port definition](#v-port-definition)
  - [VNET definition](#vnet-definition)
  - [VNET mapping table](#vnet-mapping-table)
  - [Packet transforms](#packet-transforms-1)

## Overview

This scenario is the starting point to design, implement and test the core DASH
mechanisms. In particular it allows the following features:

- VM to VM communication in VNET using the Appliance for rules and routing offload.  The details for this scenario are located in the DASH HLD (link to section), the SDN Transforms document, (link to section) and the Routing Scenarios document (link to section).  
- Route support
- LPM support
- ACL support

The intent is to verify the following performance properties: **CPS**, **flow**, **PPS**, and **rule scale**.

![vnet-to-vnet-one-dpu](./images/vnet-to-vnet-one-dpu.svg)

<figcaption><i>Figure 1 - VNET to VNET with DPU</i></figcaption><br/>

## Moving packets from source to destination VM

To understand DASH *performance enhancements and programmability*, it is important to understand the path where packets
are transferred from source to destination; in this scenario - from source VM to
destination VM in a VNET environment.

To make an analogy, it is similar to establishing a dedicated circuit between
Point A and Point B for the duration of a call in a telephonic switch, between a
caller and a receiver. The first time the connection (circuit) is initiated and
established, it takes more time due to the full setup for exchange that is
required. We call this a **slow path**. After the connection is established, the
messages between caller and receiver can be exchanged via the established path
and flow (without overhead). We call this **fast path**.

With respect to packets and flows between VMs in VNET, a tunnel (equivalent to
the circuit of a telephonic switch) is established between the source VM to the Appliance, and from the Appliance to the destination VM (after packet rules, routing, and transforms). This
tunnel (along with some SDN feature work) will redirect the packets to a DPU,
for example - in an appliance. This is where the DASH performance enhancements (so called *bump in
the wire*) happens.

## Packet transforms

Packet transformation is defined as .... and plays a crucial when moving a packet from a source to a destination.

The following is an example of packet transformation in VNET to VNET traffic.

### V-Port definition

- Physical address = `100.0.0.2`
- V-Port Mac = `V-PORT_MAC`

### VNET definition

- VNET1 ?? `10.0.0.0/24`
- VNET2 ?? `20.0.0.0/24`

### VNET mapping table

| | V4 underlay| V6 underlay| Mac-Address| Mapping Action | VNI
|:----------|:----------|:----------|:----------|:----------|:----------
| 10.0.0.1| 100.0.0.1| 3ffe :: 1| Mac1| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 100
| 10.0.0.2| 100.0.0.2| 3ffe :: 2| Mac2| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 200
| 10.0.0.3| 100.0.0.3| 3ffe :: 3| Mac3| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 300
| | | | | |

### Packet transforms

| SRC -> DST <img width=1000/>| Out-ACL1| Out-ACL2| Out-ACL3| Routing <img width=1000/>| Final <img width=1000/>|
|:----------|:----------|:----------|:----------|:----------|:----------
| | Block 10.0.0.10 Allow *| Block 10.0.0.11 Allow * | Allow*| 10.0.0.0/24 - Route Action = VNET 20.0.0.0/24 - Route Action = VNET|
| 10.0.0.1 -> 10.0.0.10 <br/>SMAC1-> DMAC_FAKE| Block| | | | Blocked
| 10.0.0.1 -> 10.0.0.11 <br/>SMAC1-> DMAC_FAKE| Allow| Block| | | Blocked
| 10.0.0.1 -> 10.0.0.2 <br/>SMAC1-> DMAC_FAKE <br/>Outer:<br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: custom <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]| Allow| Allow| Allow| Matched LPM route 10.0.0.0/24 Execute action VNET - which will lookup in mapping table and take mapping action.| Highlighted the changes in packet <br/>Outer:<br/>SRC: [100.0.0.2] <br/>DST: [100.0.0.1] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: 200 <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - Mac1 <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]
| 10.0.0.1 -> 10.0.0.3 SMAC1-> DMAC_FAKE| | | | |
| | | | | |


The following figure shows the transformation steps in a traditional VNET setting i.e., without appliance in between.

![packet-transforms-vnet-to-vnet](./images/packet-transforms-vm-to-vm-vnet.svg)


<!--
![sdn-appliance](../../general/design/images/sdn-appliance.svg) 
-->
