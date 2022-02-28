## Virtual Port and Packet Direction

An SDN appliance in a multi-tenant network appliance (meaning 1 SDN appliance will have multiple cards; 1 card will have multiple machines or bare-metal servers), which supports Virtual Ports.   These can map to policy buckets corresponding to customer workloads, example: Virtual Machines, Bare Metal servers.

- The SDN controller will create these virtual ports on SDN appliance and associate corresponding SDN policies like – Route, ACL, NAT etc. to these virtual ports.  In other words, our software will communicate with the cards, hold card inventory and SDN placement, call API’s that are exposed through the card create policies, setup ENI, routes, ACLs, NAT, and different rules.
- Each Virtual port will be created with an ENI identifier like – Mac address, VNI or more.
	- Virtual port will also have attributes like – Flow time-out, QOS, port properties related to the port.

	- Virtual port is the container which holds all policies.

	![tt](images/vport.png)

- On receiving a packet from the wire, the SDN appliance will determine the matching ENI, Packet direction and packet processing strategy based on _Encap Transformation and Rules Evaluation_.

	- On receiving a packet, the SDN appliance will perform a lookup based upon the inner source mac (VXLAN encap packet), if a matching ENI is found, and corresponding rule / flow processing will start.

	- Once the ENI is matched, the packet is first matched with flow table to see if an existing flow already matches this.  If a flow match is found, a corresponding match action is executed without going into rule processing. Flow match direction is identified based on source and destination mac.

	- If no flow match is found, the ENI rule processing pipeline will execute.

		- **Inbound rule** processing pipeline is executed if destination mac in the packet matches the ENI mac. Once rule pipeline is executed corresponding flows are created.

		- **Outbound rule** processing pipeline is executed if source mac in the packet matches the ENI mac. 

			- Once outbound rule processing is complete and final transforms are identified, the corresponding flow is created in the flow table.

			- Depending on implementation of flow table, a corresponding inbound flow may also be inserted to enable response packets to match the flow and bypass the rule processing pipeline.

            - **Example**: VM with IP 10.0.0.1 sends a packet to 8.8.8.8, VM Inbound ACL blocks all internet, VM outbound ACL allows 8.8.8.8 \- Response packet from 8.8.8.8 must be allowed without opening any inbound ACL due to the flow match.
            
	![Appliance](images/sdn_appliance.png)
- The VNI is static on the 'left-side' of the diagram
- The VNI will be different depending upon the Inbound circumstance (Internet, ER Gateway for example)
- SDN Eng to populate this further

## Packet processing Pipeline (Sequential prefix match lookups)

### ACL

- The ACL pipeline has 3-5 levels; an ACL decision is based on the most restrictive match across all 3 levels.  The 1st layer (contains default rules) is _controlled by Azure/MSFT_.  The 2nd and 3rd layers are _Customer controlled_. The 4th and 5th layers might be for example, *VM/Subnet/Subscription* layers. These layers might be security rules or a top level entity controlled by an Administrator or an IT Department. 

- If an ACL rule with bit exit ACL pipeline on hit is matched, the ACL pipeline is abandoned.

- Expected ACL scale \- max 100k prefixes, max 10k ports

- ACL table entry count = 1000 per table. (NOTE: Each table entry can have comma separated prefix list.)

- Action Definitions:  

	- Block (terminate)

		- If ‘terminate’ is not used here, the last line is the most important in ACL Level1 

	- Soft Block (general block, with specific permits, non-terminating, proceed to next group) or think of this as a Block, and then a ‘no’ for ‘termination’.

	- Allow (non-terminate, proceed to next, continue to FW rules)  

	- Default action = Deny (This is the default value if no rules are matched; traffic should be dropped.  This is the default action of firewalls, however it is OK to be configurable.  If not, we want to default Deny/Drop if no rules are matched).

- ACL Group:  evaluate rules based on Priority (within an ACL Group); Terminate vs non\-Terminate pertains to the Pipeline

