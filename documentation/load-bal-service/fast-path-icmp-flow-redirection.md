# Fast Path ICMP flow redirection

## Overview

FastPath is the feature that switches traffic from using VIP-to-VIP connectivity (which involves transiting SLB MUXes), into using a direct path between VMs (direct PA to PA path).

## Definitions

| Acronym | Definition |
|---------|------------|
| VIP     | Virtualized IP (load balanced IP). <br/> This is load balanced IP. |
| ILPIP   | Instance Level Public IP. <br/> Public IP allocated to the ENI that's Routable over the internet. |
| DIP/PA  | Physical Address / Directly Assigned IP. <br/> Actual physical address of the VM (underlay). |
| SIPo    | Outer Source IP |
| DIPo    | Outer Destination IP |
| DMACi   | Inner Destination MAC Address |

## Architecture

![load-balancer-fast-path-architecture](images/load-balancer-fast-path-architecture.png)

## How it works?

1. The VM begins communicating with a Service (or other VM) using VIP connectivity.
    - Source IP: VIP (of the source VM).
    - Destination IP: VIP (of destination service/VM).
    - In this case traffic in both directions transits SLB MUXes.

1. When traffic destined toward the VIP lands on SLB MUX (SYN packet), the MUX picks the actual destination VM (from a list of healthy VMs in the backend pool). It should redirect the packet accordingly (standard load balancing functionality).

    Once the VM is selected, the SLB MUX forwards the packet to the destination VM.
    For the packet to be accepted by the destination, the MUX needs to put the destnation VM's MacAddress into the inner packets DestMAC field.

1. The SLB MUX (in addition to forwarding packet to destination) **may** (often is!!!) sending the ICMP redirect packet towards the source VM from which the SYN packet originated.

    - The DMACi of the ICMP redirect packet is used to match the ENI that the fastpath is intended for.
    - The ICMP Rdedirect packet has 5-tuple information that can be used to lookup the flow that needs to be "fixed".
    - The ICMP Redirect packet enough information that allows the the DPU to apply the same transforms to the packet that MUX had applied to the previous packet.

1. The Source side (currently VFP) listens for ICMP redirect packets, and once received performs "flow fixup" (updates the flow to redirect next packets not to Destination VIP, but directly to the Destination PA/DIP that arrived in the ICMP redirect packet from SLB MUX).

1. Once flow is "fixed up", the next packets are direct and bypass the SLB MUX in that direction.  This achieves high performance, as after initial connection handshake (SYN, SYN+ACK, ACK), the remaining traffic is direct between VMs and does not transit the SLB MUXes.

**Notes:**

- Two (2) MUXes are used for the VIP to VIP traffic.
  - The Destination SLB MUX is used to advertise destination VIP.
  - The Source SLB MUX is used to advertise the return VIP of the VM (to which VM SNATs the outbound traffic).

- Each SLB MUX *may* send ICMP redirect independently.

- Receiving ICMP redirects from single SLB MUX means that *only flows about that specific VIP* (either destination or source VIP) must be "fixed up" (updated to point to PA instead of VIP).

- ICMP redirect is sent by SLB MUX to both: source VM and destination VM.

- It is not guaranteed that SLB MUX will send ICMP redirect packets.

- It is not guaranteed that ICMP redirect packet will be sent after initial SYN (it might be sent later).

- The ICMP redirect packet might get *lost* (SLB MUX will resend it when next packet arrives on the SLB MUX and still uses VIP) *or possibly duplicated* (multiple packets that have VIP might arrive on SLB MUX, and SLB MUX may send ICMP redirect for all the packets that it receives as still using VIP).

- The Fastpath redirect packet only changes the behavior for the subsequent outbound packets. Processing of inbound packets should remain unaffected, even if the source of the inbound packet transitioned to fastpath (Outer Source IP might change).

- NSG evaluation is skipped for the ICMP redirect packets. 

