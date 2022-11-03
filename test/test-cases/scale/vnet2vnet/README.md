# VNET to VNET 

The SONiC-DASH testbed provides a common test platform to examine an extensive collection of test cases and allow ease of duplication and modification.  The directory structure is arranged for configuring a variety of test SKUs and to reduce testing design time.

The files found within this directory serve the following purpose:
1. Define a guide for expanding DASH test scenarios.
2. Generate `packets per second` and `connections per second` benchmarks all driven from PyTest.


# test cases

| Test case                                      | Description                                               |
| ---------------------------------------------- | --------------------------------------------------------- |
| [vxlan_1eni_1ip](one-ip)                       | minimum possible config                                   |
| [vxlan_8eni_48k_IPs](48K-ips)                  | medium sized config                                       |



# minimum possible config
1 src ip , 1dst ip, 1 UDP port, 1 eni ...... 1-2 flow(s)

Intent here is to create the smallest, most basic config that will get UDP traffic to pass through in both directions.

This will prove the basic functionality is there.

Based on the design of the implementation this test will usually be able to give us also the best or the worst performance numbers.

obtain PPS and latency numbers

# minimum possible config, add few UDP ports
This builds on top of the previous test.

Intent here is to get closer to reality where we will have more than 1 flow at a time.

For highly parallel implementations have 1 flow per processing unit and it should provide the best performance numbers. 

obtain PPS and latency numbers

# minimum possible config, with random src and dest UDP ports
builds on top of minimum possible config, but since we have 65K possible source and 65K possible destination ports, we can generate 4 billion unique flows.

this test can be ran in 2 ways.

keep the flow expiration timer at 1 sec and see what is the device flow install rate.

keep the flow expiration timer at `big number` and see how many flows can be installed before device starts misbehaving.

  - is performance slowly degrading ?
  - is performance all of a sudden degrading drastically?
  - will the device crash?
  - will the device recover and return to good performance/functionality once the flows expire and flow tables are not full anymore?

# minimum possible config, cps test
This test will find the highest CPS by counting the aggregate number of connections established.
- Test uses a binary search algorithm to step up or down the CPS objective



# 48K IPs "baby hero", UDP test
this has full hero test config with 8 ENIs, 6 NSGs per ENI, 1000 ACL policies per NSG, with the only exception that it has only 1 prefix per ACL policy instead of ~200

half of ACLs are allow half are deny with alternating IPs

24K flows will be created over allowed IPs and 24K flows will be sent over the deny IPs

this test will verify that:
  - configuration can scale
  - see the scale impact on performance from the minimum config
  - see that allow/deny ACLs are respected

# 48K IPs "baby hero", tcp test
traffic will be sent over the 24K allowed IPs

test will have full 5M+1M tcp sessions by making use of tcp ports

connection rate value will be observed while maintaining 6M concurrent sessions

# few others upcoming tests
  - mix of tcp and UDP in same test
  - full hero test
  - IPv6 version of the tests
  - IPv4 with IPv6 mix, 25% IPv4, 25% IPv6, 25% IPv4 over IPv6, 25% IPv6 over IPv4
  - ...
# VNET to VNET 

The SONiC-DASH testbed provides a common test platform to examine an extensive collection of test cases and allow ease of duplication and modification.  The directory structure is arranged for configuring a variety of test SKUs and to reduce testing design time.

The files found within this directory serve the following purpose:
1. Define a guide for expanding DASH test scenarios.
2. Generate two test outcomes using separate traffic generation tools and collecting results using one testing framework: PyTest.
3. Demonstrate testbed setup requires minimum configuration as the test platform provides tools and configuration out of the box.
4. Test one seeks to find the maximum capability of the device under test to measure the raw bandwidth by identifying the Packets Per Second.
5. Test two's goal is to discover the maximum number of functioning connections that can be established per second.


# test cases

| Test case                                      | Description                                                    |
| ---------------------------------------------- | -------------------------------------------------------------- |
| [vxlan_1vpc_1ip](one-ip/README.md)             | performance numbers for best case scenario                     |
| [vxlan_8vpc_48K-ips](48K-ips/README.md)        | performance with an objective of maintaining 6M parallel flows |
