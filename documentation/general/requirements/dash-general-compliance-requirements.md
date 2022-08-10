[ [ << Back to parent directory](../README.md) ]

[ [ << Back to DASH top-level Documents](../../README.md#contents) ]

# DASH General Compliance Requirements
# DASH Versioning and Configuration Management

>**TODO** Determine a versioning system for each category as well as the overall configuration of a "release."

# Continuous Integration and Test
Continuous integration verifies the correctness of each committed configuration. Workflows can be triggered manually, or automatically (by commits). Success/failure can be  criteria for accepting pull requests.

**TODO** Define objectives and implement automation (Git Actions). The follow non-exhaustive list is just an example of what can be done:

* Automatically compile/build any source-code files into their artifacts, e.g. executables, docker images, VMs, etc. This verifies an intact code and toolchain configuration.
* Execute compiled artifacts inside CI test runner environments.
* Execute toolchains which produce downstream artifacts which are checked into the repo. An example would be generating DASH overlay `.h` header files from P4 behavior model code.
* Exercise all SAI units tests against a dummy `libsai` implementation to confirm API basic conformance.
* Execute DASH software data planes via P4 behavioral models: run test suites which configure the software Device under Test (DUT) and send traffic to/from the data plane with software traffic testers. See [DASH Testing Using P4 Simulators and SAI Thrift](../test/docs/dash-test-workflow-p4-saithrift.md) for an example workflow.


# Reference Architectures
Reference architectures for test scenarios are described in [test/docs/dash-test-ref-arch.md](../../../test/docs/dash-test-ref-arch.md)

