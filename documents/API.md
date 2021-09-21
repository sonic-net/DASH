# SiriusAPI

## 1. Overview

This document covers the Sirius API proposal for configuring of the SDN Control Plane on dedicated hardware and requirements related to implementations.

## 2. Scope

The following is in scope of the document:

* Creation/Deletion of the Interface
* ACLs
* Routing
* Mapping
* Load Balancing
* Transforms
* Billing
* Telemetry
* Diagnostics

## 3. Definitions
| Name      | Definition |
| ----------- | ----------- |
| ACL | Access Control List |
| ARP | Address Resolution Protocol |
| ASN | Autonomous System Number |
| AZ | Availability Zone |
| Baremetal | Entire node not running any custom SDN software (connected to “SDN”/”VNET” via “intelligent” router/appliance) |
| BGP | Border Gateway Protocol |
| CA | Customer Address (visible inside Customer VM) |
| Cloud | Top Level  (collection of Regions) |
| Cluster | Collection of Nodes across different Racks |
| Connection | Control plane communication between sender and receiver (usually involves handshake) |
| DC | Data Center |
| DHCP | Dynamic Host Configuration Protocol (IPv4) |
| DHCPv6 | Dynamic Host Configuration Protocol (IPv6) |
| DSR | Direct Server Return |
| DSR VIP | Virtual IP used for Direct Server Return |
| ELB | External Load Balancer |
| ENI	| Elastic Network Interface |
| ER	| Express Route (CISCO/ARISTA/etc hardware that performs point-to-point connectivity and forwards traffic) |
| Flow	| Single transposition (TBD – expand) – Data plane stream of packets between sender and receiver that shares key IP header information |
| Flow Table	| Collection of Flows |
| gRPC	| Google RPC |
| GW	| Gateway
| HA	| High Availability
| ILB	| Internal Load Balancer
| ILB	| Internal Load Balancer
| IPSec	| IPSec Tunnel or IPSec Device
| IPv4	| IP protocol Version 4 (ex. 10.1.2.3)
| IPv6	| IP protocol Version 6 (ex. 2001:1234:abcd::1)
| JSON	| JavaScript JSON Format
| LB	| Load Balancer
| LPM	| Longest-Prefix-Match algorithm commonly used in routing.
| MAC	| MAC Address
| Mapping	| Mapping transformation between CA:PA:MAC
| NA	| Neighbor Advertisement
| NDP	| NDP
| Node / Blade	| Single Physical Machine in a Rack
| NS	| Neighbor Solicitation
| NVA	| Network Virtual Appliance (VM that might have forwarding or filtering functionality)
| NVGRE / GRE	| GRE Encapsulation Protocol
| Overlay	|  
| PA	| Provider Address (internal Azure Datacenter address used for routing)
| Peering	| Network Relationship between two entities (usually between two VNETs – ex. VNET Peering)
| PhyNet	| Physical Network
| Prefix	| For IPv4: (0-32) – example 10.0.0.0/8 | For IPv6: (0-128) – example: 2001:1234:abcd::/48
| RA	| Router Advertisement
| Rack	| Collection of physical machines, switches etc
| Region	| Single Region (collection of DCs in same region)
| RS	| Router Solicitation
| SDN	| Software Defined Networking (high level name for the Virtual Network and its elements)
| SONIC	| SONIC Switch Platform
| Spoof Guard	| Rule put in place to prevent VM from spoofing traffic
| TCP	| Transmission Control Protocol
| TOR	| Top of the Rack Switch (aka ToR or T0)
| UDP	| User Datagram Protocol
| Underlay |  
| VFP	| Virtual Filtering Platform
| VIP	| Virtual IP (IP exposed on Load Balancer)
| VM	| Virtual Machine
| VNET	| Virtual Network
| VXLAN	| VXLAN Encapsulation Protocol
| XML	| XML Format (Extensible Markup Language Format)

