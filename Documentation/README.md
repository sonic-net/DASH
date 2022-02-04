# DASH Documentation 

Documentation covers project wide concerns such as high level design, SDN, high availability, load balancing, testing. See also related DASH [FAQ](https://github.com/Azure/DASH/wiki/FAQ) and [Glossary](https://github.com/Azure/DASH/wiki/Glossary). 

| Document | Description |
|----------|-------------|
| [Compliance Requirements](dash-compliance-requirements.md) | Specifies requirements for a device to be considered DASH-Compliant" |
| [High Availability and Scale](high-availability-and-scale.md) | Describes the aspect of High Availability and Scalability of the project in the SDN Appliance implementation. |
| [Load Balancer](load-balancer-v3.md) | Describes how to switch traffic from using VIP-to-VIP connectivity to using a direct path between VMs. |
| [Program Scale Testing Requirements](program-scale-testing-requirements-draft.md) | Provides a summary of the scale testing requirements for validating program deliverables. |
| [SDN-Features-Packet-Transforms](sdn-features-packet-transforms.md) | Scenarios and background. Service descriptions. Packet encapsulation formats and transformations. Scaling and performance requirements |

## Relationships between Specifications and Testing
The diagram below shows how High-Level Descriptions beget Compliance requirements, compliance requirements beget test cases, and test cases are executed by test scripts to produce Test Results.
![dash-specs-flow](images/general/dash-specs-flow.svg).

Some of the guiding principles for this aproach are:
* Define the objectives and design or proposal without clutter from performance and requirement details.
* Express hard requirements separately from the design and architecture descriptions so that the requirements are easy to define, maintain and reference from other downstream "consumers," e.g. **test cases**. All requirements are identified with some designator which allows traceability in test cases, scripts and results.
* Strive for machine-readable data which can drive test cases. Avoid burying test parameters into the test script so that requirements can be maintained/defined independently from the (often complex) code which executes tests.
* Complete auditability and tracebility of tests cases, test results, associated specs and DUT/SUT configuration. This means  a test run will record versions of every item including Git Repo commit SHA ids, branches, tags, SW versions, API versions, etc.
* Clear, concise human-readable reports, plus machine-readable results allowing dashboards, rolling-up of results, etc.