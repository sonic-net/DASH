# DASH pipeline packet flow

1. [Overview](#overview)
2. [Pipeline components](#pipeline-components)
   1. [Packet direction](#packet-direction)
   2. [Matching stages](#matching-stages)
   3. [Routing action](#routing-action)
   4. [Routing action parameter evaluation](#routing-action-parameter-evaluation)
   5. [Routing type](#routing-type)
3. [Examples](#examples)

## Overview

DASH pipeline packet flow is the core of the DASH project. It defines how the traffic is modeled to DASH, packets gets processed and transformation gets applied to the packets.

DASH pipeline is designed to work as a general purpose network function pipeline. Similar to [SAI](https://github.com/opencomputeproject/SAI), it works as a shim layer on top of DPU/ASIC SDKs, provides a set of hardware agnostic APIs that exposes the generic DPU primitives to the upper layer. So, the pipeline itself is not limited to any specific network function, but can be used to implement any network function. 

## Pipeline components

DASH pipeline is modeled as a list of stages. Each stage defines its own tables, and use the table entries to match packets in certain way. When a packet is matched, corresponding metadata will be populated along with the packets, until it passes all stages where a list of final routing actions will be defined. Then by executing these routing actions, the packet will be transformed in the way we want and corresponding flows will be generated according to the direction of the packet.

### Packet direction

In DASH pipeline, traffic can have 2 directions: `inbound` and `outbound`, and each direction has its own pipeline (see more details below). When a new packet arrives, we will first assign a direction to the packet, then process the packet in the corresponding pipeline. This ensures us to do flow match propoerly and transform the packet in the right way.

For example, today, [SONiC-DASH pipeline](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md#2-packet-flows) is used to implement the VNET routing function. In this case, a DASH pipeline represents a VM NIC, and we use VNI from outer encap to set the direction. The `outbound` pipeline is used to process the packets coming from the VM, while the `inbound` pipeline is used to process the packets going into the VM.

### Matching stages



### Routing action

In DASH pipeline, routing actions are the fundamental building blocks. Each routing action is designed to work as below:

1. Take a specific list of parameters as input:
   1. For example, `staicencap` action will take the `underlay_dip`, `underlay_sip`, `encap_type` and `encap_key` to encapsulate the packet.
   2. The parameter can come from 2 places - the metadata defined associated with the entries in each table, or the routing action definition itself. More details will be discussed in the next section.
2. Transform the packet in a specific way, e.g., encapsulate the packet, natting the address and port, etc.
3. Independent to other actions.
   1. With this design, we don't have to worry about the order of the actions. It also enables the hardware to improve the E2E pipeline latency by doing the actions in parallel.

### Routing action parameter evaluation

During the Routing and Mapping stages, when a route/mapping entry is matched, all routing actions listed in the specified routing type will be executed. The parameter for these routing actions will be evaluated along with the matching process. 

This detailed process is designed as below and being P4 compatible, so we could use P4-based implemntation for prootyping and verification, e.g., BMv2 we use today in DASH:

1. In VNI/ENI lookup stage, if an ENI definition is matched, all relevant fields defined in ENI definition and used in the pipeline will be populated as initial metadata.
2. Once passing the ACL checks, we will start routing and mapping stages, which continue evaluating the routing action parameters.
3. Entries used by Routing (matching route entry) and Mapping (matching CA-PA mapping or port) can have any routing action parameter specified. When they are matched, all parameters will be populated as metadata and override what we currently have.
    1. If any metadata is defined in multiple stages, the later ones override the earlier ones, unless stated otherwise for special fields.
    2. If any metadata is not defined in a stage or defined as default value, it will be ignored, such as IP address with value all 0s. 
4. Finally, action can also take a set of limited parameters, that will only take effect in this action only.
    1. Keeping the number of action parameters small is important, because these parameters will be static for all ENIs.
    2. The best practice should be moving the parameters to the entries in step 3, only keeping the absolutely needed ones here.
    3. For example, the encap key is better to be defined in the routing / mapping entries, because different ENI might live in different VNET and need different key.

After all parameters are evaluated, we will use the whatever we have in the latest metadata as the routing action parameters to execute all route actions.

### Routing type

To implement a network funtion, we usually need to do multiple packet transformations, such as adding a tunnel and natting the address or port. This requires us to be able to combine multiple routing actions together, and this is what routing type is for.

In DASH pipeline, routing type is defined as a list of routing actions. And by combining different routing actions into different routing types, we will be able to implement different network functions.

For example:

- We can implement the VNET routing by creating a routing type named `vnet` with only 1 action `staticencap`, which takes the next hop information from the mapping table.
- We can also add additional hop to tunnel the traffic to an firewall first, which is known as [UDR](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview), by creating another routing type named `vnetfw` with a `staticencap` action and an extra `tunnel` actions.
- We can even use `tunnel` action with multiple destinations as ECMP group to implement a simple load balancer!

This combination of routing actions is very flexible and powerful, and it enables us to implement any network function we want.

## Examples

[SONiC-DASH pipeline](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md#2-packet-flows).