## 4. Assumptions
Processing Pipeline must support both IPv4 and IPv6 protocols for both Underlay and Overlay (unless explicitly stated that some scenarios is IPv4-only or IPv6-only).

## 5. Processing Pipeline
### 5.1 ENI Selection
Once packet arrives on Inbound to the device/card, it must be forwarded to the correct ENI policy processing pipeline.

This ENI selection will be done based on the Inner Destination MAC of the packet, which will be matched against the MAC of the ENI.

### 5.2 ENI Selection
Packets will be processed via the following pipeline

#### 5.2.1 Outbound
VM->ACLs->Routing->Network

#### 5.2.2 Inbound
Network->Routing->ACLs->VM

### 5.3 Important Considerations
Packets coming from “Network” might be of the following types:
1.	Encapped within VNET traffic (from VM to VM)
2.	Encapped traffic from MUX to VM
3.	Encapped traffic from Device to VM
4.	Direct traffic from infrastructure to VM (ex. Node to VM) (no encap)

Packet going outside to “Network” might be of the following types:
1.	Direct traffic to Internet (no encap)
2.	Direct traffic to infrastructure (no encap)
3.	Encapped within VNET traffic (from VM to VM)
4.	Encapped traffic from VM to Device

## 6. API Definition
### 6.1 Creation/Deletion of Interface
Each Interface, also called Elastic Network Interface (ENI), is independent entity that has collection of routing policies.

Usually there is 1:1 mapping between VM (or Physical) NIC and the ENI (Virtual NIC).

VM/Physical NIC represents the NIC exposed directly to the VM.

#### 6.1.1 CreateENI
THIS API CREATES AN ELASTIC NETWORK INTERFACE WITH SPECIFIED ENI MATCH CRITERION.
FIRST VERSION OF THIS API ONLY SUPPORT MAC-ADDRESS AS ENI IDENTIFICATION CRITERION.

ENI IDENTIFICATION CRITERION IS ALSO USED TO IDENTIFY PACKET DIRECTION. 

FOR ENI CREATED WITH IDENTIFIER MAC1, IT ASSUMES PACKETS WITH DESTINATION MAC AS MAC1 ARE INBOUND AND PACKETS WITH SOURCE MAC AS MAC2 ARE OUTBOUND. THIS DIRECTION IS USED FOR MATCHING APPROPRIATE INBOUND AND OUTBOUND POLICIES. 

USAGE:
```
message Guid
{
  bytes Bytes = 1; // A 16-element byte array
  }
message MacAddress
{
 bytes Bytes = 1; // A 6-element byte array
}
message EniId {
    Guid eni_id = 1;
}

rpc AddEni(EniId, MacAddress) returns();
 
```

EXAMPLES
An illustrative figure of the failure handling framework is shown below.
The orchagent generates SAI calls according to the information in APPL_DB given by upper layers.
In the case of SAI failures, the orchagent gets the failure status via the feedback mechanism in synchronous mode.
Based on the failure information, the failure handling functions in the orchagent make the first attempt to address the failure.
An ERROR_DB is also introduced to support escalation to upper layers.
In the scenario where the orchagent is unable to resolve the problem, the failure handling functions would escalate the failure to the upper layers by pushing the failure into the ERROR_DB.

<img src="Framework.png">

#### 2.3.1 Failure handling functions

To support a failure handling logic in general while also allow each orch to have its specific logic, we include the following virtual functions in Orch

1. `virtual task_process_status handleSaiCreateStatus(sai_api_t api, sai_status_t status, void *context = nullptr)`
2. `virtual task_process_status handleSaiSetStatus(sai_api_t api, sai_status_t status, void *context = nullptr)`
3. `virtual task_process_status handleSaiRemoveStatus(sai_api_t api, sai_status_t status, void *context = nullptr)`
4. `virtual task_process_status handleSaiGetStatus(sai_api_t api, sai_status_t status, void *context = nullptr)`

