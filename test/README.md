# SONiC-DASH Testing
This directory contains documentation, test scripts, test configurations and other artifacts required to test a SONiC-DASH device or devices. The focus is on executable test artifacts, not test requirements.

For hard requirements, see [Compliance Requirements](../Documentation/dash-compliance-requirements.md)

You can start with the [High-Level Description (HLD) Test Specification](docs/dash-test-HLD.md) or go to the [Test Docs Table of Contents](docs/README.md).

## Organization
Please see the structure below:
* [docs/](docs/README.md) - Test documentation
* [src/](src) - Source code to build test artifacts
* [test-cases/](test_cases_) - Directory of test-cases
* [targets/](targets) - target-specific artifacts, sources and documents
* [third-party/](third-party) - third-party and external resources used by this project, typically as Git submodules
