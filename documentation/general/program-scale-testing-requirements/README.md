# Program Scale Testing Requirements for LAB Validation

>**NOTE**: This preliminary document includes a text description of a so-called **"Hero Test"** to establish minimum performance requirements and screen captures of Layer 2/3 packet generator stream configurations for IXIA IxExplorer packet tester device. These L23 streams simulate L4 connection establishment. This document, and the testing methodology, will be replaced by a more formal, complete requirements specification and  automated testing scripts in due time.

## Table of Contents

[Introduction](#introduction)

[Test Methodology and Definitions](#test-methodology-and-definitions)

[Feature Requirements](#feature-requirements)

[Policy and Route Requirements](#policy-and-route-requirements)

[Hero test implementation details](hero-implementation-details.md)


<hr/>

## Introduction

This document summarizes scale testing requirements for validating program deliverables.

This document will refer to Connection Per Second (CPS) capability as 5M
which correlates to 10M flow operations. This capability is a
placeholder for reference and the specific hardware supported value will
be used to evaluate different firmware drops.

What we are looking for in a series of testing is how well the NIC
handles:

1.  Connections/sec per ENI and per NIC
2.  Number of active connections per ENI and per NIC
3.  Number of flows per ENI and per NIC
4.  ENIs' connection pool can be oversubscribed. An oversubscription of 2:1 would be expected, so the connection pool can be more optimal if executed as one large table where ENI can be apart of the key. The connection table would be the most appropriate table for oversubscription scenarios.
5.  Throughput under max connections per second load with the remaining
    bandwidth is filled with pre-learned connections that receive at
    least one packet per second while driving the links to near 100%
    utilization. This requires some work up front to get the right mix
    of CPS and active connections with zero drops. **We do not accept
    results with drops as we cannot use that test to measure latency and
    jitter**. We therefore also run the test sufficiently long to see if
    there were any queue build-ups which would eventually lead to drops
    and distort both latency and jitter results.
6.  Aging of (TCP bi-directional connections) and (UDP bi-directional flows) such that
    after the test is complete all connections are aged within the 1
    second interval or any other interval we program.
7.  We are expecting to cover below scenarios as follow-on tests:

        a. Age arbitrary connections to verify that aging is also working
        properly under maximum load.

        b. Download new policies and delete old policies at a significant
        rate to ensure that CPS, Active Connections, Aging, and new
        Policies are properly handled with the external memory, which is
        often the bottleneck for performance.

Why are we running these tests?

1.  Many NICs require software to inspect the SYN/ACK/ACK and
    FIN/ACK/ACK packets of a connection. The software is responsible for
    the formation, deletion connection and forwarding table entries
    after significant and complex cloud policy enforcement along with
    any associated accounting. Software based connection management
    often results in poor connections/second with limits in the 10s of
    thousands/sec. The set of test and associated table parameters found
    in this document are designed to find the maximum CPS with the
    maximum number of connections all actively receiving packets every
    second. The more that is done in specialized hardware the more we
    expect the CPS to increase. **Any NIC for the application that
    cannot achieve millions of connections/sec will automatically be
    disqualified from further testing.**
2.  Many NICs can create (a large number) of connections simply by
    adding more external memory for the connection table. For example, a
    NIC can create 1M connections in its external table, however if
    packets arrive across the entire connection set in a random order,
    it forces the NIC out of its internal **connection cache** and to
    use the external connection table instead. Under this condition we
    have measured some NICs to achieve 10% advertised link throughput.
    The testing below will ensure this condition is exercised and
    provide the true worst-case throughput that is reflective of some
    real-world conditions like firewalls, load balancers, DDoS,
    v-routers etc. **It should also be noted that creating a connection
    in a table that never receives a subsequent packet (other than
    keepalives once every few minutes) is referred to as an idle
    connection and is a useless parameter that should never be
    advertised and will not be tested other than for conformance.**
3.  Aging is also a vital component of tracking connections. Even under
    the worst load the system must be able to age connections. All
    packets will require either connection setup/teardown or policy
    lookups/updates involving external memory and hence the memory
    management of the connection table is extremely important. The tests
    in this document will ensure that no matter what processing is going
    on, the connection table will be maintained providing the proper
    aging intervals to each connection.
4.  We need to be able to enter/delete many new policies at any time
    regardless of load. For this reason, we will run the test without
    updates to policy to get a baseline and then again with some
    extensive policies being added/deleted during the same test. We will
    look for any regressions while adding/deleting policies at a
    significant rate. This matches the real-world requirement of adding
    and deleting VMs to a node or to the VNET.

In the end we are looking for total invisibility for the end customer.
Customers are used to their NICs in the enterprise forwarding at
Layer-3. Most NICs and switches can do this at wire rate under a wide
variety of conditions. When the customer enters the cloud, they expect
the same behavior. When they setup their solution for the first time,
often, they will not see the same performance and in the worst case will
have to totally re-architect their already working solutions with a
scale-out model. This means that their hybrid and cloud architectures
will diverge and create a large amount of extra work for IT or solution
integrators to track and test the designs in a common manner.

## Test Methodology and Definitions

-   **CPS**: Sustained Connections Per Second. 5M and 10M flows are only
    placeholders and will be determined by the supplier as each
    implementation will vary depending on the maturity of the DASH
    design.

    -   5M CPS means that 5M new connections are established and
        destroyed over a one second interval.

    -   Every connection consists of two flows hence 5M new connections
        mean:

        -   10M flow additions every second to insert connections.

        -   10M flow deletions every second because of expiry of old
            connections which will also allow capacity for new
            connections to be formed in the next second.

        -   20M total flow operations every second

    -   5M CPS is a "per card" goal. Card must be able to sustainably
        handle 5M CPS irrespectively if either single ENI is configured
        on a card or multiple ENIs are configured. Total CPS per card
        must always be reaching same 5M goal, and this goal must not be
        degraded if card will have multiple ENIs programmed with
        different policy each. Same goes for total flows supported on a
        card.

-   **Test Runtime**: 100 seconds. We feel this is sufficient time to
    pick up any anomalies the NIC may have running interval tasks
    unknown to the tester.

-   **Effective CPS**: CPS results over 100 seconds by the Ixia
    setup/teardown rates, however, will not be accepted if there are any
    drops for any reason. Drops end up deviating the true latency and
    jitter numbers.

-   **Performance Testing Methodology**:

    -   15M TCP background connections setup before testing.

    -   15M UDP background bi-directional flows setup before testing.

    -   We use an equal mix of TCP and UDP although in the real world we
        expect more TCP and in fact in some cases we meter UDP as a
        potential source of DoS.

    -   Connection aging set to 5 sec and requires each connection or
        bi-directional flow to receive one packet every 4.9 seconds in each
        direction at a size that will fill up the links to near 100% in
        conjunction with the dynamically setup connection traffic. For
        this to be run successfully it may take a few runs as each TCP
        connection setup and teardown takes 6 packets.

    -   For UDP a bidirectional flow is created for the first packet
        seen that meets the policy for the bi-directional flow setup.
        When using this in CPS testing, we will send a total of 6
        packets to match TCP to make things more balanced. UDP
        bi-directional flows will be aged within 5 second after
        receiving the last packet. I would set all UDP bi-directional
        flows to 5 seconds aging to ensure that we do not inflate
        the connection table over time.

    -   One packet should be sent in each direction to be able to keep
        connections active in the flow table. Packet size should be set
        to a minimum that allows 6 CPS packets at maximum rate and at
        least one packet on each of the active connections in both
        directions that also allows for close to 100% link utilization
        while not exceeding the TCP aging time of 5 sec.

    -   TCP connection is established and terminated without any data
        packets.
        -   Real use case
        -   6 packets: SYN, SYN-ACK, ACK, FIN, FIN-ACK, ACK
        -   Flow Table Size: (2 \* CPS) + 15M + 15M
            //For 5M CPS, Flow Table Size: (2 \* 1000) + 15M + 15M = ~30M
        -   Effective PPS: Sustained CPS \* 6 + PPS for background flows.

-   CPS and flow results will be measured while channel bandwidth is
    saturated at 100Gbps for the duration of test runtime. At the same
    time we want as close to 100Gbps without losing packets.

-   Inactivity based aging timer of 5 second.

    -   All TCP connections should be deleted from the table after the
        test completes.

    -   The connection table should therefore be zero.

    -   All UDP bi-directional flows need to age out before the 5 second
        interval to allow for new UDP bi-directional flows to be
        established. If everything works as advertised, we should never
        see the connection table go above the 32M connections. If we do
        then it is likely that UDP bi-directional flows were not aged
        within the 5 second interval. To check this, we need to see a
        high water counter for maximum connection table size.

## Feature Requirements

The following features are required to be enabled during scale testing:

-   VNET
    -   VXLAN-IN and VXLAN-OUT
    -   Encap based on lookup table, which can change/be updated
        similarly as ENI policy

-   UDR

    -   200k routes per ENI with:
        -   MAC rewrite
        -   VNID rewrite
        -   DSCP rewrite

-   ACL
    -   3-level NSG on connection (receive/transmit) in accordance with
        the Packet Transformation document detailing our unique NSG
        requirements.

    -   For clarity, the first NSG is used by Azure to set policy for
        the connection while the next two NSGs are set by the customer.
        Think of it as a customer building their own firewall rules to
        control which VMs can communicate with any other VM with a
        unique set of policies. This allows the customer to setup the
        VMs with similar control they would have in their own
        enterprise. We cannot prevent the customer from forming complex
        policy sets. They will likely use similar policies they use in
        their own environment.

        -   NSG on VNET, vport, subnet both on ingress and egress
            traffic
        -   100k SIP prefixes/ranges per policy
        -   100k DIP prefixes/ranges per policy

-   Metering

    -   <span style="color:red">Enabled on all routes in all v-ports (Currently 15 classes are
        supported)</span>.

-   QoS per ENI BW

-   VNET Peering

## Policy and Route Requirements

The following scale of policies and routes are at minimum required to be
configured during validation and test plan needs to be executed covering
both scenarios:

|                     | per ENI    | 200G (DPU)  | 400G  | 800G  | 1.6T (smart switch) |
|---------------------|------------|-------------|-------|-------|-------|
| VNETs               |            | 1024        | 2048  | 4096  |  8192 |
| ENIs                |            | 32          | 64    | 128   |  256  |
| Outbound Routes     | 100K       | 3.2M        | 6.4M  | 12.8M | 25.6M |
| Inbound Routes      |  10K       | 320K        | 640K  | 1.28M | 2.56M |
| NSGs                | 5in + 5out | 320         | 640   | 1280  | 2560  |
| ACLs prefixes       | 10x100K    | 32MM        | 64M   | 128M  | 256M  |
| ACLs Ports          | 10x10K     | 3.2M        | 6.4M  | 12.8M | 25.6M |
| Mappings (CA to PA) | NA[^1]     | 8M          | 16M   | 32M   | 64M   |
| Act Con             | 1M         | 32M[^2]     | 64M   | 128M  | 256M  |
| CPS                 |            | 3M          | 6M    | 12M   | 24M   |
| bg flows TCP        |            | 15M[^2]     | 30M   | 60M   | 120M  |
| bg flows UDP        |            | 15M[^2]     | 30M   | 60M   | 120M  |


[^1]: per ASIC numbers, can be distributed in any way to each ENI
[^2]: flows are bidir w/ connection pool capable of oversubscription

- ACL rules per NSG = 1000
- Prefixes per ACL rule = 100
- Prefixes mapped per ACL rule = 16
- Prefixes routed per ACL rule = 84
- Routes per ACL rule = 10
- -> Change Above:  NSG per ENI changed since 5 Inbound & 5 Outbound stages are required


