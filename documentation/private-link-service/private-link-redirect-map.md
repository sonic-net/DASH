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
5. [DASH object model design](#5-dash-object-model-design)
    - 5.1 [From On-Premise to PLS direction](#51-from-on-premise-to-pls-direction)
    - 5.2 [From PLS to On-Premise direction](#52-from-pls-to-on-premise-direction)

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
The scaling requirement for PL redirect map are listed as below. The metrics are based on a 200Gbps DPU:
| Metric | Requirement |
| ---    | --- |
| # of ENIs per DPU | 32 |
| # of VNET mapping per ENI  | 64K |
| # of PPS | 64M |
| # of redirect mapping per DPU | 2000 maps (Reusable among all ENIs) |
| # of entries in each redirect mapping | 8K |
| VNET mapping change rate (CRUD) | <TBD> |
| Redirect map entry change rate (CRUD) | Monthly |
| # of fast path packets | Same as CPS. 3M per card. |

### 4.2 Reliability requirements
The flows created when redirect map will be replicated among multiple DPUs, following the SmartSwitch HA design.

For more information, please refer to [SmartSwitch HA design doc](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md).

## 5. DASH object model design
Now we have all action defined, we can use these actions to define our overall DASH pipeline.

### 5.1 From On-Premise to PLS direction
Say, we have a VM in on-premises network with IP 10.0.0.1, trying to reach the Private Endpoint in their VNET with IP 10.0.1.1, and the ExpressRoute VNI is 1000000:

#### 5.1.1 Private Link
1. **VNI Lookup**: First, we will look up the VNI to determine the packet direction. In this case, we consider all the packets from on-premises network as outbound direction from the floating NIC perspective.
```json
    "DASH_VNET_TABLE:Vnet1": { 
        "vni": "45654",
        "guid": "559c6ce8-26ab-4193-b946-ccc6e8f930b2"
    }
```

2. **ENI Lookup**: Then, we will use the inner MAC address to find the ENI pipeline. Then, the outer encap will be decap’ed, leaving inner packet going through the rest of pipeline.
```json
    "DASH_ENI_TABLE:F4939FEFC47E": { 
        "eni_id": "497f23d7-f0ac-4c99-a98f-59b470e8c7bd",
        "mac_address": "F4-93-9F-EF-C4-7E",
        "underlay_ip": "25.1.1.1",
        "admin_state": "enabled",
        "vnet": "Vnet1",
        "pl_sip_encoding": "0x0020000000000a0b0c0d0a0b/0x002000000000ffffffffffff",
        "pl_underlay_sip": "55.1.2.3"
    }
```

3. **Conntrack Lookup**: If flow already exists, we directly apply the transformation from the flow, otherwise, move on.

4. **ACL**: We don’t have any ACL rules for PL, hence no ACL rules will be hit.

5. **Routing**: The inner destination IP will be used for finding the route entry, which will be the IP range of the destination VNET. This will trigger the maprouting action to run, which makes the packet entering Mapping stage.

    The routing stage could also define the underlay_sip in the routing stage, which is already exists in current DASH VNET model. This will be used for updating the source IP of the outer encap for PL.

    The goal state that routing stage uses can be defined as below:
```json
    "DASH_ROUTE_TABLE:F4939FEFC47E:10.2.0.6/24": {
        "action_type": "vnet",
        "vnet": "Vnet1",
        "metering_class": "60000",
        "underlay_sip": "50.2.2.6"
    },

    "DASH_ROUTING_TYPE_TABLE:vnet": {
        "name": "action1",
        "action_type": "maprouting"
    },
```

6. **Mapping - VNET**: The inner destination IP will be used for finding the VNET mapping, which works on IP level. Because each mapping will be associated with a port-based service map, besides the information for the normal private link scenario, this mapping will also contains an rewrite info for the redirect map.
```json
    "DASH_VNET_MAPPING_TABLE:Vnet1:10.2.0.6": {
        "routing_type": "privatelink",
        "mac_address": "F9-22-83-99-22-A2",
        "underlay_ip": "50.2.2.6",
        "overlay_sip": "fd40:108:0:d204:0:200::0",
        "overlay_dip": "2603:10e1:100:2::3402:206",
        "metering_class": "60001",
        "svc_rewrite_info": {
            "src_prefix": "fd40:108:0:5678:0:200::/32",
            "dst_prefix": "2603:10e1:100:2::/32",
            "port_map_id": "port_map_1"
        }
    },

    "DASH_ROUTING_TYPE_TABLE:privatelink": [
        {
            "name": "action1",
            "action_type": "4to6"
        },
        {
            "name": "action2",
            "action_type": "staticencap",
            "encap_type": "nvgre",
            "key": "100"
        }
    ]
```

7. **Service port rewrite**: If “port_map_id” is defined, we need to use the service port mapping defined in that map to rewrite the packet for forwarding.

    As the policy shows below:
    - If the destination port lives in the exempted list will be bypassed using the original config from VNET mapping for packet routing. All configs inside svc_rewrite_info shall be ignored.
    - Otherwise, the entry that covers the destination port shall be picked up for rewriting the packet.

8. **Metering**: The last action we need to do is to find the corresponding metering rule.
```json
    "DASH_METER:60000": {
        "eni_id": "497f23d7-f0ac-4c99-a98f-59b470e8c7bd",
        "metadata": "ROUTE_VNET1",
        "metering_class": "60000"
    },

    "DASH_METER:60001": {
        "eni_id": "497f23d7-f0ac-4c99-a98f-59b470e8c7bd",
        "metadata": "PRIVATE_LINK_VNET1",
        "metering_class": "60001"
    },
```
9. **Conntrack Update**: Both forwarding and reverse flows will be created by this stage.

10. **Metering Update**: Metering update will update the metering counter based on the rules that we found before.

11. **Underlay routing**: Underlay routing will do the real packet transformation, e.g., 4to6 transformation and adding encaps.

After all stages in the pipeline, the packet will be sent back to wire.

#### 5.1.2 Private Link NSG
The changes needed for PL NSG is mostly the same as PL - on the VNET mapping, “src_rewrite_info” field will be added for providing the redirect map.

```json
    "DASH_VNET_MAPPING_TABLE:Vnet1:10.2.0.9": {
        "routing_type": "privatelinknsg",
        "mac_address": "F9-22-83-99-22-A2",
        "underlay_ip": "50.2.2.6",
        "overlay_sip": "fd40:108:0:d204:0:200::0",
        "overlay_dip": "2603:10e1:100:2::3402:206",
        "routing_appliance_id": 22,
        "metering_class": "60001",
        "svc_rewrite_info": {
            "src_prefix": "fd40:108:0:5678:0:200::/32",
            "dst_prefix": "2603:10e1:100:2::/32",
            "port_map_id": "port_map_1"
        }
    },
    "DASH_ROUTING_TYPE_TABLE:privatelinknsg": [
        {
            "name": "action1",
            "action_type": "4to6"
        },
        {
            "name": "action2",
            "action_type": "staticencap",
            "encap_type": "nvgre",
            "key": "100"
        },
        {
            "name": "action3",
            "action_type": "appliance"
        }
    ],
    "DASH_ROUTING_APPLIANCE_TABLE:22": {
        "appliance_guid": "497f23d7-f0ac-4c99",
        "addresses": "100.8.1.2",
        "encap_type": "vxlan",
        "vni": 101
    }
```
 
### 5.2 From PLS to On-Premise direction
With flow HA, the return packet will be forwarded to the active side of the HA pair, which will use the stored reversed flow to process the packet and forward it back to the MSEE.

#### 5.2.1 Private Link
1. VNI Lookup: First, we will use the VNI to determine the packet direction. In this case, since Private Link Key is not in the outbound VNI list, we consider all the packets from PLS side as inbound direction from the floating NIC perspective.

2. ENI Lookup: We will again uses inner destination MAC address to find the ENI pipeline. Once found, the outer encap will be decap’ed, exposing the inner packet for later processing.

    The ENI goal state that we are using will be the same as before. Hence, emitted here.

3. Conntrack Lookup: The return packet transformation will be handled by reverse flow.
4. Metering Update: Metering update will update the metering counter based on the rules that we saved in the reverse flow.
5. Underlay routing: Underlay routing will do the real packet transformation, e.g., 6to4 transformation and adding encaps.

#### 5.2.2 Private Link NSG
Since the packet that being sent to us in PL NSG scenario will be exactly the same as regular PL, and the reverse flow that being created in the PL NSG scenario will also be the same, there is nothing we need to change for the PL NSG case.
