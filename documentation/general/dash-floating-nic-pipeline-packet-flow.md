# DASH floating NIC pipeline packet flow

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 2/4/2025 | Riff Jiang | Initial version |

1. [1. Terminology](#1-terminology)
2. [2. Background](#2-background)
3. [3. Project scenario](#3-project-scenario)
4. [4. Resource modeling, requirement, and SLA](#4-resource-modeling-requirement-and-sla)
   1. [4.1. Resource modeling](#41-resource-modeling)
   2. [4.2. Scaling requirements](#42-scaling-requirements)
   3. [4.3. Reliability requirements](#43-reliability-requirements)
5. [5. Pipeline design and packet flow](#5-pipeline-design-and-packet-flow)
6. [6. SAI API design](#6-sai-api-design)
   1. [6.1. ENI attributes for floating NIC](#61-eni-attributes-for-floating-nic)
   2. [6.2. Capability query](#62-capability-query)
   3. [6.3. VNI direction lookup table](#63-vni-direction-lookup-table)
   4. [6.4. Flow API update for supporting 2 pairs of flows](#64-flow-api-update-for-supporting-2-pairs-of-flows)

## 1. Terminology

| Term | Explanation |
| --- | --- |
| FNIC | Floating NIC. |
| NVA | Network Virtual Appliance. |
| ENI | Elastic Network Interface. |
| PL | Private Link: <https://azure.microsoft.com/en-us/products/private-link>. |
| PE | Private endpoint. |
| PLS | Private Link Service. This is the term for private endpoint from server side. Customer can create their private link service, then expose them to their VNETs as a private endpoint.  |

## 2. Background

Appliances are frequently used for applying SDN policies for inter-VM traffic, such as ACLs, or to provide SDN functionality for machines that do not have the SDN stack running, such as On-Prem networks or bare metal.

To support these scenarios, we propose the floating NIC (FNIC) pipeline in DASH which helps us model the SDN behavior in the context of appliances.

## 3. Project scenario

At a high-level, the current Sirius Appliance accelerates VMs that do not support the SDN stack. The traffic is directed to the programmable HW via a traffic steering mechanism (VxLan tunnel for example) with a destination of the Appliance. The outer packet will be parsed and decap'ed in order to determine direction, and further actions to perform. This is what the floating NIC pipeline is trying to target.

![DASH NVA](images/fnic/dash-nva.svg)

Because of this, Floating NIC is modeled in a similar way to the VM NIC as below:

![DASH NVA VM vs FNIC](images/fnic/dash-nva-vm-vs-fnic.svg)

## 4. Resource modeling, requirement, and SLA

### 4.1. Resource modeling

In DASH, the floating NIC is modeled as following:

- ENI as floating NIC: Since a floating NIC is just another type of NIC, we leverages the same ENI concept for modeling. Each floating NIC will be a single ENI in DASH.
- ENI mode: A single ENI can be either a VM NIC or a floating NIC. A ENI mode is introduced to differentiate the two types of ENI and must be provided during the ENI creation. Once set, the mode cannot be changed anymore.
- Mixed-pipeline support: For supporting flexible deployment, each DPU can hold multiple ENIs, some of which are VM DASH pipeline, and some of which are floating NIC.

With this, at high-level, the ENIs in a single DPU will be represented as below:

![DASH ENI with FNIC](images/fnic/dash-eni-with-fnic.svg)

### 4.2. Scaling requirements

The floating NIC pipeline should have support the same scaling requirement as the regular VM pipeline. Please refer to the [SONiC-DASH scaling requirements](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md#14-scaling-requirements) for more details.

### 4.3. Reliability requirements

Floating NIC should still have HA support, which uses the same HA model that DASH provides, and inline sync and bulk sync should continue to be supported.

## 5. Pipeline design and packet flow

The key difference between the floating NIC pipeline and regular VM pipeline are 2 things:

1. All packets go through the inbound pipeline first, then hits the “hairpin”, and send out via outbound pipeline. Hence, there is no direction lookup stage anymore. The VNI and ENI lookup stages are used only for locating the ENI and basic security validations.
2. The flow lookup and creation will happen on both inbound and outbound directions. For a single network connection, there will be 4 flows being created in total: 2 for inbound and 2 for outbound. The 2 pair of flows will have different lifetime and expire independently.

However, most of the functionalities of the basic stages in DASH pipeline remain the same. Only the wiring is updated as below. Here we use the private link packets in the ExpressRoute gateway bypass case as the example to show how the pipeline works:

![DASH FNIC packet flow](images/fnic/dash-fnic-packet-flow.svg)

As the picture shows above, here is the high-level packet flow to show how the pipeline works:

1. First, the customer packet will land on the port of DASH pipeline with encapsulations. Because floating NIC behaves like a VM, hence it is expecting the destination MAC being set to the ENI MAC.
2. Before entering the ENI pipeline, we look into the VNI and Destination ENI MAC to find the corresponding ENI pipeline:
   1. If ENI is not found, we drop the packet and increase the drop counters.
   2. Otherwise, the packet needs to always land inbound pipeline first. This is done by setting the VNI lookup table entries.
      - In the case above, both initial packet (from VM) and return packet (from PLS) are both going into the inbound pipeline.
3. In the inbound pipeline:
   1. We first use the ENI MAC + ENI MAC is DST MAC (Value = `true`) + inner packet 5-tuples to find the flow. If the flow is found, we directly goes into the action apply stage in the inbound pipeline. Otherwise, we go through the match stages to evaluate the inbound side of policies.
   2. We evaluate the policies like what we are doing in the VM inbound pipeline.
   3. After policy evaluation is done and the packet is not dropped, we create a pair of flows in the inbound pipeline, using the same key as the flow lookup key.
   4. If any action from inbound pipeline needs to be applied, we apply it here, such as dropping the packet.
4. The packet completes the inbound pipeline and hits the hairpin rule, which does 2 things:
   1. It bounces the packet into the outbound pipeline.
   2. It rewrite the inner source MAC address into the ENI MAC and the inner destination MAC address to a dummy MAC.
5. In the outbound pipeline:
   1. We first use the ENI MAC + ENI MAC is DST MAC (Value = `false`) + inner packet 5-tuples to find the outbound side flow. If flow is found, we directly go to action apply stage and updates the packet. If not, continue.
   2. Going through the regular DASH VM outbound pipeline.
   3. Create the outbound side flow in the same way DASH VM pipeline.
   4. Applying any packet transformations that is specified during the pipeline.
6. Route the packet out based on the underlay IP to the right port.
7. The packet leaves the DASH pipeline through the port.

## 6. SAI API design

### 6.1. ENI attributes for floating NIC

A new attribute is added to the ENI object to differentiate the ENI mode:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_ENI_ATTR_DASH_ENI_MODE | sai_dash_eni_mode_t | ENI mode. By default it is set as VM. To enable the floating NIC, the mode needs to be set as floating NIC. |

The new enum is defined as below:

```c
/**
 * @brief Defines a list of enums for dash_flow_sync_state
 */
typedef enum _sai_dash_eni_mode_t
{
    SAI_DASH_ENI_MODE_VM,

    SAI_DASH_ENI_MODE_FNIC,

} sai_dash_eni_mode_t;
```

### 6.2. Capability query

To query if a platform supports floating NIC or not, we can the following attribute to query the supported ENI mode. If floating NIC pipeline is not supported, then the SAI implementation should only return the VM enum.

```c
sai_status_t sai_query_attribute_enum_values_capability(
        _In_ sai_object_id_t switch_id,
        _In_ sai_object_type_t object_type,
        _In_ sai_attr_id_t attr_id,
        _Inout_ sai_s32_list_t *enum_values_capability);
```

A simple example code would be:

```c
int32_t supported_eni_mode_list[2];
sai_s32_list_t supported_eni_modes = {
    .count = 2,
    .list = supported_eni_mode_list
};

sai_query_attribute_enum_values_capability(
    switch_id,
    SAI_OBJECT_TYPE_ENI
    SAI_ENI_ATTR_DASH_ENI_MODE,
    supported_eni_modes);
```

### 6.3. VNI direction lookup table

The VNI direction lookup table needs to have the inbound direction support, hence the new action needs to be added:

```c
/**
 * @brief Attribute data for #SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION
 */
typedef enum _sai_direction_lookup_entry_action_t
{
    ...
    SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_INBOUND_DIRECTION,
} sai_direction_lookup_entry_action_t;
```

### 6.4. Flow API update for supporting 2 pairs of flows

To differentiate the inbound and outbound flows, we need to add a new attribute to the flow entry:

```c
typedef struct _sai_flow_entry_t
{
    // ...

    /**
     * @brief Is ENI MAC destination MAC
     */
    bool is_eni_mac_dst_mac;

} sai_flow_entry_t;
```
