# DASH Private Link Redirect Map HLD
| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 01/26/2025 | Riff Jiang, Junhua Zhai| Initial version |

1. [Terminology](#1-terminology)
2. [Background](#2-background)
3. [SDN transformation](#3-sdn-transformation)
    - 3.1 [Redirect map ](#31-redirect-map)
    - 3.2 [Redirect map with PL NSG](#32-redirect-map-with-pl-nsg)
    - 3.3 [Redirect map with fast path](#33-redirect-map-with-fast-path)
    - 3.4 [Non-required features](#34-non-required-features) 
4. [Resource modeling, requirement, and SLA](#4-resource-modeling-requirement-and-sla)
    - 4.1 [Scaling requirement](#41-scaling-requirement)
    - 4.2 [Reliability requirements](#42-reliability-requirements)
5. [SAI API design](#5-sai-api-design)
    - 5.1 [DASH Outbound Port Map](#51-dash-outbound-port-map)
    - 5.2 [DASH Outbound Port Map Port Range](#52-dash-outbound-port-map-port-range)
    - 5.3 [DASH CA-PA mapping attributes](#53-dash-ca-pa-mapping-attributes)
6. [DASH pipeline behavior](#6-dash-pipeline-behavior)
    - 6.1 [VM-to-PLS direction](#61--vm-to-pls-direction-outbound)
    - 6.2 [PLS-to-VM direction](#62-pls-to-vm-direction)

## 1. Terminology
| Term | Explanation |
| ---  | --- |
| ER   | [ExpressRoute]( https://learn.microsoft.com/en-gb/azure/expressroute/expressroute-introduction)|
| MSEE | Microsoft Enterprise Edge |
| CE   | Customer Edge |
| MSEE/CE routers | Microsoft Enterprise Edge / Customer Edge routers. CE and MSEE routers are directly connected and forming pairs. |
| PL   | [PrivateLink](https://azure.microsoft.com/en-us/products/private-link) |
| PL NSG | PrivateLink NSG. NSG here is not VNET NSG, but a set of appliances that sits between PE and ER for security checks or statistics collection. |
| PE   | Private endpoint |
| PLS  | PrivateLink Service. This is the term for private endpoint from server side. Customer can create their private link service, then expose them to their VNETs as a private endpoint. |
| AZ   | Availability zone |

## 2. Background
Azure Private Link provides private connectivity from a virtual network to Azure platform as a service, by providing an 1-to-1 VNET mapping to the service. To extend the mapping, PL redirect map adds port-level rewrite info that maps a single VNET IP to a list of services.

## 3. SDN transformation
### 3.1 Redirect map 
Private Link redirect map is built on top of private link, using exactly the same sdn transformation as private link defined [here](https://github.com/sonic-net/DASH/blob/main/documentation/general/sdn-pipeline-basic-elements.md#private-link).

The only difference is that the IP address used in underlay routing and 4to6 action will be specified by a port-based service mapping – for a specified port range, different IP or destination port can be used for crafting the packet.

![PL Redirect VM-to-PLS direction](images/private-link-redirect-vm-to-pls.svg)

On the reverse direction, it reverses all the actions in the forwarding side, e.g., 6to4, as it shows below:

![PL Redirect PLS-to-VM direction](./images/private-link-redirect-pls-to-vm.svg)

### 3.2 Redirect map with PL NSG
When PL NSG is enabled, the extra encap for tunneling the packet to NSG will still be added on top the original PL encap. And the return packet will be exactly the same as the regular case without PL NSG.

### 3.3 Redirect map with fast path
The Fast Path here is not ER Fast Path, but the fast path that required by PLS. Fast path ICMP flow redirection will still take effect when redirect map is used.

- If PL NSG is not used, it changes the flow just like regular PL case.

- If PL NSG is used, it only updates the PL encap, leaving the NSG encap unchanged.

For more information on how Fast Path works, please refer to [Fast Path documentations](../load-bal-service/fast-path-icmp-flow-redirection.md).

### 3.4 Non-required features 
- RST on connection idle timeout.
- Flow resimulation should not be triggered automatically on redirect map update.

## 4. Resource modeling, requirement, and SLA
### 4.1 Scaling requirement
For scaling requirement, please refer to [SONIC DASH HLD](https://github.com/sonic-net/DASH/blob/main/documentation/general/dash-sonic-hld.md#14-scaling-requirements).

### 4.2 Reliability requirements
The flows created when redirect map will be replicated among multiple DPUs, following the SmartSwitch HA design.

For more information, please refer to [SmartSwitch HA design doc](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md).

## 5. SAI API design
### 5.1. DASH Outbound Port Map
A new object outbound-port-map is added, which aims to define SNAT/DNAT port translation in outbound direction. It includes the following attributes:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_PORT_MAP_ATTR_COUNTER_ID | sai_object_id_t | Attach a counter. |

NOTE: More attributes could be added in the future for SNAT/DNAT scenarios.

### 5.2. DASH Outbound Port Map Port Range
A new object key entry outbound-port-map-port-range is added, which aims to define port range translation in outbound direction. It is suitable for setting up the PL / PL NSG redirect map scenarios.

The entry is defined like below:
```c
typedef struct _sai_outbound_port_map_port_range_entry_t
{
    /**
     * @brief Switch ID
     *
     * @objects SAI_OBJECT_TYPE_SWITCH
     */
    sai_object_id_t switch_id;

    /**
     * @brief Exact matched key outbound_port_map_id
     *
     * @objects SAI_OBJECT_TYPE_OUTBOUND_PORT_MAP
     */
    sai_object_id_t outbound_port_map_id;

    /**
     * @brief Range matched key dst_port_range
     */
    sai_u32_range_t dst_port_range;

    /**
     * @brief Rule priority in table
     */
    sai_uint32_t priority;

} sai_outbound_port_map_port_range_entry_t;
```

 It includes the following attributes:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_ACTION | sai_outbound_port_map_port_range_entry_action_t | Action. |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_IP | sai_ip_address_t | Back end IP. |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_MATCH_PORT_BASE | sai_uint16_t | Match port base. |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_PORT_BASE | sai_uint16_t | Back end port base. |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_COUNTER_ID | sai_object_id_t | Attach a counter. |

The entry attribute **Action** is defined as below:
```c
typedef enum _sai_outbound_port_map_port_range_entry_action_t
{
    SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_SKIP_MAPPING,
    SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_MAP_TO_PRIVATE_LINK_SERVICE,
} sai_outbound_port_map_port_range_entry_action_t;
```

### 5.3. DASH CA-PA mapping attributes

The following attributes will be added to CA-to-PA entry, for supporting service port rewrites for PL/PL NSG:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OUTBOUND_PORT_MAP_ID | sai_object_id_t | Outbound port map id. |

## 6. DASH pipeline behavior
Following [DASH pipeline behavior of private link service](https://github.com/sonic-net/DASH/blob/main/documentation/private-link-service/private-link-service.md#6-dash-pipeline-behavior), it adds updates for redirect map.

### 6.1  VM-to-PLS direction (Outbound)

**Mapping - VNET**:
Each mapping will be associated with a port map object:
   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.port_map_id | `sai_object_id_t` | (SAI object ID of the port map) |

Later in the stage of outbound port map, the port map id and inner packet destination port consists of a match key to look up table outbound_port_map_port_range, the matched table entry contains a rewrite info for the redirect map.
   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.outbound_port_map_id | `sai_object_id_t` | (SAI object ID of the port map) |
   | entry.dst_port_range | `sai_u32_range_t` | 2000-2100 |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_ACTION | `sai_outbound_port_map_port_range_entry_action_t` | `SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_MAP_TO_PRIVATE_LINK_SERVICE` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_IP | `sai_ip_address_t` | `3.3.3.1` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_MATCH_PORT_BASE | `sai_uint16_t` | `2000` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_PORT_BASE | `sai_uint16_t` | `11000` |

### 6.2. PLS-to-VM direction
None of changes.
