# High-Level Design Document for SONiC-DASH Testing
This document provides the high-level design for the testing of devices which conform to the SONiC-DASH requirements.

> **TODO** Consider [SONiC Management Testbed](https://github.com/Azure/sonic-mgmt/blob/master/docs/testbed/README.testbed.Overview.md) as the standardized test environment for consistency with standard SONiC testing. The reference architectures depiected below were crafted to expedite early dataplane testing in the simplest possible fashion.

> **TODO** Articulate the testing of both dataplane and control plane features. The descriptions below focus on dataplane testing as the critical path towards DASH conformance and performance.

# Reference Testbed Architecture - Single DUT

**Figure 1. Testbed Reference Architecture**

![dash-testbed-ref-arch.](../images/dash-testbed-ref-arch.svg)

The reference architecture, See Figure 1, contains the following elements.


* **DUT** or **SUT** - the device(s) or system(s) being tested.
* **DUT Host/Chassis/Fixture** - If the DUT consists of a NIC Card, it will need a chassis or fixture to provide, at a minimum, system power. For the sake of testing a DUT, the DUT "Host" is not part of the test. Note, the DUT could conceivably be installed in the test System Controller, provided there is no degradation or impact upon the testing results.
* **Test System Controller** or just **Controller** - a compute server running in a physical, virtual or cloud-hosted environment which runs the tests by configuring DUTs, applying stimulus directly or via test packet generators, gathering test result data, analyzing the data and reporting results.
* **Test Traffic Generator/Receiver** or just **TGen** - A tester which sends and receive packets to/from the device under test, commanded by the Test System Controller. It is possible that the TGen can be combined in the Controller, e.g. a server with a suitable network interface can act as the test controller *and* traffic generator, as long as the capabilities of the embedded TGen meet the performance requirements of a particular test. This detail does not affect the roles of each element.
* **Traffic Interfaces** or **Ports** - physical network interfaces which carry traffic between the production network traffic ports and the Traffic generator (acting in lieu of a "real" network or datacenter infrastructure).
* **Traffic Cabling** - Physical cables connecting the DUT with the TGen.
* **DUT Configuration/Management Interfaces** or **APIs** - Socket-based RPCs between the Test System Controller and the Device Under test, used to configure and query the device.
* **DUT API Endpoints** - Server IP address:port(s) on the device (or a [Proxy API Endpoint Server](#proxy-api-endpoint-server)) which listens for RPC messages from the Test System Controller.

## Physical Configurations for DUT API Endpoints
Figure 1 depicts a conceptual DUT API endpoint but does not specify the actual physical means of connecting the Test Controller with the Endpoint. These endpoints may be reachable via different physical means, for example:
* Out-of-band management Ethernet port
* Out-of-band device-driver (PCIe bus))
* In-band (using one or more traffic ports)
* Proxy Server

A DUT might implement one or more of these simultaneously. DUT suppliers must provide a way to establish a connection between the Test Controller and the API endpoint(s) such that the Test Controller has a consistent socket interface. Test fixture setup should be easily automatable without special coding on the test framework and main test scripts. Suppliers must provide easy-to-use fixture setups which can be invoked by automated test pipelines.

### Out-of-Band DUT API Endpoint via Dedicated Physical Interface
This configuration is depicted in Figure 2 and uses a dedicated physical management port for API control of the DUT, e.g. an RJ-45 Ethernet jack on the DUT panel.

**Figure 2. Out of Band Access to DUT API Endpoint via Physical Interface**

![dash-testbed-out-of-band-api.](../images/dash-testbed-out-of-band-mgmt.svg)

### Out-of-Band DUT API Endpoint via PCIe Interface
This configuration is depicted in Figure 3 and uses a "virtual" management port for API control of the DUT, e.g. a network interface device driver operating over the PCIe bus. The test controller communicates to the endpoint via the device's assigned IP address. The host operating system takes care of routing to the endpoint.

**Figure 3. Out of Band Access to DUT API Endpoint via PCIe Device Driver**

![dash-testbed-out-of-band-api-via-iface.](../images/dash-testbed-out-of-band-via-iface.svg)

### In-Band DUT API Endpoint via Traffic Generator
This scenario uses a DUT traffic port(s) to convey both production traffic and API RPC traffic, and the traffic generator acts as a switch to combine and separate the flows. The test controller sends API traffic into the Traffic Generator management port (or equivalent), and the Traffic Generator combines this with test traffic into the DUT's traffic port. The reverse happens in the opposite direction. Figure 4 illustrates conceptually how this might work. The encapsulation/switching method is not stipulated, but could be e.g. via VLAN tagging.

**Figure 4. Inband Access to DUT API Endpoint Via Traffic Generator**

![dash-testbed-inband-api.](../images/dash-testbed-inband-via-tgen.svg)


### In-Band DUT API Endpoint via External Switch
This scenario uses a DUT traffic port(s) to convey both production traffic and API RPC traffic, and an external switch combines and separates the flows. The test controller sends API traffic into the switch, which combines this with test traffic into the DUT's traffic port. The reverse happens in the opposite direction. Figure 5 illustrates conceptually how this might work. The encapsulation/switching method is not stipulated, but could be e.g. via VLAN tagging.

**Figure 5. Inband Access to DUT API Endpoint Via Traffic Generator**

![dash-testbed-inband-api.](../images/dash-testbed-inband-via-switch.svg)

### Proxy API Endpoint Server
Although it is intended that the API endpoints are running natively on the DUT itself, it is conceivable that a software agent/proxy can provide this endpoint, e.g. in an appliance which hosts a SmartNIC adaptor card. Such an agent *could* translate the standardized endpoint API calls into whatever form the DUT requires, e.g. PCIe bus driver calls directly to the device, or into a non-standard proprietary RPC which then gets relayed to the device.  In all cases, the Test Controller should not have to treat the combination of proxy + device any differently than it treats an integrated device with onboard API endpoint. See Figure 6.

**Figure 6. Out-of-band Access to DUT API Endpoint Via Proxy**

![dash-testbed-inband-api.](../images/dash-testbed-out-of-band-via-proxy.svg)

# Reference Testbed Architecture - System-Level & Multiple DUTs
**TODO**

# Standardized DUT Configuration APIs
All DUTs will provide the following socket-based interfaces for configuring and controlling the devices. These are device service endpoints which are accessed via software clients running in the Controller.

Vendors *should* provide a convenient, automatable means to select between a production mode using [gNMI](https://https://github.com/openconfig/gnmi), or a dataplane evaluation image using [saithrift](https://github.com/opencomputeproject/SAI/tree/master/test/saithrift). Vendor/SKU-specific mechanisms should be included in the `/targets` directory and accessible via the automation software at test run time. As an alternative, DUTS can be supplied with fixed images to operate in one mode or the other, as long as a means to switch between these images (mode switch, image reload, etc.) is provided.

> **NOTE**: At this time, the SONiC DASH project is nascent and the early emphasis will be on performance and conformance of the underlying dataplane. Therefore, the DASH-SAI interface will be the early focus in order to eliminate the complications of debugging problems involving the entire SONiC stack. The [saithrift](https://github.com/opencomputeproject/SAI/tree/master/test/saithrift) server approach will be used for initial "lab" testing. By definition, it is not a production interface. Later on, the gNMI interface will be used for production and dataplane testing. This repo will focus on gNMI tests which are particular to DASH and not covered by "standard" SONiC test cases. Standard SONiC test cases can exercise the common parts of the stack and feature set.

## gNMI Northbound API
This is the canonical SONiC appliance management interface and it conforms to the standard SONiC Management requirements, see [SONiC Management Framework](https://github.com/Azure/SONiC/blob/master/doc/mgmt/Management%20Framework.md#3123-gnmi). This uses [gNMI](https://https://github.com/openconfig/gnmi) with [OpenConfig](https://github.com/openconfig) data models. All SONiC-DASH devices are expected to eventually conform to and be tested over this interface. See Figure 7. (Note, this diagram was adapted from the standard [SONiC Architecture](https://github.com/Azure/SONiC/wiki/Architecture) documents and may contain elements not-applicable to SONIC-DASH DUTs).

"Production" test cases will be written against the gNMI interface and organized accordingly. These exercise much of the core SONiC stack as well as the DUT dataplane.

**Figure 7. gNMI Northbound Interface**
![SONiC Architecture](../images/dash-gnmi-api.svg)

## saithrift Dataplane API
The Switch Abstraction Interface (SAI) is an internal "c" library interface in the SONiC stack, see [SONiC System Architecture](https://github.com/Azure/SONiC/wiki/Architecture#sonic-system-architecture) and [SAI](https://github.com/opencomputeproject/SAI). It represents the binding between vendor-specific shared ASIC driver library `libsai` and the `syncd` daemon's driver-calling layers. It is not normally exposed as an API endpoint. Rather, it is invoked as a consequence of interactions within the entire SONiC stack.

To simplify unit and functional testing, a Thrift server called [saithrift](https://github.com/opencomputeproject/SAI/tree/master/test/saithrift) can be compiled and bound to the SAI interface, providing a much-simplified path to the vendor ASIC library using SAI constructs expressed as Thrift RPC messages. This server replaces the normal collection of SONiC daemons and containers with a nearly direct path to vendor ASIC libraries via the SAI wrappers. See Figure 8. (Note, this diagram was adapted from the standard [SONiC Architecture](https://github.com/Azure/SONiC/wiki/Architecture) documents and may contain elements not-applicable to SONIC-DASH DUTs).

"Dataplane Evaluation" test cases will be written using the saithrift interface and organized accordingly. These primarily exercise conformance of the "DASH SAI" dataplane API and performance of the dataplane implementation, but do not exercise the SONiC core stack.

**Figure 8. SAI-Thrift Dataplane Test Interface**
![SONiC Architecture](../images/dash-thrift-sai-api.svg)

## Non-standardized DUT Configuration Methodology
Non-standard, vendor-specific APIs/utilities etc. are not officially recognized. However, for practical reasons, it should be possible to utilize non-standard DUT setup techniques in conjunction with the standardized community test cases and methodology. Towards this end, test cases and scripts *should* be structured such that it is relatively easy to substitute non-standard device setup steps with a vendor-supplied version. For example, a Pytest fixture setup class, or an imported wrapper library with subclassed methods could be instantiated to hide such details from the overall test framework.

>**NOTE**: It is incumbent on prospective suppliers of such non-standard devices/management software, to implement and integrate such accommodations in a manner which does not detract from the overall elegance, efficiency and maintainability of this repository. Code contributions to make these changes must not impose undue burden on the community at large.

# Test Automation Framework
Test Automation shall utilize the [PyTest](https://docs.pytest.org/en/6.2.x/) Framework.

**TODO** More details, replace "shall" language with actual guidelines.

# Test Objectives
## Conformance Testing
Conformance tests verify that the DUT performs all functions correctly, handles negative tests properly and obeys specified APIs. The list below summarizes the conformance tests.

**TODO** Define

## Performance Testing
Performance tests measure the DUT's capacity, speed and scale limits under various conditions. The list below summarizes the performance tests.

**TODO** Define

# Standardized Test Cases
## Test Case Organization
Test cases shall be organized in an appropriate manner. File directory structures and conventions shall be established.

**TODO** More details

## Test Case Marking
Tests shall be tagged with appropriate markers to allow selecting or deselecting categories of tests to run particular suites.

**TODO** More details, replace "shall" language with actual guidelines.

## Vendor/Platform Agnostic Traffic Generators
Where feasible, test should be designed against an abstract, vendor-neutral, platform-neutral Traffic Generator data model and API, to avoid lock-in. The [OpenTrafficGenerator](https://github.com/open-traffic-generator) project provides suitable data models and the derived [snappi libraries](https://github.com/open-traffic-generator/snappi) simplify writing client interfaces. Free (SW-only) and commercial (SW and HW) traffic generators adhering to the OTG specifications are available. These comprise the recommended solutions. 

When traffic test stimuli demand non-agnostic traffic-generator solutions, suitable  commercial solutions shall be utilized as required. Test automation software *should* implement generic wrappers in the main code to reduce vendor lock-in.

## Data-Driven Test Cases
A data-driven test methodology is preferred over an imperative (procedural) scripting approach. This means that the bulk of the information used to drive test cases derives from static data files which get translated into actual test runs using some kind of "test engine." This decouples the content from the implementation and makes it easier to contribute new test cases, as well as review proposed changes to existing test cases. The data files become the "single source of truth" and the testing framework code is merely the implementation.

Therefore, input requirements expressed as regular documents, e.g. text or spreadsheets, should be codified into some normalized data format early on in the process and thereafter become the machine-readable, single source of truth.

### Machine-Readable, Abstract Test Case (Test Vector) Formats
Many test cases are expressed as "test vectors" consisting of "inputs" and "expected outputs/results." A test suite consists of applying vectors and tallying the results.
These vectors should be declarative, abstract and not bound to a specific DUT configuration API. The test controller reads these test vectors, translates into the appropriate API to configure the DUT and Traffic Generator, runs the test and processes the results. Thus, by using a single set of test vectors, and suitable API-specific drivers, tests could be run using either the gNMI or saithrift APIs; a vendor-specific interface; or a future API yet to be specified.

**TODO** Propose/develop test-vector formats.

Test vectors *should not* be written in hard-coded gNMI or SAI representations except in special cases where there is no counterpart in the other APIs. An example of this is writing a test which performs an API-specific "corner-test" or "negative-test" towards the specific API and which would never apply to any other API type.

### Generated test Vectors
In some cases, test cases are too numerous or verbose to be represented as a list of literal test vectors; instead, they are generated on the fly e.g. in a program loop. Long lists of vectors are also difficult for humans to comprehend and maintain compared to a parameterized loop. If possible, a templating system should be used such that the test vector can still be represented as a simple-to-read document which is expanded by the templating renderer (e.g. [Jinja2](https://jinja2docs.readthedocs.io/en/stable/)).

Even when a "templating" system is not applicable, a data driven approach is preferred. An example is using high-level policy descriptions expressed in some easy-to-create format (.json, .csv, protobuf, yaml) which gets expanded into specific ACL entries using a suitable algorithm.

In other cases, procedural code which generates test vectors and performs test evaluation (assertions) *should*, where feasible, be developed in a manner which makes it agnostic to the type of traffic generator and DUT configuration API, as well as easy to maintain, copy and adapt for other cases.

### Data-Driven Device Dependencies
Test-cases should be reusable between various targets.
Practially speaking, however, devices will have varying numbers of traffic ports; speed and breakout capabilties; connector/physical layer attributes; dataplane feature sets and scaling; etc. These device-dependent attributes shall be captured in configuration files and organized per-vendor and per-SKU under the [targets/](../targets/README.md) directory. Tests should consume this metadata and adapt accordingly, again using a data-driven, test-engine approach.

### Community and Proprietary Test Cases
While it is the intent to build a community wherein participants contribute public test cases, it is also anticipated and natural that members will retain proprietary test cases as well, for commercial reasons. It is hoped that the community test framework and library of test cases can still form the core of vendor testbeds. This will avoid "reinventing the wheel," reduce the friction of adapting and contributing vendor-developed test cases to the community and vice versa, and maximize the utility and hardening of this repository for the common good. One possiblity is to use [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to import this test repository into in-house repositories, which can be extended locally with private enhancements and additions.

## P4 Model-Based Testing
The [DASH P4 behavioral models](../../sirius-pipeline/README.md) describe the DASH pipeline in an abstract, machine-readable and unambiguous fashion. There are multiple potential applications:

* It is a clear contract and specification for the dataplane, supplementing or replacing traditional diagrams, text documents etc.
* The P4 code can be used to generate dataplane programming APIs
* P4 software-based reference target running on a CPU
* P4 code-derived test cases

### P4 As Dataplane Definition
The P4 code is the definitive specification of the dataplane behavior. Additional documents and diagrams can provide more clarity and context, but the machine-readable code is the single source of truth.
### P4-Generated APIs
The P4 code can be used to generate dataplane programming APIs. P4 compilers emit P4Info which is traditionally used to drive a [P4Runtime API](https://github.com/p4lang/p4runtime). The P4Info is consumed by a client program (e.g. SDN controller) and can be used to introspect P4 program entities (e.g. tables), format messages, etc.

For DASH-SONiC, the P4Info is used to auto-generate appropriate DASH-SAI APIs (`.h` or header files). This provides a tight coupling between the canonical P4 pipeline code, and the corresponding DASH-SAI APIs. This by implication defines the saithrift APIs since these are merely RPC versions of the SAI `c` language APIs. The tooling to perform this is in progress and will be published at a later date.

### P4 Software Reference Target
The P4 behavior model could be executed in a container or VM using the [Behavioral Model Reference switch](https://github.com/p4lang/behavioral-model) also known as `bmv2`. This could be used as a reference target or DUT for regression testing and new test-case validation. Slow-ish functional testing would be possible. Performance and scale tests likely wouldn't be feasible since `bmv2` is not very fast and table sizes etc. may be limited.

However, for this proposal to be practical, the question arises "what is the API interface to configure the P4 `bmv2` DUT?" P4Runtime is the default programming API for `bmv2`, which does not correspond to the aforementioned list of APIs, namely gNMI and saithrift.

This subject is for further study.
### Aspirational: P4- Code-Derived Test Cases
A common vision espoused by networking experts is to use P4 source code as a single source of truth, not only as a specification which gets compiled and executed as a realized pipeline, but for test-case generation based on analyzing the code. Various techniques for this have been proposed in the commercial and academic domains. It is hoped that the  can eventually be used as inputs to an automatic test-case-generator. These would likely supplement, not replace, traditional "manually" generated test cases.

# Terms and Definitions

Term | Meaning |
--------------------| -----------------
API                 | Application Programming Interface; more specifically in the context of this document, one of the stipulated DUT configuration/management RPC protocols like gNMI or saithrift
DPU                 | Data Processing Unit, another term for SmartNIC
DUT or D.U.T.       | Device Under Test
endpoint            | An API server at a known address, which provids a service using an agreed-upon protocol, e.g. a gNMI server at a certain address:port
gNMI                | Google Network Management Interface, see https://github.com/openconfig/gnmi
gRPC                | Google Remote Procedure Call and tooling, see https://grpc.io
HW                  | Hardware
OpenConfig          | A collection of data models written in [YANG](https://en.wikipedia.org/wiki/YANG) used to manage network devices such as switches and routers. See https://github.com/openconfig
OTG                 | Open Traffic Generator, a vendor/platform neutral data model + client libraries for traffic generators. See https://github.com/open-traffic-generator
Pytest              | An open-source Python test framework, see https://docs.pytest.org/en/6.2.x/
RPC                 | Remote Procedure Call, e.g. a service or function invoked over a network socket. Examples of RPC protocols: gRPC, gNMI, Thrift
SAI                 | Switch Abstraction Interface, see https://github.com/opencomputeproject/SAI
SKU                 | Stocking Control Unit, a fancy name for part number; pronounced "skew."
SmartNIC            | An intelligent Network Interface Card (Adaptor) which executes the dataplane features
snappi              | A family of client wrappers to simplify usage of OTG-compliant traffic generators, see https://github.com/open-traffic-generator/snappi
SUT or S.U.T.       | System Under Test
SW                  | Software
TGen or TrafficGen  | Shorthand for "Test Traffic Generator/Receiver"
Thrift              | Apache Thrift RPC protocol and tooling, see https://thrift.apache.org


# Revision History

| Date       | Author        | Comments                 |
| ---------- | --------------| ------------------------ |
| 2021-10-14 | C. Sommers    | Originated               |
