# Table of content

1. [Objectives](#objectives)
2. [Requirements](#requirements)
3. [Automation](#automation)
4. [Test Suites](#test-suites)
    - [Basic](#eni-creation)
    - [Ageing](#eni-removal)
    - [Performance](#eni-scale)

---

# Objectives

Verify proper functioning of the connection tracking mechanism: establishing, handling, closing connections.
Connection per Second (CPS) is the most important attribute of the DASH products.

# Requirements

| Item |	Expected value
|---|---
| Active Connections/ENI | 1M (Bidirectional)
| CPS per card | 4M+

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
    -  Based on packets forwarding - check whether packets are passed or dropped
    - Based on routing and ACL counters that are incremented on slow path. So when connection is established the counters should not be incremented.

# Test suites

## Basic

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | Basic positive TCP session verification with counters check | -
| 2 | Basic positive UDP session verification with counters check | -
| 3 | TCP session verification with fragmented packets | -
| 4 | UDP session verification with fragmented packets | -
| 5 | ICMP traffic. **to clarify** no session is expected? | -
| 6 | Same overlay IPs but different ENIs | -

## Ageing

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | Standard ageing (fully correct TCP session). | -
| 2 | Standard ageing (fully correct UDP session). | -
| 3 | Open TCP session but no data and no FIN | -
| 4 | TCP session started from the middle (no SYN packet) | -

## Integration

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | Inbound and outbound configuration in parallel | -
| 2 | Routes update during active session | -
| 3 | ACL update during active session | -
| 4 | Configuration removal during active session (Route, VNET, ENI removal) | -

## Performance

**TBD**

| # | Test case | Test Class.Method
| --- | --- | ---
| 1 | CPS | -
| 2 | Max sessions per ENI. (Verify resources clean up) | -
| 3 | Max sessions per card (multiple ENIs). (Verify resources clean up) | -

## Future

1. Add IPv6 tests
