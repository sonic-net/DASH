# SAI Challenger Test Framework for DASH
This framework supports both virtual testing of SW switches/DUTs at "CPU speeds" as well as physical DUT testing with HW traffic generators up to full line rate. A number of components have been integrated to provide a powerful and convenient test framework for DASH devices.

* [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) - Based on [Pytest](https://pytest.org/),  it was originally created to test [SAI](https://github.com/opencomputeproject/SAI)-based devices using [sai-redis](https://github.com/sonic-net/sonic-sairedis) and was meant for SONiC-powered network switches. It has since been enhanced to test DASH devices with large-scale configurations by adding the following features:
  *  Data-driven configuration schema to allow cleaner and easily-scalable test vectors without having to learn or write low-level RPCs (e.g. sai-thrift)
  *  Multiple device RPC APIs via pluggable drivers, including sai-redis and sai-thrift, fed by the config data to program devices
  *  Support for scalable traffic generators via [snappi](https://github.com/open-traffic-generator/snappi) API
  *  Support for legacy [Packet Test Framework (PTF)](https://github.com/p4lang/ptf) packet utilities, which utilize the popular [Scapy](https://scapy.net) library
* [dpugen](https://pypi.org/project/dpugen/) - A Python library which can generate large-scale DASH configurations (millions of table entries) with a few input parameters; these configurations can be used by SAI Challenger to program devices.
* [snappi](https://github.com/open-traffic-generator/snappi) - A Python SDK (also available in other language bindings) to configure and query SW or HW traffic-generators compliant with the [Open Traffic Generator](https://github.com/open-traffic-generator) (OTG) data model
* [ixia-c](https://github.com/open-traffic-generator/ixia-c), a free, flow-based, [OTG](https://github.com/open-traffic-generator)-compliant SW traffic generator 

## SAI-Challenger for DASH - Architecture
The figure below depicts the integration of the components listed above:
![dash-saichallenger-enhanced](../images/dash-saichallenger-enhanced.svg)

Pytest test-cases run suites of tests. They obtain device configurations (left part of diagram), apply them to the DUT via a pluggable API, program traffic-generators to send packets to the device, measure and capture packets sent back by the device (unless they're dropped by the DUT), etc.

Some of the unique parts of the architecture, as compared say to PTF, are the config data parser, the pluggable DUT config driver and the flexible dataplane interface (to control packet generators).
 
## DUT Configuration

This framework supports several methods, listed below, to specify the DUT's configuration. The preferred way is to use "SAI records" which are per-object specifications of data (table entries and attributes) and the desired CRUD operations (create, remove, set, get). See the [spec](../test-cases/scale/saic/README-SAIC-DASH-config-spec.md). The [tutorial](../test-cases/scale/saic/tutorial/README.md) gives examples of all these methods.

### Data-Driven DUT Configuration
The following methods are recommended alternatives; they all use a data-driven approach, avoiding lock-in to a specific device RPC/API. See the left-most part of the diagram above.

* **[dpugen](https://pypi.org/project/dpugen/)** - for generating high-scale configs (or even simple ones!) with a few simple high-level configuration parameters. `dpugen` can emit JSON text for storage into a file, or "streaming" records read by SAI-Challeneger, for on-the-fly config generation which is applied to a DUT in real-time via a driver. This streaming mode avoids the need to store huge config files.
* A **stored JSON file** containing one or more SAI records. These files can be hand-edited, produced by [dpugen](https://pypi.org/project/dpugen/) or your own tool. Files are loaded via a JSON library and converted into Python dicionaries, then "applied" to the device driver of choice.
* **Literal SAI records** embedded in your test-case `.py` file and represented as Python dictionaries. This is suitable for small configs.
* **Bespoke generator code** in your test-case script which generates configuration data programatically. This might be good for larger configurations needing a custom alternative to [dpugen](https://pypi.org/project/dpugen/).

### API-Driven DUT Configuration
The legacy approach to device setup/teardown, in frameworks like PTF or even prior versions of SAI Challenger, is to configure a device via eplicit API calls using an RPC such as sai-redis or sai-thrift. This is still supported within the enhanced SAI Challenger. You can freely mix the data-driven approach with the API-driven approach.

The main drawback of API-driven code that such a test will only run using the specific API you invoke. (There are numerous other drawbacks as well.) In contrast, a data-driven test case can be run using different APIs by specifying the driver in one setup file.