**ACL_LEVEL1 (VNET Lookup)**

| Source| Destination| Source Port| Destination Port| Protocol| Action| Priority| Exit ACL pipeline on hit?(Is Terminating)
|:----------|:----------|:----------|:----------|:----------|:----------|:----------|:----------
| 10.0.0.0/24 20.0.0.0/24 30.0.0.0/24| 10.0.0.10/32 10.0.0.11/32 10.0.0.12/32 10.0.0.13/32 10.0.0.14/32 30.0.0.0/24| *| *| TCP| Allow| 0| No
| 10.0.0.0/24 20.0.0.0/24 30.0.0.0/24| 10.0.0.200/32| *| *| TCP| Allow| 1| No
| 10.0.0.0/24 20.0.0.0/24 30.0.0.0/24| 10.0.0.201/32| *| *| TCP| Block| 2| Yes
| 10.0.0.0/24 20.0.0.0/24 30.0.0.0/24| 10.0.0.202/32| *| *| TCP| Allow| 3| Yes
| 10.0.0.0/24 20.0.0.0/24 30.0.0.0/24| 10.0.0.203/32| *| *| TCP| Allow| 4| No
| *| 8.8.8.8/32| *| *| *| Block| 5| Yes
| *| 8.8.8.8/32| *| *| *| Allow| 6| Yes
| *| 9.9.9.9/32| *| *| *| Allow| 7| Yes
| *| *| *| *| *| Block| 8| No 
| | | | | | | | 
| | | | | | | | 

**ACL_LEVEL2 (Customer/User FW rules - portal.azure.com)**

| Source| Destination| Source Port| Destination Port| Protocol| Action| Priority| Exit ACL pipeline on hit?(Is Terminating)
|:----------|:----------|:----------|:----------|:----------|:----------|:----------|:----------
| 10.0.0.0/24| *| *| *| TCP| Allow| 1| No
| 10.0.0.0/24| 10.0.0.202/32| *| *| TCP| Block| 1| Yes
| 10.0.0.0/24| 10.0.0.203/32| *| *| TCP| Block| 1| Yes
| *| 8.8.8.8/32| *| *| *| Allow| 2| No
| *| 9.9.9.9/32| *| *| *| Block| 2| Yes
| *| 1.1.1.2/32| *| *| *| Allow| 30| No
| *| *| *| *| *| Block| 3| No 
| | | | | | | | 
| | | | | | | | 

**ACL_LEVEL3**

Etc…

**Order of evaluation / priority of evaluation**

- ACL_LEVEL1 \-> ACL_LEVEL2

**Test Scenarios and expected results** 

- For simplicity below table only has IP conditions, but the same combinations exist for ports also.

- ACL rules are direction aware, below example is assuming a VM with source IP = 10.0.0.100 which is trying to send packets to various destinations and has above ACL rules on its v\-port.

**Outbound Traffic example evaluation and outcome**

| Source IP| Destination IP| Decision of ACL_LEVEL1| Decision of ACL_LEVEL2| Outcome
|:----------|:----------|:----------|:----------|:----------
| 10.0.0.100| 10.0.0.200| Allow (Terminating = false)| Allow (Terminating = false)| Allow
| 100.0.0.100| 100.0.0.201| Block (Terminating = True)| Not evaluated or Ignored| Block
| 100.0.0.100| 100.0.0.202| Allow (Terminating = True)| Not evaluated or Ignored| Allow
| 100.0.0.100| 100.0.0.203| Allow (Terminating = false)| Block (Terminating = True)| Block
| 100.0.0.100| 8.8.8.8| Block (Terminating = True)| Not evaluated or Ignored| Block
| 100.0.0.100| 1.1.1.1| Block (Terminating = false)| Block (Terminating = false)| Block
| 100.0.0.100| 1.1.1.2| Block (Terminating = false)| Allow (Terminating = false)| Allow


## Routes and Route-Action

- Routes are usually LPM based Outbound

- Each route entry will have a prefix, and separate action entry

