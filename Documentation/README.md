# DASH Documentation 

Documentation comprises system descriptions, High-level design (HLD) documents and detailed compliance requirements.

See also DASH [FAQ](https://github.com/Azure/DASH/wiki/FAQ) and [Glossary](https://github.com/Azure/DASH/wiki/Glossary). 


## Organization of Documents
Documentation consists of separate, but related *System Descriptions* (HLDs, architecture, theory of operations, etc.) and *Compliance Requirements* (hard specifications, typically numerical  but also behavioral). These two types of documents are deliberately kept separated, see [Relationships and Flow of Documents](#relationships-and-flow-of-documents).

Documentation is organized into folders as follows. Each feature or topic has all the high-level specs  and the compliance requirements in the same parent folder, e.g. General, High-Availability, etc., making it easier to access related information about one topic. As the complexity grows, this helps keep things organized according to "functional topic." 
```
topic1
    design
        Topic1 High-level Descriptions and architecture
    requirements
        Topic1 compliance Requirements

topic2
    design
        topic2 High-level Descriptions
    requirements
        topic2 compliance Requirements

etc
...
```
## Contents


| Topic   | Links to Folders |
| ------- | ---------|
| General Architecture and Requirements| [ Design](general/design/README.md) \| [Compliance Requirements](general/requirements/README.md)|
|                                      | General Performance and scale compliance requirements       |
| High-Availability (HA)               | High-Availability and Scale HLD                             |
| Dataplane                            | Dataplane HLD                                               |
|                                      | Dataplane Compliance Requirements                           |
|                                      | HA and Scale Compliance Requirements                        |
| VNET Service                         | VNET Service HLD                                            |
|                                      | VNET Service Packet Transforms                              |
|                                      | VNET Service Compliance Requirements                        |
| Load Balancer Service                | Load Balancer Service HLD                                   |
|                                      | Load Balancer Service Compliance Requirements               |
| SAI Southbound API                   | SAI HLD                                                     |
|                                      | SAI Compliance Requirements                                 |
| gNMI Northbound API                  | gNMI HLD                                                    |
|                                      | gNMI schema (unless described under SONiC repo)             |
|                                      | gNMI Compliance Requirements                                |

Original ToC Structure - not scalable:

| Document | Description |
|----------|-------------|
| [Compliance Requirements](dash-compliance-requirements.md) | Specifies requirements for a device to be considered DASH-Compliant" |
| [High Availability and Scale](high-availability-and-scale.md) | Describes the aspect of High Availability and Scalability of the project in the SDN Appliance implementation. |
| [Load Balancer](load-balancer-v3.md) | Describes how to switch traffic from using VIP-to-VIP connectivity to using a direct path between VMs. |
| [Program Scale Testing Requirements](program-scale-testing-requirements-draft.md) | Provides a summary of the scale testing requirements for validating program deliverables. |
| [SDN-Features-Packet-Transforms](sdn-features-packet-transforms.md) | Scenarios and background. Service descriptions. Packet encapsulation formats and transformations. Scaling and performance requirements |

## Relationships and Flow of Documents
The diagram below shows how High-Level Descriptions beget Compliance requirements, compliance requirements beget test cases, and test cases are executed by test scripts to produce Test Results.
![dash-specs-flow](images/general/dash-specs-flow.svg).

Some of the guiding principles for this aproach are:
* Define the objectives and design or proposal without clutter from performance and requirement details.
* Express hard requirements separately from the design and architecture descriptions so that the requirements are easy to define, maintain and reference from other downstream "consumers," e.g. **test cases**. All requirements are identified with some designator which allows traceability in test cases, scripts and results.
* Strive for simultaneous human- and machine-readable data which can drive test cases. Avoid burying test parameters into the test script so that requirements can be maintained/defined independently from the (often complex) code which executes tests. Many projects exist where only a programmer can locate and ferret out actual test criteria, often expressed as hard-coded constants buried within thousands of lines of test automation code. In contrast, these criteria should be easily accessible, reviewable and maintainable, to anyone familiar with the project.
* Complete auditability and tracebility of tests cases, test results, associated specs and DUT/SUT configuration. This means  a test run will record versions of every item including Git Repo commit SHA ids, branches, tags, SW versions, API versions, etc.
* Clear, concise human-readable reports, plus machine-readable results allowing dashboards, rolling-up of results, etc.