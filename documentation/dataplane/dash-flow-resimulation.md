# DASH flow resimulation

In DASH pipeline, after flow is created, it may not remain unchanged until it is deleted. Things like policy updates could cause flow to be modified or deleted. This is called flow resimulation. And this doc is trying to describe this behavior in depth.

1. [1. Full flow resimulation](#1-full-flow-resimulation)
   1. [1.1. Flow incarnation id](#11-flow-incarnation-id)
   2. [1.2. Flow resimulation process](#12-flow-resimulation-process)
   3. [1.3. Flow incarnation id overflow](#13-flow-incarnation-id-overflow)
   4. [1.4. Flow resimulation w/ flow HA](#14-flow-resimulation-w-flow-ha)
   5. [1.5. Object model change summary for full flow resimulation](#15-object-model-change-summary-for-full-flow-resimulation)
2. [2. Policy-based flow resimulation](#2-policy-based-flow-resimulation)
   1. [2.1. Flow tracking key and flow resimulated bit](#21-flow-tracking-key-and-flow-resimulated-bit)
   2. [2.2. Active flow tracking](#22-active-flow-tracking)
   3. [2.3. Passive flow tracking](#23-passive-flow-tracking)
   4. [2.4. Flow tracking key in flow HA](#24-flow-tracking-key-in-flow-ha)
   5. [2.5. Object model change summary for policy-based flow resimulation](#25-object-model-change-summary-for-policy-based-flow-resimulation)
3. [3. Learning-based flow resimulation](#3-learning-based-flow-resimulation)
4. [4. Explicit per flow consistency (PCC) support](#4-explicit-per-flow-consistency-pcc-support)

## 1. Full flow resimulation

Full flow resimulation is the most common flow resimulation. For example, after ACL is updated, we will need to resimulate all flows for this pipeline, e.g., ENI.

### 1.1. Flow incarnation id

To implement this, A flow incarnation id is introduced:

- Each pipeline will store its own flow incarnation id, which starts from 0 and changes whenever all flows needs to resimulated by updating the SAI attribute on the pipeline.
- Each flow also stores the current id when it is created.

### 1.2. Flow resimulation process

With flow incarnation id, we can implement full flow resimulation as follows:

- When a new packet arrives, the current flow incarnation id will be stored into the metadata bus.
- In Conntrack Lookup stage, if we found the id stored in its flow doesn't match the one in the pipeline, we treat this flow as resimulated.
- For simulated flows, we continue to run the later ACL and match stages instead of directly applying the actions saved in the flow.
- In Conntrack Update stage, a new pair of flow will be generated and replaces the current flow, which finishes the process of flow resimulation.

After this, the later packet will directly hit the new flow and bypass the later stages.

### 1.3. Flow incarnation id overflow

Some flows can be very low volume and causing flow incarnation id stops working. Say, if the flow incarnation id is 8 bits, and not it is set to 1, a low volume flow is created. And after 256 flow resimulation calls, the next packet finally arrives and see the same id, which bypasses the flow resimulation process.

To solve this, whenever the incarnation id overflows, we will need to treat all flows as resimulated. Implementation-wise, this can be done by adding another bit to indicate overflow happened, then reset the flow incarnation id to 0 in each flow during the next flow aging process. After flow aging is done, we can reset the overflow bit.

This is a really rare case, so we don't need to worry about the performance impact of this, as the traffic volume is super low for these flows anyway.

### 1.4. Flow resimulation w/ flow HA

When flow HA is enabled, both flow incarnation id and the updated flow needs to be synced to the standby pipeline.

The process follows the flow HA design. When replacing the current flow with the newly generated flows, the new flows will be marked as "not-synced". Then the packet will be sent back to the pipeline, which triggers the inline flow sync logic and takes the flow information to the other side.

Since the flow incarnation id is part of the flow state, it will also be synched to the standby side and updates the stored id there. Although in flow HA design, the policy will be programmed to both active and standby side, but we cannot use the id in the standby side directly, because these 2 pipelines are programmed independently, so we don't have a way to ensure that the standby one always matches the active one. To solve this, we make the standby pipeline always follows the active side, which follows the flow lifetime management design in flow HA.

### 1.5. Object model change summary for full flow resimulation

To summarize, the following changes are needed to implement full flow resimulation:

- 2 properties needs to be added for each pipeline:

    ```json
    "DASH_SAI_ENI_TABLE|123456789012": {
        "flow_incarnation_id": 0,
        "flow_incarnation_overflowed": false,
        // ...
    }
    ```

- 1 property needs to be added on flow state:
  
  ```c
  typedef enum _sai_flow_state_metadata_attr_t {
      SAI_FLOW_ATTR_START,
      // ...
      SAI_FLOW_METADATA_ATTR_INCARNATION_ID, // Saved flow incarnation id.
      SAI_FLOW_METADATA_ATTR_END
  } sai_flow_metadata_attr_t;
  ```

## 2. Policy-based flow resimulation

Another typical case of flow resimulation is policy-based resimulation. For example, whenever a VNET CA-PA mapping is updated, we need and only need to update the flows for this single mapping. This requirement can be applied to other policy updates as well, for example, routing entry or port mapping.

### 2.1. Flow tracking key and flow resimulated bit

To solve this, a 128-bit flow tracking key can be set in each match stage entry. Additionally, this key and a flow resimulated bit is added to each flow.

Whenever a match stage entry is updated which has a non-zero flow tracking key specified, all flows that shares the same flow tracking key will be resimulated together, which set the flow resimulated bit in each associated flow.

### 2.2. Active flow tracking

To implement the flow tracking for each key, we can leverage the "Conntrack Update" stage:

- When a flow is created, we can get the flow tracking key from the metadata bus. If it is non-zero, we will store this mapping in a hash table.
- When a flow is destroyed or resimulated, we can get the current flow tracking key from the flow state as well as the new one from metadata bus, then fix the mapping.

When a match stage entry is updated, we can then find all flows that stored in the hash table and resimulate them by flipping their flow resimulated bit to true one by one.

### 2.3. Passive flow tracking

Although active flow tracking can resimulate the flows very fast, it requires us to maintain a flow mapping actively in the memory, which could consume a lot of of memory. When memory is a concern, we can also use passive flow tracking as described below.

The implementation is simple:

- Whenever a match stage with non-zero flow tracking key is updated, we add the key into the pending resimulation list of the pipeline.
- Then kick off the flow aging process immediately, pickup the keys from the pending list, and resimulate all flows that matches the keys.
- If the flow aging process completes, check if any more keys in the pending list. If yes, kick off the flow aging process again.

This approach doesn't require any additional memory, however, it will be slower.

### 2.4. Flow tracking key in flow HA

Policy-based flow resimulation introduced another problem in flow HA. Since both active and standby side are programmed independently, how can we ensure that the flows associated to a policy on one side will be associated to the same policy on the other side? What if the policy is not even programmed yet on the other side?

This is the reason that flow tracking key is introduced and has 128-bits. Essentially, the flow tracking key **MUST** be unique within the pipeline for all policies that we want to trigger the flow resimulation separately. And it must be programmed and aware by our caller to ensure both active side and standby side shares the same key for the same policy.

During planned switchover, we will ensure the policy on active side and standby side are updated to the same version and all future updates will be paused until the switchover is done. So we don't need to worry about the policy mismatch, such as one side has the flow tracking key while the other side doesn't.

During unplanned events and standby side is forced to become the new active, the 2 sides could run different set of policies, hence we need to reconcile the flow tracking key.

- When active flow tracking is used, the flow tracking key to flow mapping hash table can be constructed on the standby side as part of the flow sync process. Hence, we can directly check if the keys are matched between policy and the hash table. If a key exists in the hash table, but not found in the policy, we will mark all the flow as resimulated to get them fixed when next packet arrives.
- When passive flow tracking is used, we can enumerate all flows and resimulate the flow that contains unknown flow tracking key. A more brute force way is to increase the flow incarnation id, which makes all flows to be resimulated, but it may cause temporary high pressure on the entire pipeline.

### 2.5. Object model change summary for policy-based flow resimulation

To summarize, the following changes are needed to implement policy-based flow resimulation:

- 1 property needs to be added on match stage entry:

    ```json
    "DASH_SAI_SOME_ENTRY_TABLE|<entry partition key>|<stage_index>|<Unique Key of the entry>": {
        // ...
        "flow_tracking_key": "0x1234567890abcdef1234567890abcdef"
    }
    ```

- 2 property needs to be added on flow state:

    ```c
    typedef enum _sai_flow_state_metadata_attr_t {
        SAI_FLOW_ATTR_START,
        // ...
        SAI_FLOW_METADATA_ATTR_FLOW_TRACKING_KEY, // Flow tracking key.
        SAI_FLOW_METADATA_ATTR_RESIMULATED,       // Flow resimulated bit.
        SAI_FLOW_METADATA_ATTR_END
    } sai_flow_metadata_attr_t;
    ```

## 3. Learning-based flow resimulation

The last type of flow resimulation trigger is learning-based. For example, [Tunnel Learning](../general/dash-sai-pipeline-packet-flow.md#5621-tunnel-learning).

When tunnel change happens, the flow will be marked as to be resimulated. After [the flow resimulation process](#12-flow-resimulation-process), the new pair of flow will be generated, which contains the new tunnel information in the reverse flow and to be used to replace the current flow.

## 4. Explicit per flow consistency (PCC) support

As we can see above, all flow resimulation will cause everything in the flow to be updated. This behavior might not be desired in some cases. For example, in load balancer case, we may only want to update the VTEP tunnel while keep the selected backend server unchanged, even when the backend server list is changed. This property of load balancer is called "per flow consistency" (PCC).

To help maintain PCC, we can specify any routing action as `bypass_resimulation` as below. This will ignore the packet transformations from this action. Implementation-wise, this can be done by copying the original flow state to the new flow state.

```json
[
    // Load balancing rule for port 443.
    "DASH_SAI_TCP_PORT_MAPPING_TABLE|lb-portmap-1-1-1-1": [
        {
            "routing_type": "lbnat",

            "src_port_min": 0,
            "src_port_max": 65535,
            "dst_port_min": 443,
            "dst_port_max": 443,

            // Specify the VTEP info for the backend pool.
            "underlay0_tunnel_id": "lb-backend-pool-vtep-1-1-1-1-443",
            
            // NAT destination IP to multiple VM IPs as ECMP group and a different port.
            "nat_dips": "10.0.0.1,10.0.0.2",
            "nat_dport": "8443"
        }
    ],

    // This is the final routing type that gets executed. The tunnel_nat action will nat the inner packet destination
    // from public ip to VM IP, also adds the corresponding vxlan tunnel to the destination.
    //
    // To start simple, all destination IPs can be treated as an ECMP group. And algorithm can be defined as metadata
    // in the VIP entry as well.
    "DASH_SAI_ROUTING_TYPE_TABLE|lbnat": [
        { "action_type": "tunnel", "target": "underlay0" },
        { "action_type": "nat", "bypass_resimulation": true }
    ]
]
```