- The lookup table is per ENI, but could be Global, or multiple Global lookup tables per ENIs

- Outer Encap IPv4 using permits routing between servers within a Region; across the Region we use IPv6

*Why would we want to use these?* 

- Example:  to block prefixes to internal DataCenter IP addresses, but Customer uses prefixes inside of their own VNET

- Example:  Lookup between CA (inside Cx own VNET) and PA (Provider Address) using lookup table (overwrite destination IP and MAC before encap)

- Example:  Customer sends IPv4, we encap with IPv6

- Example:  ExpressRoute with 2 different PAs specified (load balancing across multiple PAs) using 5 tuples of packet to choose 1st PA or 2nd PA

| Route Type| Example 
|:----------|:----------
| Encap_with_lookup_V4_underlay| Encap action is executed based on lookup into the mapping table.V4 underlay is used
| Encap_with_lookup_V6_underlay| Encap action is executed based on lookup into the mapping table.V6 underlay is used
| Encap_with_Provided_data (PA)| Encap action is executed based on provided data.Multiple PA can be provided.
| Outbound NAT (SNAT)_L3| L3 NAT action is executed on source IP, based on provided data.
| Outbound NAT (SNAT)_L4| L4 NAT action is executed on source IP, source port based on provided data.
| Null | Blocks the traffic 
| Private Link | -
| | 

**Mapping Table for a v-port**

| Customer Address| Physical Address - V4 | Physical Address - V6| Mac-Address for D-Mac Rewrite| VNI to Use
|:----------|:----------|:----------|:----------|:----------
| 10.0.0.1| 100.0.0.1| 3ffe::1| E4-A7-A0-99-0E-17| 10001
| 10.0.0.2| 100.0.0.2| 3ffe::2| E4-A7-A0-99-0E-18| 10001
| 10.0.0.3| 100.0.0.3| 3ffe::3| E4-A7-A0-99-0E-19| 20001
| 10.0.0.4| 100.0.0.4| 3ffe::3| E4-A7-A0-99-0E-20| 10001

**Route Table for a v-port**

- LPM decides which route is matched.
- Once the route is matched, a corresponding action is executed.

| Route| Action | Route Type| Route Id
|:----------|:----------|:----------|:----------
| 10.0.0.0/24, <br/> 20.0.0.0/24, <br/> 30.0.0.0/24, <br/> 10.0.0.0/8, <br/>…… more prefixes (up-to 20k) <img width=500/>| Encap Type: VXLAN <br/> Action - lookup mapping table for exact destination, VNI and D-Mac re-write info.| Encap_with_lookup_V4_underlay| 1
| 10.0.0.100/32| Encap Type: VXLAN <br/> Action: Encap_with_Provided_data <ul><li>Encap with source PA = 100.0.0.1</li><li>Encap with destination PA = 23.0.0.1</li><li>Re-write D-Mac to E4-A7-A0-99-0E-28</li><li>Use VNI = 90000</li></ul>| Encap_with_Provided_data| 2
| 10.0.0.101/32| Encap Type: VXLAN <br/> Action: Encap_with_Provided_data <br/> <ul><li>Encap with source PA = 100.0.0.1</li> <li>Encap with destination PA = 23.0.0.10, 23.0.0.11, 23.0.0.13, 23.0.0.14</li> <li>Re-write D-Mac to E4-A7-A0-99-0E-29</li><li>Use VNI = 90000</li> </ul>| Encap_with_Provided_data_ECMP| 3
| 8.8.8.8/32 | L3 NAT <br/> Action: Transpose source IP to provided NAT IP, keep all ports same.NAT IP: 10.0.0.1 -> 15.0.0.1| Outbound NAT (SNAT)_L3| 4
| 9.9.9.9.9/32| L4 NAT <br/> Action: Transpose source IP and source port re-write ports from configured port pool.| Outbound NAT (SNAT)_L4| 5
| 0.0.0.0/32| NULL| Null| 6
| 23.0.0.1/32| Service endpoint| ST| 7
| 23.0.0.2/32| Private Link - TBD| Private Link - TBD| 8

