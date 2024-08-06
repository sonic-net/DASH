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
| Item                   |    Expected value    |
|------------------------|:--------------------:|
| VNETs                  |         1024         |
| ENI per card           |          64          |
| Routes per ENI         |         100k         |
| NSGs per ENI           |     5 in + 5 out     |
| ACLs per ENI           |   10x100K prefixes   |
| ACLs per ENI           | 10x10K SRC/DST ports |
| CA-PA Mappings per ENI |         160k         |
| Active Connections/ENI |  1M (Bidirectional)  |

### Performance
| Item                | Expected value |
|---------------------|:--------------:|
| CPS per 200G        |      3.75M     |
| Flows per ENI       |         1M     |
| Flows per 200G card |        64M     |
| Flows per 400G card |       128M     |


### Other

1. Bulk update of LPM and CA-PA Mapping tables.
2. Mapping updates can occur as much as 100 mappings/sec
3. ACL operations (rules adding/deleting) per group for a stage must be handled atomically.
4. Support ability to get all ACL rules/groups based on guid.
5. During VNET or ENI delete, implementation must support ability to delete all mappings or routes in a single API call.
6. Add and Delete APIs are idempotent.
7. During a delete operation, if there is a dependency, implementation shall return error and shall not perform any force-deletions or delete dependencies implicitly.
8. During a bulk operation, if any part/subset of API fails, implementation shall return error for the entire API.
9. Implementation must have flexible memory allocation for ENI and not reserve max scale during initial create (e.g 100k routes). This is to allow oversubscription.
10. Implementation must not have silent failures for APIs.

