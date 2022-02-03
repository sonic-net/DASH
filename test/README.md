# SONiC-DASH Testing
This directory contains documentation, test scripts, test configurations and other artifacts required to test a SONiC-DASH device or devices.


| Document | Description |
|----------|-------------|
| [High-Level Description (HLD) Test Specification](docs/sonic-dash-test-HLD.md) | High-level design for the testing of devices which conform to the SONiC-DASH requirements.|  
| [DASH SAI-Thrift Test Workflow](docs/dash-test-workflow-saithrift.md) | DASH test workflow with SAI-thrift. |
| [DASH P4 SAI-Thrift Test Workflow](docs/dash-test-workflow-p4-saithrift.md) | Use of P4-based simulators or SW dataplanes to verify DASH behavior, using saithrift API. |


You can start with the [High-Level Description (HLD) Test Specification](docs/sonic-dash-test-HLD.md). 


## Organization
Please see the structure below:
* [docs/](docs) - Test documentation
* [src/](src) - Source code to build test artifacts
* [test-cases/](test_cases_) - Directory of test-cases
* [targets/](targets) - target-specific artifacts, sources and documents
* [third-party/](third-party) - third-party and external resources used by this project, typically as Git submodules