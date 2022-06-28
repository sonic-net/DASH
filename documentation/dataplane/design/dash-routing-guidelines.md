---
title: Routing guidelines and scenarios
last update: 02/28/2022
---

# Routing guidelines and scenarios

- [Routing guidelines and scenarios](#routing-guidelines-and-scenarios)
  - [Overview](#overview)
    - [Routing](#routing)
    - [Mapping](#mapping)
  - [Routing examples](#routing-examples)
    - [Example route table (basic customer setup)](#example-route-table-basic-customer-setup)
    - [VNET, Mappings, Private Link, Express Route, Internet Examples](#vnet-mappings-private-link-express-route-internet-examples)
  - [SCENARIOS (these build upon each other)](#scenarios-these-build-upon-each-other)
    - [Scenario: VM to VM in the same VNET](#scenario-vm-to-vm-in-the-same-vnet)
    - [Scenario:  Peered VNET using mappings](#scenario--peered-vnet-using-mappings)
    - [Scenario: Direct communication between subnets](#scenario-direct-communication-between-subnets)
    - [Scenario: Filter default route](#scenario-filter-default-route)
    - [Scenario: Trusted versus Untrusted Internet-bound traffic](#scenario-trusted-versus-untrusted-internet-bound-traffic)
    - [Scenario: Set an on premises route to a express route (ExR) PA](#scenario-set-an-on-premises-route-to-a-express-route-exr-pa)
    - [Scenario: Private Endpoints](#scenario-private-endpoints)
    - [Scenario: Private Endpoints plumbed as Route](#scenario-private-endpoints-plumbed-as-route)
    - [Scenario: Intercept Specific Traffic / Exempt a Specific IP/VM](#scenario-intercept-specific-traffic--exempt-a-specific-ipvm)
  - [References](#references)

## Overview

This article is an effort to explain common customer scenarios and configurations, showing the basic steps how to build a **routing table** and how **mappings** may be used to direct traffic.  

It is important to keep in mind that a route is a concept of the ENI/VNIC, not a VNET (i.e. the route table is attached
to ENI/VNIC).  **Routing** and **Mapping** are two different but complementary concepts, specifically:

### Routing

The route table is configured by the customer to provide the desired traffic routing behavior; traffic can also be intercepted or redirected.  
It must be clear that the routing table has the final say in the way the traffic is routed (Longest Prefix Match = wins). Routes can intercept **part** of the
traffic and forward to a next hop for the purpose of filtering.  The order is:  LPM->Route->Mapping.  We ONLY look at mappings, AFTER LPM decides
that a route wins.  The 'routing-type') determines the 'routing action' such as 'direct' or 'appliance' or 'drop' (examples).  Next matches a lookup in the mapping table, which holds an entry CA to PA mapping and proceeds with packet transformation (actions such as encap, or other).

For example, a default route looks like this:
  
0/0 -> Internet (Default)

The following example shows how a customer can override the default entry and route the traffic differently:

- 8.8.0.0/16 -> Internet (SNAT to VIP)
- 0/0 -> Default Hop: 10.1.2.11 (direct to a Firewall in current VNET)

Please notice, a routing table is *attached* to a specific VM DASH DPU in the VNET, not to the VNET itself.  The route is an ENI/VNIC concept, not a VNET one (i.e., a route table is *attached* to ENI/VNIC).  In a VNET a VM DASH DPU functions like a router, to which a routing table is *attached*.  This must be taken into consideration in metering.

![dash-dataplane-routing-table-vm](./images/dash-dataplane-routing-table-vm.svg)

<figcaption><i>Figure 1. Routing tables per VM</i></figcaption><br/>

### Mapping

Mappings for a local VM reside on a VM's host.  
Mapping lookups determine the network provider address (PA) spaces to redirect traffic.  
A mapping is a CA to PA (Customer Address to Provider Address) lookup table, and the parameters that would be required to transform the packet before forwarding to the right interface (for example: Encap determination).   

  `10.3.0.0/16 -> VNET C (Peered) (use mapping)`

Notice that a routing table has a size limit of about 100K while mapping table
has a limit of 2M. Using mappings extends the amount of data
that can be contained in the routing table.  

One of the main objectives of a routing table, more specifically **LPM routing
table**, is to allow the customers to enter static or mapped entries per their
requirements. The LPM routing rules determine the order. The rules can be either
static or can refer to a mapping. But mappings do not control routing, which is
decided via the LPM table.  

- **Static** :  when an entry is created in the table, the exact physical address (PA) is known; there is no mapping (lookup).
- **Mapping** : for a particular entry, the desired behavior is to route to dynamic destination based on mapping, in order to apply
packet transformatoin actions apart from the ones associated with the rest of the traffic.

## Routing examples

This section provides guidelines, along with some examples, for how to build
routing tables statically and/or by using mapping.  It includes the types of entries an LPM routing table may
contain. We'll describe the various entries as we progress with the explanation.

### Example route table (basic customer setup)

```

- 10.1/16 -> VNET A (via mapping lookup)
- 10.1.0/24 -> UDR to transit next hop 10.2.0.5 (ex. intercept this subnet through firewall VM in peered vnet)
- 10.1.0.7/32 -> VNET A (exempt this IP from being intercepted by UDR above and use normal VNET route, as LPM on /32 wins)
- 10.1.0.10/32 -> UDR to transit next hop 10.2.0.5 (ex. customer wants to intercept traffic to this destination and filter it via firewall)
- 10.1.0.11/32 -> This is a Private Endpoint plumbed as /32 route
- 10.1.0.12/32 -> This is another Private Endpoint plumbed as /32 route
- 10.2/16 -> Peered VNET B (via mapping lookup)
- 10.2.0.8/32 -> This is another Private Endpoint in peered vnet plumbed as /32 route
- 50/8 -> Internet (allow this 50/8 traffic to be exempt from transiting the firewall, and allow it to go directly to internet)
- 20.1/16 -> Static Route to on-prem (encap with some GRE key and send to CISCO Express Route device, that later redirects to onprem)
- 20.2/16 -> Static Route to on-prem (encap with some GRE key and send to CISCO Express Route device, that later redirects to onprem)
- 0/0 -> UDR to transit next hop 10.1.0.7 (ex. firewall all traffic going originally through internet via firewall which is in the same vnet)

```

### VNET, Mappings, Private Link, Express Route, Internet Examples

```
VNET: 10.1.0.0/16
- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall)
- Subnet 3: 10.1.3.0/24
- Mappings: . VM 1: 10.1.1.1 (y) . VM 2: 10.1.3.2 . Private Link 1: 10.1.3.3 .
 Private Link 2: 10.1.3.4 . VM 3: 10.1.3.5
 
RouteTable attached to VM 10.1.1.1
- 10.1.0.0/16 -> VNET (use mappings)
- 10.1.3.0/24 -> Hop: 10.1.2.11 Customer Address (CA) -> Provider Address (PA)
  (Firewall in current VNET)
- 10.1.3.0/26 -> Hop: 10.1.2.88 Customer Address (CA) -> Provider Address
  (PA)(Firewall in peered VNET)
- 10.1.3.5/27 -> VNET A (mapping)
- 10.1.3.3/32 -> Private Link Route (Private Link 1)
- 10.2.0.0/16 -> VNET B (Peered) (use mapping)
- 10.2.1.0/24 -> Hop: 10.1.2.11 Hop: 10.1.2.88(CA->PA) (Firewall in peered VNET)
- 10.2.0.0/16 -> VNET B (Peered) (use mappings)
- 10.3.0.0/16 -> VNET C (Peered)  (use mappings)
- 50.3.5.2/32 -> Private Link Route (Private Link 7)
- 50.1.0.0/16 -> Internet
- 50.0.0.0/8 -> Hop: CISCO ER device PA (100.1.2.3, 10.1.2.4), GRE Key: X
- 8.8.0.0/16 -> Internet (SNAT to VIP)
- 0/0 -> Default Hop: 10.1.2.11 (Firewall in current VNET)

```

## SCENARIOS (these build upon each other)

### Scenario: VM to VM in the same VNET

Customers configure routing tables based upon their requirements.  This example shows a single VNET with **direct traffic** between different subnets in the same VNET.  

In this example, if Subnet 1 wants to communicate with Subnet 2, **the direct path would be taken** ✔️  

If VM 1 10.1.1.1 wanted to communicate with VM 2 10.1.3.2 it would use a mapping in the mapping table to translate the CA to PA, and apply further packet transformation 🟢

Customer VNET A: 10.1.0.0/16 divided into subnets (below)

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24
- Subnet 3: 10.1.3.0/24

**Mappings**: 
- *VM 1: 10.1.1.1 - 🟢
- *VM 2: 10.1.3.2
- *Private Link 1: 10.1.3.3
- *Private Link 2: 10.1.3.4
- *VM 3: 10.1.3.5

Route Table - attached to VM 10.1.1.1

- 10.1.0.0/16 -> define VNET space as a prefix  - take this path ✔️
- 10.2.0.0/16 -> a peered VNET B
- 10.3.0.0/16 -> a peered VNET C
- 10.1.3.5/32 -> VNET A (mapping) **(CA -> PA) then apply action to encap (ex: NVGRE) to destination VM**
- 0/0 -> Default (to Internet for example, or Customer-owned VIPs, no action, no encap)



### Scenario:  Peered VNET using mappings

<!-- Will be good to maybe have visual diagram of 1 vnet peered to B and C and specify that VNET A is local vnet, and B and C are peered. -->

Route Table - attached to VM x.x.x.x 

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 0/0 -> Default (Internet)

### Scenario: Direct communication between subnets

This scenario shows communication between subnets with mapping and addition of next hop (such as a firewall)

In the following example the customer filter traffic from subnet 1 to subnet 3 through a firewall on subnet 2.

> [!NOTE]
> Bold and the checkmark indicate changes from the example above.

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) **Customer places firewall** :heavy_check_mark:
- Subnet 3: 10.1.3.0/24
  
<!-- Needs diagram -->

**Add firewall hop to the routes**

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/24 -> Next Hop: (10.1.2.11) - **Customer adds subnet 3 next hop through firewall in current VNET** :heavy_check_mark:
- 10.1.3.0/26 -> Next Hop: (10.2.0.88) - **Another example. Firewall next hop in a peered VNET** :heavy_check_mark:
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 0/0 -> Default (Internet)

Ex. traffic going to 10.1.3.5, or any other address in 10.1.3.0/24.. Is intercepted and encapped and goes thru 10.1.2.11, and this 10.1.2.11 is from VNET A

### Scenario: Filter default route

The example shows how to route all Internet destined traffic through a firewall

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (Subnet contains a customer placed VM/NVA: 10.1.2.11) ✔️) 
- Subnet 3: 10.1.3.0/24

**Add firewall hop to the routes**

This scenario shows communication between subnets with firewall (NVA) next hop route entry.

RouteTable attached to VM 10.1.1.1

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/26 -> Next Hop: (10.1.2.11)
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 0/0 -> Next Hop: 10.1.2.11 **Customer overrides default route with a next hop of 10.1.2.11 (firewall in VNET)** :heavy_check_mark:

### Scenario: Trusted versus Untrusted Internet-bound traffic

This scenario shows how to route directly **trusted** Internet-bound traffic while routing **untrusted** trafffic to a firewall

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) ✔️
- Subnet 3: 10.1.3.0/24

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/26 -> Next Hop: (10.1.2.11) 
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 8.8.0.0/16 -> Internet traffic exits directly **For trusted traffic can be SNAT to VIP** :heavy_check_mark:
- 0/0 -> Next Hop: 10.1.2.11 **For untrusted traffic** :heavy_check_mark:

### Scenario: Set an on premises route to a express route (ExR) PA

<!-- Needs diagram from MSDN, use address below as On-Prem address in visual -->

The example shows how to set an on premises route to an express route (ER) for a
specific provider address (PA).

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) 
- Subnet 3: 10.1.3.0/24

**On-Prem: 50.0.0.0/8 - Customer On Prem space**

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/24 -> Next Hop in VNET A: 10.1.2.11 **(CA -> PA, traffic encapped w/PA and VXLAN key of VNET A) - next hop here from previous example** :heavy_check_mark:
- 10.1.3.0/26 -> Next Hop in VNET B: 10.2.0.88 **(CA -> PA) - firewall in peered VNET B** :heavy_check_mark:
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 50.1.0.0/16 -> Internet **Used for intercept of other traffic** :heavy_check_mark:
- 50.0.0.0/8 -> Next Hop: **ER device pair PAs (100.1.2.3, 100.1.2.4) 2 endpoints, GRE Key: X** :heavy_check_mark:
- 8.8.0.0/16 -> Internet (for Trusted traffic) - (can be SNAT to VIP)
- 0/0 -> Next Hop: 10.1.2.11 for Untrusted traffic

### Scenario: Private Endpoints

<!-- Needs diagram -->

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) Customer places FW here :heavy_check_mark:
- Subnet 3: 10.1.3.0/24
- Mappings:     **Customer adds some VMs below, Private Links, etc...in the VNET** :heavy_check_mark:
- VM 1: 10.1.1.1     **In subnet 1** ✔️
- VM 2: 10.1.3.2     **In subnet 3** ✔️
- Private Link 1: 10.1.3.3     **In subnet 3** ✔️
- Private Link 2: 10.1.3.4     **Private Links are Mappings, but we also support Customers plumbing them as a Route** :heavy_check_mark:
- VM 3: 10.1.3.5     **In subnet 3** ✔️

On-Prem: 50.0.0.0/8 - Customer On Prem space

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/24 -> Next Hop: 10.1.2.11 (CA -> PA) - next hop here from previous example
- 10.1.3.0/26 -> Next Hop: 10.2.0.88 (CA -> PA) - firewall in peered VNET **From LPM perspective, this route is taken** :heavy_check_mark:
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 50.1.0.0/16 -> Internet Used for intercept of other traffic
- 50.0.0.0/8 -> Next Hop: ER device PA (100.1.2.3, 100.1.2.4) 2 endpoints, GRE Key: X
- 8.8.0.0/16 -> Internet (for Trusted traffic) - (can be SNAT to VIP)
- 0/0 -> Next Hop: 10.1.2.11 for Untrusted traffic

### Scenario: Private Endpoints plumbed as Route

Customer can also send Private Link directly as a route

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) Customer places FW here :heavy_check_mark:
- Subnet 3: 10.1.3.0/24
- Mappings:     **Customer adds some VMs below, Private Links, etc...in the VNET** :heavy_check_mark:
- VM 1: 10.1.1.1     In subnet 1
- VM 2: 10.1.3.2     In subnet 3
- Private Link 1: 10.1.3.3     **From Route Table below, specific /32 route** ✔️
- Private Link 2: 10.1.3.4     Private Links are Mappings, but we also support Customers plumbing them as a Route
- VM 3: 10.1.3.5     In subnet 3

On-Prem: 50.0.0.0/8 - Customer On Prem space

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings)
- 10.1.3.0/24 -> Next Hop: 10.1.2.11 (CA -> PA) - next hop here from previous example
- 10.1.3.0/26 -> Next Hop: 10.2.0.88 (CA -> PA) - firewall in peered VNET
- 10.1.3.3/32 -> **Private Link Route (should 'win' b/c it is part of a route, not part of a mapping** ✔️
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 50.1.0.0/16 -> Internet Used for intercept of other traffic
- 50.0.0.0/8 -> Next Hop: ER device PA (100.1.2.3, 100.1.2.4) 2 endpoints, GRE Key: X
- 8.8.0.0/16 -> Internet (for Trusted traffic) - (can be SNAT to VIP)
- 0/0 -> Next Hop: 10.1.2.11 for Untrusted traffic

### Scenario: Intercept Specific Traffic / Exempt a Specific IP/VM

Customer wants to exempt 1 IP or perhaps a VNET.  Example:  A customer routing through a FW by default (for traffic inspection, or security policies), however would like to direct more specific routes/subnets to exit directly.  

**Mappings**

VNET A: 10.1.0.0/16

- Subnet 1: 10.1.1.0/24
- Subnet 2: 10.1.2.0/24  (VM/NVA: 10.1.2.11 - Firewall) Customer places FW here :heavy_check_mark:
- Subnet 3: 10.1.3.0/24
- Mappings:     **Customer adds some VMs below, Private Links, etc...in the VNET**
- VM 1: 10.1.1.1     In subnet 1
- VM 2: 10.1.3.2     In subnet 3
- Private Link 1: 10.1.3.3
- Private Link 2: 10.1.3.4
- VM 3: 10.1.3.5     In subnet 3 **This is still here as a Mapping as part of the VNET** ✔️

On-Prem: 50.0.0.0/8 - Customer On Prem space

Route Table attached to VM x.x.x.x

- 10.1.0.0/16 -> VNET A (use mappings) **Default catch-all for prefix**
- 10.1.3.0/24 -> Next Hop: 10.1.2.11 (CA -> PA) - next hop here from previous example
- 10.1.3.0/26 -> Next Hop: 10.2.0.88 (CA -> PA) - firewall in peered VNET
- 10.1.3.5/32 -> **VNET A (mapping) customer wants to exempt this IP to 'go direct'** ✔️
- 10.1.3.3/32 -> Private Link Route
- 10.2.0.0/16 -> VNET B (use mappings)
- 10.3.0.0/16 -> VNET C (use mappings)
- 50.1.0.0/16 -> Internet Used for intercept of other traffic
- 50.0.0.0/8 -> Next Hop: ER device PA (100.1.2.3, 100.1.2.4) 2 endpoints, GRE Key: X
- 8.8.0.0/16 -> Internet (for Trusted traffic) - (can be SNAT to VIP)
- 0/0 -> Next Hop: 10.1.2.11 for Untrusted traffic

Route Table attached to VM **10.1.1.2** **Different ENI using same route table above; the VNET object is shared**
Customer wants to be able to communicate with 10.1.3.5 (via the route table), but **does not** want to intercept any traffic ✔️

- 10.1.0.0/16 -> VNET A (use mappings)

## References

- [What is Azure Virtual Network?](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Virtual network traffic routing](https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview)
- [ExpressRoute routing requirements](https://docs.microsoft.com/en-us/azure/expressroute/expressroute-routing?toc=/azure/virtual-network/toc.json)
