## Scale per DPU (Card)
**Note: Below are the expected numbers per Data Processing Unit (DPU); this applies to both IPV4 and IPV6 underlay and overlay*

**IPV6 numbers will be lower*

| Syntax | Description |
| ----------- | ----------- |
| Flow Scale <img style="width:400px"/>| <ul><li>1+ million flows per v-port (aka ENI)</li> <li>50 million per DPU/Card<ul><li>single encap IPv4 overlay and IPV6 underlay</li> <li>single encap IPv6 overlay and IPV6 underlay. (This can be lower)</li> <li>single encap IPV4</li> <li>Encap IPv6 and IPV4</li></ul></ul> *These are complex flows, details are below.* | |  
| CPS | 4 million+ (max)  |
| Routes | 100k per v-port (max)  |
| ACLs | 100k IP-Prefixes, 10k Src/Dst ports per v-port (max)  |
| NAT | tbd  |
| V-Port (aka ENI or Source VM) | 10k (max)  |
| Mappings (VMS deployed) | 10 million total mapping per DPU; mappings are the objects that help us bridge the customer's virtual space (private ip address assigned to each VM) with Azure's physical space (physical/routable addresses where the VMs are hosted)  |
|  | For each VPC, we have a list of mappings of the form: PrivateAddress -> (Physical Address v4, Physical Address V6, Mac Address, etc...) | VPC can have up to 1M mappings

