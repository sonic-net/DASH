# DASH Private Link and Private Link NSG HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/29/2024 | Riff Jiang | Initial version |

1. [1. Terminology](#1-terminology)
2. [2. Background](#2-background)
3. [3. SDN transformation](#3-sdn-transformation)
   1. [3.1. Private Link](#31-private-link)
      1. [3.1.1. VM-to-PLS direction](#311-vm-to-pls-direction)
      2. [3.1.2. PLS-to-VM direction](#312-pls-to-vm-direction)
   2. [3.2. Private Link NSG](#32-private-link-nsg)
      1. [3.2.1. VM-to-PLS direction](#321-vm-to-pls-direction)
      2. [3.2.2. PLS-to-VM direction](#322-pls-to-vm-direction)
   3. [3.3. Load balancer fast path support](#33-load-balancer-fast-path-support)
   4. [3.4. Non-required features](#34-non-required-features)
4. [4. Resource modeling, requirement, and SLA](#4-resource-modeling-requirement-and-sla)
   1. [4.1. Scaling requirements](#41-scaling-requirements)
   2. [4.2. Reliability requirements](#42-reliability-requirements)
5. [5. SAI API design](#5-sai-api-design)
   1. [5.1. DASH ENI attributes](#51-dash-eni-attributes)
   2. [5.2. DASH CA-PA mapping attributes](#52-dash-ca-pa-mapping-attributes)
   3. [5.3. DASH tunnel table and attributes](#53-dash-tunnel-table-and-attributes)
6. [6. DASH pipeline behavior](#6-dash-pipeline-behavior)
   1. [6.1. VM-to-PLS direction (Outbound)](#61-vm-to-pls-direction-outbound)
      1. [6.1.1. Private Link](#611-private-link)
      2. [6.1.2. Private Link NSG](#612-private-link-nsg)
   2. [6.2. PLS-to-VM direction](#62-pls-to-vm-direction)
7. [7. DASH database schema](#7-dash-database-schema)

## 1. Terminology

| Term | Explanation |
| --- | --- |
| PL | Private Link: <https://azure.microsoft.com/en-us/products/private-link>. |
| NSG | Network Security Group. |
| PE | Private endpoint. |
| PLS | Private Link Service. This is the term for private endpoint from server side. Customer can create their private link service, then expose them to their VNETs as a private endpoint.  |

## 2. Background

Azure Private Link provides private connectivity from a virtual network to Azure platform as a service, by providing an 1-to-1 VNET mapping to the service.

This doc is used to capture the requirements for implementing the Private Link and Private Link NSG in the context of DASH APIs.

## 3. SDN transformation

### 3.1. Private Link

#### 3.1.1. VM-to-PLS direction

When a packet coming from the VM and being sent to PLS, it will be transformed as below:

![PL VM-to-PLS direction](./images/private-link-vm-to-pls.svg)

#### 3.1.2. PLS-to-VM direction

And the return packet from PLS to VM, will be transformed as below:

![PL PLS-to-VM direction](./images/private-link-pls-to-vm.svg)

### 3.2. Private Link NSG

#### 3.2.1. VM-to-PLS direction

When NSG appliance is enabled, the VM-to-PLS packet will have an additional outer encap that tunnels the packet to NSG appliance as below:

![PL NSG VM-to-PLS direction](./images/private-link-nsg-vm-to-pls.svg)

#### 3.2.2. PLS-to-VM direction

The return packet will be the same as Private Link, coming directly from PLS bypassing the NSG appliance.

### 3.3. Load balancer fast path support

The fast path here is not the DASH hardware fast path, but the [load balancer fast path ICMP flow redirection](../load-bal-service/fast-path-icmp-flow-redirection.md).

1. If PL NSG is not used, it changes the flow just like regular PL case.
2. If PL NSG is used, it updates the PL encap, and **removes** the outer NSG encap.

For more information on how Fast Path works, please refer to [Fast Path design doc](../load-bal-service/fast-path-icmp-flow-redirection.md).

### 3.4. Non-required features

- RST on connection idle timeout.

## 4. Resource modeling, requirement, and SLA

### 4.1. Scaling requirements

| Metric | Requirement |
| --- | --- |
| # of ENIs per DPU | 32 |
| # of VNET mapping per ENI | 64K |
| # of PPS | 64M |
| VNET mapping change rate (CRUD) | (TBD) |
| # of fast path packets | Same as CPS. 3M per card. |
| # of tunnels | (TBD) |
| # of next hop in each tunnel | (TBD)  |

### 4.2. Reliability requirements

The flows replication follows the SmartSwitch HA design.

For more information, please refer to [SmartSwitch HA design doc](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md).

## 5. SAI API design

The following SAI API only includes the SAI updates that used for setting up the PL / PL NSG scenarios.

### 5.1. DASH ENI attributes

The following attributes will be added on ENI:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_ENI_ATTR_PL_UNDERLAY_SIP | sai_ip_address_t | Underlay IP that will be used for private link routing type. |

### 5.2. DASH CA-PA mapping attributes

The following attributes will be added to CA-to-PA entry, for supporting service rewrites for PL/PL NSG:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_SIP_MASK | sai_ip_address_t | Used with overlay sip to support src prefix rewrite. |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DIP_MASK | sai_ip_address_t | Used with overlay dip to support dst prefix rewrite. |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_TUNNEL_ID | sai_object_id_t | Used to specify the tunnel. It can be a tunnel next hop id or the tunnel id, depending on if multiple dips as ECMP group is required. |

The PL and PL NSG will share the same routing type on the CA-PA mapping entry:

```c
typedef enum _sai_outbound_ca_to_pa_entry_action_t
{
    // ...

    SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_PRIVATE_LINK_MAPPING,

    // ...
} sai_outbound_ca_to_pa_entry_action_t;
```

### 5.3. DASH tunnel table and attributes

A new tunnel next hop table needs to be added with the following attributes:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_DASH_TUNNEL_ENTRY_ATTR_DASH_ENCAPSULATION | sai_dash_encapsulation_t | Encapsulation type, such as VxLan, NvGRE. Optional. If not specified, the encap from tunnel will be used. |
| SAI_DASH_TUNNEL_ENTRY_ATTR_VNI | sai_uint32_t | VNI used in the encap. Optional. If not specified, the VNI from tunnel will be used. |
| SAI_DASH_TUNNEL_NEXT_HOP_ENTRY_ATTR_DIP | sai_ip_address_t | Destination IP of the next hop. |

When multiple DIPs are required, the tunnel table and tunnel member will be used to specify the tunnel with multiple next hop information:

- A new tunnel table needs to be added with the following attributes:

  | Attribute name | Type | Description |
  | --- | --- | --- |
  | SAI_DASH_TUNNEL_ENTRY_ATTR_DASH_ENCAPSULATION | sai_dash_encapsulation_t | Encapsulation type, such as VxLan, NvGRE. |
  | SAI_DASH_TUNNEL_ENTRY_ATTR_VNI | sai_uint32_t | VNI used in the encap. |

- A new tunnel member table needs to be added to create the bindings between tunnel and next hop:

  | Attribute name | Type | Description |
  | --- | --- | --- |
  | SAI_DASH_TUNNEL_MEMBER_ENTRY_ATTR_TUNNEL_ID | sai_object_id_t | Tunnel Id |
  | SAI_DASH_TUNNEL_MEMBER_ENTRY_ATTR_TUNNEL_NEXT_HOP_ID | sai_object_id_t | Tunnel next hop id |

## 6. DASH pipeline behavior

### 6.1. VM-to-PLS direction (Outbound)

The VM-to-PLS direction is modeled as outbound pipeline in DASH.

To demonstrate how the DASH pipeline works, let's say, we have a VM in with IP 10.0.0.1, trying to reach the Private Endpoint in their VNET with IP 10.0.1.1, and the VM Outbound VNI is 1000000.

#### 6.1.1. Private Link

For private link, the packet will go through the pipeline with following setup:

1. **Direction Lookup**: First, we will look up the VNI to determine the packet direction. In this case, we consider all the packets from on-premises network as outbound direction from the floating NIC perspective.

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.vni | `sai_uint32_t` | `1000000` |
   | entry_attr.SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION | `sai_direction_lookup_entry_action_t` | `SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION` |

2. **ENI Lookup**: Then, we will use the inner MAC address to find the ENI pipeline. Then, the outer encap will be decap’ed, leaving inner packet going through the rest of pipeline.

   First, we use ENI ether address map table to find the ENI id:

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.address | `sai_mac_t` | `11-22-33-44-55-66` |
   | entry_attr.SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID | `sai_object_id_t` | (SAI object ID of the ENI) |

   Then, we use the ENI id to find the ENI, which contains the PL underlay source IP as below:

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry_attr.SAI_ENI_ATTR_PL_UNDERLAY_SIP | `sai_ip_address_t` | 2.2.2.1 |

3. **Conntrack Lookup**: If flow already exists, we directly apply the transformation from the flow, otherwise, move on.
4. **ACL**: No changes in the ACL stage, it will work just like the other cases.
5. **Routing**: The inner destination IP (a.k.a. overlay dip) will be used for finding the route entry. This will trigger the maprouting action to run, which makes the packet entering Mapping stage.

   The routing stage could also have underlay source ip defined, but the `PL_UNDERLAY_SIP` will be used first, whenever the routing type is set to `privatelink`.

   The outbound routing entry will look like as below:

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.eni_id | `sai_object_id_t` | (SAI object ID of the ENI) |
   | entry.destination | `sai_ip_prefix_t` | `10.0.1.0/24` |
   | entry_attr.SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION | `sai_outbound_routing_entry_action_t` | `SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET` |
   | entry_attr.SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID | `sai_object_id_t` | (SAI object ID of the destination VNET) |
   | entry_attr.SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS | `sai_uint16_t` | `60000` |

6. **Mapping - VNET**: The inner destination IP will be used for finding the outbound CA-PA mapping entry, of which the routing type will be set to private link.

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.dst_vnet_id | `sai_object_id_t` | (SAI object ID of the destination VNET) |
   | entry.dip | `sai_ip_address_t` | `10.0.1.1` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_ACTION | `sai_outbound_ca_to_pa_entry_action_t` | `SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_PRIVATE_LINK_MAPPING` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP | `sai_ip_address_t` | `3.3.3.1` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC | `sai_mac_t` | `99-88-77-66-55-44` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_SIP | `sai_ip_address_t` | `9988::` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_SIP_MASK | `sai_ip_address_t` | `FFFF:FFFF:FFFF:FFFF:FFFF:FFFF::` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DIP | `sai_ip_address_t` | `1122:3344:5566:7788::303:301/128` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DIP_MASK | `sai_ip_address_t` | `FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF` |
   | entry_attr.SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS | `sai_uint16_t` | `60001` |

7. **Metering**: The last action we need to do is to find the corresponding metering rule.
8. **Conntrack Update**: Both forwarding and reverse flows will be created by this stage.
9. **Metering Update**: Metering update will update the metering counter based on the rules that we found before.
10. **Underlay routing**: Underlay routing will move the packet to the right port and forward it out.

#### 6.1.2. Private Link NSG

The changes needed for PL NSG is mostly the same as PL. In addition, on the VNET mapping, we need to provide the extra tunnel info.

| SAI field name | Type | Value |
| --- | --- | --- |
| entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_TUNNEL_ID | `sai_object_id_t` | (SAI object ID of the NSG tunnel) |

And we can use the following things to specify the tunnel information:

1. **Tunnel Table**: The tunnel table will be used to specify the tunnel information.

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry_attr.SAI_DASH_TUNNEL_ENTRY_ATTR_DASH_ENCAPSULATION | `sai_dash_encapsulation_t` | `SAI_DASH_ENCAPSULATION_VXLAN` |
   | entry_attr.SAI_DASH_TUNNEL_ENTRY_ATTR_VNI | `sai_uint32_t` | `2000000` |

2. **Tunnel Next Hop Table**: The tunnel next hop table will be used to specify the tunnel next hop information.

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry_attr.SAI_DASH_TUNNEL_NEXT_HOP_ENTRY_ATTR_TUNNEL_ID | `sai_object_id_t` | (SAI object ID of the NSG tunnel) |
   | entry_attr.SAI_DASH_TUNNEL_NEXT_HOP_ENTRY_ATTR_DIP | `sai_ip_address_t` | `100.0.1.1` |

### 6.2. PLS-to-VM direction

On the return path, we will leverage the reverse flow that is created by the outbound side to process the packet and forward it back to the original source.

Since the packet that being sent back to the VM in PL NSG scenario will be exactly the same as regular PL, and the reverse flow that being created in the PL NSG scenario will also be the same, there is nothing we need to change for the PL NSG case.

The packet will go through the DASH pipeline as below:

1. **Direction Lookup**: First, we will use the VNI to determine the packet direction. In this case, since Private Link Key is not in the outbound VNI list, we consider all the packets from PLS side as inbound direction.

2. **ENI Lookup**: We will use the inner destination MAC address to find the ENI pipeline. Once found, the outer encap will be decap'ed, exposing the inner packet for later processing.

   The ENI entry that we are using will be the same as before. Hence, omitted here.

3. **Conntrack Lookup**: The return packet transformation will be handled by reverse flow.
4. **Metering Update**: Metering update will update the metering counter based on the rules that we saved in the reverse flow.
5. **Underlay routing**: Underlay routing will move the packet to the right port and forward it out.

## 7. DASH database schema

For the DASH database schema, please refer to the [SONIC-DASH HLD](https://github.com/sonic-net/SONiC/blob/master/doc/dash/dash-sonic-hld.md).
