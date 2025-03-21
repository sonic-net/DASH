# DASH Private Link Redirect Map HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 01/26/2025 | Riff Jiang, Junhua Zhai| Initial version |

1. [Terminology](#1-terminology)
2. [Background](#2-background)
3. [SDN transformation](#3-sdn-transformation)
    - 3.1 [Redirect map](#31-redirect-map)
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
    - 5.4 [DASH ENI counters](#54-dash-eni-counters)
6. [DASH pipeline behavior](#6-dash-pipeline-behavior)
    - 6.1 [VM-to-PLS direction](#61--vm-to-pls-direction-outbound)
    - 6.2 [PLS-to-VM direction](#62-pls-to-vm-direction)
    - 6.2 [PL NSG](#63-pl-nsg)

## 1. Terminology

| Term | Explanation |
| ---  | --- |
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

Please refer to [private link load balancer fast path support](./private-link-service.md#33-load-balancer-fast-path-support).

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

A new object `outbound-port-map` is added to manage port mappings in the outbound direction, which includes the following attributes:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_PORT_MAP_ATTR_COUNTER_ID | sai_object_id_t | A counter that tracks the number of packets and bytes associated with the matching outbound-port-map. |

### 5.2. DASH Outbound Port Map Port Range

A new object key entry `outbound-port-map-port-range` is designed to define port range translation in the outbound direction. It is particularly useful for scenarios involving Private Link (PL) or Private Link Network Security Group (PL NSG) redirect maps. The key entry for this object specifies how port ranges should be translated when traffic is directed outbound.

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

} sai_outbound_port_map_port_range_entry_t;
```

The member `dst_port_range` designates the match field of port range, targeting packet TCP/UDP destination port. The entry includes the following attributes:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_ACTION | sai_outbound_port_map_port_range_entry_action_t | Action `skip_mapping` or `map_to_private_link_service`. |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_IP | sai_ip_address_t | The IP of private link service backend, used in both overlay and underlay |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_MATCH_PORT_BASE | sai_uint16_t | Match port base, aka begin port of port range |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_PORT_BASE | sai_uint16_t | Back end port base, aka begin port of translated port range |
| SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_COUNTER_ID | sai_object_id_t | A counter that tracks the number of packets and bytes associated with the matching port range entry  |

The entry attribute **Action** is defined as below:

```c
typedef enum _sai_outbound_port_map_port_range_entry_action_t
{
    SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_SKIP_MAPPING,
    SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_MAP_TO_PRIVATE_LINK_SERVICE,
} sai_outbound_port_map_port_range_entry_action_t;
```

The action `skip_mapping` means to skip the mapping operation. The action `map_to_private_link_service` means to do private link mapping operation as below:

```c
packet.underlay.destination_ip = attr_BACKEND_IP
packet.overlay.ipv6.src_addr = ((((bit<128>)packet.overlay.ipv4.src_addr & ~ca_pa.attr_OVERLAY_SIP_MASK) | ca_pa.attr_OVERLAY_SIP) & ~eni.attr_SAI_ENI_ATTR_PL_SIP_MASK) | eni.attr_SAI_ENI_ATTR_PL_SIP
packet.overlay.ipv6.dst_addr = ((bit<128>)attr_BACKEND_IP & ~ca_pa.attr_OVERLAY_DIP_MASK) | ca_pa.attr_OVERLAY_DIP
packet.overlay.destination_port = attr_BACKEND_PORT_BASE + (packet.overlay.destination_port - attr_MATCH_PORT_BASE)
```

### 5.3. DASH CA-PA mapping attributes

The following attributes will be added to CA-to-PA entry, for supporting service rewrites for PL/PL NSG redirect map:

| Attribute name | Type | Description |
| --- | --- | --- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OUTBOUND_PORT_MAP_ID | sai_object_id_t | Outbound port map id. |

### 5.4. DASH ENI counters

The two drop counters for port-map/port-range-entry missing are added to ENI stats as below:

```c
typedef enum _sai_eni_stat_t
{
    ...

    /** DASH ENI OUTBOUND_PORT_MAP_MISS_DROP_PACKETS stat count */
    SAI_ENI_STAT_OUTBOUND_PORT_MAP_MISS_DROP_PACKETS,

    /** DASH ENI OUTBOUND_PORT_RANGE_ENTRY_MISS_DROP_PACKETS stat count */
    SAI_ENI_STAT_OUTBOUND_PORT_RANGE_ENTRY_MISS_DROP_PACKETS,

} sai_eni_stat_t;
```

## 6. DASH pipeline behavior

Following [DASH pipeline behavior of private link service](https://github.com/sonic-net/DASH/blob/main/documentation/private-link-service/private-link-service.md#6-dash-pipeline-behavior), it adds updates for redirect map.

### 6.1  VM-to-PLS direction (Outbound)

**Mapping - VNET**:
The inner destination IP will be used for finding the outbound CA-PA mapping entry, of which the action will be set to `SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_PRIVATE_LINK_MAPPING`. The mapping entry will be associated with the service rewrite info and a port map object:

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry_attr.outbound_port_map_id | `sai_object_id_t` | (SAI object ID of the port map) |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_SIP | `sai_ip_address_t` | `1111:2222:3333:4444:5555:6666::` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_SIP_MASK | `sai_ip_address_t` | `ffff:ffff:ffff:ffff:ffff:ffff::` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DIP | `sai_ip_address_t` | `9999:8888:7777:6666::` |
   | entry_attr.SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DIP_MASK | `sai_ip_address_t` | `ffff:ffff:ffff:ffff::` |

The attributes OVERLAY_SIP/DIP and port map id could be cached in pipeline/packet metadata and later retrieved in the stage of outbound port map.

**Mapping - outbound port map**:

In this stage, it accomplishes the operation of PL redirect map with the following steps:

1. It validates the port map object exists according to the port map id. If the port map is missing, eni drop counter `SAI_ENI_STAT_OUTBOUND_PORT_MAP_MISS_DROP_PACKETS` increases with one and the pipeline drops the packet, otherwise continues to the next.

1. It looks up the table `outbound port range` with the match key (port_map_id, packet.overlay.destination_port). If none of table entry is matched, it drops the packet and increases eni drop counter `SAI_ENI_STAT_OUTBOUND_PORT_RANGE_ENTRY_MISS_DROP_PACKETS` with 1, otherwise continues to the next.

1. One table entry is matched. If the entry attribute ACTION is `skip_mapping`, the operation in this stage will be skipped, otherwise goes to the next.

1. The entry attribute ACTION must be `map_to_private_link_service`, it starts to do PL redirect map with the entry attr info and the cached CA-PA entry attributes OVERLAY_SIP/DIP. Assume the matched entry attributes are like below:

   | SAI field name | Type | Value |
   | --- | --- | --- |
   | entry.outbound_port_map_id | `sai_object_id_t` | (SAI object ID of the port map) |
   | entry.dst_port_range | `sai_u32_range_t` | 2000-2100 |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_ACTION | `sai_outbound_port_map_port_range_entry_action_t` | `SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ACTION_MAP_TO_PRIVATE_LINK_SERVICE` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_IP | `sai_ip_address_t` | `3.3.3.1` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_MATCH_PORT_BASE | `sai_uint16_t` | `2000` |
   | entry_attr.SAI_OUTBOUND_PORT_MAP_PORT_RANGE_ENTRY_ATTR_BACKEND_PORT_BASE | `sai_uint16_t` | `11000` |

    And packet overlay destination port is 2010, the operation details are as below:

    - port translation

    ```c
    packet.overlay.destination_port = 11000 + 2010 - 2000
    ```

    - nat 4to6

    ```c
    packet.overlay.ipv6.src_addr = (((1111:2222:3333:4444:5555:6666::packet.overlay.ipv4.src_addr) & ~eni.attr_SAI_ENI_ATTR_PL_SIP_MASK) | eni.attr_SAI_ENI_ATTR_PL_SIP
    packet.overlay.ipv6.dst_addr = 9999:8888:7777:6666::3.3.3.1
    ```

    - underlay destination ip update

    ```c
    packet.underlay.destination_ip = 3.3.3.1
    ```

    - counter update

    ```c
    port_map.attr_counter.packets += 1
    port_map.attr_counter.bytes += packet.size
    port_map_port_range_entry.attr_counter.packets += 1
    port_map_port_range_entry.attr_counter.bytes += packet.size
    ```

**Metering**:

Same as PL scenario.

### 6.2. PLS-to-VM direction

None of changes.

### 6.3. PL NSG

Same of section 6.1, none of extra operations..
