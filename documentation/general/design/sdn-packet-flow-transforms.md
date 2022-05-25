[<< Back to parent directory](../README.md) ]

[<< Back to DASH top-level Documents](../../README.md#contents) ]

# Packet direction flow and transforms

- [Packet flow - selecting packet direction](#packet-flow---selecting-packet-direction)
- [Packet flow - selecting packet path](#packet-flow---selecting-packet-path)
  - [Fast path](#fast-path)
    - [Inbound fast path](#inbound-fast-path)
    - [Outbound fast path](#outbound-fast-path)
  - [Slow path](#slow-path)
    - [Inbound slow path](#inbound-slow-path)
    - [Outbound slow path](#outbound-slow-path)
- [Packet processing pipeline (sequential prefix match lookups)](#packet-processing-pipeline-sequential-prefix-match-lookups)
  - [ACL](#acl)
    - [ACL levels](#acl-levels)
    - [ACL rules](#acl-rules)
    - [ACL actions](#acl-actions)
- [Packet transforms](#packet-transforms)
  - [VM to VM (in VNET) communication](#vm-to-vm-in-vnet-communication)
  - [Internal Load balancer (in VNET) communication](#internal-load-balancer-in-vnet-communication)
  - [Private Link](#private-link)
  - [Private Link Service](#private-link-service)
  - [Service Tunneling](#service-tunneling)
  - [Inbound from LB](#inbound-from-lb)
  - [Outbound NAT - L4](#outbound-nat---l4)
- [References](#references)

## Packet flow - selecting packet direction

On receiving a packet from the wire, the SDN appliance will determine the **packet direction**, **matching ENI**, and **packet processing strategy** based on *Encap Transformation and Rules Evaluation*. See also [2 Packet Flows](dash-sonic-hld.md#2-packet-flows) in the *SONiC-DASH integration high level design* document. 

- **Packet direction**. It is evaluated based on the most-outer **VNI** lookup (implementation dependent) from the left-side (see figure below, a DASH optimized VM sending Outbound packets) behind the Appliance.  If there is no match, the direction is Inbound.

- **ENI selection**. Outbound uses source-MAC, Inbound uses destination-MAC
- **SLB decap** if packet was encapped by SLB.
- **Decap VNET** GRE key

The following figure shows the preliminary steps to determine the packet direction prior to selecting a fast or slow path.

![eni-match-flow-direction](./images/sdn/eni-match-flow-direction.svg)

## Packet flow - selecting packet path

For the **first packet** of a TCP flow, the **slow path** is selected, running the transposition engine and matching at each layer.  
For **subsequent packets**, the **fast path** is selected,
matching a unified flow via UFID and applying a transposition directly against rules.

### Fast path

Once the ENI is matched, the packet is first matched with flow table to check whether an existing flow already matches.  If a flow match is found (**fast path**), a corresponding match action is executed without entering into rule processing. Flow match direction is identified based on source and destination MAC.

#### Inbound fast path

  ![inbound-fast-path](./images/sdn/inbound-fast-path-flow.svg)

#### Outbound fast path

  ![outbound-fast-path](./images/sdn/outbound-fast-path-flow.svg)

### Slow path

If no flow match is found (**slow path**), the ENI rule processing pipeline will execute.

#### Inbound slow path

**Inbound rule** processing pipeline is executed if destination MAC in the packet matches the ENI MAC. Once rule pipeline is executed corresponding flows are created.

![inbound-slow-path](./images/sdn/inbound-slow-path-flow.svg)

#### Outbound slow path

**Outbound rule** processing pipeline is executed if source MAC in the packet matches the ENI MAC.

![outbound-slow-path](./images/sdn/outbound-slow-path-flow.svg)

- Once outbound rule processing is complete and final transforms are identified, the corresponding flow is created in the flow table.

- Depending upon the implementation of the flow table, a corresponding inbound flow may also be inserted to enable response packets to match the flow and bypass the rule processing pipeline.
- Note: the VNI is **static** on the 'left-side' (most-outer) of the diagram (there is only 1 encap) from the reserved VNI range
- The VNI will be **different** depending upon the Inbound 'right-side' circumstance (Internet, ER Gateway for example)

<!-- 
**Example**: VM with IP 10.0.0.1 sends a packet to 8.8.8.8, VM Inbound ACL blocks all internet, VM outbound ACL allows 8.8.8.8 \- Response packet from 8.8.8.8 must be allowed without opening any inbound ACL due to the flow match.

 ![sdn-appliance](images/sdn-appliance.svg)
-->
## Packet processing pipeline (sequential prefix match lookups)

### ACL

#### ACL levels

The ACL pipeline has 3-5 levels; an ACL decision is based on the most restrictive match across all 3 levels.  

- The first layer (contains default rules) is *controlled by Azure/MSFT*.  
- The second and 3rd layers are *Customer controlled*.
- The 4th and 5th layers might be for example, *VM/Subnet/Subscription* layers. These layers might be security rules or a top level entity controlled by an Administrator or an IT Department.

#### ACL rules

- If an ACL rule with bit exit ACL pipeline on hit is matched, the ACL pipeline is abandoned.
- Expected ACL scale \- max 100k prefixes, max 10k ports
- ACL table entry count = 1000 per table. (NOTE: Each table entry can have comma separated prefix list.)

#### ACL actions  

- Block (terminate)
- If ‘terminate’ is not used here, the last line is the most important in ACL Level1
- Soft Block (general block, with specific permits, non-terminating, proceed to next group) or think of this as a Block, and then a ‘no’ for ‘termination’.
- Allow (non-terminate, proceed to next, continue to FW rules)  
- Default action = Deny. This is the default value if no rules are matched; traffic should be dropped.  This is the default action of firewalls, however it is OK to be configurable.  If not, we want to default Deny/Drop if no rules are matched.

- ACL Group:  evaluate rules based on Priority (within an ACL Group); Terminate vs non-Terminate pertains to the Pipeline

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

## Packet transforms

This section describes the packet transformations that are specific for each scenario.
After rule processing is complete and transforms are identified, the corresponding flow is created in the flow table.

> [!NOTE]
> The following diagrams show transforms as they are done currently, without the appliance in the path. 

### VM to VM (in VNET) communication

![VMtoVM](./images/sdn/sdn-packet-transforms-vm-to-vm.svg)

### Internal Load balancer (in VNET) communication

![VMtoVMloadBalancer](./images/sdn/sdn-packet-transforms-vm-internal-load-balancer.svg)

### Private Link

![PL](./images/sdn/sdn-packet-transforms-private-link.svg)

### Private Link Service

![PL](./images/sdn/sdn-packet-transforms-private-link-service.svg)

### Service Tunneling

![ST](./images/sdn/sdn-packet-transforms-service-tunneling.svg)

### Inbound from LB

![InbfromLB](./images/sdn/sdn-packet-transforms-inbound-from-lb.svg)

### Outbound NAT - L4

![OutNATL4](./images/sdn/sdn-packet-transforms-outbound-nat-l4.svg)

> [!NOTE]
> L3 works in same way except port re-write

## References

- [Disaggregated API for SONiC Hosts (DASH) high level design](dash-high-level-design.md)
- [SONiC-DASH integration high level design](dash-sonic-hld.md)