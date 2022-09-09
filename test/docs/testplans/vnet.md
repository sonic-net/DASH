# Table of content

1. [Objectives](#objectives)
2. [Requirements](#requirements)
3. [Automation](#automation)
4. [Test Suites](#test-suites)
    - [Outbound VNET routing](#outbound-vnet-routing)
    - [Inbound VNET routing](#inbound-vnet-routing)
    - [Integration](#integration)
    - [Negative](#negative)
    - [Scaling & Performance](#scaling--performance)
    - [To clarify / Future](#to-clarify--future)

---

# Objectives

The VNET-to-VNET scenario is the starting point to design, implement and test the core DASH mechanisms in VM to VM communication in VNET, using an Appliance for rules and routing offload.

The scenario allows the following:
- Route/LPM support
- Underlay IPv4 and IPv6
- Stateful ACL support
- TCP state tracking on flows
- Telemetry and Monitoring

## Requirements

### Scale
| Item |	Expected value
|---|---
| VNETs | 1024
| ENI per card | 64
| Routes per ENI | 100k (**to clarify** in some md docs it is 200k)
| NSGs per ENI | 6
| ACLs per ENI | 6x100K prefixes
| ACLs per ENI | 6x10K SRC/DST ports
| CA-PA Mappings | 10M
| Active Connections/ENI | 1M (Bidirectional)

### Performance
| Item |	Expected value
|---|---
| CPS per card | 4M+
| Flows per ENI | 1M
| Flows per card | 16M per 200G


### Other

1. Bulk update of LPM and CA-PA Mapping tables.
1. Mapping updates can occur as much as 100 mappings/sec
1. ACL operations (rules adding/deleting) per group for a stage must be handled atomically.
1. Support ability to get all ACL rules/groups based on guid.
1. During VNET or ENI delete, implementation must support ability to delete all mappings or routes in a single API call.
1. Add and Delete APIs are idempotent.
1. During a delete operation, if there is a dependency, implementation shall return error and shall not perform any force-deletions or delete dependencies implicitly.
1. During a bulk operation, if any part/subset of API fails, implementation shall return error for the entire API.
1. Implementation must have flexible memory allocation for ENI and not reserve max scale during initial create (e.g 100k routes). This is to allow oversubscription.
1. Implementation must not have silent failures for APIs.

More details may be found in [DASH SONiC HLD](https://github.com/Azure/DASH/blob/main/documentation/general/design/dash-sonic-hld.md#15-design-considerations).


# Automation

Test cases are automated using SAI PTF test framework, except scale and performance tests.

# Test suites

**NOTE**: Each test has to send multiple traffic types:
- Traffic that matches applied configuration (positive case)
- Traffic that doesn't match applied configuration for each applied attribute (negative case).

### **Outbound VNET routing**
| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | Route action ROUTE_VNET | -
| 2 | Route action ROUTE_VNET_DIRECT | Vnet2VnetInboundTest.<br>Vnet2VnetOutboundRouteVnetDirectTest
| 3 | Route action ROUTE_DIRECT | Vnet2VnetOutboundTest.<br>Vnet2VnetOutboundRouteDirectTest
| 4 | dst_vnet_id True/False in OUTBOUND_CA_TO_PA_ENTRY | -
| 5 | Use same CA prefixes in different outbound routing tables (different ENIs) | -
| 6 | Use multiple overlapping routing prefixes in the same outbound routing table. | -
| 7 | Use same prefixes in CA and PA networks. | -

Original table [link](https://github.com/Azure/DASH/blob/main/documentation/general/design/sdn-features-packet-transforms.md#routing-routes-and-route-action).

### **Inbound VNET routing**

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | VNET2VNET routing with PA validation entry PERMIT.<br>SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE<br>SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT| Vnet2VnetInboundTest.<br>vnet2VnetInboundPaValidatePermitTest
| 2 | Direction lookup DENY action | Vnet2VnetInboundTest.<br/>vnet2VnetInboundDenyVniTest
| 3 | Drop if CA DMAC does not match | Vnet2VnetInboundTest.<br/>vnet2VnetInboundInvalidEniMacTest
| 4 | Drop if PA SIP does not match on PA validation | Vnet2VnetInboundTest.<br/>vnet2VnetInboundInvalidPaSrcIpTest
| 5 | VNET2VNET routing without PA validation entry<br>SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP | -


### **Integration**

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 |Multiple inbound and outbound configurations at the same time. Send multiple allowed and forbidden traffic types. | -
| 2 |Send non VXLAN traffic. (**to clarify** underlay routing?) | VnetRouteTest
| 3 |Use multiple VIPs | -

### **Negative**

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | Traffic with invalid VIP (Inbound and Outbound) | -
| 2 | Traffic with valid VNI but no match to any ENI MAC | -
| 3 | Invalid configurations:<br>- Multiple MACs for same ENI<br>- All different VNIs in ENI, direction lookup, vnet configuration.<br>- Add same VNI for different direction lookup entries. | -

### **Scaling & Performance**

To be defined.


### **To clarify / Future**

1. What is relation between vm_vni and vnet_id in ENI create?
1. The lookup table is per ENI, but could be Global, or multiple Global lookup tables per ENIs. How to configure global lookup? Multiple lookups?
1. In Encap and Decap rules we have:
    - static rule
    - based on mapping lookup
    - inner packet SRC/DEST IP calculated based on part of outer packet SRC/DEST IP<br>
Question: What is static rule nad calculated values?
1. How to test - Inbound (priority) route rules processing:
    - Most Outer Source IP Prefix
    - Most Outer Destination IP Prefix
    - VXLAN/GRE key
1. Need examples: Transpositions. 
    - Direct traffic – pass thru with static SNAT/DNAT (IP, IP+Port)
    - Packet upcasting (IPv4 -> IPv6 packet transformation)
    - Packet downcasting (IPv6 -> IPv4 packet transformation)
1. Need example: Up to 3 level of routing transforms (example: decap + decap + transpose).
1. LB on outbound VNET scenario (different PAs)
1. TODO: Example: Lookup between CA (inside Cx own VNET) and PA (Provider Address) using lookup table (overwrite destination IP and MAC before encap)