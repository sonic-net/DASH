# DASH flow resimulation HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/30/2024 | Riff Jiang | Initial version |

1. [1. Terminology](#1-terminology)
2. [2. Background](#2-background)
3. [3. Use cases](#3-use-cases)
   1. [3.1. Full flow resimulation](#31-full-flow-resimulation)
   2. [3.2. Policy-based flow resimulation](#32-policy-based-flow-resimulation)
4. [4. Packet flow overview](#4-packet-flow-overview)
5. [5. Resource modeling, requirement, and SLA](#5-resource-modeling-requirement-and-sla)
   1. [5.1. Resource modeling](#51-resource-modeling)
   2. [5.2. Scaling requirements](#52-scaling-requirements)
   3. [5.3. Reliability requirements](#53-reliability-requirements)
      1. [5.3.1. Flow replication for flow HA support](#531-flow-replication-for-flow-ha-support)
      2. [5.3.2. Flow resimulation continuation on HA switchover / failover](#532-flow-resimulation-continuation-on-ha-switchover--failover)
   4. [5.4. Impact of CPS path and rate limiting](#54-impact-of-cps-path-and-rate-limiting)
   5. [5.5. Resimulation scope](#55-resimulation-scope)
   6. [5.6. Routing type change after resimulation](#56-routing-type-change-after-resimulation)
   7. [5.7. Flow resimulation after fast path](#57-flow-resimulation-after-fast-path)
6. [6. SAI API Design](#6-sai-api-design)
   1. [6.1. Full flow resimulation](#61-full-flow-resimulation)
   2. [6.2. Policy-based flow resimulation](#62-policy-based-flow-resimulation)
   3. [6.3. Flow resimulation rate limiting](#63-flow-resimulation-rate-limiting)
   4. [6.4. Resimulation scope control](#64-resimulation-scope-control)
   5. [6.5. Counters](#65-counters)

## 1. Terminology

| Term | Explanation |
| --- | --- |
| ENI | Elastic Network Interface |
| CA | Customer Address |
| PA | Provider Address |
| CPS | Connection Per Second |
| PLS | Private Link Service |
| LB | Load Balancer |

## 2. Background

Flow resimulation is one of the frequently involved data plane actions. It is usually invoked whenever the network policy is changed implicitly or explicitly to ensure the existing flow matches with the latest policy.

Whenever flow resimulation is triggered, impacted flows will be marked as resimulation needed. Then the next network packet will be usually used as the actual trigger, bypass the current flow, evaluate the latest network policy, then generate a new flow that replaces the correct flow to make sure the traffic will be forwarded to the correct location.

## 3. Use cases

At high level, flow resimulation will be used in several key cases.

### 3.1. Full flow resimulation

Full flow resimulation is the most common flow resimulation. It is used in cases such as ACL is updated, or in any case where we could not or did not track the flow on policy level, such as mapping.

When flow resimulation happens, all flows on a specific ENI will be resimulated.

### 3.2. Policy-based flow resimulation

Policy-based flow resimulation tries to lower the cost of flow resimulation by creating a relationship between flows and certain policies . For example, whenever a VNET CA-PA mapping is updated, we need and only need to update the flows for this single mapping.

Policy-based flow resimulation can be applied to other policies as well, it can only be applied when the policy change only affects itself (no overlap with other policies). Some typical counter-cases would be ACL or route entry. For example - say, an ENI has a routing entry 10.0.0.0/16 programmed and some flows created that matched this entry. Later on, a new entry 10.0.1.0/24 is programmed, and it requires part of existing flows to be resimulated to hit this new entry. In this case, full flow resimulation is preferred.

Policy-based flow resimulation can only be triggered on-demand, hence will not be triggered by flow resimulation. For example, when a CA-PA mapping is removed, the association between this mapping and all flows that were associated with it will be removed. These flows will eventually idle timeout. And new mapping even with the same key (CA) will not cause these flows to be associated again.

## 4. Packet flow overview

To explain how flow resimulation works in high level, here is how flow resimulation usually works, but the real implementation is not limited to the following approach:

- **Step 1 – Trigger**: Certain events happens, that triggers flow resimulation request to be invoked.
- **Step 2 – Flow marking**: On request, certain flags will be updated which indicates a specific set of flows need to be resimulated, which could be the whole ENI or for a mapping or a specific flow.
- **Step 3 – Resimulation**: Actual resimulation is usually triggered by the very next packet that hits the impacted forwarding-side flow. We cannot use the reverse side packet, as policies are programmed asymmetrically. In the context of DASH, the workflow is roughly:
  - In Conntrack Lookup stage, if we found the id stored in its flow doesn't match the one in the ENI, we treat this flow as resimulated.
  - For resimulated flows, we continue to run the later ACL and match stages instead of directly applying the actions saved in the flow.
  - In Conntrack Update stage, a new pair of flow will be generated and replaces the current flow, which finishes the process of flow resimulation.

## 5. Resource modeling, requirement, and SLA

### 5.1. Resource modeling

Flow resimulation uses the ENI and each policy, which follows the same resource modeling as SmartSwitch. No special requirement is needed here.

### 5.2. Scaling requirements

| Metric (200Gb card) | Requirement |
| --- | --- |
| ENI per card | 32 |
| # of flows per card | 32M (Bidirectional) |
| # of CA-PA mappings per card | 8M |
| CPS + Flow resimulation | 3M |
| Max # of flows to update per second | Configurable on ENI level |
| Max latency of completing full flow resimulation API call | (TBD) |
| Max latency of completing policy-based flow resimulation API call | (TBD)  |

### 5.3. Reliability requirements

#### 5.3.1. Flow replication for flow HA support

In HA setup, whenever flow is resimulated:

1. We should always use the SDN policy from the active side, who makes flow decisions, to update the flow with the new flow actions (SDN transformations).
2. The new flow actions need to be replicated to the standby side as it is without evaluating the policies on the standby side.

#### 5.3.2. Flow resimulation continuation on HA switchover / failover

In HA setup, we will have 2 ENIs forming active-standby pair. Since both ENIs are programmed independently, the flow resimulation could be still in progress, when switchover / failover happens.

To ensure the existing flows can pick up the right policy, a flow reconcile operation will be called on the new active side, which ensures the latest policy can be picked up by the existing flows.

For more information, please refer to the HA design docs.

### 5.4. Impact of CPS path and rate limiting

As the high-level workflow shows, the flow resimulation will make the network packet go through the slow path. Hence, the more flows being resimulated, the less new connections we could make every second.

This means at least, flow resimulation will share the limit of CPS, hence New connection + Flow resimulated <= 3M/s on a 200Gb card.

Since flow resimulation without rate limiting can cause serious impact of CPS performance, or even completely kill the CPS path, to avoid flow resimulation from seriously impacting the CPS path, a limit shall be added on the ENI level to limit the max number of flows that can be resimulated per seconds as below.

### 5.5. Resimulation scope

To control the resimulation scope, we have 2 requirements:

1. Disable the resimulation:
   1. This is needed for PL/PLS mappings, because we should not change the flows and keep sending it to the same destination.
2. Partial flow resimulation:
   1. VFP has a layer flow cache feature, which allows part of the final action being resimulated, but keep the others unchanged.
   2. This will help the future scenarios.

### 5.6. Routing type change after resimulation

In corner case of mapping update and ends up with different routing type, the resimulation flow could send unexpected packet and break the connection, which is expected and acceptable.

### 5.7. Flow resimulation after fast path

After flow is updated by LB fast path packet, the flow will not be resimulated by any type of flow resimulation request anymore.

For example, in Private Link case, after fast path updates the flow, it will be pointed to the backend VM of PLS. If we resimulate the flow, it will start to point to the PLS PA again, which could be new and break the flow.

## 6. SAI API Design

### 6.1. Full flow resimulation

To support full flow resimulation on the ENI level, here are the attributes we are adding on the ENI object:

| Attribute name | Type | Description |
| -------------- | ---- | ----------- |
| SAI_ENI_ATTR_FULL_FLOW_RESIMULATION_REQUESTED | `bool` | Full flow resimulation requested. Once request is received, the value shall be reset to false. |

### 6.2. Policy-based flow resimulation

Similar attributes can be added on the CA-PA mapping table or any new table that is needed in the future.

| Attribute name | Type | Description |
| -------------- | ---- | ----------- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_FLOW_RESIMULATION_REQUESTED | `bool` | Flow resimulation requested on CA-PA mapping entry. Once request is received, the value shall be reset to false. |

### 6.3. Flow resimulation rate limiting

To provide the ENI level flow resimulation rate limiting, here are the attributes we are adding on the ENI object:

| Attribute name | Type | Description |
| -------------- | ---- | ----------- |
| SAI_ENI_ATTR_MAX_RESIMULATED_FLOW_PER_SECONDS | `sai_uint64_t` | Max flow resimulation speed (PPS). Default is 0, means no limit enforced. |

Both full and policy-based flow resimulation also shares the same rate limiting from the ENI.

### 6.4. Resimulation scope control

To provide similar feature as layer flow cache in the ASIC world, we could add a flag that bypass some transformations that we do for each routing types.

The ingredients we have today are the actions that defined in each routing types, hence we are going to have routing actions defined in SAI API and use them to control the resimulation scope.

```c
typedef enum _sai_dash_routing_action_t
{
    SAI_DASH_ROUTING_ACTION_STATIC_ENCAP = (1 << 0),
    SAI_DASH_ROUTING_ACTION_4TO6 = (1 << 1),
    ...
} sai_dash_routing_action_t;
```

Essentially, every entry that can publish routing types needs to have an attribute added to disable the actions in the flow resimulation, which is shown as below:

On routing entry:

| Attribute name | Type | Description |
| -------------- | ---- | ----------- |
| SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ROUTING_ACTIONS_DISABLED_IN_FLOW_RESIMULATION | `sai_uint64_t` | Routing actions that need to be disabled in flow resimulation. |

On CA-PA mapping entry:

| Attribute name | Type | Description |
| -------------- | ---- | ----------- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_ROUTING_ACTIONS_DISABLED_IN_FLOW_RESIMULATION | `sai_uint64_t` | Routing actions that need to be disabled in flow resimulation. |

### 6.5. Counters

To monitor how flow resimulation works, we can add the following counters on ENI level for counting the flow manipulation operations.

| SAI stats name | Description |
| --- | --- |
| SAI_ENI_STAT_FLOW_CREATED | Total flow created on ENI. |
| SAI_ENI_STAT_FLOW_CREATE_FAILED | Total flow failed to create on ENI. |
| SAI_ENI_STAT_FLOW_UPDATED | Total flow updated on ENI. |
| SAI_ENI_STAT_FLOW_UPDATE_FAILED | Total flow failed to update on ENI. |
| SAI_ENI_STAT_FLOW_DELETED | Total flow deleted on ENI. |
| SAI_ENI_STAT_FLOW_DELETE_FAILED | Total flow failed to delete on ENI. |
| SAI_ENI_STAT_FLOW_AGED | Total flow aged on ENI. |

We also add 2 dedicated counters for flow resimulation. The reason is that we also have other reasons to update the flow, such as load balancer fast path.

| SAI stats name | Description |
| --- | --- |
| SAI_ENI_STAT_FLOW_UPDATED_BY_RESIMULATION | Total flow updated by resimulation on ENI. |
| SAI_ENI_STAT_FLOW_UPDATE_BY_RESIMULATION_FAILED | Total flow failed to update by resimulation on ENI. |
