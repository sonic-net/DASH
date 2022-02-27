---
title: Routing guidelines
last update: 02/28/2022
---

# Routing guidelines

This article explains the basic steps to build a **routing table** and how to
use **mappings** during the process.  
It is important to notice from the get go, **routing** and **mapping** are two
different but complementary concepts, specifically:

1. **Routing**. It is used by the customer to configure the way the traffic must
be routed. It must be clear that routing table has the last say in the way the
traffic is routed. For example, by defaut usually this entry applies:

    `0/0 -> Internet (Default)`

    But the customer can override the entry and route the traffic as follows:

    `8.8.0.0/16 -> Internet (SNAT to VIP)`

    `0/0 -> Default Hop: 10.1.2.11 (Firewall in current VNET)`

1. **Mapping**. It allows to relate the customer’s defined routing to the
   network physical space that is transparent to the customer . In other words,
   mapping allows to know what is the **physical address** (PA) for a specific
   **customer address** (CA) and if it requires different encap, etc.
1. On the other hand, we want to be able to insert in the routing table
   any entry with a specific mapping, for example:  

    `10.3.0.0/16 -> VNET C (Peered) (use mapping)`

Notice that a routing table has a size limit of about 100 K while mapping has a
limit of 1 M. Using mapping allows you to extendd the amount of data that can be
contained in a routing table.

One of the main objectives of a routing table, more specifically **LPM
routing table**, is to allow the customers to enter static or mapped
entries the way they see fit. The LPM routing rules determine the order. 
The rules can be either static or can refer to mapping. But mappings does not 
control routing which is done via the LPM table.  

- **Static** means that when you create an entry into the table, you know exactly the physical address (PA). 
  Here there is no mapping (lookup).
- **Mapping** means that for that particular entry, you want to intercept the traffic and exempt it from the standard routing. 
Instead, you want to apply different actions than the ones associated with the rest of the traffic. 