**Route example- Outbound packets**

| Original Packet <img width=1000/>| Matched route <img width=500/> | Transform <img width=1000/> | Route Type
|:----------|:----------|:----------|:----------
| 10.0.0.1 -> 10.0.0.2 <br/> SMAC1-> DMAC_FAKE </br> Outer: <br/> SRC: [Physical IP of host] <br/> DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/> &nbsp; &nbsp; &nbsp;VNI: custom <br/>Inner Mac: <br/> &nbsp; &nbsp; &nbsp; SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP:<br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 1| Outer: <br/>SRC: [SDN Appliance IP] <br/>DST: [100.0.0.2] # Came from mapping table lookup <br/>VXLAN <br/> &nbsp; &nbsp; &nbsp;VNI: 10001 <br/>Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-18 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Encap_with_lookup_V4_underlay
| 10.0.0.1 -> 10.0.0.100 <br/> SMAC1-> DMAC_FAKE <br/> Outer: <br/> SRC: [Physical IP of host] <br/> DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/> Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 2| Outer: <br/>SRC: [SDN Appliance IP] DST: [23.0.0.1] # Came from mapping table lookup <br/>VXLAN VNI: 90000 <br/>Inner Mac:<br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-28 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.100]| Encap_with_Provided_data
| 10.0.0.1 -> 10.0.0.101 <br/>SMAC1-> DMAC_FAKE <br/>Outer: <br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/>VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/>Inner Mac: <br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [10.0.0.2]| Route Id = 3| Outer: <br/>SRC: [SDN Appliance IP] <br/>DST: ECMP on <br/>[23.0.0.10, 23.0.0.11, 23.0.0.13, 23.0.0.14] <br/># Came from mapping table lookup <br/>VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: 90000 <br/>Inner Mac:<br/>&nbsp; &nbsp; &nbsp;SRC - SMAC1 DST - E4-A7-A0-99-0E-29 <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp; [10.0.0.1] -> [10.0.0.100]| Encap_with_Provided_data_ECMP
| 10.0.0.1 -> 8.8.8.8 <br/>SMAC1-> DMAC_FAKE <br/>Outer: <br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/> VXLAN <br/>&nbsp; &nbsp; &nbsp;VNI: custom <br/> Inner Mac: <br/>&nbsp; &nbsp; &nbsp; SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp; &nbsp; &nbsp;[10.0.0.1] -> [8.8.8.8]| Route Id = 4| | 
| | | | 


 ## Packet Flow
 
For the first packet of a TCP flow, we take the Slow Path, running the transposition engine and matching at each layer.  For subsequent packets, we take the Fast Path, 
matching a unified flow via UFID and applying a transposition directly against rules.


### Inbound

 **Fast Path - Flow Match**
 ![Inb](images/inb_fast_path_flow_match.png)

 **Slow Path - No flow match**
 ![InbSP](images/in_slow_path_no_flow_match.png)

### Outbound

 **Fast path - flow match**
![OutFP](images/out_fast_path_flow_match.png)

 **Slow Path (policy evaluation) - No flow match**
![OutSP](images/out_slow_path_pol_eval_no_flow_match.png)

## Packet Transform Examples

### VNET to VNET Traffic

 **V-Port**

- **Physical address = 100.0.0.2**

- **V-Port Mac = V-PORT_MAC**

 **VNET Definition:**

	- 10.0.0.0/24 

	- 20.0.0.0/24


**VNET Mapping Table**
| | V4 underlay| V6 underlay| Mac-Address| Mapping Action | VNI
|:----------|:----------|:----------|:----------|:----------|:----------
| 10.0.0.1| 100.0.0.1| 3ffe :: 1| Mac1| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 100
| 10.0.0.2| 100.0.0.2| 3ffe :: 2| Mac2| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 200
| 10.0.0.3| 100.0.0.3| 3ffe :: 3| Mac3| VXLAN_ENCAP_WITH_DMAC_DE-WRITE| 300
| | | | | | 
 
