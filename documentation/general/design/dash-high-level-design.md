---
title: SONiC-DASH High Level Design
description: Describe SONiC-DASH High Level Design
last update: 02/08/2022
---

[ [ << Back to parent directory](../README.md) ]

[ [ << Back to DASH top-level Documents](../../README.md#contents) ]


**Table of Contents**

- [SONiC-DASH High Level Design (WIP)](#sonic-dash-high-level-design-wip)
  - [Overview](#overview)
    - [Objectives](#objectives)
  - [Architecture](#architecture)
    - [SDN controller](#sdn-controller)
      - [SDN and DPU High-Availability (HA)](#sdn-and-dpu-high-availability-ha)
    - [Traditional SONiC Application Containers](#traditional-sonic-application-containers)
    - [DASH container](#dash-container)
      - [Multiple DPUs device](#multiple-dpus-device)
    - [Switch State Service (SWSS)](#switch-state-service-swss)
    - [Switch Abstraction Interface (SAI) DASH](#switch-abstraction-interface-sai-dash)
    - [ASIC Drivers](#asic-drivers)
    - [DASH capable ASICs](#dash-capable-asics)
  - [Detailed architectures](#detailed-architectures)
    - [DASH NOS single DPU on NIC](#dash-nos-single-dpu-on-nic)
    - [DASH appliance architecture](#dash-appliance-architecture)
      - [High Level Architecture](#high-level-architecture)
      - [Low level architecture](#low-level-architecture)
    - [DASH smart switch architecture](#dash-smart-switch-architecture)
      - [High level architecture](#high-level-architecture-1)
      - [Low level architecture](#low-level-architecture-1)
  - [DASH container state interactions representation](#dash-container-state-interactions-representation)
  - [DASH deployment options](#dash-deployment-options)
  - [Repositories](#repositories)
  - [References](#references)


# SONiC-DASH High Level Design (WIP)

> [!WARNING] 
> **This document is work in progress**

This document describes the **SONiC Disaggregated API for SONiC Hosts** (SONiC-DASH) high level design and architecture. SONiC-DASH (DASH for short) is an open source project that will deliver enterprise network performance to critical cloud applications. The ultimate goal is that DASH will have the same success as [SONiC](https://github.com/Azure/SONiC) for switches and also be widely adopted as a major **Open NOS for Programmable Hardware Technologies**, including [SmartNICs](https://blogs.nvidia.com/blog/2021/10/29/what-is-a-smartnic/), to supercharge a variety of cloud and enterprise applications.

## Overview 

DASH extends SONiC APIs and a comprehensive set of object models that initially describe Microsoft Azure’s networking services for the cloud. The project enlists cloud and enterprise providers to further extend DASH to meet their specific needs.

See the project [Scenario Milestone and Scoping](SDN-Features-Packet-Transforms.md#scenario-milestone-and-scoping). 

### Objectives

The overall objective is to **optimize network SMART Programmable Technologies performance**, and **leverage commodity hardware technology** to achieve **10x or even 100x stateful connection performance**.
- With the help of network hardware technology suppliers, create an open forum that capitalizes on the use of **programmable networking hardware** including SmartNICs, SmartToRs, SmartAppliances. 
- Optimize **stateful L4** performance and connection scale by 10x or even 100x when compared to implementations that make extensive use of a generic software stack approach that compromises performance for flexibility.  This flexibility was needed early on, whereas the cloud is maturing and is ready for a further optimized approach.  As host networking in the cloud is performed at L4, the resulting performance improvements should be truly significant.
- Microsoft Azure will integrate and deploy DASH solutions to ensure that scale, monitoring, reliability, availability and constant innovation are proven and hardened. Other enterprise and cloud providers may deploy DASH as well, and we hope to hear similar feedback and contributions as we move forward.  It should be noted that innovations for **in-service software upgrades** (ISSU) and **high availability** (HA) are key tenets of the DASH charter.   

> [!NOTE] 
> **The figures shown are a work in progress**

## Architecture

SONiC is structured into various containers that communicate through multiple logical databases via a shared Redis instance. DASH will make use of the SONiC infrastructure as shown in the figure below. The following is a high level view of DASH architecture. DASH builds upon the traditional SONiC Architecture, which is documented in the SONiC Wiki under [Sonic System Architecture](https://github.com/Azure/SONiC/wiki/Architecture#sonic-system-architecture). The following descriptions assume familiarity with the SONiC architecture and will describe DASH as incremental changes relative to traditional SONiC. Notice that DASH adds a new SDN control plane via **gNMI** with the **DASH container**. 

**DASH software stack**

![dash-layered-architecture](images/dash-layered-architecture.svg)
### SDN controller

The SDN controller is **primarily responsible for controlling the DASH overlay services**, while the traditional SONiC application containers are used to manage the underlay (L3 routing) and hardware platform. Both the DASH container and the traditional SONiC application containers sit atop the Switch State services (SWSS) layer, and manipulate the Redis application-layer DBs; these in turn are translated into SAI dataplane obects via the normal SONiC orchestration daemons inside SWSS.

The SDN controller controls the overlay built on top of the physical layer of the infrastructure.  From the point of view of the SDN control plane, when a customer creates an operation, for example a VNET creation, from the cloud portal, the controller allocates the resources, placement management, capacity, etc. via the  **NorthBound interface APIs**.

#### SDN and DPU High-Availability (HA)

For **High Availability** (HA), the SDN controller selects the pair of cards and configures them identically.  The only requirement on the card from the HA perspective is for the cards to setup a channel between themselves for flow synchronization.  The synchronization mechanism is left for technology suppliers to define and implement. For more information, see [High Availability and Scale]() document.   

### Traditional SONiC Application Containers

 In the figure above, the "SONiC Containers" box comprises the normal collection of optional/customizable application daemons and northbound interfaces, which provide BGP, LLDP, SNMP, etc, etc. These are described thoroughly in the [Sonic System Architecture](https://github.com/Azure/SONiC/wiki/Architecture#sonic-system-architecture) wiki and reproduced in diagram form under the [Detailed Architectures](#detailed-architectures) section of this document.
 ### DASH container
 
The SDN controller communicates with a DASH device through a **[gNMI](https://github.com/Azure/DASH/wiki/Glossary#gnmi) endpoint** served by a new DASH SDN agent **running inside a new SONiC DASH container**.  

In summary:
- The DASH container translates SDN configuration modeled in gNMI into **SONiC DB** objects. The gNMI schema is closely related to the DASH DB schema so in effect, the gNMI server is a a thin RPC shim layer to the DB.
- The **SONiC orchagent** inside the Switch State Service (SWSS) Container will be enhanced to transform and translate these objects into **SAI_DB objects**, including the new **DASH-specific SAI objects**.  
- An **enhanced syncd** will then configure the dataplane using the **technology supplier-specific SAI library**.

A **gNMI schema** will manage the following DASH services: 
- Elastic Network Interface (ENI)
- Access Control Lists (ACLs) 
- Routing and mappings
- Encapsulations 
- Other  

See [**TODO**] for DASH gNMI schema.

#### Multiple DPUs device

In the case of a multiple DPUs device the following applies:

- Each DPU provides a gNMI endpoint for SDN controller through a unique IP address. 
- An appliance or smart switch containing multiple DPUs therefore contains multiple gNMI endpoints for SDN controller, and the controller treats each DPU as a separate entity. 
- To conserve IPv4 addresses, such an appliance or switch _might_ contain a proxy (NAT) function to map a single IP address:port combination into multiple DPU endpoints with unique IPv4 addresses.  
- No complex logic will run on the switches (switches do not have a top-level view of other/neighboring switches in the infrastructure). 


### Switch State Service (SWSS)
The SWSS container comprises many daemons which operate on conceptual SONIC config objects across several databases. DASH affects the following daemons, as follows:
* `orchagent`, which translates `XX_DB` objects (application and state DBs - **TODO** - identify) into `ASIC_DB` objects, must be enhanced to manage new DASH overlay objects, such as ACL1,2,3 rules, ENI mappings, etc. The `orchagent` has to manage both representations of SONiC objects (`XX_DB` and `ASIC_DB`) and translates between them bidirectionally as required.
* `syncd`, which translates `ASIC_DB` conceptual objects into technology supplier SAI library API calls, must likewise be enhanced to handle new DASH SAI objects.

### Switch Abstraction Interface (SAI) DASH

The Switch Abstraction Interface (SAI) is a common API that is supported by many switch ASIC technology suppliers. SONiC uses SAI to program the ASIC. This enables SONiC to work across multiple ASIC platforms naturally. DASH uses a combination of traditional SAI headers and new DASH pipeline-specific headers. Technology suppliers must implement this interface for their DASH devices. This is the primary integration point of DASH devices and the SONiC stack. It will be rigorously tested for performance and conformance. See [DASH Testing documentation](https://github.com/Azure/DASH/tree/main/test).

SAI "schema" are represented as fixed c-language header files and derived metadata header files. The underlay and overlay schema have different origins:
* Traditional SAI headers are defined in the [OCP SAI project repo](https://github.com/opencomputeproject/SAI/tree/master/inc).These are hand-generated and maintained. DASH uses a subset of these to manage underlay functions, e.g. device management, Layer 3 routing and so forth.
* DASH SAI "overlay" objects are derived from a [P4 Behavioral Model](https://github.com/Azure/DASH/tree/main/sirius-pipeline). A script reads the P4 model and generates SAI header files.

DASH uses an **enhanced syncd** to configure the dataplane using the technology supplier-specific SAI library.

### ASIC Drivers
The term "ASIC Drivers" is borrowed from traditional SONiC and SAI, where a datacenter switch was implemented almost entirely inside an ASIC (or multiple ASICs). These devices are programmed using a technology supplier Software Development Kit (SDK) which includes device drivers, kernel modules, etc.

A contemporary DASH "SmartNIC" may consist of many complex hardware components including multi-core System On A Chip (SoC) ASICs, and the associated software. For simplicity, the software for such systems which interfaces to the SAI layer is collectively called the "ASIC driver." More importantly, the technology supplier SAI library will hide all details and present a uniform interface.

### DASH capable ASICs
These comprise the main dataplane engines and are the core of what are variously called SmartNICs, DPUs, IPUs, NPUS, etc. The actual cores may be ASICs, SoCs, FPGAs, or some other high-density, performant hardware.

## Detailed architectures
### DASH NOS single DPU on NIC

![dash-single-dpu-architecture](images/dash-single-dpu-architecture.svg)

The figure above highlights the primary SONiC and DASH software stack components and relationships, and will appear as variations within the DASH configurations described below.

### DASH appliance architecture
A DASH "appliance" contains multiple (e.g., six) DASH NIC/DPU/Other devices installed as PCIe adaptors in a chassis. This chassis provides power and cooling with options for manageability/servicing/supportability (as needed), and other capability through PCIe bus, but no large-scale data path traversal of PCIe is needed. 
Each NIC/DPU runs its own SONiC instance in such a way that it could also potentially operate as a standalone component once programed through the control plane given the chassis power / cooling / management.  
The PCIe bus *can* be used to bootstrap/upgrade cards and perform some platform management functions but is not a participant in steady-state datacenter traffic. 
Each DASH NIC/DPU Will run a version of SONiC that runs its own gNMI endpoint for SDN Control.  This endpoint is reachable in band through the "front-panel" DPU traffic ports via L3 routing. In other words, the SDN controller can reach the DPU management endpoints over the ToR-to-DPU fabric links. 
In some cases, DPUs might provide separate management Ethernet ports, or PCIe netdevs which can be used for control purposes, in accordance with deployment and security needs.

#### High Level Architecture

![dash-high-level-appliance](images/dash-high-level-appliance.svg)

#### Low level architecture
![dash-appliance-architecture](images/dash-appliance-architecture.svg)

### DASH smart switch architecture
A DASH "Smart Switch" is a merging of a datacenter switch and one or more DPUs into an integrated device. The "front-panel" network interfaces of the DPU(s) are wired directly into the switching fabric instead of being presented externally, saving cabling, electronics, space and power. There can also be some consolidation of software stacks, for example see [SONiC Multi-ASIC](https://github.com/Azure/SONiC/blob/master/doc/multi_asic/SONiC_multi_asic_hld.md) for how this is accomplished in standard SONiC multi-ASIC devices.
#### High level architecture

![dash-high-level-smart-switch](images/dash-high-level-smart-switch.svg)

#### Low level architecture

![dash-smart-switch-architecture](images/dash-smart-switch-architecture.svg)

## DASH container state interactions representation

The system architecture for SONiC-DASH relies upon the [SONiC system architecture](https://github.com/Azure/SONiC/wiki/Architecture), as shown in the following figure.

![dash-high-level-design](./images/dash-high-level-design.svg)
 
This architecture introduces the following DASH modifications:

1. A *new docker container* in the user space named **dash container** to create the functional component for DASH.

1. In the **sync-d container**, the **sai api DASH** (as opposed to *sai api* in the original SONiC architecture).  

The *DPU/IPU/SmartNic* hardware will run a separate instance of SONiC-DASH on the hardware.  

The component interactions will be executed as a new user space container implementation; relying on the existing SONiC infrastructure and components to interact as they normally would.  

The functionality of the new *dash container* in the user space is to receive content from the Software Defined Networking (SDN) controller to control setup for the overlay configurations. DASH receives the objects, translates them with a **gNMI agent**, provides them to the *SONiC OrchAgent* for further translation onto the dataplane via the **SAI database**. 

Note the following:

- **DASH API** shall be exposed as gNMI interface as part of the SONiC gNMI container. 
- **DASH clients** shall configure SONiC via gRPC get/set calls. 
- **gNMI container** has the config backend to translate/write  DASH objects to CONFDB and/or APPDB.
- **SWSS** (Underlay) for DASH shall have a small initialization and shall support a defined set of SAI APIs.
- **DashOrch** (DASH orchestration agent) (Overlay) in the SWSS container subscribes to the DB objects programmed by the DASH agent. These objects are not expected to be programmed to kernel, so orchestration agent writes to ASICDB for the DASH technology provider SAI implementation to finally program the DPU. The DASH orchestration agent shall write the state of each tables to STATEDB used by the applications to fetch the programmed status of DASH configured objects. 

> [!NOTE] 
> @lihuay @lguohan @prsunny - would you review and/or improve this write-up?

## DASH deployment options

The following figure is a simplified representation of DASH deployment in a datacenter. 

![dash-simplified-physical-deployment-example](images/dash-simplified-physical-deployment-example.svg) 

## Repositories

- [SONiC](https://github.com/Azure/SONiC)
- [SAI Thrift PR](https://github.com/opencomputeproject/SAI/pull/1325)
- [P4](https://opennetworking.org/p4) and [P4 working group](https://p4.org/working-groups)
- [PINS](opennetworking.org/pins)
- [PNA Consortium Spec](https://p4.org/p4-spec/docs/PNA-v0.5.0.html)
- [IPDK](https://ipdk.io/) and [IPDK GitHub](https://github.com/ipdk-io/ipdk-io.github.io)
- [bmv2 - behavioral model v2](https://github.com/p4lang/behavioral-model)
- [DPDK](https://www.dpdk.org)


## References

- [Glossary](https://github.com/Azure/DASH/wiki/Glossary)
- [SAI](../SAI)
- [Test](../test)
- [SDN Features Packet Transforms](SDN-Features-Packet-Transforms.md)
- [Load Balancer](Load%20Balancer_v3.md)
- [Program Scale Testing Requirements - Draft](Program%20Scale%20Testing%20Requirements%20-%20Draft.md)
