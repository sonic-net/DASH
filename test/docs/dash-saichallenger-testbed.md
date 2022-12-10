# SAI Challenger Test Framework for DASH

This framework supports both virtual testing of SW switches/DUTs as well as hardware device testing at full line rate. A number of components have been integrated to provide a powerful and convenient test framework for DASH devices.

* [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) - Based on [Pytest](https://pytest.org/) , it was originally created to test [SAI](https://github.com/opencomputeproject/SAI)-based devices using [sai-redis](https://github.com/sonic-net/sonic-sairedis) and was meant for SONiC-powered network switches. I has since been enhanced to test DASH devices with large-scale configurations by adding the following features:
  *  Data-driven configuration schema to allow cleaner and easily-scalable test vectors without having to learn or write low-level RPCs (e.g. sai-thrift)
  *  Mltiple device RPC APIs via pluggable drivers, including sai-redis and sai-thrift, fed by the config data to program devices
  *  support for scalable traffic generators via [snappi](https://github.com/open-traffic-generator/snappi), while still maintaining support for legacy [Packet Test Framework (PTF)](https://github.com/p4lang/ptf) packet utilities, which utilize the popular [Scapy](https://scapy.net) library
* [dpugen](https://pypi.org/project/dpugen/) - A Python library which can generate large-scale DASH configurations (millions of table entries) with a few input parameters; these configurations can be used by SAI Challenger to progam devices.
* [snappi](https://github.com/open-traffic-generator/snappi) - A Python SDK (also available in other language bindings) to configure and query SW or HW traffic-generators compliant with the [Open Traffic Generator](https://github.com/open-traffic-generator) (OTG) data model

## SAI-Challenger for DASH Architecture
The figure below depicts the integration of the components listed above:
![dash-saichallenger-enhanced](../images/dash-saichallenger-enhanced.svg)

The generator is one of several options to produce SAI (or possibly gNMI) configuration *records* which are applied to the DUT via one of several possible APIs, including saithrift, sairedis, gNMI, etc. The generator can provide streaming records which are translated on-the-fly into appropriate device API calls.

In addition, the generator can produce textual representations (e.g. JSON, YAML) of configuration records for usage as stored configurations which the framework can consume as test data input. Configuration files can be produced by other means including other scripts, text-editors, etc.

Finally, the framework can use literal configuration declarations represented as JSON, YAML, Python structures, etc. embedded directly into test-case code. This makes the most sense when the test cases are relatively simple.