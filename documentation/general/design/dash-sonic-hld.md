# SONiC-DASH HLD
## High Level Design Document
### Rev 0.2

# Table of Contents

  * [Revision](#revision)

  * [About this Manual](#about-this-manual)

  * [Definitions/Abbreviation](#definitionsabbreviation)
 
  * [1 Requirements Overview](#1-requirements-overview)
    * [1.1 Functional requirements](#11-functional-requirements)
    * [1.2 CLI requirements](#12-cli-requirements)
    * [1.3 Warm Restart requirements ](#13-warm-restart-requirements)
    * [1.4 Scaling requirements ](#14-scaling-requirements)
  * [2 Packet Flows](#2-packet-flows)
  * [3 Modules Design](#3-modules-design)
    * [3.1 Config DB](#31-config-db)
    * [3.2 Dash DB](#32-dash-app-db)
    * [3.3 Module Interaction](#33-module-interaction)
    * [3.4 CLI](#34-cli)
    * [3.5 Test Plan](#35-test-plan)

###### Revision

| Rev |     Date    |       Author       | Change Description                |
|:---:|:-----------:|:------------------:|-----------------------------------|
| 0.1 | 02/01/2022  |     Prince Sunny   | Initial version                   |
| 0.2 | 03/09/2022  |     Prince Sunny   | Packet Flows/DB Objects           |


# About this Manual
This document provides more detailed design of DASH APIs, DASH orchestration agent, Config and APP DB Schemas and other SONiC buildimage changes required to bring up SONiC image on an appliance card. General DASH HLD can be found at [dash_hld](https://github.com/Azure/DASH/blob/main/documentation/general/design/dash-high-level-design.md).

# Definitions/Abbreviation
###### Table 1: Abbreviations
|                          |                                |
|--------------------------|--------------------------------|
| DASH                     | Disaggregated APIs for SONiC Hosts |
| VNI                      | Vxlan Network Identifier       |
| VTEP                     | Vxlan Tunnel End Point         |
| VNET                     | Virtual Network                |
| ENI                      | Elastic Network Interface      |
| gNMI                     | gRPC Network Management Interface |
| vPORT                    | VM's NIC. Eni, Vnic, VPort are used interchangeably |

# 1 Requirements Overview

## 1.1 Functional requirements

At a high level the following should be supported:
  
- Bringup SONiC image for DEVICE_METADATA subtype - `appliance`
- Bringup Swss/Syncd containers for switch_type - `dpu`
- Able to program DASH objects configured via gRPC client to appliance card via SAI DASH API

  Phase 1
    - Vnet-Vnet scenario
    - Route/LPM support
    - Underlay IPv4 and IPv6
    - Stateful ACL support
    - TCP state tracking on flows
    - Telemetry and Monitoring

  Phase 2
    - Private Link
    - Service Tunnel
    - Overlay IPv6 
  

## 1.2 CLI requirements
Initial support is only for `show` commands

- User should be able to show the DASH configured objects

## 1.3 Warm Restart requirements
Warm-restart support is not considered in Phase 1. TBD

## 1.4 Scaling requirements
Following are the minimal scaling requirements
| Item                     | Expected value              |
|--------------------------|-----------------------------|
| VNETs                    | 1024                     |
| ENI                      | 32 Per Card              |
| Routes per ENI           | 100k                     |
| NSGs per ENI             | 6                        |
| ACLs per ENI             | 6x100K prefixes          |
| ACLs per ENI             | 6x10K SRC/DST ports      |
| CA-PA Mappings           | 10M                      |
| Active Connections/ENI   | 1M                       |

# 2 Packet Flows
	
The following section captures at a high-level on the VNET packet flow. Detailed lookup and pipeline behavior can be referenced *here*.

## 2.1 Outbound packet processing pipeline
	
  ![dash-outbound](https://github.com/prsunny/DASH/blob/main/Assets/pkt_flow_outbound.png)
	
Based on the incoming packet's VNI matched against the reserved VNI assigned for VM->Appliance, the pipeline shall set the direction as TX(Outbound) and using the inner src-mac, maps to the corresponding ENI.The incoming packet will always be vxlan encapped and outer dst-ip is the appliance VIP. The pipeline shall parse the VNI, and for VM traffic, the VNI shall be a special reserved VNI. Everything else shall be treated as as network traffic(RX). Pipeline shall use VNI to differentiate the traffic to be VM (Inbound) or Network (Outbound).

In the outbound flow, the appliance shall assume it is the first appliance to apply policy. It applies the outbound ACLs in three stages (VNIC, Subnet and VNET), processed in order, with the outcome being the most restrictive of the three ACLs combined. 

After the ACL stage, it does LPM routing based on the inner dst-ip and applies the respective action (encap, subsequent CA-PA mapping). Finally, update the connection tracking table for both inbound and outbound. 
	
## 2.2 Inbound packet processing pipeline
	
   ![dash-intbound](https://github.com/prsunny/DASH/blob/main/Assets/pkt_flw_inbound.png)

Based on the incoming packet's VNI, if it does not match against any reserved VNI, the pipeline shall set the direction as RX(Inbound) and using the inner dst-mac, maps to the corresponding ENI. In the inbound flow, Routing (LPM) lookup happens first based on the inner dst-ip and does a CA-PA validation based on the mapping. After LPM is the three stage ACL, processed in order. ACLs can have multiple src/dst IP ranges or port ranges as match criteria.
	
It is worth noting that CA-PA mapping table shall be used for both encap and decap process
	
# 3 Modules Design

The following are the schema changes. The NorthBound APIs shall be defined as sonic-yang in compliance to [yang-guideline](https://github.com/Azure/SONiC/blob/master/doc/mgmt/SONiC_YANG_Model_Guidelines.md)

For DASH objects, the proposal is to have its own DB instance (DASH_APP_DB). Ref [link](https://github.com/Azure/sonic-buildimage/blob/master/dockers/docker-database/database_config.json.j2), thus ensuring isolation from regular configs that are persistent in the appliance across reboots. All the DASH objects are programmed by SDN and hence treated differently from the existing Sonic L2/L3 'switch' DB ojects 

```
        "DASH_APP_DB" : {
            "id" : 15,
            "separator": ":",
            "instance" : "redis"
        }
	
	"DASH_STATE_DB" : {
            "id" : 16,
            "separator": "|",
            "instance" : "redis"
        }
```

## 3.1 Config DB

### 3.1.1 DEVICE Metadata Table

```
"DEVICE_METADATA": {
    "localhost": {
        "subtype": "appliance",
        "type": "sonichost",
        "switch_type": "dpu",
        "sub_role": "None"
     }
}
```

### 3.1.2 VXLAN Table

```
VXLAN_TUNNEL|{{tunnel_name}} 
    "src_ip": {{ip_address}} 
    "dst_ip": {{ip_address}} (OPTIONAL)
```

## 3.2 DASH APP DB

Following diagram captures the object reference model.

  ![dash-eni-vnet-obj-model](https://github.com/prsunny/DASH/blob/main/Assets/dash_object_model.png)

### 3.2.1 VNET
  
```
DASH_VNET:{{vnet_name}} 
    "vxlan_tunnel": {{tunnel_name}}
    "vni": {{vni}} 
    "guid": {{"string"}}
    "address_spaces": {{[list of addresses]}} (OPTIONAL)
    "peer_list": {{vnet_name_list}} (OPTIONAL)
```

### 3.2.2 QOS
  
```
DASH_QOS:{{qos_name}} 
    "qos_id": {{string}}
    "bw": {{bw}} 
    "cps": {{cps}}
    "flows": {{flows}}
```
```
key                      = DASH_QOS:qos_name ; Qos name as key
; field                  = value 
bw                       = bandwidth in kbps
cps                      = Number of connection per second
flows                    = Number of flows
```

### 3.2.3 ENI
  
```
DASH_ENI:{{eni}} 
    "eni_id": {{string}}
    "mac_address": {{mac_address}} 
    "qos": {{qos_name}}
    "vnet": {{[list of vnets]}}
```
```
key                      = DASH_ENI:eni ; ENI MAC as key
; field                  = value 
mac_address              = MAC address as string
qos                      = Associated Qos profile
vnet                     = list of Vnets that ENI belongs to
```
### 3.2.4 ACL
  
```
DASH_ACL_V4_IN:{{eni}} 
    "stage": {{stage}}
    "acl_group_id": {{group_id}} 
```
```
DASH_ACL_V4_OUT:{{eni}} 
    "stage": {{stage}}
    "acl_group_id": {{group_id}} 
```

```
key                      = DASH_ACL_V4_IN:eni ; ENI MAC as key
; field                  = value 
stage                    = ACL stage {1, 2, 3 ..}
acl_group_id             = ACL group ID
```

```
DASH_ACL_GROUP:{{group_id}} 
    "ip_version": {{ipv4/ipv6}}
```

```
DASH_ACL_RULE:{{group_id}}|{{rule_num}}
    "priority": {{priority}}
    "action": {{action}}
    "terminating": {{bool}}
    "protocol": {{list of protocols}}
    "src_addr": {{list of address}}
    "dst_addr": {{list of address}}
    "src_port": {{list of range of ports}}
    "dst_port": {{list of range of ports}}
    
```

```
key                      = DASH_ACL_RULE:group_id:rule_num ; unique rule num within the group.
; field                  = value 
priority                 = INT32 value  ; priority of the rule, lower the value, higher the priority
action                   = allow/deny
terminating              = true/false   ; if true, stop processing further rules
protocols                = list of INT ',' separated; E.g. 6-udp, 17-tcp
src_addr                 = list of source ip prefixes ',' separated
dst_addr                 = list of destination ip prefixes ',' separated
src_port                 = list of range of source ports ',' separated
dst_port                 = list of range of destination ports ',' separated
```

### 3.2.5 ROUTING TYPE
	
```
DASH_ROUTING_TYPE:{{routing_type}}:{{action_type}} 
    "encap_type": {{encap type}} (OPTIONAL)
    "vni": {{list of vni}} (OPTIONAL)
```

```
key                      = DASH_ROUTING_TYPE:routing_type:action_type ; routing type can be {direct, vnet, vnet_direct, appliance, privatelink, privatelinknsg, servicetunnel} action_type can be {maprouting, direct, staticencap, appliance, 4to6, mapdecap, decap, drop}
; field                  = value 
encap_type               = encap type depends on the action_type - {vxlan, nvgre}
vni                      = vni value associated with the corresponding action. Applicable if encap_type is specified. 
```

### 3.2.6 APPLIANCE
	
```
DASH_APPLIANCE:{{appliance_id}} 
    "sip": {{ip_address}}
    "vm_vni": {{list of vnis}}
```

```
key                      = DASH_APPLIANCE:id ; attributes specific for the appliance
; field                  = value 
sip                      = source ip address, to be used in encap
vm_vni                   = list of VNIs that need special treatment. Chosen for setting direction etc. 
```

### 3.2.7 ROUTE TABLE

``` 
DASH_ROUTE_TABLE:{{eni}}:{{prefix}} 
    "action_type": {{routing_type}} 
    "vnet":{{vnet_name}} (OPTIONAL)
    "appliance":{{appliance_id}} (OPTIONAL)
    "overlay_ip":{{ip_address}} (OPTIONAL)
    "underlay_ip":{{ip_address}} (OPTIONAL)
    "overlay_sip":{{ip_address}} (OPTIONAL)
    "underlay_dip":{{ip_address}} (OPTIONAL)
    "customer_addr":{{ip_address}} (OPTIONAL)
    "metering_bucket": {{bucket_id}}(OPTIONAL) 
```
  
```
key                      = DASH_ROUTE_TABLE:eni:prefix ; ENI route table with CA prefix
; field                  = value 
action_type              = routing_type              ; reference to routing type
vnet                     = vnet name                 ; vnet name if routing_type is {vnet, vnet_direct}
appliance                = appliance id              ; appliance id if routing_type is {appliance} 
overlay_ip               = ip_address                ; overlay_ip to override if routing_type is {servicetunnel}, use dst ip from packet if not specified
underlay_ip              = ip_address                ; underlay_ip to override if routing_type is {servicetunnel}, use dst ip from packet if not specified
overlay_sip              = ip_address                ; overlay_sip if routing_type is {servicetunnel}  
underlay_sip             = ip_address                ; overlay_sip if routing_type is {servicetunnel}
customer_addr            = ip_address                ; CA address if routing_type is {vnet_direct}
metering_bucket          = bucket_id                 ; metering and counter
```

### 3.2.8 VNET MAPPING TABLE

``` 
DASH_MAPPING_TABLE:{{vnet}}:{{ip_address}} 
    "routing_type": {{routing_type}} 
    "underlay_ip":{{ip_address}}
    "mac_address":{{mac_address}} (OPTIONAL) 
    "metering_bucket": {{bucket_id}}(OPTIONAL)
```
```
key                      = DASH_ROUTE_TABLE:eni:ip_address ; ENI route table with CA IP
; field                  = value 
action_type              = routing_type              ; reference to routing type
underlay_ip              = ip_address                ; PA address for the CA
mac_address              = MAC address as string     ; Inner dst mac
metering_bucket          = bucket_id                 ; metering and counter
```

## 3.3 Module Interaction

A high-level module interaction is captured in the following diagram.

  ![dash-high-level-diagram](https://github.com/prsunny/DASH/blob/main/Assets/dash-high-level-design.svg)
  
### 3.3.1 SONiC host containers

The following containers shall be enabled for sonichost and part of the image. Switch specific containers shall be disabled for the image built for the appliance card.
  
| Container/Feature Name   | Is Enabled?     |
|--------------------------|-----------------|
|	SNMP | Yes |
|	Telemetry	| Yes |
|	LLDP | Yes |
|	Syncd |	Yes |
|	Swss | Yes |
|	Database | Yes |
|	BGP | Yes |
|	Teamd	| No |
|	Pmon | Yes |
|	Nat | No |
|	Sflow | No |
|	DHCP Relay | No |
|	Radv | No |
|	Macsec | No |
|	Resttapi | No |
|	gNMI | Yes |

### 3.3.2 DASHOrch (Overlay)
A new orchestration agent "dashorch" shall be implemented that subscribes to DASH APP DB objects and programs the ASIC_DB via the SAI DASH API. DASHOrch shall have sub-orchestrations to handle ACLs, Routes, CA-PA mappings. DASH orchestration agent shall write the state of each tables to STATEDB that applications shall utilize to fetch the programmed status of configured objects.
  
DASH APIs shall be exposed as gNMI interface and part of the SONiC gNMI container. Clients shall configure the SONiC via gRPC get/set calls. gNMI container has the config backend to translate/write DASH objects to CONFIG_DB and/or DASH APP_DB.

### 3.3.3 SWSS Lite (Underlay)
SONiC for DASH shall have a lite swss initialization without the heavy-lift of existing switch based orchestration agents that SONiC currently have. The initialization shall be based on switch_type "dpu". For the underlay support, the following SAI APIs are expected to be supported:
  
| Component                | SAI attribute                                         |
|--------------------------|-------------------------------------------------------|
| Host Interface           | SAI_HOSTIF_ATTR_NAME |
|                          | SAI_HOSTIF_ATTR_OBJ_ID |
|                          | SAI_HOSTIF_ATTR_TYPE |
|                          | SAI_HOSTIF_ATTR_OPER_STATUS |
|                          | SAI_HOSTIF_TABLE_ENTRY_ATTR_CHANNEL_TYPE |
|                          | SAI_HOSTIF_TABLE_ENTRY_ATTR_HOST_IF |
|                          | SAI_HOSTIF_TABLE_ENTRY_ATTR_TRAP_ID |
|                          | SAI_HOSTIF_TABLE_ENTRY_ATTR_TYPE |
|                          | SAI_HOSTIF_TRAP_ATTR_PACKET_ACTION |
|                          | SAI_HOSTIF_TRAP_ATTR_TRAP_GROUP |
|                          | SAI_HOSTIF_TRAP_ATTR_TRAP_PRIORITY |
|                          | SAI_HOSTIF_TRAP_ATTR_TRAP_TYPE |
|                          | SAI_HOSTIF_TRAP_GROUP_ATTR_POLICER |
|                          | SAI_HOSTIF_TRAP_GROUP_ATTR_QUEUE | 
| Neighbor                 | SAI_NEIGHBOR_ENTRY_ATTR_DST_MAC_ADDRESS |
| Nexthop                  | SAI_NEXT_HOP_ATTR_IP  | 
|                          | SAI_NEXT_HOP_ATTR_ROUTER_INTERFACE_ID  | 
|                          | SAI_NEXT_HOP_ATTR_TYPE  |
| Packet                   | SAI_PACKET_ACTION_FORWARD  | 
|                          | SAI_PACKET_ACTION_TRAP  | 
|                          | SAI_PACKET_ACTION_DROP  | 
| Policer                  | SAI_POLICER_ATTR_CBS |
|                          | SAI_POLICER_ATTR_CIR |
|                          | SAI_POLICER_ATTR_COLOR_SOURCE |
|                          | SAI_POLICER_ATTR_GREEN_PACKET_ACTION |
|                          | SAI_POLICER_ATTR_METER_TYPE |
|                          | SAI_POLICER_ATTR_MODE |
|                          | SAI_POLICER_ATTR_PBS  |      
|                          | SAI_POLICER_ATTR_PIR  |  
|                          | SAI_POLICER_ATTR_RED_PACKET_ACTION  |  
|                          | SAI_POLICER_ATTR_YELLOW_PACKET_ACTION  |  
| Port                     | SAI_PORT_ATTR_ADMIN_STATE  |  
|                          | SAI_PORT_ATTR_ADVERTISED_AUTO_NEG_MODE  |  
|                          | SAI_PORT_ATTR_ADVERTISED_FEC_MODE  |  
|                          | SAI_PORT_ATTR_ADVERTISED_INTERFACE_TYPE  |  
|                          | SAI_PORT_ATTR_ADVERTISED_MEDIA_TYPE  |  
|                          | SAI_PORT_ATTR_ADVERTISED_SPEED
|                          | SAI_PORT_ATTR_AUTO_NEG_MODE  |  
|                          | SAI_PORT_ATTR_FEC_MODE  |  
|                          | SAI_PORT_ATTR_HW_LANE_LIST  |  
|                          | SAI_PORT_ATTR_INTERFACE_TYPE  |  
|                          | SAI_PORT_ATTR_MTU  |  
|                          | SAI_PORT_ATTR_OPER_SPEED  |  
|                          | SAI_PORT_ATTR_OPER_STATUS  |  
|                          | SAI_PORT_ATTR_SPEED  |  
| RIF                      | SAI_ROUTER_INTERFACE_ATTR_ADMIN_V4_STATE  |  
|                          | SAI_ROUTER_INTERFACE_ATTR_ADMIN_V6_STATE  |  
|                          | SAI_ROUTER_INTERFACE_ATTR_MTU  |
|                          | SAI_ROUTER_INTERFACE_ATTR_PORT_ID  |
|                          | SAI_ROUTER_INTERFACE_ATTR_SRC_MAC_ADDRESS |
|                          | SAI_ROUTER_INTERFACE_ATTR_TYPE  |  
|                          | SAI_ROUTER_INTERFACE_ATTR_VIRTUAL_ROUTER_ID  |  
| Route                    | SAI_ROUTE_ENTRY_ATTR_NEXT_HOP_ID  |  
|                          | SAI_ROUTE_ENTRY_ATTR_PACKET_ACTION  |  
| Switch                   | SAI_SWITCH_ATTR_CPU_PORT  |  
|                          | SAI_SWITCH_ATTR_DEFAULT_TRAP_GROUP  |  
|                          | SAI_SWITCH_ATTR_DEFAULT_VIRTUAL_ROUTER_ID  |
|                          | SAI_SWITCH_ATTR_DEFAULT_VLAN_ID  |
|                          | SAI_SWITCH_ATTR_ECMP_DEFAULT_HASH_SEED |
|                          | SAI_SWITCH_ATTR_INIT_SWITCH  |  
|                          | SAI_SWITCH_ATTR_PORT_LIST  |  
|                          | SAI_SWITCH_ATTR_PORT_NUMBER  |  
|                          | SAI_SWITCH_ATTR_PORT_STATE_CHANGE_NOTIFY  |  
|                          | SAI_SWITCH_ATTR_SHUTDOWN_REQUEST_NOTIFY  |  
|                          | SAI_SWITCH_ATTR_SRC_MAC_ADDRESS |
|                          | SAI_SWITCH_ATTR_SWITCH_ID   |  
|                          | SAI_SWITCH_ATTR_TYPE  |  
|                          | SAI_SWITCH_ATTR_VXLAN_DEFAULT_PORT  |  
|                          | SAI_SWITCH_ATTR_VXLAN_DEFAULT_ROUTER_MAC |  

### 3.3.4 Underlay Routing
DASH Appliance shall establish BGP session with the connected ToR and advertise the prefixes (VIP PA). In turn, the ToR shall advertise default route to appliance. With two ToRs connected, the appliance shall have route with gateway towards both ToRs and does ECMP routing. Orchagent install the route and resolves the neighbor (GW) mac and programs the underlay route/nexthop and neighbor. In the absence of a default-route, appliance shall send the packet back on the same port towards the recieving ToR and can derive the underlay dst mac from the src mac of the received packet or from the neighbor entry (IP/MAC) associated with the port. 

### 3.3.5 Memory footprints
TBD

## 3.4 CLI

The following commands shall be added :

```
	- show dash <eni> routes all
	- show dash <eni> acls stage <ingress/egress/all>
	- show dash <vnet> mappings
	- show dash route-types
	- show dash qos
	- show dash vnet brief
```

## 3.5 Test Plan

Refer DASH documentation for the test plan. 
