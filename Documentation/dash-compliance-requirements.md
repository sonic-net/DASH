# DASH Compliance Requirements
This document describes the criteria for a device to be considered "DASH Compliant." Individual detailed specifications for each category are divided into separate documents. For actual testing methodology, configuration artifacts and scripts, etc. see [test/docs/README.md](../test/docs/README.md). 

# Categories
The table below lists the compliance categories and links to the respective detailed documents. Notice that the requirements for the different configuation APIs (northbound: gNMI; southbound: SAI) are specified separately from the underlying dataplane requirements. The various APIs have specific transport and semantic requirements to effect the configuration operations (e.g. CRUD operations on stored configuration objects). The dataplane has requirements for carrying and processing traffic, regardless of which configuration API is used. The dataplane should behave identically when configured through any interface.

Test methodology, configurations and scripts are located under the [test/](../test/README.md) directory

| Category | Description | Detailed Document Links |
| -------- | ----------- | ----------------------- |
| Scaling and performance |Overall device scale and performance objectives |(Need to split doc) [ high-availability-and-scale.md](high-availability-and-scale.md) |
| High Availability |Overall High Availability architecture and requirements | (Need to split doc) [ high-availability-and-scale.md](high-availability-and-scale.md) |
| Dataplane | Detailed dataplane Conformance and performance requirements, independent of the configuration API |[dash-dataplane.md](dash-dataplane.md)
| SAI API | Detailed Switch Abstraction Interface API conformance and performance | [dash-sai-compliance.md]( dash-sai-compliance.md) |
| gNMI API | Detailed gNMI SDN API conformance and performance requirements | [dash-gnmi-compliance.md]( dash-gnmi-compliance.md) |


# Versioning and Configuration Management

>**TODO** Determine a versioning system for each category as well as the overall configuration of a "release."

# Continuous Integration and Test
>**TODO** Continuous integration verifies the correctness of each committed configuration. It can potentially create virtual versions of the entire DASH stack including a simulated (e.g. P4 modeled) version of the DASH pipeline. Define automated (Git Action) workflows for building and/or executing DASH components, and how these are triggered (e.g. for each PR commit, manually triggered, periodically against main, etc.).

# Reference Architectures
Reference architectures for test scenarios are described in 

