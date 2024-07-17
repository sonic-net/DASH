# DASH ExpressRoute Gateway Bypass HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 07/09/2024 | Riff Jiang | Initial version |

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
         1. [5.2.2.1. Reverse routing stage](#5221-reverse-routing-stage)
            1. [5.2.2.1.1. Reverse routing group](#52211-reverse-routing-group)
            2. [5.2.2.1.2. Reverse routing group entry](#52212-reverse-routing-group-entry)
         2. [5.2.2.2. Reverse tunnel table and entry](#5222-reverse-tunnel-table-and-entry)
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

In the ER gateway bypass scenario, the return traffic needs to be routed back to MSEE per customer's configuration, which is a MSEE device list per subnet.

Since the flow creation happens at the MSEE-to-PLS direction, as this is where the first packet lands on DASH. This configuration is essentially a LPM table lookup using the source IP to find the reverse tunnel to use. The tunnel provides a list of next hops as an ECMP group. And DASH needs to select a valid next hop to use and save it into the reverse flow to avoid further lookup.

Furthermore, when MSEE failover, we need to update the reverse tunnel on all existing flows to point to the working ones.

#### 5.2.2. MSEE device selection

To handle this, we are leveraging similar concepts as the RPF (Reverse Path Forwarding) in network devices, which checks the source IP during the forwarding path.

##### 5.2.2.1. Reverse routing stage

To support this behavior, we add the reverse routing stage in DASH.

Unlike the regular routing stage, the reverse routing stage will not be specified in the routing types and will be default to be executed before the action apply stage.

If no route entries are being hit in this stage, the packet should not be dropped but continue to later stages. This behavior is the same as having a default route with allow action.

###### 5.2.2.1.1. Reverse routing group

The reverse routing group is used for defining the reverse routing table. Once created, we can bind its object id to ENI to make it taking effect:

| SAI attribute name | Type | Description |
| --------------- | ---- | ----------- |
| SAI_OUTBOUND_REVERSE_ROUTING_GROUP_ATTR_DISABLED | bool | If true, this entries in this routing group will not take effect, but won't drop the packets. |

To specify which reverse group should be used on an ENI, we add the following attribute on ENI:

| SAI attribute name | Type | Description |
| --------------- | ---- | ----------- |
| SAI_ENI_ATTR_OUTBOUND_REVERSE_ROUTING_GROUP_ID | sai_object_id_t | Reverse routing group object ID |

###### 5.2.2.1.2. Reverse routing group entry

The reverse routing table is essentially a LPM lookup table with each entry takes the IP prefix as key:

| SAI entry field | Type | Description |
| --------------- | ---- | ----------- |
| outbound_reverse_routing_group_id | sai_object_id_t | SAI object ID of the reverse routing table |
| source | sai_ip_prefix_t | Source IP prefix |

The attributes will only have action and reverse tunnel id, as it won't change anything else:

| SAI attribute name | Type | Description |
| ------------------ | ---- | ----------- |
| SAI_OUTBOUND_REVERSE_ROUTE_ENTRY_ATTR_ACTION | sai_outbound_reverse_route_entry_action_t | Action to take |
| SAI_OUTBOUND_REVERSE_ROUTE_ENTRY_ATTR_REVERSE_TUNNEL_ID | sai_object_id_t | SAI object ID of the reverse tunnel |
| SAI_OUTBOUND_REVERSE_ROUTING_ENTRY_ATTR_ROUTING_ACTIONS_DISABLED_IN_FLOW_RESIMULATION | sai_uint64_t | Routing actions that need to be disabled in flow resimulation. |

##### 5.2.2.2. Reverse tunnel table and entry

Besides the reverse routing stage, we also need to split the tunnel table into tunnel and reverse tunnel table. It makes the API clean, also allows P4 to support it, because each P4 table can be only matched once in the pipeline:

The reverse tunnel table will have the following attributes that is common to all next hops:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_DASH_REVERSE_TUNNEL_ATTR_DASH_ENCAPSULATION | sai_dash_encapsulation_t | Encapsulation type, such as VxLan, NvGRE. Optional. If not specified, the encap from tunnel will be used. |
| SAI_DASH_REVERSE_TUNNEL_ATTR_TUNNEL_KEY | sai_uint32_t | Tunnel key used in the encap, e.g. VNI in VxLAN. |

A reverse tunnel supports multiple destination IPs as an ECMP group, the reverse tunnel member and reverse tunnel next hop objects will be used to specify these information:

- The reverse tunnel next hop object defines the tunnel information for each destination:

  | Attribute name | Type | Description |
  | --- | --- | --- |
  | SAI_DASH_REVERSE_TUNNEL_NEXT_HOP_ATTR_DIP | sai_ip_address_t | Destination IP used in tunnel. |
  | SAI_DASH_REVERSE_TUNNEL_NEXT_HOP_ATTR_SIP | sai_ip_address_t | Source IP used in tunnel. |

- The reverse tunnel member defines the bindings between tunnel and next hop:

  | Attribute name | Type | Description |
  | --- | --- | --- |
  | SAI_DASH_REVERSE_TUNNEL_MEMBER_ATTR_TUNNEL_ID | sai_object_id_t | Tunnel Id |
  | SAI_DASH_REVERSE_TUNNEL_MEMBER_ATTR_TUNNEL_NEXT_HOP_ID | sai_object_id_t | Tunnel next hop id |

#### 5.2.3. MSEE failover handling using flow resimulation

##### 5.2.3.1. Reverse tunnel updates

When MSEE failover, the tunnel configuration will be updated. Since the tunnel is route based, we can leverage the existing [flow resimulation APIs](../dataplane/dash-flow-resimulation.md) to update the nexthop list.

Whenever the reverse tunnel id is set, we consider the reverse tunnel routing action bit is set in the pipeline, this allows us to control the flow resimulation behavior using the same mechanism.

1. Step 1: Update the DIP list in the reverse tunnel object, which will cover all the new flows.
2. Step 2: Request a full flow resimulation, which will cover the existing flows.

##### 5.2.3.2. Maintaining per connection consistency (PCC)

For cases like private link, the flow resimulation should not change the SDN transformation in VM-to-PLS direction. Here, we use the same flow resimulation scope control APIs to achieve this goal.

For more information, please refer to the [flow resimulation scope control APIs](../dataplane/dash-flow-resimulation.md#64-resimulation-scope-control) to have the related routing action disabled in the flow resimulation. For example:

- For PL, it will be `SAI_DASH_ROUTING_ACTION_STATIC_ENCAP` and `SAI_DASH_ROUTING_ACTION_4TO6`.
- For PL NSG, we need add 1 more tunnel: `SAI_DASH_ROUTING_ACTION_TUNNEL`.

##### 5.2.3.3. Flow resimulation on return path

In flow resimulation, flow is usually updated when packets lands on the forwarding path, however this introduces extra downtime for the reverse tunnel update. The reason is that the return packet will still take the old tunnel in the flow, and being sent to the wrong destination, although the policy is updated and flow resimulation is triggered.

To avoid this impact, it is required for the return packet to check the resimulation status and update the reverse tunnel in the flow if needed. This means when a packet coming from PLS to MSEE, if reverse tunnel is changed, the reverse routing stage should be evaluated and updating the flow accordingly.

##### 5.2.3.4. Flow resimulation on flow redirected flows

Another thing in flow resimulation is [load balancer fast path flow redirection](../load-bal-service/fast-path-icmp-flow-redirection.md) related. When a flow is redirected by fast path ICMP packet, this flow will be ignored in the flow resimulation. However, this behavior should only apply for the forwarding side of transformation, but not the reverse side.

This means when a packet lands on DASH pipeline and it belongs to a flow that is redirected by fast path ICMP packet, the reverse routing stage should be evaluated and updating the flow accordingly.

## 6. References

- [Azure Private Link](https://azure.microsoft.com/en-us/products/private-link)
- [Azure Private Link Service](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview)
- [SmartSwitch HA design](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md)
- [DASH HA SAI API design](https://github.com/sonic-net/DASH/blob/main/documentation/high-avail/ha-api-hld.md)
