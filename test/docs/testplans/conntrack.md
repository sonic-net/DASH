# Table of content

1. [Objectives](#objectives)
2. [Requirements](#requirements)
3. [Automation](#automation)
4. [Test Suites](#test-suites)
    - [Basic](#basic)
    - [Ageing](#ageing)
    - [Performance](#performance)

---

# Objectives

Verify proper functioning of the connection tracking mechanism: establishing, handling, closing connections.
Connection per Second (CPS) is the most important attribute of the DASH products.

# Requirements

| Item               | Expected value           |
|:-------------------|:-------------------------|
| Active Connections | 1M per ENI (Bidirectional, +oversubscription capabilities)       |
| CPS                | 4M+ per card                      |
| bg TCP flows       | - |
| bg UDP flows       | - |

**To clarify**
1. Ageing time

# Automation

Test cases are automated:
1. Functional - using SAI PTF test framework.
1. Scale/Performance - to be defined.

## Automation notes

1. Each test should be executed using TCP and UDP streams.
1. Each test should be executed for Inbound and Outbound routing scenario.
1. So far there is **no direct API to get active connection number** or CPS. Verification might be done using indirect ways:
    - Based on packets forwarding - check whether packets are passed or dropped
    - Based on routing and ACL counters that are incremented on slow path. So when connection is established the counters should not be incremented.

# Test suites

## Basic

|  #  | Test case purpose                                           | Test Class.Method                                                                                                                                                        | Test description                                                                                                                                                                                                          |
|:---:|:------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  1  | Basic positive TCP session verification with counters check for VNET Outbound Routing. | `ConnTrackOutboundSessionTest.`<br/> `connTrackOutboundTcpSessionTest`                                                                                                     | Creates single ENI outbound configuration. Verifies connection tracking with bidirectional TCP traffic and counters verification.                                                                                          |
|  2  | Basic positive TCP session verification with counters check for VNET Inbound Routing. | `ConnTrackInboundSessionTest.`<br/> `connTrackInboundTcpSessionTest`                                                                                                   | Creates single ENI inbound configuration. Verifies connection tracking with bidirectional TCP traffic and counters verification.                                                                                         |
|  3  | Basic positive UDP session verification with counters check for VNET Outbound Routing. | `ConnTrackOutboundSessionTest.`<br/> `connTrackOutboundUdpSessionTest`                                                                                                   | Creates single ENI outbound configuration. Verifies connection tracking with bidirectional UDP traffic and counters verification.                                                                                         |
|  4  | Basic positive UDP session verification with counters check for VNET Inbound Routing. | `ConnTrackInboundSessionTest.`<br/> `connTrackInboundUdpSessionTest`                                                                                                     | Creates single ENI inbound configuration. Verifies connection tracking with bidirectional UDP traffic and counters verification.                                                                                          |
|  5  | TCP session verification with fragmented packets            | -                                                                                                                                                                        | -                                                                                                                                                                                                                         |
|  6  | UDP session verification with fragmented packets            | -                                                                                                                                                                        | -                                                                                                                                                                                                                         |
|  7  | ICMP traffic for VNET Inbound routing. **to clarify** no session is expected? | `ConnTrackInboundSessionTest.`<br/> `connTrackInboundIcmpSessionTest`                                                                                                    | Creates single ENI inbound configuration. Verifies connection tracking with bidirectional ICMP traffic (echo request & reply) and counters verification.                                                                  |
|  8  | ICMP traffic for VNET Outbound routing. **to clarify** | `ConnTrackOutboundSessionTest.`<br/> `connTrackOutboundIcmpSessionTest`                                                                                                  | Creates single ENI outbound configuration. Verifies connection tracking with bidirectional ICMP traffic (echo request & reply) and counters verification.                                                                 |
|  9  | Same overlay MAC/IP but different ENI, Inbound Routing. | `ConnTrackInboundSameOverlayIpDiffEniTest.`<br/>`verifyEni0TcpSessionTest`<br/>`verifyEni0UdpSessionTest`<br/>`verifyEni1TcpSessionTest`<br/>`verifyEni1UdpSessionTest`  | Creates two the same ENIs with same MAC addresses and different VNIs. Creates the same Inbound configuration for ENIs.<br/> Verifies connection tracking with bidirectional TCP & UDP traffic and counters verification.  |
| 10  | Same overlay MAC/IP but different ENI, Outbound Routing. | `ConnTrackOutboundSameOverlayIpDiffEniTest.`<br/>`verifyEni0TcpSessionTest`<br/>`verifyEni0UdpSessionTest`<br/>`verifyEni1TcpSessionTest`<br/>`verifyEni1UdpSessionTest` | Creates two the same ENIs with same MAC addresses and different VNIs. Creates the same Outbound configuration for ENIs.<br/> Verifies connection tracking with bidirectional TCP & UDP traffic and counters verification. |

## Ageing

|  #  | Test case purpose                                                                  | Test Class.Method                                                                   | Test description                                                                                                                                                                                                                                                                 |
|:---:|:-----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  1  | Verify standard ageing (fully correct TCP session).   | `ConnTrackInboundSessionAgeingTest.`<br/> `connTrackInboundTcpStandardAgeingTest`   | Creates single ENI inbound configuration. Bidirectionally send TCP packets needed for standard TCP session start and termination.<br/> Send TCP inbound packet to verify session is terminated and packet is dropped immediately after last TCP termination packet.               |
|  2  | -//- (but VNET Outbound Routing)                      | `ConnTrackOutboundSessionAgeingTest.`<br/> `connTrackOutboundTcpStandardAgeingTest` | Creates single ENI outbound configuration. Bidirectionally send TCP packets needed for standard TCP session start and termination.<br/> Immediately after last TCP termination packets sends TCP outbound packet to verify session is terminated and packet dropped.             |
|  3  | Verify standard ageing (fully correct UDP session). | `ConnTrackInboundSessionAgeingTest.`<br/> `connTrackInboundUdpStandardAgeingTest`   | Creates single ENI inbound configuration. Bidirectionally send UDP packets. Wait default ageing time for session termination.<br/> Send UDP packet to verify session is terminated and packet is dropped after default ageing time.                                    |
|  4  | -//- (but VNET Outbound Routing)                      | `ConnTrackOutboundSessionAgeingTest.`<br/> `connTrackOutboundUdpStandardAgeingTest` | Creates single ENI outbound configuration. Bidirectionally send UDP packets. Wait default ageing time for session termination.<br/> Immediately after default ageing time sends UDP packet to verify session is terminated and packet dropped.                                   |
|  5  | Verify custom ageing (fully correct TCP session).     | -                                                                                   | -                                                                                                                                                                                                                                                                                |
|  6  | Verify custom ageing (fully correct UDP session).     | -                                                                                   | -                                                                                                                                                                                                                                                                                |
|  7  | Verify open TCP session but no data and no FIN.       | `ConnTrackInboundSessionAgeingTest.`<br/> `connTrackInboundTcpAgeingTest`           | Creates single ENI inbound configuration. Bidirectionally send TCP packets needed only for TCP session start. Wait default ageing time for session termination.<br/> Immediately after default ageing time sends TCP packet to verify session is terminated and packet dropped.  |
|  8  | -//- (but VNET Outbound Routing)                      | `ConnTrackOutboundSessionAgeingTest`.<br/> `connTrackOutboundTcpAgeingTest`         | Creates single ENI outbound configuration. Bidirectionally send TCP packets needed only for TCP session start. Wait default ageing time for session termination.<br/> Immediately after default ageing time sends TCP packet to verify session is terminated and packet dropped. |
|  6  | Verify TCP session started from the middle (no SYN packet). | -                                                                                   | -                                                                                                                                                                                                                                                                                |

## Integration

|  #  | Test case purpose                                                             | Test Class.Method                                                                                                                                                                             | Test description                                                                                                                                            |
|:---:|:------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  1  | Verify Inbound and outbound configuration in parallel                         | `ConnTrackInboundOutboundParallelConfigsTest.`<br/> `verifyOutboundTcpSessionTest`<br/> `verifyInboundTcpSessionTest`<br/> `verifyOutboundUdpSessionTest`<br/> `verifyOutboundUdpSessionTest` | Creates Inbound and Outbound configuration on single ENI.<br/> Verifies connection tracking with bidirectional TCP & UDP traffic and counters verification. |
|  2  | Verify Routes update during active session                                    | -                                                                                                                                                                                             | -                                                                                                                                                           |
|  3  | Verify ACL update during active session                                       | -                                                                                                                                                                                             | -                                                                                                                                                           |
|  4  | Verify configuration removal during active session (Route, VNET, ENI removal) | -                                                                                                                                                                                             | -                                                                                                                                                           |

## Performance

**TBD**

|  #  | Test case                                                          | Test Class.Method | Test description |
|:---:|:-------------------------------------------------------------------|:------------------|:-----------------|
|  1  | CPS                                                                | -                 | -                |
|  2  | Max sessions per ENI. (Verify resources clean up)                  | -                 | -                |
|  3  | Max sessions per card (multiple ENIs). (Verify resources clean up) | -                 | -                |

## Future

1. Add IPv6 tests