- ICMP Redirect packets are always GRE Encapped. The platform uses GRE Key 253 (0xfd) for PublicIP, PublicLB scenarios, and 254 (0xfe) for ServiceEndpoints, PrivateEndpoint and Internal Loadbalancer scenario.

- ICMP Redirects are generated only for TCP traffic.

## Flow redirection packet

The fast path ICMP flow redirection packet is based on ICMP redirect packet ([IPv4 - RFC762](https://datatracker.ietf.org/doc/html/rfc792) / [IPv6 - RFC2461](https://datatracker.ietf.org/doc/html/rfc2461#section-4.5)).

The ICMP (v4) Redirect packet contains the IP and the TCP header. This information can be used to match the 5-tuple flow targeted for fixup.

```
ICMP Redirect (Type=5):
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type      |     Code      |          Checksum             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Gateway Internet Address                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Internet Header + 64 bits of Original Data Datagram      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

The ICMPv6 Redirect packet enriched with the Redirect option serves the same purpose for ipv6 scenarios:
```
ICMPV6 Redirect (Type=137)
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type      |     Code      |          Checksum             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Reserved                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                                                               +
|                                                               |
+                       Target Address                          +
|                                                               |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                                                               +
|                                                               |
+                     Destination Address                       +
|                                                               |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Options ...
+-+-+-+-+-+-+-+-+-+-+-+-

Redirect Option:
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type      |    Length     |            Reserved           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Reserved                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
~                       IP header + data                        ~
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

The detailed packet format is described as below:

|SLB IP|APPL IP|GRE|SLB MAC|VM MAC|IP|Inner Src IP|Inner Dst IP|ICMP v4/v6 Redirect|Redirect Option (IPv6 only)|Redirection Info|
|------|-------|---|-------|------|--|------------|------------|------------------|---------------------------|----------------|



The `RedirectOption` and `RedirectInfo` structs are defined as below:

- ICMP redirect shall have the original inner IPv6 address as the IP header's src and dst address.
- Redirect info shall contain the transposed IPv6 address, src and dst ports, sequence number and the encap type (NVGRE in this case) in addition to redirect address.

```c
struct 
{
    uint8 Type;
    uint8 Length;
    uint8 Reserved2[6];
    IPV6_HEADER Ipv6Header;
    uint16 SourcePort;
    uint16 DestinationPort;
    uint32 SequenceNumber;
} RedirectOption;

struct 
{ 
    uint32 Version; 
    uint16 AddrFamily; 
    uint16 EncapType; 
    uint32 EncapId; 
    union { 
        struct { 
            in_addr DipPAv4; 
            char VMMac[MAC_ADDR_SIZE]; 
        } Info4; 
        struct { 
            in6_addr DipPAv6; 
            char VMMac[MAC_ADDR_SIZE]; 
        } Info6; 
} RedirectInfo; 
```

The following shall be used for translations:

| Field                         | Mapping                       |
| ----------------------------- | ----------------------------- |
| VM Mac                        | Source ENI                    |
| Inner Src IP                  | Original Src IP               |
| Inner Dst IP                  | Original Dst IP               |
| Target Address                | Original Dst IP               |
| Redirect Header               | Original IPv6 Header + TCP ports (5 tuple) |
| Addr Family                   | AF_INET/AF_INET6              |
| Encap Type                    | NVGRE 1 / VXLAN 2 / IPINIP 3  |
| Encap Id                      | Redirect GRE Key/ VXLAN Id    |
| Custom Redirect Info          | Redirect DIP and Dst Mac      |


## Packet transformation

### VIP / ILPIP Scenario
In scenario applies to the ENI that's sending traffic to a VIP or PublicIP hosted by the LoadBalancer.

![packet-transform](images/vip-transformation.svg)

#### Pre-fastpath flow
- Outbound flow with no encap.
-  Traffic snatted to either the PhysicalAddress (RoutableAddress) of the ENI, or a PublicIP assigned to an ENI. 

#### Redirect format
- ICMP

#### GRE Key in the encapped ICMP Redirect packet
- 0x00fd (253)

#### Post-fastpath flow modifications
- Add Encap of the type RedirectInfo.EncapType. (In practice this is always NVGRE)
- GreKey = RedirectInfo.EncapId. (this is from the trusted VNI range)
- DIPo = RedirectInfo.Info4.DipPAv4
- SIPo = PreFastpathFlow.SIPo
- DMACi = RedirectInfo.Info4.VMMac


#### Packet signatures from captures

- TCP handshake uses VIP (20.69.29.62)

  ![TCP-Syn](images/vip-tx-syn.png)

- ICMP Redirect packet

  ![ICMP-redirect.png](images/vip-rx-redirect.png)

- After the ICMP redirect, the packets start using DIPo/DMACi (10.126.24.81 00:22:48:c2:a4:bf)

  ![after-ICMP-redirect](images/vip-tx-after-redirect.png)

### PE / ST Scenario
In this scenario, the ENI is sending traffic to a PrivateEndpoint or a ServiceEndpoint. Since the NPU will be operating on the source side, it should be able to honor the ICMP Redirect sent from DST side SLB MUX, and bypass the mux in the subsequent packets. The Redirect packet received in this case is of the ICMPv6 format.

 ![PL-packet-transform](images/pl-transformation.svg)

#### Pre-fastpath flow
- Outbound flow encapped with Private Link GRE key.
- Inner packet is IPV6.

#### Redirect format
- ICMPv6

#### GRE Key in the encapped ICMPv6 Redirect packet
- 0x00fe (254)

#### Post-fastpath flow modifications
- GreKey = PreFastpathFlow.GreKey
- DIPo = RedirectInfo.Info6.DipPAv6
- DMACi = RedirectInfo.Info6.VMMac

#### Packet signatures from captures
- TCP Syn. The packet is headed to Mux with ip 52.165.104.174
![PE TCP-Syn](images/pe-tx-syn.png)

- ...[SYN ACK]...
- ...[ACK]...
- ICMPv6 Redirect packet
![ICMP-redirect.png](images/pl-rx-redirect.png)

- After the ICMP redirect, the packets start using DIPo/DMACi (100.116.86.45 00:22:48:6d:27:ce)
![after-ICMP-redirect](images/pl-tx-after-redirect.png)


### ILB Scenario
In this scenario, the ENI is sending traffic to an InternalLoadBalander. The NPU could be serving either of the Source or Destination ENIs. This specific example is shows how a Redirect packet should be handled on the source ENI. NPU should be able to honor the ICMP Redirect sent from DST side SLB MUX, and bypass the mux in the subsequent packets.
The behavior would be the same had we considered the case where dest ENI is receiving the Redirect

Note: In the below diagram, the encap to packet 3 and 13 shows NVGRE, but we have now switched this to VXLAN encap for intra-VPC traffic.
![ILB-packet-transform](images/ilb-transformation.svg)

#### Pre-fastpath flow
- Outbound flow VxLAN encapped with VNI belonging to ENI's VPC.

#### Redirect format
- ICMP

#### GRE Key in the encapped ICMPv6 Redirect packet
- 0x00fe (254)

#### Post-fastpath flow modifications
- Maintain the VxLan encap from pre-fastpath flow.
- DIPo = RedirectInfo.Info4.DipPav4
- DMACi = RedirectInfo.Info4.VMMac
- VNI doesn't change

#### Packet signatures from captures

- TCP Syn. The packet is headed to Mux with ip 52.159.22.123
![ILB TCP-Syn](images/ilb-tx-syn.png)

- ICMP Redirect
![ICMP-redirect.png](images/ilb-rx-redirect.png)

- After the ICMP redirect, the packets start using DIPo/DMACi (10.72.82.11 00:22:48:c2:ae:3f) with VNI same as pre-fastpath
![after-ICMP-redirect](images/ilb-tx-after-redirect.png)



## Detailed design

### SAI API for fast path implementation

All fast path packet handling and flow manipulation are done under the SAI API, hence there is no SAI API added for implementing the feature.

### SAI API for enabling and disabling fast path

In case of live sites, for example, fast path goes wrong and incorrectly updates the flow, we will need a toggle to disable this behavior.

There should be 3 knobs for controlling the 3 individual scenarios mentioned above.
1.  vip / ilpip fastpath toggle - if enabled, honor ipv4 redirect with gre key 253
1.  ST / PE fastpath toggle - if enabled, honor ipv6 redirect packet with gre key 254
1.  ILB fastpath toggle - if enabled, honor ipv4 redirect with gre key 254

By default, the knobs are enabled. 
This toggle is added as an attribute to ENI:

```c
typedef enum _sai_eni_attr_t
{
    // ...

    /**
     * @brief Action set_eni_attrs parameter DISABLE_VIP_FAST_PATH_ICMP_FLOW_REDIRECTION
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_ENI_ATTR_DISABLE_VIP_FAST_PATH_ICMP_FLOW_REDIRECTION,

    /**
     * @brief Action set_eni_attrs parameter DISABLE_FAST_PATH_ICMPV6_FLOW_REDIRECTION
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_ENI_ATTR_DISABLE_FAST_PATH_ICMPV6_FLOW_REDIRECTION,

    /**
     * @brief Action set_eni_attrs parameter DISABLE_ILB_FAST_PATH_ICMP_FLOW_REDIRECTION
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_ENI_ATTR_DISABLE_ILB_FAST_PATH_ICMP_FLOW_REDIRECTION,

    // ...
} sai_eni_attr_t;
```

### Fast Path counters

For debugging purposes, we will also need to add counters in order to give insights on how fast path works internally.

In order to provide a unified way for retrieving all counters for any DASH counters, all counters below will be added as stats, because many DASH counters are not [regular data path counters that modeled in SAI](https://github.com/opencomputeproject/SAI/blob/master/inc/saicounter.h), which tracks packets and bytes.

#### Port stats attributes

Port level counter will be added as port stats extensions following the [SAI extension model](https://github.com/opencomputeproject/SAI/blob/master/doc/SAI-Extensions.md#extension-custom-attributes).

| Attribute name | Description |
| -------------- | ----------- |
| SAI_PORT_STAT_LB_FAST_PATH_ICMP_IN_PACKETS | The number of fast path packets received |
| SAI_PORT_STAT_LB_FAST_PATH_ICMP_IN_BYTES | The total bytes of fast path packets received |
| SAI_PORT_STAT_LB_FAST_PATH_ENI_MISS_PACKETS | The number of fast path packet received but could not find corresponding ENI to process |
| SAI_PORT_STAT_LB_FAST_PATH_ENI_MISS_BYTES | The total bytes of fast path packet received but could not find corresponding ENI to process |

#### ENI stats attributes

| Attribute name | Description |
| -------------- | ----------- |
| SAI_ENI_STAT_LB_FAST_PATH_ICMP_IN_PACKETS | The number of fast path packets received |
| SAI_ENI_STAT_LB_FAST_PATH_ICMP_IN_BYTES | The total bytes of fast path packets received |

#### Flow table stats attributes

| Attribute name | Description |
| -------------- | ----------- |
| SAI_ENI_STAT_LB_FAST_PATH_FLOW_REDIRECTED_COUNT | The number of flows that redirected due to fast path packet received |
| SAI_ENI_STAT_LB_FAST_PATH_FLOW_MISS_COUNT | The number of flows that is missing when trying to redirected by fast path packets |
| SAI_ENI_STAT_LB_FAST_PATH_ACTIVE_FLOW_COUNT |The number of active flows that are on fastpath|
