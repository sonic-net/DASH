[<< Back to parent directory](../README.md) ]

[<< Back to DASH top-level Documents](../../README.md#contents) ]

# SDN Features, Packet Transforms and Scale

> [!NOTE] This document is in the process of being restructured into general and
> per-service specifications.

- [First Target Scenario:  SKU for Networked Virtual Appliance
  (NVA)](#first-target-scenario--sku-for-networked-virtual-appliance-nva)
- [Scale per DPU (Card)](#scale-per-dpu-card)
- [Scenario Milestone and Scoping](#scenario-milestone-and-scoping)
- [Virtual Port (or Elastic Network Interface / ENI) and Packet
  Direction](#virtual-port-or-elastic-network-interface--eni-and-packet-direction)
- [First Target Scenario:  SKU for Networked Virtual Appliance
  (NVA)](#first-target-scenario--sku-for-networked-virtual-appliance-nva)
- [Scale per DPU (Card)](#scale-per-dpu-card)
- [Scenario Milestone and Scoping](#scenario-milestone-and-scoping)
- [Virtual Port (aka Elastic Network Interface / ENI) and Packet
  Direction](#virtual-port-aka-elastic-network-interface--eni-and-packet-direction)
- [Routing (Routes and Route-Action)](#routing-routes-and-route-action)
  - [Outbound routing](#outbound-routing)
  - [Inbound routing](#inbound-routing)
  - [Route rules processing](#route-rules-processing)
    - [Outbound (LPM) route rules
      processing](#outbound-lpm-route-rules-processing)
    - [Inbound (priority) route rules
      processing](#inbound-priority-route-rules-processing)
- [SDN Features, Packet Transforms and Scale](#sdn-features-packet-transforms-and-scale)
  - [First Target Scenario:  SKU for Networked Virtual Appliance (NVA)](#first-target-scenario--sku-for-networked-virtual-appliance-nva)
  - [Scale per DPU (Card)](#scale-per-dpu-card)
  - [Scenario Milestone and Scoping](#scenario-milestone-and-scoping)
  - [Virtual Port (aka Elastic Network Interface / ENI) and Packet Direction](#virtual-port-aka-elastic-network-interface--eni-and-packet-direction)
  - [Routing (Routes and Route-Action)](#routing-routes-and-route-action)
    - [Outbound routing](#outbound-routing)
    - [Inbound routing](#inbound-routing)
    - [Route rules processing](#route-rules-processing)
      - [Outbound (LPM) route rules processing](#outbound-lpm-route-rules-processing)
      - [Inbound (priority) route rules processing](#inbound-priority-route-rules-processing)
  - [Packet Flow](#packet-flow)
  - [Packet transforms](#packet-transforms)
  - [Packet Transform Examples](#packet-transform-examples)
    - [VNET to VNET Traffic](#vnet-to-vnet-traffic)
    - [VNET to Internet - TBD](#vnet-to-internet---tbd)
    - [VNET to Service Endpoints - TBD](#vnet-to-service-endpoints---tbd)
    - [VNET to Private Link  - TBD](#vnet-to-private-link----tbd)
  - [Metering](#metering)
  - [VNET Encryption](#vnet-encryption)
  - [Telemetry](#telemetry)
  - [Counters](#counters)
  - [BGP](#bgp)
  - [Watchdogs](#watchdogs)
  - [Servicing](#servicing)
  - [Debugging](#debugging)
  - [Flow Replication](#flow-replication)
  - [Unit Testing and development](#unit-testing-and-development)
  - [Internal Partner dependencies](#internal-partner-dependencies)

## First Target Scenario:  SKU for Networked Virtual Appliance (NVA)

Highly Optimized Path, Dedicated Appliance, Little Processing or Encap to SDN
Appliance and Policies on an SDN Appliance Why do we need this scenario?  There
is a huge cost associated with establishing the first connection (and the CPS
that can be established)

- A high Connections per Second (CPS) / Flow SKU for Networked Virtual
  Appliances (NVA)

 ![sdn-high-cps](images/sdn-high-cps.svg)

## Scale per DPU (Card)

**Note: Below are the expected numbers per Data Processing Unit (DPU); this
applies to both IPV4 and IPV6 underlay and overlay*

**IPV6 numbers will be lower*

| Syntax | Description | Notes |
| ----------- | ----------- |-------|
| Flow Scale <img style="width:200px"/>| <ul><li>1+ million flows per v-port (aka ENI)</li> <li>16 million per DPU/Card per 200G<ul><li>single encap IPv4 overlay and IPV6 underlay</li> <li>single encap IPv6 overlay and IPV6 underlay. (This can be lower)</li> <li>single encap IPV4</li> <li>Encap IPv6 and IPV4</li></ul></ul> *These are complex flows, details are below.* | |  
| CPS | 4 million+ (max)  | |
| Routes | 100k per v-port (max)  | |
| ACLs | 100k IP-Prefixes, 10k Src/Dst ports per v-port (max)  | |
| NAT | tbd  | |
| V-Port (aka ENI or Source VM) | 32 Primary, 32 Secondary assuming 2x OverSub, 32GB RAM, No ISSU, 10k (theoretical max)  | Each ENI 1M total active connections and 2M flows |
| Mappings (VMS deployed) | 10 million total mapping per DPU; mappings are the objects that help us bridge the customer's virtual space (private ip address assigned to each VM) with Azure's physical space (physical/routable addresses where the VMs are hosted)  | |
|  | For each VPC, we have a list of mappings of the form: PrivateAddress -> (Physical Address v4, Physical Address V6, Mac Address, etc...) | VPC can have up to 1M mappings |

## Scenario Milestone and Scoping

| Scenario | Feature | Performance Metrics | Timeline |
|:---------|:---------|:-----|-----|
| 1 | <ul> <li>VNET <-> VNET </li> <ul><li>Route Support </li> <li>LPM Support </li> <li>ACL Support</li></ul></ul>|CPS<br/>Flow<br/>PPS</br>Rule Scale<img width=400/></br> |
| 2  | <ul> <li>Load Balancer Inbound</li><li>VIP Inbound</li></ul>  |  | |
| 3 | Private Link Outbound (transposition), encapsulate and change packet IPv4 to IPv6 (4 bits embedded)  |  | |
| 4 | L3 / L4 Source NAT (correlated w/#2) outbound perspective (Cx address) to Internet; changing Cx source IP to Public IP (1:1 mapping)  |  | |
| 5 | Private Link Service Link Service (dest side of Private Link) IPv6 to IPv4; DNATing     |  | |
| 6 | Flow replication; supporting High Availability (HA); flow efficiently replicates to secondary card; Active/Passive (depending upon ENI policy) or can even have Active/Active; OR provision the same ENI over multiple devices w/o multiple SDN appliances – Primaries for a certain set of VMS can be on both     |  | Not a must have for Private Preview <img width=400/>|

## Virtual Port (aka Elastic Network Interface / ENI) and Packet Direction

An SDN appliance in a multi-tenant network appliance (meaning 1 SDN appliance
will have multiple cards; 1 card will have multiple machines or bare-metal
servers), which supports Virtual Ports.   These can map to policy buckets
corresponding to customer workloads, for example: Virtual Machines or Bare Metal
servers servers.

The Elastic Network Interface (ENI), is an independent entity that has a
collection of routing policies. Usually there is a 1:1 mapping between the VM
NIC (Physical NIC) and the ENI (Virtual NIC).  The ENI has specific match
identification criteria, which is used to identify **packet direction**. The
current version only supports **mac-address** as ENI identification criteria. 
  
Once a packet arrives **Inbound** to the target (DPU), it must be forwarded to
the correct ENI policy processing pipeline. This ENI selection is done based on
the **inner destination MAC** of the packet, which is matched against the MAC of
the ENI. 

The SDN controller will create these virtual ports / ENIs on an SDN appliance
and associate corresponding SDN policies such as – Route, ACL, NAT etc. to these
virtual ports.  In other words, our software will communicate with the cards,
hold card inventory and SDN placement, call APIs that are exposed through the
card:  create policies, setup ENI, routes, ACLs, NAT, and different rules.

The following applies:

- Each Virtual Port (ENI) will be created with an ENI identifier such as – Mac
  address, VNI or more.
- A Virtual Port also has attributes such as : *flow time-out*, *QOS*, *port
  properties* related to the port.
- The Virtual Port is the container which holds all policies.

![sdn-virtual-port](images/sdn/sdn-virtual-port.svg)

For more information, see **[SDN pipeline basic elements](sdn-pipeline-basic-elements.md#packet-flow---selecting-packet-direction)**.

## Routing (Routes and Route-Action)

Routing must be based on the **Longest Prefix Match** (LPM) and must support all
**underlay and overlay** combinations described below:

- inner IPv4 packet encapsulated in outer IPv4 packet 
- inner IPv4 packet encapsulated in outer IPv6 packet 
- inner IPv6 packet encapsulated in outer IPv4 packet 
- inner IPv6 packet encapsulated in outer IPv6 packet 

The routing pipeline must support the routing models shown below.

### Outbound routing 

1. **Transpositions** 
   - Direct traffic – pass thru with static SNAT/DNAT (IP, IP+Port
   - Packet upcasting (IPv4 -> IPv6 packet transformation) 
   - Packet downcasting (IPv6 -> IPv4 packet transformation) 
1. **Encap** 
   - VXLAN/GRE encap – static rule 
   - VXLAN/GRE encap – based on mapping lookup 
   - VXLAN/GRE encap – calculated based on part of SRC/DEST IP of inner packet 
1. **Up to 3 levels of routing transforms** (example: transpose + encap + encap) 

### Inbound routing 

1. **Decap** 
   - VXLAN/GRE decap – static rule 
   - VXLAN/GRE decap – based on mapping lookup 
   - VXLAN/GRE decap – inner packet SRC/DEST IP calculated based on part of
     outer packet SRC/DEST IP 
1. **Transpositions** 
   - Direct traffic – pass thru with static SNAT/DNAT (IP, IP+Port) 
   - Packet upcasting (IPv4 -> IPv6 packet transformation) 
   - Packet downcasting (IPv6 -> IPv4 packet transformation) 
1. **Up to 3 level of routing transforms** (example: decap + decap + transpose) 

All routing rules must optionally allow for **stamping** the source MAC (to
**enforce Source MAC correctness**), `correct/fix/override source mac`. 

### Route rules processing

#### Outbound (LPM) route rules processing

- Matching is based on destination IP only - using the Longest Prefix Match
(LPM) algorithm.
- Once the rule is matched, the correct set of **transposition, encap** steps
must be applied depending on the rule.
- Only one rule will be matched.

#### Inbound (priority) route rules processing

All inbound rules are matched based on the priority order (with lower priority
value rule matched first). Matching is based on multiple fields (or must match
if field is populated). The supported fields are: 

- Most Outer Source IP Prefix 
- Most Outer Destination IP Prefix 
- VXLAN/GRE key 

Once the rule is matched, the correct set of **decap, transposition** steps must
be applied depending on the rule. **Only one rule will be matched**. 

Also notice the following: 

- Routes are usually LPM based Outbound
- Each route entry will have a prefix, and separate action entry
- The lookup table is per ENI, but could be Global, or multiple Global lookup
  tables per ENIs
- Outer Encap IPv4 using permits routing between servers within a Region; across
  the Region we use IPv6

**Why would we want to use these?**

- Example:  to block prefixes to internal DataCenter IP addresses, but Customer
  uses prefixes inside of their own VNET
- Example:  Lookup between CA (inside Cx own VNET) and PA (Provider Address)
  using lookup table (overwrite destination IP and MAC before encap)
- Example:  Customer sends IPv4, we encap with IPv6
- Example:  ExpressRoute with 2 different PAs specified (load balancing across
  multiple PAs) using 5 tuples of packet to choose 1st PA or 2nd PA

| Route Type| Example
|:----------|:----------
| Encap_with_lookup_V4_underlay| Encap action is executed based on lookup into the mapping table.V4 underlay is used
| Encap_with_lookup_V6_underlay| Encap action is executed based on lookup into the mapping table.V6 underlay is used
| Encap_with_Provided_data (PA)| Encap action is executed based on provided data.Multiple PA can be provided.
| Outbound NAT (SNAT)_L3| L3 NAT action is executed on source IP, based on provided data.
| Outbound NAT (SNAT)_L4| L4 NAT action is executed on source IP, source port based on provided data.
| Null | Blocks the traffic
| Private Link | -
| |

**Mapping Table for a v-port**

| Customer Address| Physical Address - V4 | Physical Address - V6| Mac-Address for D-Mac Rewrite| VNI to Use
|:----------|:----------|:----------|:----------|:----------
| 10.0.0.1| 100.0.0.1| 3ffe::1| E4-A7-A0-99-0E-17| 10001
| 10.0.0.2| 100.0.0.2| 3ffe::2| E4-A7-A0-99-0E-18| 10001
| 10.0.0.3| 100.0.0.3| 3ffe::3| E4-A7-A0-99-0E-19| 20001
| 10.0.0.4| 100.0.0.4| 3ffe::3| E4-A7-A0-99-0E-20| 10001

**Route Table for a v-port**

- LPM decides which route is matched.
- Once the route is matched, a corresponding action is executed.

| Route| Action | Route Type| Route Id
|:----------|:----------|:----------|:----------
| 10.0.0.0/24, <br/> 20.0.0.0/24, <br/> 30.0.0.0/24, <br/> 10.0.0.0/8, <br/>…… more prefixes (up-to 20k) <img width=500/>| Encap Type: VXLAN <br/> Action - lookup mapping table for exact destination, VNI and D-Mac re-write info.| Encap_with_lookup_V4_underlay| 1
| 10.0.0.100/32| Encap Type: VXLAN <br/> Action: Encap_with_Provided_data <ul><li>Encap with source PA = 100.0.0.1</li><li>Encap with destination PA = 23.0.0.1</li><li>Re-write D-Mac to E4-A7-A0-99-0E-28</li><li>Use VNI = 90000</li></ul>| Encap_with_Provided_data| 2
| 10.0.0.101/32| Encap Type: VXLAN <br/> Action: Encap_with_Provided_data <br/> <ul><li>Encap with source PA = 100.0.0.1</li> <li>Encap with destination PA = 23.0.0.10, 23.0.0.11, 23.0.0.13, 23.0.0.14</li> <li>Re-write D-Mac to E4-A7-A0-99-0E-29</li><li>Use VNI = 90000</li> </ul>| Encap_with_Provided_data_ECMP| 3
| 8.8.8.8/32 | L3 NAT <br/> Action: Transpose source IP to provided NAT IP, keep all ports same.NAT IP: 10.0.0.1 -> 15.0.0.1| Outbound NAT (SNAT)_L3| 4
| 9.9.9.9.9/32| L4 NAT <br/> Action: Transpose source IP and source port re-write ports from configured port pool.| Outbound NAT (SNAT)_L4| 5
| 0.0.0.0/32| NULL| Null| 6
| 23.0.0.1/32| Service endpoint| ST| 7
| 23.0.0.2/32| Private Link - TBD| Private Link - TBD| 8

**Route example- Outbound packets**

| Original Packet <img width=1000/>| Matched route <img width=500/> | Transform <img width=1000/> | Route Type
|:----------|:----------|:----------|:----------
| 10.0.0.1 -> 10.0.0.2 <br/> SMAC1-> DMAC_FAKE </br> Outer: <br/> SRC: [Physical IP of host] <br/> DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/> &nbsp; &nbsp; &nbsp;VNI: custom <br/>Inner Mac: <br/> &nbsp; &nbsp; &nbsp; SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP:<br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 1| Outer: <br/>SRC: [SDN Appliance IP] <br/>DST: [100.0.0.2] # Came from mapping table lookup <br/>VXLAN <br/> &nbsp; &nbsp; &nbsp;VNI: 10001 <br/>Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-18 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Encap_with_lookup_V4_underlay
| 10.0.0.1 -> 10.0.0.100 <br/> SMAC1-> DMAC_FAKE <br/> Outer: <br/> SRC: [Physical IP of host] <br/> DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/> Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 2| Outer: <br/>SRC: [SDN Appliance IP] DST: [23.0.0.1] # Came from mapping table lookup <br/>VXLAN VNI: 90000 <br/>Inner Mac:<br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-28 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.100]| Encap_with_Provided_data
| 10.0.0.1 -> 10.0.0.101 <br/>SMAC1-> DMAC_FAKE <br/>Outer: <br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/>VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/>Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 3| Outer: <br/>SRC: [SDN Appliance IP] <br/>DST: ECMP on <br/>[23.0.0.10, 23.0.0.11, 23.0.0.13, 23.0.0.14] <br/># Came from mapping table lookup <br/>VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: 90000 <br/>Inner Mac:<br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-29 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp; [10.0.0.1] -> [10.0.0.100]| Encap_with_Provided_data_ECMP
| 10.0.0.1 -> 8.8.8.8 <br/>SMAC1-> DMAC_FAKE <br/>Outer: <br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/> Inner Mac: <br/>&nbsp; &nbsp; &nbsp; SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [8.8.8.8]| Route Id = 4| |
| | | |

## Packet Flow

For the first packet of a TCP flow, we take the Slow Path, running the
transposition engine and matching at each layer.  For subsequent packets, we
take the Fast Path, matching a unified flow via UFID and applying a
transposition directly against rules.

For more information, see **[SDN pipeline basic elements](sdn-pipeline-basic-elements.md#packet-flow---selecting-packet-direction)**. 

## Packet transforms

See packet transforms in **[SDN pipeline basic elements](sdn-pipeline-basic-elements.md#packet-transforms)**.

## Packet Transform Examples

### VNET to VNET Traffic

 **V-Port**

- **Physical address = 100.0.0.2**

- **V-Port Mac = V-PORT_MAC**

 **VNET Definition:**

- 10.0.0.0/24

- 20.0.0.0/24

**VNET Mapping Table** | | V4 underlay| V6 underlay| Mac-Address| Mapping
Action| VNI |
|:----------|:----------|:----------|:----------|:----------|:---------- |
|10.0.0.1| 100.0.0.1| 3ffe :: 1| Mac1| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 100 |
|10.0.0.2| 100.0.0.2| 3ffe :: 2| Mac2| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 200 |
|10.0.0.3| 100.0.0.3| 3ffe :: 3| Mac3| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 300 | | |
| | | | |

**Packet Transforms**

| SRC -> DST <img width=1000/>| Out-ACL1| Out-ACL2| Out-ACL3| Routing <img width=1000/>| Final <img width=1000/>|
|:----------|:----------|:----------|:----------|:----------|:----------
| | Block 10.0.0.10 Allow *| Block 10.0.0.11 Allow * | Allow*| 10.0.0.0/24 - Route Action = VNET 20.0.0.0/24 - Route Action = VNET|
| 10.0.0.1 -> 10.0.0.10 <br/>SMAC1-> DMAC_FAKE| Block| | | | Blocked
| 10.0.0.1 -> 10.0.0.11 <br/>SMAC1-> DMAC_FAKE| Allow| Block| | | Blocked
| 10.0.0.1 -> 10.0.0.2 <br/>SMAC1-> DMAC_FAKE <br/>Outer:<br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: custom <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]| Allow| Allow| Allow| Matched LPM route 10.0.0.0/24 Execute action VNET - which will lookup in mapping table and take mapping action.| Highlighted the changes in packet <br/>Outer:<br/>SRC: [100.0.0.2] <br/>DST: [100.0.0.1] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: 200 <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - Mac1 <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]
| 10.0.0.1 -> 10.0.0.3 SMAC1-> DMAC_FAKE| | | | |
| | | | | |

### VNET to Internet - TBD

### VNET to Service Endpoints - TBD

### VNET to Private Link  - TBD

## Metering

- Metering will be based on per flow stats, metering engine will consume per
  flow stats of bytes\-in and bytes\-out.

## VNET Encryption

## Telemetry

## Counters

Counters are objects for counting data per ENI. The following are their main
characteristics:

- A counter is associated with only one ENI that is, it is not shared among
  different ENIs.
- If you define a counter as a global object, it cannot reference different
  ENIs.
- The counters live as long as the related ENI exists.  
- The counters persist after the flow is completed.
- You use API calls to handle these counters.
- When creating a route table, you will be able to reference the counters.

The control plane is the consumer of counters that are defined in the data
plane. The control plane queries every 10 seconds.

Counters can be assigned on the route rule, or assigned onto a mapping. If the
mapping does not exist, you revert to the route rule counter. A complete
definition will follow when we have more information other than software defined
devices.  

In the flow table we list the packet counter called a 'metering' packet; once we
have the final implementation that does the packet processing, we can do
metering.

Essentially, whenever a route table is accessed and we identify the right VNET
target (based on the mapping from the underlay IP), will have an ID of the
metering packet preprogrammed earlier.  We will reference this counter in the
mappings. When the flow is created it will list this counter ID.  When the
packet transits inbound or outbound through the specific flow, this counter is
incremented and tracked separately for the inbound and outbound.

Some specific counters (such as memory use of a card, etc...) are global,
however most of the counters should be per ENI as processing of rules and drops,
accepts, list of flows etc are per ENI.

We need more information around Counters, Statistics, and we need to start
thinking about how to add Metering- and reconcile this in the P4 model.  

| Counter Name       | Description           | ENI or Global  |
| ------------- |:-------------:| -----:|
| TotalPacket      | Total packets to/from a VM. Exposed to customer; 2 counters, 1 per direction | ENI |
| TotalBytes      | Total bytes to/from a VM. Exposed to customer; 2 counters, 1 per direction     |   ENI |
| TotalUnicastPacketForwarded |       |    ENI |
| TotalMulticastPacketsForwarded |       |    ENI |
| TcpConnectionsResetHalfTTL | TCP connections that had a TCP reset and its TTL cut down to 5 seconds      |    ENI |
| NonSynStateful | Non-SYN TCP packets that are natted and not dropped by setting (SLB scenario)      |    ENI |
| NumberOfFlowResimulated DuringPortTimer | Number of connections updated in an internal port-level update      |    ENI |
| RedirectRuleResimulatedUf | Number of times a redirect packet impacted a connection      |    ENI |
| DropPacket | Number of packets dropped on a port      |    ENI |
| DropBroadcastPacket | Number of broadcast packets dropped by guard      |    ENI |
| DropInvalidPacket | Number of packets dropped due to being unable to extract valid information from it      |    ENI |
| DropIPv4SpoofingPacket | Number of packets not using the programmed source address       |    ENI |
| DropIPv6SpoofingPacket | Number of packets not using the programmed source address       |    ENI |
| DropBlockedPacket | Number of packets dropped due to the port in a blocked state      |    ENI |
| TcpConnectionsResetByInjected Reset | Number of TCP connections reset with an injected reset      |    ENI |
| DroppedRedirectPackets | Number of redirect packets saw and dropped(All redirect packets are dropped by design)      |    ENI |
| DroppedPADiscoveryPackets | Number of "PA Discovery" packets dropped intentionally as part of VNET encryption      |    ENI |
| DroppedResourcesMemory | Number of packets dropped due to unable to allocate memory      |    ENI |
| DroppedPARouteRule | Number of packets dropped due to PA route rule failure to determine outer mac address to use      |    ENI |
| DroppedFragPacket | Number of fragments dropped due to fragmention cache collision or unable to apply transposition      |    ENI |
| DroppedResourcesPacket | Number of packets dropped due to a lack of some object or memory      |    ENI |
| DroppedAclPacket | Packets dropped due to matching a block rule      |    ENI |
| DroppedMalformedPacket | Number of packets dropped due to determining them to be malformed      |    ENI |
| DroppedForwardingPacket | Number of packets unable to be forwarded to it's next destination      |    ENI |
| DroppedNoRuleMatchPacket | Number of packets dropped because the networking device did not find the matching action      |    ENI |
| DroppedMonitoringPingPacket | Number of pingmesh packets dropped by design      |    ENI |
| DroppedResourcesUnifiedFlow MaxFlowsLimit | Number of packets dropped due to reaching the UF limit and being unable to create any more      |    ENI |
| TcpSynPacket | Number of TCP Syn packets seen      |    ENI |
| TcpSynAckPacket | Number of TCP SynAck packets seen      |    ENI |
| FINPackets | Number of FIN packets seen      |    ENI |
| RSTPackets | Number of RST packets seen      |    ENI |
| TransientFlowTimeouts | Number of connections deleted after resimulation      |    ENI |
| TcpConnectionsVerified | Number of TCP connections that completed their syn handshake      |    ENI |
| TcpConnectionsTimedOut | Number of TCP connections that timed out their full TTL(Syn handshake finished, but Fin handshake didn't start)      |    ENI |
| TcpConnectionsReset | Number of TCP connections that received a reset      |    ENI |
| TcpConnectionsResetBySyn | Number of TCP connections that got destroyed and recreated by a SYN on the same tuples      |    ENI |
| TcpConnectionsClosedByFin |       |    ENI |
| TcpHalfOpenTimeouts |       |    ENI |
| TcpConnectionsTimeWait | Number of TCP connections that timed out in the time wait state      |    ENI |
| CurrentTotalFlowEntry | Current number of unified flows (aka connections)      |    ENI |
| CurrentTotalFlow | Current number of main unified flows(Side of the connection that initiated the connection)      |    ENI |
| CurrentHalfOpenFlow | Current number of Ufs in a half open state      |    ENI |
| CurrentTcpFlow | Current number of Ufs that are for a TCP connection      |    ENI |
| CurrentUdpFlow | Current number of Ufs for UDP      |    ENI |
| CurrentOtherFlow | Current number of Ufs for something other than TCP or UDP      |    ENI |
| MaxTotalFlowEntry | Maximum number of Ufs since the initialization of the port      |    ENI & Global|
| MaxHalfOpenFlow | Maximum number of Ufs in a half-open state since the initialization of the port      |    ENI |
| MaxTcpFlow | follow above      |    ENI |
| MaxUdpFlow | follow above      |    ENI |
| MaxOtherFlow | follow above      |    ENI |
| CreatedTotalFlowEntry | Total number of Ufs created      |    ENI |
| CreatedHalfOpenFlow | Total number of flows in a half open state      |    ENI |
| CreatedTcpFlow | follow above      |    ENI |
| CreatedUdpFlow | follow above      |    ENI |
| CreatedOtherFlow | follow above      |    ENI |
| MatchedTotalFlowEntry | Total number of times a UF was matched and used      |    ENI |
| MatchedHalfOpenFlow | follow above      |    ENI |
| MatchedTcpFlow | follow above      |    ENI |
| MatchedUdpFlow | follow above      |    ENI |
| MatchedOtherFlow | follow above      |    ENI |
| CreationRateMaxTotalFlowEntry | Maximum creation rate for Unified flows in a second      |    ENI |
| CreationRateMaxHalfOpenFlow | follow above      |    ENI |
| CreationRateMaxTcpFlow | follow above      |    ENI |
| CreationRateMaxUdpFlow | follow above      |    ENI |
| CreationRateMaxOtherFlow | follow above      |    ENI |
| No ENI Match | evident      |    ENI |
| CPS Counters |       |    ENI & Global |


**Questions**  

- How often will we read?  
- What type of API to use?  
- Will we push or pull from the Controller?

## BGP

Border Gateway Protocol (BGP) is a standardized exterior gateway protocol
designed to exchange routing and reachability information among autonomous
systems on the Internet. BGP is classified as a path-vector routing protocol and
it makes routing decisions based on paths, network policies, or rule-sets
configured by a network administrator. For more information, see [Border Gateway
Protocol](https://en.wikipedia.org/wiki/Border_Gateway_Protocol).

## Watchdogs

## Servicing

## Debugging

Counters per rule to trace an increment per layer, ACL hits, Packet Captures,
Bandwidth Metering for Routing Rules to count bytes (each flow associated with a
bandwidth counter when an LPM is hit \- many flows *may* share the same
counters).

## Flow Replication

For information about flow replication, see **[DASH
High-Availability](../../high-avail/README.md)**.

## Unit Testing and development

- Need ability to run rule processing behavior on dev box / as part of merge
  validation.

## Internal Partner dependencies

- SLB VXLAN support

- Reduced tuple support on host.


