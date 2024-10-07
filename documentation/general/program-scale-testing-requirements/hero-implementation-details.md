# Hero test from theory to practice

## Introduction

Hero test is a synthetic test designed to stress the device under the worst-case scenario. Reality is that worst case scenario for device A need not always equal the worst case for device B. Moreover, vendors aim to present both the best and worst cases, not only the worst ones. Since the predicted performance in production will likely fall somewhere between the best- and worst-case scenarios, knowing the lower and upper bounds will give a solid idea of how well the device performs. This makes knowing both the best- and worst-case scenarios valuable.

For this reason, the Hero Test implementation is actually a collection of tests that gather multiple datapoints.

As philosophy goes for the Hero test suite of tests we believe it is important not to provide a PASS/FAIL but a characterization of the hardware with multiple data points and let each individual decide based on data if the hardware is suitable for their deployment scenario or not. (Functionality is assumed to be working, and the purpose here is to assess performance.)

## Life cycle

### Hardware and setup bring up

#### Common topologies:

The end objective is to test the smart switch, but we can start testing much earlier by using a standalone DPU or by combining a switch with an appliance. 

###### stand alone DPU

Comes in form on a PCIE card. Small in size, lower price, easy to ship, already available. Used for the initial testing and validation of a single ASIC.

###### appliance

An enclosure/server hosting multiple DPUs. Combined with a switch can provide a deployment with off the shelf components for an out of server solution.

###### smart switch

Fully integrated solution of a switching ASIC with multiple DPU ASICs. 


#### Test Tools packet generator (Keysight version)

Using the Keysight (Ixia) packet generator is one way to test the smart switch. For TCP traffic, we use CloudStorm & IxLoad, and for UDP traffic, we use Novus & IxNetwork, with UHD Connect blending everything together.

https://github.com/sonic-net/sonic-mgmt/blob/master/docs/testbed/README.testbed.Keysight.md 
https://www.keysight.com/us/en/products/network-test/network-test-hardware/cloudstorm-100ge-2-port.html
https://www.keysight.com/us/en/products/network-test/network-test-hardware/novus-qsfp28-1005025ge.html
https://www.keysight.com/us/en/product/944-1188/uhd400t.html
https://www.keysight.com/us/en/products/network-test/network-test-hardware/xgs12-chassis-platform.html

The hardware requirements vary according to the performance of the device. The current DASH requirement specifies 24M CPS as minimum requirements, but each vendor wants to showcase how much more they can do so based on that plus adding a 10%-20% for the headroom we can determine how much hardware is required. 

### Putting everything together

#### Cables

The most economical option is to use DAC cables, although optical fibers will be needed if the equipment is in separate racks. Breakout cables 1x400G to 4x100G are also used to connect the UHD400C to Novus and CloudStorm.

#### Layer 1 considerations

- Device port speeds for DASH are 100G or 200G or 400G, PAM4 or NRZ are UHD400C device port speeds are 100G or 200G or 400G, PAM4 or NRZ so far the 2 should interface with no issues.
- IEEE defaults autonegotiation is preferable but at a minimum if AN is disabled please ensure FEC is enabled. With FEC disabled we observed few packet drops in the DACs and that can create a lot of hassle hunting down a lost packet that has nothing to do with DASH performance.  

#### Testbed examples

Few examples below with 100G cables, with 400G cables with fan-out cables, single DPU or appliance or smart switch.

Example of a testbed for smart switch testing with:
- 4x 400G links from test gear to the smart witch for a total of 1.6T
- 9x 400G to 4x100G fan-out cables between the UHD400C and CloudStorm and Novus load modules

![testbed1](./testbed1.svg)

Example of testbed for appliance or standalone DPU testing
- all connected via 100G DAC cables
- physical connections between many DPUs and UHD400C allow us to route traffic to the one we wish to test at that time via configuration.

![testbed2](./testbed2.svg)

Example of smart switch testbed with all 100G DAC cables

![testbed3](./testbed3.svg)


>**NOTE**: At this point all hardware should be in the lab powered on, accessible via IP and have link up on all the interfaces.

### Programming the DPU:

