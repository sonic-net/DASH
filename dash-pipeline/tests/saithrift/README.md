# saithrift tests directory
This directory contains tests for DASH pipeline using python `saithrift` client libraries. The following frameworks are supported; see the corresponding directories:
* [ptf/](ptf) directory - Tests using the [PTF](https://github.com/p4lang/ptf) or Packet test framework, as used in [SAI/ptf](https://github.com/opencomputeproject/SAI/tree/master/ptf) test cases
* [pytest/](pytest/) directory - Tests using the [Pytest](https://docs.pytest.org/en/7.1.x/index.html) testing framework

The tests use the same thrift and saithrift client libraries and in general the configuration and setup of the DASH data plane will use the same APIs and command sequences. The frameworks differ primarily in how test suites are designed and orchestrated. Each framework has advantages and disadvantages, hence both are supported as first-class citizens.

In particular the PTF test framework has a significant body of helper libraries which simplify setup. The corollary is that the PTF libraries make a lot of embedded assumptions about the test target, the environment and the data plane SW packet generator (scapy).