<h1>Contents</h1>

- [SAI Challenger Test Framework for DASH](#sai-challenger-test-framework-for-dash)
  - [SAI-Challenger for DASH - Architecture](#sai-challenger-for-dash---architecture)
  - [DUT Configuration Data](#dut-configuration-data)
    - [Data-Driven DUT Configuration](#data-driven-dut-configuration)
    - [API-Driven DUT Configuration](#api-driven-dut-configuration)
  - [DUT Configuration APIs](#dut-configuration-apis)
- [Dataplane (Test Traffic Generation)](#dataplane-test-traffic-generation)
  - [snappi for flow-based testing](#snappi-for-flow-based-testing)
  - [snappi for PTF-style testing (packet at a time)](#snappi-for-ptf-style-testing-packet-at-a-time)
  - [Native PTF/Scapy testing](#native-ptfscapy-testing)

# SAI Challenger Test Framework for DASH
This framework supports both virtual testing of SW switches/DUTs at "CPU speeds" as well as physical DUT testing with HW traffic generators up to full line rate. A number of components have been integrated to provide a powerful and convenient test framework for DASH devices.

* [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) - Based on [Pytest](https://pytest.org/),  it was originally created to test [SAI](https://github.com/opencomputeproject/SAI)-based devices using [sai-redis](https://github.com/sonic-net/sonic-sairedis) and was meant for SONiC-powered network switches. It has since been enhanced to test devices with large-scale configurations and different configuration APIs, by adding the following features:
  *  Data-driven configuration schema to allow cleaner and easily-scalable test vectors without having to learn or write low-level RPCs (e.g. sai-thrift)
  *  Multiple device RPC APIs via pluggable drivers, including sai-redis and sai-thrift, fed by the config data to program devices
  *  Support for scalable traffic generators via [snappi](https://github.com/open-traffic-generator/snappi) API
  *  Support for legacy [Packet Test Framework (PTF)](https://github.com/p4lang/ptf) packet utilities, which utilize the popular [Scapy](https://scapy.net) Python package
* [dpugen](https://pypi.org/project/dpugen/) - A Python library which can generate large-scale DASH configurations (millions of table entries) with a few input parameters; these configurations can be used by SAI Challenger to program devices.
* [snappi](https://github.com/open-traffic-generator/snappi) - A Python SDK (also available in other language bindings) to configure and query SW or HW traffic-generators compliant with the [Open Traffic Generator](https://github.com/open-traffic-generator) (OTG) data model
* [ixia-c](https://github.com/open-traffic-generator/ixia-c), a free, flow-based, [OTG](https://github.com/open-traffic-generator)-compliant SW traffic generator 

## SAI-Challenger for DASH - Architecture
The figure below depicts the integration of the components listed above:
![dash-saichallenger-enhanced](../images/dash-saichallenger-enhanced.svg)

Pytest test-cases run suites of tests. They obtain device configurations (left part of diagram), apply them to the DUT via a pluggable API, program traffic-generators to send packets to the device, measure and capture packets sent back by the device (unless they're dropped by the DUT), etc.

Some of the unique parts of the architecture, as compared say to PTF, are the config data parser, the pluggable DUT config driver and the flexible dataplane interface (to control packet generators).
 
## DUT Configuration Data

This framework supports several methods, listed below, to specify the DUT's configuration. The recommended way is to use "SAI records," which are per-object specifications of data (table entries and attributes) and the desired CRUD operations (SAI create, remove, set, get). See the [spec](../test-cases/scale/saic/README-SAIC-DASH-config-spec.md). The [tutorial](../test-cases/scale/saic/tutorial/README.md) gives examples of all these methods.

### Data-Driven DUT Configuration
The following methods are preferred alternatives; they all use a data-driven approach, avoiding lock-in to a specific device RPC/API. Refer to the left-most part of the diagram above.

* **[dpugen](https://pypi.org/project/dpugen/)** - for generating high-scale configs (or even simple ones!) with a few simple high-level configuration parameters. `dpugen` can emit JSON text for storage into a file, or "streaming" records consumed by SAI-Challenger, for on-the-fly config generation which is applied to a DUT in real-time via a driver. This streaming mode avoids the need to store huge config files.
* A **stored JSON file** containing one or more SAI records. These files can be hand-edited, produced by [dpugen](https://pypi.org/project/dpugen/) or your own tool. Files are loaded via a JSON library and converted into Python dicionaries, then "applied" to the device driver of choice.
* **Literal SAI records** embedded in your test-case `.py` file and represented as Python dictionaries. This is suitable for small configs.
* **Bespoke generator code** in your test-case script which generates configuration data programmatically. This might be good for larger configurations needing a custom alternative to [dpugen](https://pypi.org/project/dpugen/).
### API-Driven DUT Configuration
The legacy approach to device setup/teardown, in frameworks like PTF or even prior versions of SAI Challenger, is to configure a device via explicit API calls using an RPC such as sai-redis or sai-thrift. This is still supported within the enhanced SAI Challenger. You can freely mix the data-driven approach with the API-driven approach.

The main drawback of API-driven code that such a test will only run using the specific API you invoke. (There are numerous other drawbacks as well.) In contrast, a data-driven test case can be run using different APIs by specifying the driver in one setup file.
## DUT Configuration APIs
SAI Challenger supports a pluggable "device driver" approach. The intent is to express DUT configuration as "data" (not code) and let the framework operate a variable set of DUT configuration APIs "under the hood."

The following APIs are supported:
* sai-redis - The device is configured by modifying/creating the entries in SONiC's redis ASIC DB, using a CRUD-style RPC bound tightly to SONiC redis schema. SAI Challenger automatically translates abstract config data records into sai-redis CRUD operations. This approach requires building and installing suitable SONiC daemons/containers (redis, syncd, etc.) on the DUT.
* sai-thrift - The device is configured by calling the DUT's SAI API layer using a Thrift RPC. The DUT requires a Thrift server expecially built for this purpose. This is a more direct DUT dataplane config interface and is NOS-agnostic.
# Dataplane (Test Traffic Generation)
Testing networing DUTs consists of configuring a device and sending and receiving packets via its virtual or physical traffic ports. 
SAI Challenger supports both the legacy PTF dataplane (based on the CPU-driven [Scapy](https://scapy.net) package) and the newer [Open Traffic Generator](https://github.com/open-traffic-generator)-based approach which allows SW or HW-based traffic-generator usage, using a single [snappi](https://github.com/open-traffic-generator/snappi) API, regardless of the underlying taffic-generator platform.

The choice of platforms is dictated by a setup JSON file. The same Pytest script can be called and passed the appropriate setup file (via the `--setup` option) to perform tests using a SW traffic generator such as [ixia-c](https://github.com/open-traffic-generator/ixia-c), or a commercial, hardware-based traffic generator, as long as it supports the [Open Traffic Generator](https://github.com/open-traffic-generator) specification.

## snappi for flow-based testing
For flow-based traffic tests, e.g. one or more continuous traffic streams with well-defined packet headers at a specified rate, use the native snappi approach. This requires using the snappi SDK, which is a Python (or other language) library providing idiomatic access the OTG constructs. OTG/snappi also provides several other advantages such as precision scheduling, high data rates, incrementing (or other pattern) header fields, flow tracking using special instrumentation fields injected into the packet payload, etc.
## snappi for PTF-style testing (packet at a time)
For convenience, SAI Challenger includes some wrapper libraries which present familiar [PTF](https://github.com/p4lang/ptf) packet utilities to send a single packet at a time. This allows you to utilize an OTG-compliant packet generator with familiar PTF contructs. The main advantages are:
- Ease of migration of older PTF scripts
- Simplicity when constructing and sending a few simple packets, versus setting up continuous streams or flows. Flow-based testing is powerful, but somewhat more complex.
## Native PTF/Scapy testing
Finally, you can elect to use the native PTF dataplane, which employs Scapy as the traffic generator. In this case, the same APIs as  described in the previous paragraph are used to directly call Scapy.