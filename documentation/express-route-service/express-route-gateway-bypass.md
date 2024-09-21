# DASH ExpressRoute Gateway Bypass HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 07/09/2024 | Riff Jiang | Initial version |
| 0.2 | 08/30/2024 | Riff Jiang | Simplify the MSEE failover handling |

1. [1. Terminology](#1-terminology)
2. [2. Background](#2-background)
3. [3. SDN transformation](#3-sdn-transformation)
   1. [3.1. Private Link](#31-private-link)
   2. [3.2. Private Link NSG](#32-private-link-nsg)
   3. [3.3. Fast Path and other features](#33-fast-path-and-other-features)
4. [4. Resource modeling, requirement, and SLA](#4-resource-modeling-requirement-and-sla)
   1. [4.1. Scaling requirement](#41-scaling-requirement)
   2. [4.2. Reliability requirements](#42-reliability-requirements)
5. [5. Pipeline design](#5-pipeline-design)
   1. [5.1. ENI MAC handling](#51-eni-mac-handling)
   2. [5.2. MSEE selection and failover handling](#52-msee-selection-and-failover-handling)
      1. [5.2.1. Background](#521-background)
      2. [5.2.2. MSEE device selection](#522-msee-device-selection)
      3. [5.2.3. MSEE failover handling using flow resimulation](#523-msee-failover-handling-using-flow-resimulation)
         1. [5.2.3.1. Reverse tunnel updates](#5231-reverse-tunnel-updates)
         2. [5.2.3.2. Maintaining per connection consistency (PCC)](#5232-maintaining-per-connection-consistency-pcc)
         3. [5.2.3.3. Flow resimulation on return path](#5233-flow-resimulation-on-return-path)
         4. [5.2.3.4. Flow resimulation on flow redirected flows](#5234-flow-resimulation-on-flow-redirected-flows)
6. [6. References](#6-references)

## 1. Terminology

| Term | Definition |
| ---- | ---------- |
| ER | ExpressRoute |
| MSEE | Microsoft Enterprise Edge |
| PL | Private Link: <https://azure.microsoft.com/en-us/products/private-link> |
| PE | Private Endpoint |
| PLS | Private Link Service: <https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview> |

## 2. Background

Azure Private Link provides private connectivity from a virtual network to Azure platform as a service, by providing an 1-to-1 VNET mapping to the service. In addition, it is also used by ExpressRoute for providing the similar functionality for On-Prem network.

This doc is used to capture the additional requirements for ExpressRoute, such as MSEE failover scenarios.

## 3. SDN transformation

The SDN transformation is almost identical to the regular VM-to-PLS case, with only 2 differences:

- The packet sends the DASH pipeline will have DST mac set to DASH ENI MAC, instead of source MAC.
- The return packet needs to be able to specify the underlay source IP to be something different from the SmartSwitch VIP.

### 3.1. Private Link

When a packet comes from the MSEE and being sent to PLS, it will be transformed as below:

![Express Route PL initial packet transformation](./images/ergw-bypass-pl-initial.svg)

And the return packet from PLS to MSEE, will be transformed as below:

![Express Route PL return packet transformation](./images/ergw-bypass-pl-return.svg)

### 3.2. Private Link NSG

When NSG appliance is enabled, we will apply the same additional transformation as VM-to-PLS – the additional NSG appliance encap will be applied on the MSEE-to-PLS direction, while the return path is the same as regular Private Link:

![Express Route PL NSG packet transformation](./images/ergw-bypass-pl-nsg.svg)

### 3.3. Fast Path and other features

All other data path features, such as fast path, RST on idle timeout will be the same as the regular VM-to-PL scenario, hence the details are omitted here.

## 4. Resource modeling, requirement, and SLA

### 4.1. Scaling requirement

The scaling requirement for PL redirect map are listed as below. The metrics are based on a 200Gbps DPU:

| Metric | Requirement |
| ------ | ----------- |
| # of ENIs per DPU | 32 |
| # of VNET mapping per ENI | 64K |
| # of PPS | 64M |
| VNET mapping change rate (CRUD) | (TBD) |
| # of fast path packets | Same as CPS. 3M per card. |
| # of tunnels | (TBD) |
| # of next hop in each tunnel | (TBD)  |

### 4.2. Reliability requirements

The flows replication follows the SmartSwitch HA design.

For more information, please refer to the [SmartSwitch HA design doc](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md) and [SAI API design](https://github.com/sonic-net/DASH/blob/main/documentation/high-avail/ha-api-hld.md).

## 5. Pipeline design

### 5.1. ENI MAC handling

There are 2 pipelines in DASH for each ENI – outbound and inbound, and all PL-related SDN policies are placed in the outbound side. To steer the packet into the right ENI and pipeline, currently, DASH uses "Direction Lookup" stage and "ENI Lookup" stage to steer the packet based on the VNI and MAC address.

1. If the VNI exists and is known to DASH, it will be treated as outbound direction.
2. If direction is set to outbound, DASH will use source mac to find the ENI, otherwise, DASH will use the destination mac to find the ENI.

Here is the outbound pipeline in DASH:

![DASH outbound pipeline](https://github.com/sonic-net/SONiC/raw/master/images/dash/dash-hld-outbound-packet-processing-pipeline.svg)

To support the ER gateway bypass scenario, we need to extend the "Direction Lookup" and "ENI Lookup" stages, because the destination MAC will be used as the ENI MAC on both directions.

The approach is straightforward – If the VNI matches the MSEE VNIs, we override the ENI lookup to use the specified MAC type – source or destination. And here is the SAI API design:

```c
typedef enum _sai_eni_mac_override_type_t {
    SAI_ENI_MAC_OVERRIDE_TYPE_NONE,
    SAI_ENI_MAC_OVERRIDE_TYPE_SRC_MAC,
    SAI_ENI_MAC_OVERRIDE_TYPE_DST_MAC,
} sai_eni_mac_overrride_type_t;

typedef enum _sai_direction_lookup_entry_attr_t {
    ...

    /**
     * @brief Override MAC type for ENI lookup
     *
     * @type sai_eni_mac_override_type_t
     * @flags CREATE_AND_SET
     * @default SAI_ENI_MAC_TYPE_NONE
     */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_OVERRIDE_ENI_MAC_TYPE,

    ...
} sai_direction_lookup_entry_attr_t;
```

### 5.2. MSEE selection and failover handling

#### 5.2.1. Background

In the ER gateway bypass scenario, return traffic needs to be routed back to MSEE where the traffic is originated.

Furthermore, when MSEE failover, we need to update the reverse tunnel on all existing flows to point to the new MSEE where the traffic will be coming from after failover.

#### 5.2.2. MSEE device selection

Unlike VM-to-* scenarios, the reverse tunnel can only have 1 single destination IP that specified using the `SAI_ENI_ATTR_VM_UNDERLAY_DIP` attribute. MSEE devices can have active-active pairs, so this single IP solution won't work.

To handle this, we learn the PLS-to-MSEE tunnel information from the first packet when flow is created, including the encap type, key, and destination IP, and create the reverse tunnel in the reverse flow, which make sure the return traffic will be sent back to the originating MSEE. To avoid changing the behavior of VM-to-* scenarios, this behavior can be turned on or off by the SDN controller for each ENI using a dedicated attribute (see below).

In some cases, we will need the ability to specify the source IP of the reverse tunnel. To support this, we added another new attribute in the ENI object.

| SAI attribute name | Type | Description |
| --------------- | ---- | ----------- |
| SAI_ENI_ATTR_REVERSE_TUNNEL_SIP | sai_ip_address_t | Source IP used in the reverse tunnel. |
| SAI_ENI_ATTR_ENABLE_REVERSE_TUNNEL_LEARNING | bool | If true, the reverse tunnel will be learned from the first packet. |

#### 5.2.3. MSEE failover handling using flow resimulation

##### 5.2.3.1. Reverse tunnel updates

When MSEE failover, it could impact all flows that are created. In this case, we will leverage the full flow resimulation API in the existing [flow resimulation APIs](../dataplane/dash-flow-resimulation.md) to help us keep the reverse tunnel updated.

Following the flow resimulation design, all flow resimulation request will be explicitly requested by the SDN controller. Hence, when MSEE failover, the SDN controller will request a full flow resimulation that marks all flows as resimulation needed.

When the next packet from MSEE comes in for a flow, the flow will be resimulated and the reverse tunnel will be updated accordingly, by picking up the new MSEE tunnel information.

##### 5.2.3.2. Maintaining per connection consistency (PCC)

For cases like private link, the flow resimulation should not change the SDN transformation in VM-to-PLS direction. Here, we use the same flow resimulation scope control APIs to achieve this goal.

For more information, please refer to the [flow resimulation scope control APIs](../dataplane/dash-flow-resimulation.md#64-resimulation-scope-control) to have the related routing action disabled in the flow resimulation. For example:

- For PL, it will be `SAI_DASH_ROUTING_ACTION_STATIC_ENCAP` and `SAI_DASH_ROUTING_ACTION_4TO6`.
- For PL NSG, we need add 1 more tunnel: `SAI_DASH_ROUTING_ACTION_TUNNEL`.

##### 5.2.3.3. Flow resimulation on return path

As we can see, in flow resimulation, flow is updated when packets lands on the forwarding path, which introduces extra downtime for the reverse tunnel update. The reason is that the return packet will still take the old tunnel in the flow, and being sent to the wrong destination, until the next MSEE-to-PLS packet comes in and updates the flow.

For now, this behavior will be acceptable, as the downtime is limited to the time between the MSEE failover and the next packet from MSEE. However, this behavior will be improved in the future.

##### 5.2.3.4. Flow resimulation on flow redirected flows

Another thing in flow resimulation is [load balancer fast path flow redirection](../load-bal-service/fast-path-icmp-flow-redirection.md) related. When a flow is redirected by fast path ICMP packet, this flow will be ignored in the flow resimulation. However, this behavior should only apply for the forwarding side of transformation, but not the reverse side.

This means when a packet lands on DASH pipeline and it belongs to a flow that is redirected by fast path ICMP packet, the reverse tunnel should still be evaluated and updating accordingly.

## 6. References

- [Azure Private Link](https://azure.microsoft.com/en-us/products/private-link)
- [Azure Private Link Service](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview)
- [SmartSwitch HA design](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md)
- [DASH HA SAI API design](https://github.com/sonic-net/DASH/blob/main/documentation/high-avail/ha-api-hld.md)
