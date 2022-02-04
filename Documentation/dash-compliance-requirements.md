[[ << DASH/Documents Table of Contents ]](README.md)

[[ << DASH main README ]](../README.md)

>**NOTE** This may be superceded by the rethought main [README](README.md) structure. This might still have use in case we need to document profiles of related requirements, which could benefit from a top-level compliance doc.
# DASH Compliance Requirements
This document describes the criteria for a device to be considered "DASH Compliant." Individual detailed specifications for each category are divided into separate documents. For actual testing methodology, configuration artifacts and scripts, etc. see [test/docs/README.md](../test/docs/README.md) and follow the links to respective areas. 

# Categories
The table below lists the compliance categories and links to the respective detailed documents. Notice that the requirements for the different configuation APIs (northbound: gNMI; southbound: SAI) are specified separately from the underlying dataplane requirements. The various APIs have specific transport and semantic requirements to effect the configuration operations (e.g. CRUD operations on stored configuration objects). The dataplane has requirements for carrying and processing traffic, regardless of which configuration API is used. The dataplane should behave identically when configured through any interface.
>**Note**: The original 'high-availability-and-scale.md" document was split into "dash-dataplane.md" and "high-availability-and-scale.md."

Test methodology, configurations and scripts are located under the [test/](../test/README.md) directory

| Category | Description | Detailed Document Links |
| -------- | ----------- | ----------------------- |
| Dataplane | Detailed dataplane **Scaling, Conformance and Performance** requirements, independent of the configuration API |[dash-dataplane.md](dash-dataplane.md)
| High Availability |Overall High Availability architecture and requirements | (Need to split doc) [ high-availability-and-scale.md](high-availability-and-scale.md) |
| SAI API | Detailed Switch Abstraction Interface API conformance and performance | [dash-sai-compliance.md]( dash-sai-compliance.md) |
| gNMI API | Detailed gNMI SDN API conformance and performance requirements | [dash-gnmi-compliance.md]( dash-gnmi-compliance.md) |


# Versioning and Configuration Management

>**TODO** Determine a versioning system for each category as well as the overall configuration of a "release."

# Continuous Integration and Test
Continuous integration verifies the correctness of each committed configuration. Workflows can be triggered manually, or automatically (by commits). Success/failure can be  criteria for accepting pull requests.

**TODO** Define objectives and implement automation (Git Actions). The follow non-exhaustive list is just an example of what can be done:

* Automatically compile/build any source-code files into their artifacts, e.g. executables, docker images, VMs, etc. This verifies an intact code and toolchain configuration.
* Execute compiled artifacts inside CI test runner environments.
* Execute toolchains which produce downstream artifacts which are checked into the repo. An example would be generating DASH overlay `.h` header files from P4 behavior model code.
* Exercise all SAI units tests against a dummy `libsai` implementation to confirm API basic conformance.
* Execute DASH software dataplanes via P4 behavioral models: run test suites which configure the sotware Device under Test (DUT) and send traffic to/from the dataplane with software traffic testers. See [DASH Testing Using P4 Simulators and SAI Thrift](../test/docs/dash-test-workflow-p4-saithrift.md) for an example workflow.


# Reference Architectures
Reference architectures for test scenarios are described in [test/docs/dash-test-ref-arch.md](../test/docs/dash-test-ref-arch.md)

