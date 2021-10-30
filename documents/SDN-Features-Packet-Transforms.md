# SDN Features, Packet Transforms and Scale

## First Target Scenario:  Highly Optimized Path, Dedicated Appliance, Little Processing or Encap to SDN Appliance and Policies on an SDN Appliance
Why do we need this scenario?  There is a huge cost associated with establishing the first connection (and the CPS that can be established).

- A high Connections per Second (CPS) / Flow SKU for Networked Virtual Appliances (NVA)

- insert image here

## Scale per DPU (Card)
**Note: Below are the expected numbers per Data Processing Unit (DPU); this applies to both IPV4 and IPV6 underlay and overlay*

**IPV6 numbers will be lower*

| Syntax | Description |
| ----------- | ----------- |
| Flow Scale | •	1+ million flows per v-port (aka ENI) |
|  | •	50 million per DPU/Card |
|  | o	single encap IPv4 overlay and IPV6 underlay |
|  | o	single encap IPv6 overlay and IPV6 underlay. (This can be lower) |
|  | o	single encap IPV4 |
|  | o	Encap IPv6 and IPV4 |
|  | *These are complex flows, details are below*
| CPS | 4 million+ (max)  |
| Routes | 100k per v-port (max)  |
| ACLs | 100k IP-Prefixes, 10k Src/Dst ports per v-port (max)  |
| NAT | tbd  |
| V-Port (aka ENI or Source VM) | 10k (max)  |
| Mappings (VMS deployed) | 10 million total mapping per DPU; mappings are the objects that help us bridge the customer's virtual space (private ip address assigned to each VM) with Azure's physical space (physical/routable addresses where the VMs are hosted)  |
|  | For each VPC, we have a list of mappings of the form: PrivateAddress -> (Physical Address v4, Physical Address V6, Mac Address, etc...) |

## Scenario Milestone and Scoping


| Scenario #        | Feature          | Perf |  
| ------------- |-------------| -----|
| 1      | VNET <-> VNET | • CPS
|| Route Support | •Flow
|| LPM Support | •PPS
|| ACL Support | •Rule Scale
| 2      | Load Balancer Inbound      |  |
|| VIP Inbound
| 3 | Private Link Outbound (transposition), encapsulate and change packet IPv4 to IPv6 (4 bits embedded)     |  |
| 4 | L3 / L4 Source NAT (correlated w/#2) outbound perspective (Cx address) to Internet; changing Cx source IP to Public IP (1:1 mapping)     |  |
| 5 | Private Link Service Link Service (dest side of Private Link) IPv6 to IPv4; DNAT’ing     |  |
| 6 | Flow replication; supporting High Availability (HA); flow efficiently replicates to secondary card; Active/Passive (depending upon ENI policy) or can even have Active/Active; OR provision the same ENI over multiple devices w/o multiple SDN appliances – Primaries for a certain set of VMS can be on both     |  |