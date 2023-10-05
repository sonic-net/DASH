# DASH-SAI pipeline packet flow

1. [1. Overview](#1-overview)
2. [2. Pipeline Overview](#2-pipeline-overview)
3. [3. Pipeline components](#3-pipeline-components)
   1. [3.1. Per-packet Metadata bus](#31-per-packet-metadata-bus)
   2. [3.2. Direction Lookup](#32-direction-lookup)
   3. [3.3. Pipeline Lookup](#33-pipeline-lookup)
   4. [3.4. Packet Decap](#34-packet-decap)
   5. [3.5. Conntrack Lookup and Update](#35-conntrack-lookup-and-update)
      1. [3.5.1. Flow table](#351-flow-table)
      2. [3.5.2. Flow creation](#352-flow-creation)
   6. [3.6. Pre-pipeline ACL and Post-pipeline ACL](#36-pre-pipeline-acl-and-post-pipeline-acl)
   7. [3.7. Matching stages and metadata publishing](#37-matching-stages-and-metadata-publishing)
      1. [3.7.1. Matching stage](#371-matching-stage)
      2. [3.7.2. Device role and stage connections](#372-device-role-and-stage-connections)
      3. [3.7.3. Stage transitions](#373-stage-transitions)
      4. [3.7.4. Metadata publishing](#374-metadata-publishing)
   8. [3.8. Routing action](#38-routing-action)
   9. [3.9. Routing type](#39-routing-type)
4. [4. Examples](#4-examples)
   1. [4.1. VNET routing](#41-vnet-routing)
   2. [4.2. Load balancer (L4 DNAT)](#42-load-balancer-l4-dnat)
   3. [4.3. Load balancer (L3 SNAT)](#43-load-balancer-l3-snat)
   4. [4.4. More](#44-more)

## 1. Overview

DASH-SAI pipeline packet flow is the core of the DASH project. It defines from device perspective, how the traffic is modeled in DASH, packets gets processed and transformation gets applied to the packets.

DASH-SAI pipeline is designed to work as a general purpose network function pipeline. Similar to [SAI](https://github.com/opencomputeproject/SAI), it works as a shim layer on top of DPU/ASIC SDKs, provides a set of low level hardware agnostic APIs that exposes the generic DPU primitives to the upper layer. So, the pipeline itself is not limited to any specific network function, but can be used to implement any network function.

## 2. Pipeline Overview

DASH-SAI pipeline is modeled as a list of stages. Each stage defines its own tables, and use the table entries to match packets in certain way and publishing thecorresponding metadata when an entry is matched. After all stages are processed, a list of final routing actions will be defined. Then, by executing these routing actions, the packet will be transformed in the way we want and corresponding flows will be generated according to the direction of the packet.

On the high level the pipeline looks like below:

```mermaid
flowchart TB
    DL[Direction<br>Lookup]
    PL[Pipeline<br>Lookup]
    PD[Packet<br>Decap]

    subgraph P0[DASH Pipeline 0]
        subgraph In0[Inbound Pipeline]
            CTL0[Conntrack<br>Lookup]
            PreACL0[Pre-pipeline<br>ACL]
            MATS0[Matching<br>Stages]
            AA0[Action<br>Apply]
            PostACL0[Post-pipeline<br>ACL]
            CTU0[Conntrack<br>Update]
            MS0[Meter<br>Update]
        end

        subgraph Out0[Outbound Pipeline]
            CTL1[Conntrack<br>Lookup]
            PreACL1[Pre-pipeline<br>ACL]
            MATS1[Matching<br>Stages]
            AA1[Action<br>Apply]
            PostACL1[Post-pipeline<br>ACL]
            CTU1[Conntrack<br>Update]
            MS1[Meter<br>Update]
        end
    end

    subgraph P1[DASH Pipeline 1]
        In1[Inbound Pipeline<br>...]
        Out1[Outbound Pipeline<br>...]
    end

    Out[Packet<br>Out]

    DL --> PL
    PL --> PD

    PD --> In0
    PD --> Out0
    PD --> In1
    PD --> Out1 
    PD --> |No Match| Out

    CTL0 --> PreACL0
    CTL0 --> |Flow Match| AA0
    PreACL0 --> MATS0
    MATS0 --> AA0
    AA0 --> PostACL0
    PostACL0 --> CTU0
    AA0 --> |Flow Match| MS0
    CTU0 --> MS0
    MS0 --> Out

    CTL1 --> PreACL1
    CTL1 --> |Flow Match| AA1
    PreACL1 --> MATS1
    MATS1 --> AA1
    AA1 --> PostACL1
    PostACL1 --> CTU1
    AA1 --> |Flow Match| MS1
    CTU1 --> MS1
    MS1 --> Out
```

This design allows our upper layers to be flexible and doesn't limit to any specific object models for modeling their own policies. For example, [SONiC-DASH pipeline](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md#2-packet-flows) uses DASH-SAI pipelie to implement VNET routing scenarios by translating the [SONiC DASH APIs](https://github.com/sonic-net/sonic-dash-api/tree/master/proto) to DASH-SAI model:

- A DASH-SAI pipeline is used to represent a VM NIC (ENI).
- The VxLAN VNI is used to do the direction lookup.
- The inner MAC address is used for pipeline lookup, a.k.a. ENI lookup (ENI). 
- Once it goes into the corresponding DASH pipeline, the `outbound` pipeline will be used to process the packets coming from the VM, while the `inbound` pipeline will be used to process the packets going into the VM.

## 3. Pipeline components

### 3.1. Per-packet Metadata bus

First of all, since we have multiple matching stages in the pipeline, we need a way to pass the information from the matched entries in the earlier stages to the later ones to help us making final decisions on packet transformation. And this is what metadata bus is for.

At high-level, the metadata bus is a set of fields that being carried all the way through the pipeline along with the packet. It contains:

- The information from the original packet, such as encap information.
- The information from each matched entry and related data structures, e.g., when a VNET mapping entry is matched, we will publish the information from VNET to the metadata bus. 
- The routing action and its inline parameters from the matched entry.

Implementation-wise, this is similar to Packet Header Vector or Bus in NPL.

### 3.2. Direction Lookup

In DASH-SAI pipeline, traffic are split into 2 directions: `inbound` and `outbound`. Each direction has its own pipeline (see pipeline overview above). When a new packet arrives, we will assign a direction to the packet, then process the packet in the corresponding pipeline. This ensures us to do flow match propoerly and transform the packet in the right way.

### 3.3. Pipeline Lookup

DASH supports multi-tenancy model for traffic handling. A single device can have multiple pipelines, and each pipeline is used to handle traffic for a specific tenant. When a packet arrives, besides direction lookup, we also need pipeline lookup to determine which pipeline to use for processing the packet.

For example, if we like to implement a VM NIC with, then we can model one pipeline as one VM NIC, then use the inner packet MAC to find the pipeline. However, if we would like to implement a load balancer, we can use a DASH-SAI pipeline to represent a load balancer instance and use the Public IP to find the SAI pipeline.

```mermaid
flowchart TD
    subgraph ENI
        EL[ENI Lookup]

        EP0[ENI 0 Pipeline]
        EP1[ENI 1 Pipeline]
        EP2[ENI 2 Pipeline]
    end

    subgraph LoadBalancer
        VL[Vip Lookup]

        LBP0[LB 0 Pipeline]
        LBP1[LB 1 Pipeline]
        LBP2[LB 2 Pipeline]
    end

    EL --> |ENI 0| EP0
    EL --> |ENI 1| EP1
    EL --> |ENI 2| EP2

    VL --> |LB 0| LBP0
    VL --> |LB 1| LBP1
    VL --> |LB 2| LBP2
```

A pipeline can also define its initial matching stages, which will be used for starting processing the packets if no flow is matched.

> NOTE:
> 
> DASH-SAI pipeline is a logical concept. It doesn't have to be 1 to 1 mapping to a physical ASIC pipeline. The underlying implementation can be as simple as a metadata field update with a specific value, when the entry getting matched, e.g., `ENI = Inner Source/Destination MAC`.

### 3.4. Packet Decap

If a pipeline is found, before processing the packets, all outer encaps will be decaped, and with key information saved in metadata bus, such as encap type, source IP and VNI / GRE Key, exposing the inner most packet going through the pipeline. This simplifies the flow matching logic and also allow us to create the reverse flow properly.

### 3.5. Conntrack Lookup and Update

After entering a specific pipeline, the first stage will be the Conntrack Lookup stage, which does the flow lookup. If any flow is matched, the saved actions will be applied, the metering counters will be updated, and the rest of pipeline will be skipped.

#### 3.5.1. Flow table

The core of the Conntrack Lookup and Update stage is flow table, whose usage **MUST** follow the rules below:

1. Flows **MUST** be stored based on the pipeline direction. 
   1. When outbound pipeline creates a flow, the forwarding flow should be created on the outbound side, while reverse flow should be created on the inbound side.
   2. When inbound pipeline creates a flow, it creates the flow in reversed way.
2. The flow lookup **MUST** use the information of inner most packet.
   1. The matching keys can be configurated via the DASH flow APIs during the DASH initialzation.
   2. Although the outer encaps are decap'ed and not used in flow matching, the source information of each encap **MUST** be compared. If any change is detected, the flow lookup **MUST** fail, pushing the packet going through the rest of pipeline, just like a new flow.
      1. This is because the source information will be used for creating reverse flow, and failover can happen to whoever that sends us packet, so we need this behavior to fix the reverse flow actions.

After the flow lookup, if a flow is matched, we will apply the saved actions in the flow direction and skip the rest of the pipeline. Otherwise, we will continue the pipeline processing.

#### 3.5.2. Flow creation

After all packet transformations are applied, we will create a new flow in the flow table.

- The forwarding flow creation is straight forward, because all the final transformations are defined in the flow actions and metadata bus.
- To properly create the reverse flow, we will use the information from the original tunnels, and reverse them as return encaps, which is why we need to save all the original tunnel information when doing packet decaps.

There could be cases where the encaps are asymmetrical, which means the incoming packet and return packet uses different encaps. To fix this issue, a special action called `reverse_tunnel` is defined, which enables reverse side of the encaps.

### 3.6. Pre-pipeline ACL and Post-pipeline ACL

Pre-pipeline ACL and Post-pipeline ACL are used to drop the unexpected traffic before and after the packet transformation. It works as below:

1. As the high-level pipeline shows above, if an incoming packet hits a flow, it will skip matching all the ACLs. If an incoming packet is denied by a ACL, the packet will be dropped without creating a flow.
2. Both outbound and inbound pipeline has its own ACL stages, and only used for matching the packets in their direction.

A typical usage of the ACLs is to implement security policies. For example, in SONiC-DASH pipeline, we use the pre/post-pipeline ACLs to implement the underlay and overlay ACLs in both directions, where overlay ACLs will be used for implementing customer policies, while underlay ACLs will be used for implementing the infrastructure policies.

```mermaid
flowchart TD
    subgraph Outbound Pipeline
        Out_PreACL[Overlay ACL<br>== Outbound Pre-Pipeline ACL ==]
        Out_MS[Match Stages]
        Out_PostACL[Underlay ACL<br>== Outbound Post-Pipeline ACL ==]
    end

    subgraph Inbound Pipeline
        In_PreACL[Underlay ACL<br>== Inbound Pre-Pipeline ACL ==]
        In_MS[Match Stages]
        In_PostACL[Overlay ACL<br>== Inbound Post-Pipeline ACL ==]
    end

    Out_PreACL --> Out_MS
    Out_MS --> Out_PostACL

    In_PreACL --> In_MS
    In_MS --> In_PostACL
```

### 3.7. Matching stages and metadata publishing

#### 3.7.1. Matching stage

Matching stage is the one of the core part of the DASH-SAI pipeline and the components that gives the pipeline flexibility.

In DASH-SAI pipeline, a matching stage is a basic building block for packet matching and metadata publishing. And the DASH-SAI pipeline basically works as matching and metadata publishing until the final routing actions are executed. Currently, we support the following types of matching stages:

| Stage type | Match Type | Match Fields | Metadata Behavior |
| ---------- | ---------- | ------------ | -------- |
| Routing | LPM | Source IP or Destination IP | Publish metadata from matched routing entry |
| VNET Mapping | Exact Match | Source IP or Destination IP | Publish metadata from matched VNET and VNET mapping entry |
| Port Mapping | Range Match | Source Port + Destination Port | Publish metadata from matched port mapping entry |

For more on the metadata publishing, please refer to the metadata publishing section below.

#### 3.7.2. Device role and stage connections

Although, ideally, by simply creating different matching stages and connecting them in different ways, we can easily implement different network functions. However, in reality, it might make the pipeline hard to implement, model, debug and validate or test at this moment. For example, changing matching fields, matching type and connection dynamically or on pipeline creation is simply beyond the ability of P4. 

To address this problem, we can define a set of predefined device roles, each device role has their own predefined stages and connections in the pipeline.

For example, today the only device role we support is ENI, which is used to implement the VM NIC. To ensure we have enough flexibility, the match stages are designed to be connected from larger range to smaller range as below:

```mermaid
flowchart LR
    RoutingDst[Routing<br>Destination IP]
    RoutingSrc[Routing<br>Source IP]
    MapDst[VNET Mapping<br>Destination IP]
    MapSrc[VNET Mapping<br>Source IP]
    TcpPortMap[TCP Port Mapping<br>Source + Dest Port]
    UdpPortMap[UDP Port Mapping<br>Source + Dest Port]

    RoutingDst --> | srclpmrouting | RoutingSrc
    RoutingSrc --> | maprouting | MapDst
    MapDst --> | srcmaprouting | MapSrc
    MapSrc --> | portmaprouting | TcpPortMap
    MapSrc --> | portmaprouting | UdpPortMap
```

#### 3.7.3. Stage transitions

To transit between stages, we can set the `transit_to` field in the matched entry. This will instruct the pipeline to skip the stages before the `transit_to` stage and resume from there. Now, DASH supports the following stages:

| `transit_to` value | Stage |
| --------------------- | ----- |
| `lpmrouting` | Routing stage by checking destination IP |
| `srclpmrouting` | Routing stage by checking source IP |
| `maprouting` | VNET Mapping stage by checking destination IP |
| `srcmaprouting` | VNET Mapping stage by checking source IP |
| `portmaprouting` | TCP or UDP Port Mapping stage |
| `rss` | Sending it to CPU |
| `drop` | Drop the packet |

Here is an example that shows how the routing stage entry looks like:

```json
// Routing stage entry:
// When this entry is matched, we will move to VNET mapping stage, which executes maprouting action and jump to VNET mapping stage.
"DASH_ROUTE_TABLE:123456789012:10.0.1.0/24": {
    "transit_to": "maprouting",
    "vnet": "Vnet1"
}
```

To avoid loop shows up in the pipeline, the pipeine is designed to be forward only. The transition behavior can simply be described by the code below:

```c
if (meta.transit_to == DASH_MATCH_STAGE_MAPROUTING) {
    maprouting.apply();
}
if (meta.transit_to == DASH_MATCH_STAGE_SRCMAPROUTING) {
    srcmaprouting.apply();
}
// ...
```

This allows us easily bypass the stages as needed, also avoid loop being accidentally created. Take Routing stage + TCP flow as an example, it can use different transition to jump to different stages. 

```mermaid
flowchart LR
    RoutingDst[Routing<br>Destination IP]
    RoutingSrc[Routing<br>Source IP]
    MapDst[VNET Mapping<br>Destination IP]
    MapSrc[VNET Mapping<br>Source IP]
    TcpPortMap[TCP Port Mapping<br>Source + Dest Port]

    RoutingDst --> | srclpmrouting | RoutingSrc
    RoutingDst --> | maprouting | MapDst
    RoutingDst --> | srcmaprouting | MapSrc
    RoutingDst --> | portmaprouting | TcpPortMap

    RoutingSrc --> | maprouting | MapDst
    MapDst --> | srcmaprouting | MapSrc
    MapSrc --> | portmaprouting | TcpPortMap
```

#### 3.7.4. Metadata publishing

When an entry is matched in the matching stages, we will publish the metadata defined in the entry to the metadata bus, and overrides the existing ones, if any. This means, all the entries in each matching stage can all be defined similarly as below:

```json
"DASH_SOME_OBJECT_TABLE:<Unique Key of the object>": {
    "transit_to": "<next stage name>",
    "routing_type": "<routing type name>",

    // Metadata properties/attributes ...
}
```

Take the VNET mapping as an example. When following VNET mapping is matched, `underlay_dip`, `4to6_sip_encoding`, `4to6_dip_encoding` and `metering_class` will be published to the metadata bus.

```json
// VNET mapping entry (VNET mapping stage)
"DASH_VNET_MAPPING_TABLE:Vnet1:10.0.1.1": {
    "transit_to": "portmaprouting",
    "routing_type": "do_something",

    // Underlay destination IP address. Used by staticencap action.
    "underlay_dip": "3.3.3.1",

    // Overlay IP address encoding from v4 to v6. Used by 4to6 action.
    "4to6_sip_encoding": "9988::/ffff::",
    "4to6_dip_encoding": "1122:3344:5566:7788::0303:0301/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",

    // Metering ID. Used in metering stage.
    "metering_class": "60001"
}
```

After all matching stages is done, we will start applying all the actions. All the latest values in the metadata bus will be used as the input parameters for the routing actions.

> NOTE:
> 
> The Direction Lookup and Pipeline Lookup stages are also matching stages, so they can also populate metadatas too, e.g., ENI-level metadata for underlay encap.

### 3.8. Routing action

In DASH-SAI pipeline, routing actions are the fundamental building blocks for packet transformations. Each routing action is designed to work as below:

1. Take a specific list of metadata fields as input parameters:
   1. For example, `staicencap` action will take the `underlay_dip`, `underlay_sip`, `encap_type` and `encap_key` to encapsulate the packet.
   2. The parameters can come from 2 places - the metadata defined associated with the entries in each table, or the routing action definition itself. More details will be discussed in the next section.
2. Transform the packet in a specific way, e.g., encapsulate the packet, natting the address and port, etc.
3. Independent to other actions.
   1. With this design, we don't have to worry about the order of the actions.
   2. This also enables the hardware to improve the E2E pipeline latency by doing the actions in parallel.

Take `staticencap` as an example, it can be defined as below:

- Action parameters:
    - `encap_type`: "nvgre|vxlan|..."
- Metadata parameters:
    - `underlay_dip`: Destination IP used in encap.
    - `underlay_sip`: Source IP used in encap.
    - `encap_key`: GRE key in NvGRE or VNI in VxLAN
- Actions:
    - Enable the underlay encap header based on the `encap_type`.
    - Update the underlay encap header with `encap_key`, `underlay_dip`, `underlay_sip`.

### 3.9. Routing type

To implement a network funtion, we usually need to do multiple packet transformations, such as adding a tunnel and natting the address or port. This requires us to be able to combine multiple routing actions together, and this is what routing type is for.

In DASH-SAI pipeline, routing type is defined as a list of routing actions. And by combining different routing actions into different routing types, we will be able to implement different network functions.

For example:

- We can implement the VNET routing by creating a routing type named `vnet` with only 1 action `staticencap`, which takes the next hop information from the mapping table.
- We can also add additional hop to tunnel the traffic to an firewall or network virtual appliance first, which is known as [UDR](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview), by creating another routing type named `vnetfw` with a `staticencap` action and an extra `tunnel` actions.
- We can even use `tunnel` action with multiple destinations as ECMP group to implement a simple load balancer!

This combination of routing actions is very flexible and powerful, and it enables us to implement any network function we want.

## 4. Examples

### 4.1. VNET routing

```json
[
    // When sending to anywhere in the VNET, we start to lookup the destination
    "DASH_ROUTE_TABLE:123456789012:10.0.1.0/24": {
        "transit_to": "maprouting",
        "vnet": "Vnet1"
    },

    // If we are sending to 10.0.1.1, this entry will be matched and set the underlay destination IP for staticencap action.
    "DASH_VNET_MAPPING_TABLE:Vnet1:10.0.1.1": {
        "routing_type": "vnet",
        "underlay_dip": "3.3.3.1",
    }

    // The corresponding table level information will also be populated, in this case - "encap_key"
    "DASH_VNET_TABLE:Vnet1": {
        "name": "559c6ce8-26ab-4193-b946-ccc6e8f930b2",
        "encap_key": "45654"
    },

    // This is the final routing type that gets executed because VNET mapping table gets matched,
    // which addes the vxlan tunnel to the destination.
    "DASH_ROUTING_TYPE_TABLE:vnet": [
        {
            "name": "action1",
            "action_type": "static_encap",
            "encap_type": "vxlan",
        }
    ]
]
```

### 4.2. Load balancer (L4 DNAT)

```json
[
    // When ENI is matched, we can set the initial stage to maprouting.
    "DASH_ENI_TABLE:123456789012": {
	    "eni_id": "497f23d7-f0ac-4c99-a98f-59b470e8c7bd",
        "transit_to": "maprouting",
	    "vnet": "vipmapping"
        // ...
    },

    // If the packet is sent to 1.1.1.1, we start to do port mapping
    "DASH_VNET_MAPPING_TABLE:Vnet1:1.1.1.1": {
        "transit_to": "portmaprouting",
        "port_mapping_id": "lb-portmap-1-1-1-1",
    }

    "DASH_TCP_PORT_MAPPING_TABLE:lb-portmap-1-1-1-1": [
        {
            "routing_type": "lbdnat",

            "src_port_min": 0,
            "src_port_max": 65535,
            "dst_port_min": 443,
            "dst_port_max": 443,

            "underlay_tunnel_id": "lb-portmap-backend-1-1-1-1"
        }
    ]

    // The corresponding table level information will also be populated, in this case - "encap_key"
    "DASH_VNET_TABLE:vipmapping": {
        "name": "559c6ce8-26ab-4193-b946-ccc6e8f930b2",
        "encap_key": "45654"
    },

    // This is the final routing type that gets executed. The tunnel_nat action will nat the inner packet destination
    // from public ip to VM IP, also adds the corresponding vxlan tunnel to the destination.
    //
    // To start simple, all destination IPs can be treated as an ECMP group. And algorithm can be defined as metadata
    // in the VIP entry as well.
    "DASH_ROUTING_TYPE_TABLE:lbnat": [
        {
            "name": "action1",
            "action_type": "tunnel_nat",
            "target": "underlay"
        }
    ]
]
```

### 4.3. Load balancer (L3 SNAT)

```json
[
    // Routing to Internet.
    "DASH_ROUTE_TABLE:123456789012:0.0.0.0/0": {
        "routing_type": "l3snat",
        "nat_sips": "1.1.1.1,2.2.2.2"
    },

    // This is the final routing type that gets executed.
    // 
    // The nat action will nat the inner packet source ip based on the nat_sips defined in the routing entry.
    // All IPs will be treated as an ECMP group. And algorithm can be defined as metadata in the routing entry as well.
    "DASH_ROUTING_TYPE_TABLE:l3snat": [
        {
            "name": "action1",
            "action_type": "nat"
        }
    ]
]
```

### 4.4. More

- [SONiC-DASH packet flows](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md#2-packet-flows)
