---
title: SONiC-DASH High Level Design
description: Describe SONiC-DASH High Level Design
last update: 01/13/2022
---

# SONiC-DASH High Level Design (WIP)

> [!WARNING] 
> **This document is work in progress**

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Architecture](#architecture)
- [High-Level Design](#high-level-design)
- [Repositories](#repositories)
- [Configuration and management](#configuration-and-management)
- [Restrictions / Limitations](#restrictions--limitations)
- [Glossary](https://github.com/Azure/DASH/wiki/Glossary)
- [References](#supplementary-documents)


## Overview 

This document describes the **SONiC Disaggregated API for SONiC Hosts** (SONiC-DASH) high level design and architecture. SONiC-DASH (DASH for short) is an open source project that will deliver enterprise network performance to critical cloud applications. The ultimate goal is that DASH will have the same success as SONiC for switches and also be widely adopted as a major **Open NOS for Programmable Hardware Technologies**, including [SmartNICs](https://blogs.nvidia.com/blog/2021/10/29/what-is-a-smartnic/), to supercharge a variety of cloud and enterprise applications.
  
DASH extends SONiC APIs and a comprehensive set of object models that initially describe Microsoft Azure’s networking services for the cloud.The project enlists cloud and enterprise providers to further extend DASH to meet their specific needs.

See the project [Scenario Milestone and Scoping](SDN-Features-Packet-Transforms.md#scenario-milestone-and-scoping). 

## Requirements

The overall requirement is to **optimize network SMART Programmable Technologies performance**, and **leverage commodity hardware technology** to achieve **10x or even 100x stateful connection performance**.
- With the help of network hardware vendors, create an open forum that capitalizes on the use of **programmable networking hardware** including SmartNICs, SmartToRs, SmartAppliances. 
- Optimize **stateful L4** performance and connection scale by 10x or even 100x when compared to implementations that make extensive use of software. As host networking in the cloud is performed at L4 the resulting performance improvements should be truly significant.
- Microsoft Azure will integrate and deploy DASH solutions to ensure that scale, monitoring, reliability, availability and constant innovation are proven and hardened. It should be noted that innovations for **in-service software upgrades** (ISSU) and **high availability** (HA) are key tenets of the DASH charter.   


## Architecture

SONiC is structured into various containers that communicate through multiple logical databases via a shared Redis instance. DASH will make use of the SONiC infrastructure as shown in the figure below.

> [!NOTE] 
> **The figures shown are a work in progress**

### DASH NOS single DPU on NIC

![dash-single-dpu-architecture](images/hld/dash-single-dpu-architecture.svg)


### DASH appliance architecture

#### High level architecture

![dash-high-level-appliance](images/hld/dash-high-level-appliance.svg)

#### Low level architecture

![dash-appliance-architecture](images/hld/dash-appliance-architecture.svg)


### DASH smart switch architecture

#### High level architecture

![dash-high-level-smart-switch](images/hld/dash-high-level-smart-switch.svg)

#### Low level architecture

![dash-smart-switch-architecture](images/hld/dash-smart-switch-architecture.svg)


## High-Level Design

**DASH high level design**

The system architecture for SONiC-DASH relies upon the [SONiC system architecture](https://github.com/Azure/SONiC/wiki/Architecture) and adds a *new docker container* in the user space named **dash container** to create the functional component for DASH.  

In the **sync-d container** we will add **sai api DASH** (as opposed to *sai api* in the original SONiC architecture).  

The *DPU/IPU/SmartNic* hardware will run a separate instance of SONiC-DASH on the hardware.  

The component interactions will be executed as a new user space container implementation; relying on the existing SONiC infrastructure and components to interact as they normally would.  

The functionality of the new *dash container* in the user space is to receive content from the Software Defined Networking (SDN) controller to control setup for the overlay configurations. DASH receives the objects, translates them with a **gNMI agent**, provides them to the *SONiC OrchAgent* for further translation onto the dataplane via the **SAI database**. 

> [!NOTE]
> Need a drawing and descriptions of the DASH user space **state interactions** (example such as shown in the figure [LLDP-state interactions](https://github.com/Azure/SONiC/wiki/Architecture).  

@lihuay @lguohan @prsunny - would you review and/or improve this write-up?

## Repositories

TBD


## References

- [Glossary](https://github.com/Azure/DASH/wiki/Glossary)
- [SAI](../SAI)
- [Test](../test)
- [SDN Features Packet Transforms](SDN-Features-Packet-Transforms.md)
- [Load Balancer](Load%20Balancer_v3.md)
- [Program Scale Testing Requirements - Draft](Program%20Scale%20Testing%20Requirements%20-%20Draft.md)