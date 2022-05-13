# Routing, ACL, Mapping Updates
### This information needs a home in documentation somewhere

Configuration updates are mostly customer driven (ACLs, Routes), and should be very rare.

**Routes:**  Alternately, routes (if a customer is connected to On-Prem via ER GW, etc... for example), can be received and updated every 30 seconds.

This amounts for majority of routes per ENI, 10K for IPv4, + 10K for IPv6.  Thee 10K might be more in the future once CISCO supports more routes from On-Prem.

The entire goal state will initially be fully plumbed once when the ENI lands.  For example, it's possible that every 10 seconds we will change (let's say) 100 mappings per VNET.  It depends upon whether the VNET is very large.  
We need to support both (removing single route, but also replacing entire route set).

**Mappings:**  Mapping updates (a single mapping) can be a more frequent occurance.  A customer can start/stop the VM, add remove Private Links, VMs can service heal, and the like...
Mappings can be either, meaning an entire mapping set per VNET, or per each mapping.  

**ACLs:** ACLs - entire policy per group; need to be applied in atomic way.  The ACL group is sent/updated together, and needs to be replaces in atomic way.

Atomic means everything at the same time, like if we have 100 rules, those rules work TOGETHER as set of rules

new ACL policy must be applied as entire set of rules, like a batch, so the new policy must be applied in a way that all those rules gets replaced together, in atomic way, like 1

If they are replaced one by one, then policy will be in transient state, and rules will not work as customer intended, as customer never intended transient state where some rules are there but some are different




