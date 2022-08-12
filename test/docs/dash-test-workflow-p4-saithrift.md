
[[ << Test docs Table of Contents ]](./README.md)

[[ << DASH/test main README ]](../README.md)

[[ << DASH main README ]](../../README.md)
# DASH Testing Using P4 Simulators and SAI Thrift

This article documents the use of P4-based simulators or SW data planes to verify DASH behavior, using saithrift API. Refer to the following figure. Also, refer to [DASH Test Workflow with saithrift](dash-test-workflow-saithrift.md) as it contains some context and common elements which are not repeated here. The discussion below will assume a working knowledge of the saithrift workflow.

Other documents on this site have explained the rationale of a P4 Behavioral model, with uses including:
* Modeling and verifying the DASH data plane intent
* Executing functional and regression tests of the entire stack and data plane in a [CI/CD](https://en.wikipedia.org/wiki/CI/CD) pipeline.

We will describe how it relates to the DASH test workflow.

> **NOTE**: This captures the current state of work which is very much in progress. It reflects updates from the Working Group Meeting on Dec 15, 2021. It might lag behind actual developments. We will strive to keep it updated in a timely fashion.

## Workflow overview 

![dash-test-wflow-p4-saithrift](../images/dash-test-wflow-p4-saithrift.svg)

The previous figure highlights the following important test work-flow concepts:

* The similarity between the P4 Simulation test workflow described here, and the "normal" workflow described in [DASH Test Workflow with saithrift](dash-test-workflow-saithrift.md)
* The different implementations of P4 Simulators currently being developed
* How saithrift endpoints are "grafted" onto the native P4Runtime APIs of the simulators
* How the simulators are "wired" to software traffic generators using virtual Ethernet connections, yielding a testable, pure-SW DASH data plane which can process packets.
## Standardize test cases and test-runners.
The P4 Simulator tests will use a subset of the standard DASH test cases using the same test scripts and framework. Some tests may not be practical to execute on certain simulation targets due to their performance limitations. Test cases should be marked to indicate which targets they may run successfully on, and only those test shall be run against said target. Some examples:
* "API conformance tests" which do not stress the data plane performance should run on any target, with the understanding that the scale of tests may need to be reduced accordingly. For example, a slow simulator may not handle thousands of SAI table configuration operations in an acceptable amount of time, whereas a hardware DUT will do so.
* "Data plane functional tests" which send a few packets and measure the outcome might run on any target.
* "Data plane performance tests" might need to be scaled back to match the performance of some simulators (e.g. P4-DPDK), or eliminated entirely for others (bmv2).

## SAI Data plane Programming Interface
A simulator must provide a standard DASH SAI programming interface allowing integration with the DASH test fixtures, via a saithrift endpoint. The simulator must have an associated `libsai` shared library which can be linked to the saithrift server skeleton. The resulting saithrift server executes in the simulator and converts saithrift API calls into the  simulator's underlying internal operations, whose details are not apparent to the client using the sai interface. 

This approach will also allow integration with the SONiC stack by building a `syncd` image linked to the device's libsai and executing it on the device. This would allow a pure-software simulation of SONiC DASH including traffic processing. A `syncd` daemon would replace the `saithrift` server shown in the diagram. It would interface to the standard lower SONiC stack, e.g. talk to the redis ASIC DB. This might be used if DASH testing is extended to use the `sairedis` interface as done in PLVision's [SAI Challenger](https://plvision.eu/rd-lab/blog/opensource/sai-challenger-sonic-based-framework) which is being offered to the [Open Compute Project (OCP)](https://www.opencompute.org/) Community, which hosts the SAI project.

See [SONiC Architecture](https://github.com/Azure/SONiC/wiki/Architecture) for more details about the complete SONiC stack.

## Optional P4Runtime Data plane Programming Interface
P4 data planes generally provide the standard [P4Runtime](https://github.com/p4lang/p4runtime) ("P4RT") API to configure P4 entities (tables, meters, etc.) and read state (counters, registers, etc.). Therefore this capability will exist "for free" in a DASH P4 simulator. It will not be used in standardized DASH conformance and performance tests; only the SAI interface will be used.

It might be useful or even necessary to use this API to develop, test and continuously verify the P4 Data plane itself. This detail will probably be left as an internal implementation issue and not exposed to the official DASH testbed. This can be reconsidered in the future. The diagram shows P4Runtime endpoints being accessed by an optional P4RT Test script.

## SAI Data plane Traffic Interface
A simulator normally uses virtual Ethernet ("veth") interfaces instead of physical ports. These are "wired" to software-based traffic generators using Linux bridges or similar. This allows pure software-based traffic testing. No traffic leaves the CPU which hosts these programs. The tests can be run in a developer's or test engineer's workstation environment, or in a CI/CD pipeline runner's instance.

An alternative approach (not illustrated) is to bind or bridge the SW simulators to physical Ethernet ports, on the CPU which is hosting the simulator. These ports can then be physically cabled to external HW traffic generators, *or* to external SW traffic generators (on a different host) which are similarly bound to physical Ethernet ports. This use-case is out of scope for community DASH testing, but might serve some R&D lab needs.

## Simulator Implementations
Currently, two complementary simulator implementations are being developed by the DASH community:
* A modified Behavioral Model ([bmv2](https://github.com/p4lang/behavioral-model)), championed by NVidia. Currently this uses a customized codebase based on a modified v1model P4 architecture. Discussions are in-progress whether this will eventually converge to use the PNA model.
* A [P4-DPDK](https://github.com/p4lang/p4-dpdk-target) based software data plane championed by Intel, using the PNA architecture. This is much more than a "simulator," it is a first-class, SW data plane implementation. When executing on a normal CPU (versus a dedicated hardware device) it can serve as a fairly performant DASH data plane simulator.

### BMv2 Simulator Design Details
The diagram show a few details about the design of the [bmv2](https://github.com/p4lang/behavioral-model) simulator. The community bmv2 program is modified to support DASH requirements (e.g. stateful connection tracking). The source code assumes an enhanced v1model.

A saithrift server skeleton is linked to a libsai library to yield a saithrift API endpoint, used by the test runner.

The bmv2 simulator has a built-in P4Runtime server. A SAI-to-P4Runtime adaptor maps SAI API calls made to the libsai API, into P4Runtime API gRPC calls over a socket to the bmv2 endpoint. SAI object operations are thus converted into P4 entity operations. Note that data plane configuration thus requires two socket-based RPC hops, because saithrift messages are translated into equivalent P4RT gRPC messages.

The bmv2 simulator is bound to host veth ports at startup.  These are "wired" to the software traffic generator using Linux bridging or similar.

### P4-DPDK Simulator Design Details
The diagram shows a few details about the design of the [P4-DPDK](https://github.com/p4lang/p4-dpdk-target) data plane, which as stated previously, is not merely  a simulator, but can be used as one for DASH purposes.

The P4-DPDK data plane has an internal, compiled [Table-Driven Interface (TDI)](https://github.com/p4lang/tdi). This abstraction is analogous to the Switch Abstraction Interface (SAI), except tailored to P4 Data planes.

A libsai library will be developed which maps SAI conceptual APIs into the [dash_pipeline.p4](../dash_pipeline.p4) TDI implementation, all done in-process. This is very efficient because it avoids serialization over P4Runtime.

The P4-DPDK data plane also has a built-in P4Runtime server which can be used develop and test the P4 Model. This is not part of the official DASH test workflow. Note that P4RT and saithrift servers are available simultaneously and operate "in parallel," sharing the native TDI layer.

The P4-DPDK data plane is bound to host veth ports at startup.  These are "wired" to the software traffic generator using Linux bridging or similar.

## Summarizing it all
* Standard DASH test cases and test runners apply conformance and performance tests against software-based DASH data plane simulators.
* Software data plane have lower scale and performance capabilities compared to production hardware implementations. Therefore, tests must be marked for suitability on each target to respect performance and scale limitations of each software implementation. The test runners will run only the appropriate subset for a given target.
* Two different software simulators are being developed independently (bmv2 and P4-DPDK), with various characteristics. They are works-in-progress and details may evolve quickly over time.
* The simulators will have libsai libraries allowing compilation into a saithrift server. This server exposes a saithrift API endpoint used by the test scripts to configure and query the data plane.
* The native P4Runtime API endpoints are not used in standard DASH tests, but they may serve a purpose for developing the P4 model and simulations themselves.
* Packets are sent into and out of veth interfaces of the simulator. These connect via Linux bridges or similar, to software-based packet generators. Complete data plane tests can be performed solely in software, supporting development and CI/CD testing.


## References
- [DASH Test Workflow with saithrift](dash-test-workflow-saithrift.md)
- [CI/CD](https://en.wikipedia.org/wiki/CI/CD)
- [SAI Challenger](https://plvision.eu/rd-lab/blog/opensource/sai-challenger-sonic-based-framework)
- [Open Compute Project (OCP)](https://www.opencompute.org/)
- [SONiC Architecture](https://github.com/Azure/SONiC/wiki/Architecture) 
- [P4Runtime](https://github.com/p4lang/p4runtime)
- [bmv2](https://github.com/p4lang/behavioral-model)
- [P4-DPDK](https://github.com/p4lang/p4-dpdk-target)