At this moment we can program the DPU in 3 ways.
- via DASH API, it assumes a full SONiC stack is present and functional. (preferred method) 
- via SAI API it assumes at least one of the SAI redis or SAI thrift interfaces are available. (intermediary method)
- via vendor specific private API (used in the early development cycle before SAI or DASH is available)

This is a test in its own right and validates:
- API support, single calls as well as bulk calls
- how fast can a full dash configuration be loaded
- how memory efficient the DASH implementation is (for holding such a large configuration)

The full DASH configuration for the Hero test in json format can be anywhere between 10G and 20G in size adding stress on memory and compute during load time.

### "1 IP" test

Minimum configuration possible to run traffic through. 

#### Objectives

##### validate the hardware and software. 

- It ensures we can configure the DPU
- It ensures we can configure the NPU (if present)
- Validates 1 flow/connection working end to end from traffic generator through the device under test and back.

##### can also provide best case scenario performance numbers

Not always, but occasionally, this test also yields the best-case scenario values because the best case scenario is frequently reached at the lowest scale.


### Baby Hero test

It is meant to be an intermediary step between the 1 IP test and the Hero test. 

We try to keep the scale at ~1% of the Hero test by using only one prefix per ACL instead of 100

| Metric                       | Baby Hero | % of HERO  |
|------------------------------|-----------|------------|
| VNIs                         | 32        | 3%         |
| ENIs                         | 32        | 100%       |
| NSGs per ENI                 | 10        | 100%       |
| NSGs                         | 320       | 100%       |
| ACL rules per NSG            |  1,000    | 100%       |
| ACL rules                    |  320,000  | 100%       |
| ACL prefixes per ACL rule    | 1         | 1%         |
| ACL prefixes                 |  320,000  | 1%         |
| ACL ports                    | NA        | 0%         |
| VNETs (Outbound)             | 32        | 100%       |
| Outbound routes per ENI      | 5K        |            |
| Outbound routes              | 160K      | 5%         |
| CA-to-PA mapping (Outbound)  | 80320     | 1%         |
| Inbound Routes per ENI       | 1         | 0%         |
| Inbound Routes               | 32        | 100%       |
| PAs (Inbound PA Validation)  | 32        | 100%       |


### In between scale

Before the final solution is finished, we can add another checkpoint to collect further data if the Hero test scale numbers are not fulfilled.
This will have custom scale values agreed upfront by all the parties and constitute an intermediary point in the DASH development.
Usually becomes irrelevant as soon as the Hero test scale is achieved.

### Hero test

The test exactly as specified in the DASH requirements.

### Best case scenario

If we can find a scenario where we obtain better performance numbers then the numbers previously obtained during (1ip, baby hero, hero test, etc) will be added as a new data point to the results.

### Worst case scenario

If we can find a scenario where we obtain lower performance numbers then the numbers previously obtained during (1ip, baby hero, hero test, etc) will be added as a new data point to the results.


## Metrics

Besides CPS we actually collect for all those different scale points multiple metrics.

### PPS

PPS (packets per second) is the first metric we collect. UDP packets are usually used.
Packets must be as small as possible, so we do not to hit link speed constraints.
This test shows the fast path performance.

### Latency

Latency is the time it takes for a packet to go through the device under test.

Latency value is most accurate when we have the highest PPS, smallest packet, and zero packet loss. and is measured using IxNetwork and Novus card.

When testing the smart switch we have to run a test to get the switch latency without running the traffic through the DPU and then get the total system latency with the understanding that each packet travels once through the NPU to reach the DPU, then it travels through the DPU and once more it will travel through the NPU after it leaves the DPU. 

smart switch latency = 2 x NPU latency + DPU latency

Latency is mostly a metric for fast path performance. Since we collect min/avg/max, the maximum value in most cases will be impacted by the slow path. that first packet that arrives may have the highest latency.

If slow path latency is desired configure random source/dest ports this way each packet will be a new flow and will hit the slow path only. Care must be taken to send a fixed number of packets not exceeding the flow table size.

### Throughput

Throughput is the amount of data that can be sent through the device under test.

Set PPS to a value lower than the maximum PPS we measured in the previous test and increase the packet size until we reach the maximum throughput.

