---
Note: Work in progress
Last update: 05/12/2022
---

[[<< Back to parent directory](../README.md)]

[[<< Back to DASH top-level Documents](../../README.md#contents)]

# VNET to VNET scenario

- [Overview](#overview)
- [Moving packets from source to destination VM](#moving-packets-from-source-to-destination-vm)
- [Packet handling detailed steps](#packet-handling-detailed-steps)
  - [Rule processing pipeline](#rule-processing-pipeline)
    - [Inbound rule](#inbound-rule)
    - [Outbound rule](#outbound-rule)

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

	![sdn-appliance](../../general/design/images/sdn-appliance.svg)