**Packet Transforms**

| SRC -> DST <img width=1000/>| Out-ACL1| Out-ACL2| Out-ACL3| Routing <img width=1000/>| Final <img width=1000/>|
|:----------|:----------|:----------|:----------|:----------|:----------
| | Block 10.0.0.10 Allow *| Block 10.0.0.11 Allow * | Allow*| 10.0.0.0/24 - Route Action = VNET 20.0.0.0/24 - Route Action = VNET| 
| 10.0.0.1 -> 10.0.0.10 <br/>SMAC1-> DMAC_FAKE| Block| | | | Blocked
| 10.0.0.1 -> 10.0.0.11 <br/>SMAC1-> DMAC_FAKE| Allow| Block| | | Blocked
| 10.0.0.1 -> 10.0.0.2 <br/>SMAC1-> DMAC_FAKE <br/>Outer:<br/>SRC: [Physical IP of host] <br/>DST: [Physical IP of SDN Appliance] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: custom <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - DMAC_FAKE <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]| Allow| Allow| Allow| Matched LPM route 10.0.0.0/24 Execute action VNET - which will lookup in mapping table and take mapping action.| Highlighted the changes in packet <br/>Outer:<br/>SRC: [100.0.0.2] <br/>DST: [100.0.0.1] <br/>VXLAN <br/>&nbsp;&nbsp;&nbsp;&nbsp;VNI: 200 <br/>Inner Mac: <br/>&nbsp;&nbsp;&nbsp;&nbsp;SRC - SMAC1 DST - Mac1 <br/>Inner IP: <br/>&nbsp;&nbsp;&nbsp;&nbsp;[10.0.0.1] -> [10.0.0.2]
| 10.0.0.1 -> 10.0.0.3 SMAC1-> DMAC_FAKE| | | | | 
| | | | | | 


## Metering

- Metering will be based on per flow stats, metering engine will consume per flow stats of bytes\-in and bytes\-out.

## VNET Encryption

## Telemetry


## Counters

Counters are objects for counteing data per ENI. The following are their main characteristics:

- A counter is associated with only one ENI that is, it is not shared among different ENIs. 
- If you define a counter as a global object, it cannot reference different ENIs. 
- The counters live as long as the related ENI exists.  
- The counters persist after the flow is completed. 
- You use API calls to handle these counters. 
- When creating a route table, you will be able to reference the counters.


The control plane is the consumer of counters that are defined in the data plane. The control plane queries every 10 seconds. 

Counters can be assigned on the route rule, or assigned onto a mapping. If mapping does not exist, you revert to the route rule counter. A complete definition will follow when we have more information other than software defined devices.  

In the flow table we list the packet counter called a metering packet; once we have the final implementation that does the packet processing, we can do metering. 

Essentially, whenever a route table is accessed and we identify the right VNET target (based on the mapping from the underlay IP), will have an ID of the metering packet preprogrammed earlier.  We will reference this counter in the mappings. When the flow is created it will list this counter ID.  When the packet transits inbound or outbound through the specific flow, this counter is incremented and tracked separately for the inbound and outbound.

We need more information around Counters, Statistics, and we need to start thinking about how to add Metering- and reconcile this in the P4 model.  

**Questions**  
- How often will we read?  
- What type of API to use?  
- Will we push or pull from the Controller?


## BGP

## Watchdogs

## Servicing

## Debugging

Counters per rule to trace an increment per layer, ACL hits, Packet Captures, Bandwidth Metering for Routing Rules to count bytes (each flow associated with a bandwidth counter when an LPM is hit \- many flows _may_ share the same counters).   

## Flow Replication

## Unit Testing and development

- Need ability to run rule processing behavior on dev box / as part of merge validation.

## Internal Partner dependencies

- SLB VXLAN support

- Reduced tuple support on host.