PPM may need to be adjusted between test gear and device under test to get that 100G or 200G or 400G perfect number.

Consider looking at UHD400C stats and when looking at IxNetwork/Ixload stats will show less because the vxlan header is added later by UHD so we are interested in packet size as it enters the DPU x pps to get the throughput.


### CPS

CPS (connections per second) this is a metric that shows the slow path performance, and we can get both TCP and UDP values.

For TCP we use IxLoad since it has a full TCP stack that is very configurable and can simulate a lot of different scenarios.

While the Hero test calls for 6 TCP packets SYN/SYNACK/ACK/FIN/FINACK/ACK, we make use of HTTP as necessarily that runs over TCP and on the wire, we will end up with 7 packets for every connection. 

PPS used for CPS test can be seen the L23 stats in IxLoad.

Keep an eye on TCP failures on client and server a retransmit is bad it symbolizes packet drop that was detected and the TCP stack had to retransmit. a connection drop is super extra bad it means even after 3-5 retries packet did not make it. 

We also look at the number of concurrent connections while the test is running. traffic generator puts on the wire equally time spaced SYN packets to match the desired CPS but the rest of communication happens as fast as possible. impacted by line rate and latency. in theory if line rate is high and latency is low the whole exchange of 7 packets could finish before the next SYN is sent resulting in 0 concurrent connections. (flow table will be 1), while a slow travel time for packets will result in connections that have not been terminated yet as new connections get initiated and this will result in a certain number of concurrent connections. Ideally we want to see the concurrent connections number as low as possible.

test tries to cycle through all the millions of IPs, the source port is chosen at random in a specified range and the destination port is fixed to 80

we can do variations like which side initiates the fin and see if we observe any differences in performance

for the UDP CPS slow path test use random source/dest ports and send a fixed amount of packets not exceeding the flow table size.

Note down the bandwidth utilized by the CPS test.

### Flow table size

The flow timer must be set to a very high value so flows do not expire during the test

For TCP we set the desired number of concurrent connections and make sure we have a transaction rate that is a bit faster than the flow timer to make sure flows do not expire.

for UDP we use random source/destination ports and we set rate to 100K PPS and for 32M flows it should work fine for 320 seconds. (32M flows / 100K PPS = it will take 320 sec for all flows to receive 1 packet and be inserted into the flow table)

we see here if the flow table can be filed to desired level.

one item to note here is to characterize what happens when the flow table is full. will it crash? will it drop anything after? will all the extra packets be processed as slow path?

### Background UDP flows


### Background UDP flows


### Hero test

Putting it all together and running the CPS test with background traffic.

Start first the background traffic and ensure the flow table is close to full but not full (need room for CPS), increase packet size to ensure bandwidth is utilized at 100% - bandwidth needed by CPS test - a 5%-10% margin

Run the CPS

Provided each component of the Hero test was run in isolation before it should all work when combined and provide performance numbers usually lower than the standalone CPS numbers

### Loss

It must be 0 (zero) but this is a hard topic and requires characterization that is vendor to vendor specific.

We gather few datapoints here:
- zero loss performance
- minimal loss performance (1 to thousands of packets lost). Why is this important? Let's say that we get 0 packets dropped at 100K CPS but whenever we try 200K CPS all the way to 5M CPS we get a random number of 1 to 10 packets dropped, and if we try 5.1M CPS we get 1 million packets dropped. yes the test requires 0 drops but instead of having a "if > 0  FAIL" we believe it is more valuable to provide a characterization and let everyone decide for themselves if this is acceptable for their deployment scenario or not.
- point after which everything gets lost

![loss](./loss.svg)


## The results

Results are presented as a graph trying to show a performance band, if the tests are done correctly the real performance in production should be somewhere in that band.

Ideally, the difference between the highest point and the lowest point should be as small as possible and the lowest point is above the minimum DASH requirements.

![results](./results.svg)

best case scenario is the scale and traffic profile where the hardware obtains the best performance numbers, the highest point in the graph.
worst case scenario is the scale and traffic profile where the hardware obtains the worst performance numbers, the lowest point in the graph.

