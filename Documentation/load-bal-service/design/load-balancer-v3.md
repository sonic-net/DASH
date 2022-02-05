# Fast Path (aka Load  Balancer)

## Overview

FastPath is the feature that switches traffic from using VIP-to-VIP 
connectivity (which involves transiting SLB MUXes), into using a direct
path between VMs (direct PA to PA path).

## Definitions

| Acronym | Definition |
|---------|------------|
| VIP     | Virtualized IP (load balanced IP). <br/> This is load balanced IP. |
| DIP/PA  | Physical Address / Directly Assigned IP. <br/> Actual physical address of the VM (underlay). |


## Architecture

![load-balancer-architecture](images/load-balancer-architecture.png)

## How it works?

1. The VM begins communicating with a Service (or other VM) using VIP connectivity.
    - Source IP: VIP (of the source VM).
    - Destination IP: VIP (of destination service/VM).
    - In this case traffic in both directions transits SLB MUXes.

1. When traffic destined toward the VIP lands on SLB MUX (SYN packet), the MUX picks the actual 
destination VM (from a list of healthy VMs in the backend pool). 
It should redirect the packet accordingly (standard load balancing functionality).

    Once the VM is selected, the SLB MUX forwards the packet to the destination VM.

1. The SLB MUX (in addition to forwarding packet to destination) **may** (often is!!!) 
sending the ICMP redirect packet towards the source VM from which the SYN packet originated.

    This ICMP redirect will have information that the SLB MUX selected specific destination VM (will have VM PA information).

1. The Source side (currently VFP) listens for ICMP redirect packets, and once received 
performs "flow fixup" (updates the flow to redirect next packets not to Destination VIP, 
but directly to the Destination PA/DIP that arrived in the ICMP redirect packet from SLB MUX).

1. Once flow is "fixed up", the next packets are direct and bypass the SLB MUX in that direction. 
This achieves high performance, as after initial connection handshake (SYN, SYN+ACK, ACK), the remaining 
traffic is direct between VMs and does not transit the SLB MUXes.

**Notes**

-   Two (2) MUXes are used for the VIP to VIP traffic.\
    The Destination SLB MUX is used to advertise destination VIP.\
    The Source SLB MUX is used to advertise the return VIP of the VM (to
    which VM SNATs the outbound traffic).

-   Each SLB MUX *may* send ICMP redirect independently.

-   Receiving ICMP redirects from single SLB MUX means that *only flows
    about that specific VIP* (either destination or source VIP) must be
    "fixed up" (updated to point to PA instead of VIP).

-   ICMP redirect is sent by SLB MUX to both: source VM and destination
    VM.

-   It is not guaranteed that SLB MUX will send ICMP redirect packets.

-   It is not guaranteed that ICMP redirect packet will be sent after
    initial SYN (it might be sent later).

-   The ICMP redirect packet might get *lost* (SLB MUX will resend it
    when next packet arrives on the SLB MUX and still uses VIP) *or
    possibly duplicated* (multiple packets that have VIP might arrive on
    SLB MUX, and SLB MUX may send ICMP redirect for all the packets that
    it receives as still using VIP).

## Packet signatures

- TCP handshake uses VIP (52.184.168.32)

    ![TCP-handshake](images/TCP-handshake.png)

- ICMP Redirect packet

    ![ICMP-redirect.png](images/ICMP-redirect.png)

- After the ICMP redirect, the packets start using DIP/PA (100.110.225.76)

    ![after-ICMP-redirect](images/after-ICMP-redirect.png)

## Packet transformation

![packet-transform](images/packet-transform.png)
