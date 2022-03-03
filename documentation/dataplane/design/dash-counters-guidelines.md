---
title: Counters guidelines and scenarios
last update: 03/03/2022
---

# Counters guidelines and scenarios

This article is an effort to explain common customer scenarios and
configurations, showing the basic steps how to build network traffic counters. 

## Overview

> [!NOTE] When and how metering is done depends on the way routing is done that
> is statically or via mapping,

The following applies:

- We need a Counter on both the Route and the Mapping.
- The idea is to treat private endpoints as customer addresses (CA).
- We are only evaluating private links mappings not using explicit routes.
- Private endpoints mappings take precedence over everything.
- If the VMs in a peer VNET have meters, they are going to be used because they
  are attached to the ultimate destination.
- Because the mapping of the (metering) object is at VNET level, not at VNIC
  level, the metering object means different things depending where the source
  came from.

The question is do you need to specify for each ENI every possible destination
for correct application of the metering (counters)?  
The answer is because VNET is global (there is no VNET for each ENI), those
counters will be global. Otherwise, we have to copy the entire VNET object for
each ENI that would be impossible. But you can get the counters meaning from the
VNET context.  

Different ENI in peered VNET need to have context on the ENI counter for every
other NIC. Mapping and Peered VNET and statically isolate each value (right now
we rely on the fact that the mappings are not hit by different ENIs).  
At time of programming of ENI, we now we have to know..?

## References

- [What is Azure Virtual
  Network?](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Virtual network traffic
  routing](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview)
- [ExpressRoute routing
  requirements](https://docs.microsoft.com/en-us/azure/expressroute/expressroute-routing?toc=/azure/virtual-network/toc.json)