More details may be found in [DASH SONiC HLD](https://github.com/sonic-net/DASH/blob/main/documentation/general/dash-sonic-hld.md#16-design-considerations).


# Automation

Test cases are automated using SAI PTF test framework, except scale and performance tests.
Scale and performance tests automation approach - to be defined.

# Test suites

**Overall comments**
1. Each scenario should be executed with and without underlay route table configuration:
    - without underlay route table entries - no default or static routes defines. Same rx/tx port are used for traffic send and receive.
    - with underlay route table entries - Add static or default route entries to forward packets from one port to another. Use two different ports for traffic send/receive forwarding verification.
1. Each test should send multiple traffic types:
    - Traffic that matches applied configuration (positive case)
    - Traffic that doesn't match applied configuration for each applied attribute (negative case).
1. Each scenario should be verified in the following combinations:
    - IPv4 underlay + IPv4 overlay
    - IPv4 underlay + IPv6 overlay

### **Outbound VNET routing**
|   #   | Test case purpose | Test Class.Method | Test description |
|:-----:|:----------------|:--------------|:----------|
|  1-2  | Verify route action ROUTE_VNET                                                | `Vnet2VnetOutboundRouteVnetSinglePortTest.`<br/>`vnet2VnetOutboundRoutingTest`<br><br>`Vnet2VnetOutboundRouteVnetTwoPortsTest.`<br/> `vnet2VnetOutboundRoutingTest`                                                                                                                                                                      | Creates single ENI outbound (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET) overlay configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                                                    |
|  3-4  | Verify route action ROUTE_VNET_DIRECT                                         | `Vnet2VnetOutboundRouteVnetDirectSinglePortTest.`<br/>`vnet2VnetOutboundRoutingTest`<br><br>`Vnet2VnetOutboundRouteVnetDirectTwoPortsTest.`<br/> `vnet2VnetOutboundRoutingTest`                                                                                                                                                          | Creates single ENI outbound (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT) overlay configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                                             |
|   5   | Verify route action ROUTE_DIRECT                                              | `Vnet2VnetOutboundRouteDirectTwoPortsTest`<br/> `outboundRouteDirectTest`                                                                                                                                                                                                                                                                | Creates single ENI outbound (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT) overlay configuration with underlay rote configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.                                                                                                                          |
|   6   | (**Clarify no-underlay scenario**)                                            | `Vnet2VnetOutboundRouteDirectSinglePortTest.`<br>`outboundRouteDirectTest`                                                                                                                                                                                                                                                               | Creates single ENI outbound (SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_DIRECT) overlay configuration without underlay route configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.                                                                                                                      |
|   7   | dst_vnet_id True/False in OUTBOUND_CA_TO_PA_ENTRY                             | `Vnet2VnetOutboundDstVnetIdRouteVnetSinglePortTest.`<br/> `vnet2VnetOutboundDstVnetIdTrueTest`<br/> `vnet2VnetOutboundDstVnetIdFalseTest`<br><br>`Vnet2VnetOutboundDstVnetIdRouteVnetTwoPortsTest.`<br/> `vnet2VnetOutboundDstVnetIdTrueTest`<br/> `vnet2VnetOutboundDstVnetIdFalseTest`                                                 | Creates single ENI with two outbound routing entries (with SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET action) and ca_to_pa entries (with use_dst_vnet_vni attribute True and False values).<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route        |
|   8   | Verify route action ROUTE_VNET_DIRECT with CA to PA mappings                  | `Vnet2VnetOutboundDstVnetIdRouteVnetDirectSinglePortTest.`<br/> `vnet2VnetOutboundDstVnetIdTrueTest`<br/> `vnet2VnetOutboundDstVnetIdFalseTest`<br><br>`Vnet2VnetOutboundDstVnetIdRouteVnetDirectTwoPortsTest.`<br/> `vnet2VnetOutboundDstVnetIdTrueTest`<br/> `vnet2VnetOutboundDstVnetIdFalseTest`                                     | Creates single ENI with two outbound routing entries (with SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET_DIRECT action) and ca_to_pa entries (with use_dst_vnet_vni attribute True and False values).<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route |
| 9-10  | Use same CA prefixes in different outbound routing tables (different ENIs)    | `Vnet2VnetOutboundMultipleEniSameIpPrefixSinglePortTest.`<br/> `outboundEni0Test`<br/> `outboundEni1Test`<br/> `outboundEni2Test`<br><br>`Vnet2VnetOutboundMultipleEniSameIpPrefixTwoPortsTest.`<br/> `outboundEni0Test`<br/> `outboundEni1Test`<br/> `outboundEni2Test`                                                                 | Creates three ENI with the same Customer and Physical IP addresses but with different MACs and VNIs.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                                                 |
| 11-12 | Use multiple overlapping routing prefixes in the same outbound routing table. | `Vnet2VnetOutboundSingleEniMultipleIpPrefixSinglePortTest.`<br/> `singleEniToOutboundVm1Test`<br/> `singleEniToOutboundVm2Test`<br/> `singleEniToOutboundVm3Test`<br><br>`Vnet2VnetOutboundSingleEniMultipleIpPrefixTwoPortsTest.`<br/> `singleEniToOutboundVm1Test`<br/> `singleEniToOutboundVm2Test`<br/> `singleEniToOutboundVm3Test` | Creates single ENI with three outbound routing entries with overlapping IP prefixes (ENI 9.0.0.1 <--> 10.5.4.4/8, 10.0.1.2/24, 10.1.1.1/32).<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                         |
| 13-14 | Use same prefixes in CA and PA networks.                                      | `Vnet2VnetOutboundSameCaPaIpPrefixesSinglePortTest.`<br/> `vnet2VnetOutboundRouteVnetTest`<br><br>`Vnet2VnetOutboundSameCaPaIpPrefixesTwoPortsTest.`<br/> `vnet2VnetOutboundRouteVnetTest`                                                                                                                                               | Creates single ENI with the same Customer and Physical IP address outbound configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                                                            |
| 15-16 | Verify VNET2VNET outbound routing with single ENI admin state UP/DOWN         | `Vnet2VnetOutboundEniSetUpDownSinglePortTest.`<br/>`vnet2VnetEniUpTrafficTest`<br>`setEniStateTest`<br>`vnet2VnetEniDownTrafficTest`<br><br>`Vnet2VnetOutboundEniSetUpDownTwoPortsTest.`<br/>`vnet2VnetEniUpTrafficTest`<br>`setEniStateTest`<br>`vnet2VnetEniDownTrafficTest` | Creates single ENI and Outbound routing entry and verifies packet routing during ENI admin state setting UP/DOWN.<br/>1. With underlay route<br/>2. Without underlay route                                                                                                                                                           |
 | 17-18 | Verify VNET2VNET outbound routing with single Outbound route and multiple Ca2Pa entries | `Vnet2VnetSingleOutboundRouteMultipleCa2PaSinglePortTest.`<br/>`vnet2VnetOutboundRoutingTest`<br>`vnet2VnetOutboundNegativeTest`<br><br>`Vnet2VnetSingleOutboundRouteMultipleCa2PaTwoPortsTest.`<br/>`vnet2VnetOutboundRoutingTest`<br>`vnet2VnetOutboundNegativeTest`<br> | Creates single ENI and Outbound routing entry with multiple Ca2Pa entries.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                                                                           |


Original table [link](https://github.com/sonic-net/DASH/blob/main/documentation/general/sdn-features-packet-transforms.md#routing-routes-and-route-action).

### **Inbound VNET routing**

|   #    | Test case purpose | Test Class.Method | Test description |
|:------:|:-----------|:---|:------|
|  1-2   | Verify VNET2VNET routing with PA validation entry PERMIT.<br>SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP_PA_VALIDATE<br>SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT | `Vnet2VnetInboundDecapPaValidateSinglePortTest.`<br>`vnet2VnetInboundRoutingTest`<br><br>`Vnet2VnetInboundDecapPaValidateTwoPortsTest.`<br/> `vnet2VnetInboundRoutingTest` | Creates single ENI inbound (SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP_PA_VALIDATE) overlay configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                   |
|  3-4   | Verify VNET2VNET routing without PA validation entry<br>SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP                                                           | `Vnet2VnetInboundDecapSinglePortTest.`<br/> `vnet2VnetInboundRoutingTest`<br><br>`Vnet2VnetInboundDecapTwoPortsTest.`<br/> `vnet2VnetInboundRoutingTest` | Creates single ENI inbound (SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP) overlay configuration.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                               |
|  5-6   | Verify VNET2VNET routing when multiple Inbound routing entries and multiple PA validate exist with single ENI                                                  | `Vnet2VnetInboundMultiplePaValidatesSingleEniSinglePortTest.`<br/>`vnet2VnetInboundRoutingPositiveTest`<br><br>`Vnet2VnetInboundMultiplePaValidatesSingleEniTwoPortsTest.`<br/> `vnet2VnetInboundRoutingPositiveTest` | Creates single ENI with multiple Inbound routing entries.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                                                      |
|  7-8   | Verify VNET2VNET routing when multiple Inbound routing entries and multiple PA validate exist with multiple ENI                                                | `Vnet2VnetInboundMultiplePaValidatesMultipleEniSinglePortTest.`<br/>`vnet2VnetInboundRoutingPositiveTest`<br><br>`Vnet2VnetInboundMultiplePaValidatesMultipleEniTwoPortsTest.`<br/> `vnet2VnetInboundRoutingPositiveTest` | Creates 2 ENI: 1st ENI with 2 Inbound routes (with and without PA Validate), 2nd ENI with 1 Inbound route and 1 PA validation.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route |
 |  9-10  | Verify VNET2VNET routing when single ENI and single Inbound routing entry exist with multiple PA validation entries                                            | `Vnet2VnetSingleInboundRouteMultiplePaValidateSinglePortTest.`<br/>`vnet2VnetInboundRoutingTest`<br><br>`Vnet2VnetSingleInboundRouteMultiplePaValidateTwoPortsTest.`<br/> `vnet2VnetInboundRoutingTest` | Creates single ENI with single Inbound routing entry and with multiple PA validation entries.<br/> Verifies configuration with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route                                |
 | 11-12  | Verify VNET2VNET inbound routing with single ENI admin state UP/DOWN                                                                                           | `Vnet2VnetInboundEniSetUpDownSinglePortTest.`<br/>`vnet2VnetEniUpTrafficTest`<br>`setEniStateTest`<br>`vnet2VnetEniDownTrafficTest`<br><br>`Vnet2VnetInboundEniSetUpDownTwoPortsTest.`<br/>`vnet2VnetEniUpTrafficTest`<br>`setEniStateTest`<br>`vnet2VnetEniDownTrafficTest` | Creates single ENI and Inbound routing entry and verifies packet routing during ENI admin state setting UP/DOWN.<br/>1. With underlay route<br/>2. Without underlay route                                                                                      |


### **Integration**

|  #  | Test case purpose | Test Class.Method                                                                                                                                                                                                                                                                                                                                                                  | Test description |
|:---:|:---|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---|
|  1-2  | Multiple inbound and outbound configurations at the same time. Send multiple allowed and forbidden traffic types. | `Vnet2VnetInboundOutboundMultipleConfigsSinglePortTest.`<br/> `outboundHost0toHost2Test`<br/> `inboundHost2toHost0Test`<br/> `outboundHost3toHost1Test`<br/> `inboundHost1toHost3Test`<br><br>`Vnet2VnetInboundOutboundMultipleConfigsTwoPortsTest.`<br/> `outboundHost0toHost2Test`<br/> `inboundHost2toHost0Test`<br/> `outboundHost3toHost1Test`<br/> `inboundHost1toHost3Test` | Creates two ENIs, each with Inbound and Outbound configuration.<br/> Verifies configurations with mono/bidirectional VXLAN TCP traffic.<br/>1. With underlay route<br/>2. Without underlay route |
|  3  | Send non VXLAN traffic. | `UnderlayRouteTest.`<br/> `l3UnderlayHost1toHost2RoutingTest`<br/> `l3UnderlayHost2toHost1RoutingTest`                                                                                                                                                                                                                                                                             | Creates single ENI with outbound configuration and underlay configuration.<br/> Verifies regular L3 Underlay routing with mono/bidirectional simple TCP packets sending. |
|  3  | Use multiple VIPs | -                                                                                                                                                                                                                                                                                                                                                                                  | |
|  4  | Use same prefixes in CA and PA networks for outbound and inbound VNET at the same time | -                                                                                                                                                                                                                                                                                                                                                                                  | (**to clarify**) VNI configuration for Inbound. |

### **Negative**

|  #  | Test case purpose | Test Class.Method | Test description |
|:---:|:---|:---|:---|
|  1-4  | Inbound/Outbound: Verify packet drop with invalid VIP | `Vnet2VnetInboundDecapPaValidateTest.vnet2VnetInboundNegativeTest`<br/> `Vnet2VnetInboundDecapTest.vnet2VnetInboundNegativeTest`<br><br>`Vnet2VnetOutboundRouteVnetDirectTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteVnetTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteDirectTest.outboundRouteDirectNegativeTest` | Creates single ENI.<br/> Sends VXLAN TCP packet with wrong VIP address and verifies packet drop.<br/>1. Inbound routing without underlay default route<br/>2. Outbound routing without default underlay route |
|  2  | Outbound: Verify packer drop with valid VNI but no match to any ENI MAC (CA SMAC) | `Vnet2VnetOutboundRouteVnetDirectTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteVnetTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteDirectTest.outboundRouteDirectNegativeTest` | Creates single ENI outbound configuration.<br/> Sends VXLAN TCP packet with VNI matches direction lookup entry but wrong Customer SMAC (ENI MAC) address and verifies packet drop. |
|  3  | Outbound: Verify packet drop if CA Dst IP does not match any routing entry (routing drop) | `Vnet2VnetOutboundRouteVnetDirectTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteVnetTest.vnet2VnetOutboundNegativeTest`<br/> `Vnet2VnetOutboundRouteDirectTest.outboundRouteDirectNegativeTest` | Creates single ENI outbound configuration.<br/> Sends VXLAN TCP packet with wrong Customer DIP address (does not match any routing entry) and verifies packet drop. |
|  4  | Outbound: Verify packet drop if CA Dst IP matches routing entry prefix but drops by ca_to_pa (mapping drop) | `Vnet2VnetOutboundRouteVnetTest.vnet2VnetOutboundNegativeTest` | Creates single ENI outbound configuration.<br/> Sends VXLAN TCP packet with Customer DIP address that matches routing entry but does not match any ca_to_pa entry and verifies packet drop. |
|  5  | Inbound: Verify packet drop if ENI MAC (CA DMAC) does not match | `Vnet2VnetInboundDecapPaValidateTest.vnet2VnetInboundNegativeTest`<br/> `Vnet2VnetInboundDecapTest.vnet2VnetInboundNegativeTest` | Creates single ENI inbound configuration.<br/> Sends VXLAN TCP packet with wrong Customer DMAC (ENI MAC) and verifies packet drop. |
|  6  | Inbound: Verify packet drop if PA SIP match Inbound routing entry but does not match on PA validation | `Vnet2VnetInboundDecapPaValidateTest.vnet2VnetInboundNegativeTest` | Creates single ENI inbound configuration.<br/> Sends VXLAN TCP packet with Physical SIP address that matches inbound routing entry but does not match any PA validation entry and verifies packet drop. |
|  7  | Inbound: Verify packet drop if PA SIP does not match any Inbound routing entry | `Vnet2VnetInboundDecapPaValidateTest.vnet2VnetInboundNegativeTest`<br/> `Vnet2VnetInboundDecapTest.vnet2VnetInboundNegativeTest` | Creates single ENI inbound configuration.<br/> Sends VXLAN TCP packet with Physical SIP address that does not matches any inbound routing entry and verifies packet drop. |
|  8  | Inbound: Verify packet drop if VNI does not match any ENI | `Vnet2VnetInboundDecapPaValidateTest.vnet2VnetInboundNegativeTest`<br/> `Vnet2VnetInboundDecapTest.vnet2VnetInboundNegativeTest` | Creates single ENI inbound configuration.<br/> Sends VXLAN TCP packet with wrong VNI (does not match any inbound routing entry) and verifies packet drop. |
|  9  | Verify invalid configurations:<br>- Multiple MACs for same ENI<br>- All different VNIs in ENI, direction lookup, vnet configuration.<br>- Add same VNI for different direction lookup entries. | - | - |

### **Scaling & Performance**

To be defined.


### **To clarify / Future**

1. Items 5 and 7 in [other requirements](#other) are conflicting to each other.
2. What is relation between vm_vni and vnet_id in ENI create?
3. The lookup table is per ENI, but could be Global, or multiple Global lookup tables per ENIs. How to configure global lookup? Multiple lookups?
4. In Encap and Decap rules we have:
    - static rule
    - based on mapping lookup
    - inner packet SRC/DEST IP calculated based on part of outer packet SRC/DEST IP<br>
Question: What is static rule and calculated values?
5. How to test - Inbound (priority) route rules processing:
    - Most Outer Source IP Prefix
    - Most Outer Destination IP Prefix
    - VXLAN/GRE key
6. Need examples: Transpositions.
    - Direct traffic – pass through with static SNAT/DNAT (IP, IP+Port)
    - Packet upcasting (IPv4 -> IPv6 packet transformation)
    - Packet downcasting (IPv6 -> IPv4 packet transformation)
7. Need example: Up to 3 level of routing transforms (example: decap + decap + transpose).
8. LB on outbound VNET scenario (different PAs)
9. TODO: Example: Lookup between CA (inside Cx own VNET) and PA (Provider Address) using lookup table (overwrite destination IP and MAC before encap)
