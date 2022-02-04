# DASH Documentation 

Documentation comprises system descritions, High-level design (HLD) documetns and detgailed compliance reqauirements.

See also DASH [FAQ](https://github.com/Azure/DASH/wiki/FAQ) and [Glossary](https://github.com/Azure/DASH/wiki/Glossary). 


## Organization of Documents
Documentation consists of separate, but realted *System Descriptions* (HLDs, architecture, theory of operations, etc.) and *Compliance Requirements* (hard specifications, typically numerical  but also behavioral). These two types of documents are deliberately kept separated, see [Relationships and Flow of Documents](#relationships-and-flow-of-documents).

Documentation is organiaed into folders as follows:

>**Chris' Commentary about current organization**:
Currently, we have everything lumped into one folder and the high-level design and performance requirements are somewhat intermingled. There is no roadmap to future growth, no common format and no clear way how to create traceable, rigorous test cases from these documents in a maintainable fashion. Hence my proposals below.

### Chris' Proposal 1 - Group HLDs & compliance requirements by category/feature/service (my first choice)
In this format, each feature or aspect has all the high-level specs  and the compliance requirements in the same folder, making it easier to access related information about one topic. As the complexity grows, this helps keep things organised according to "functional topic."
```
General
    General High-level Descriptions
    General compliance Requirements (performance and scale...unless it's tied to VNET service in which case we move it below into VNET Service folder)

High Availability
    HA High-level Descriptions
    HA compliance Requirements

Vnet Service
    VNET service HLDs
    VNET Service Compliance Requirements

Load Balancer Service
    VNET service HLDs
    VNET Service Compliance Requirements

Service XYZ
    Service XYZ service HLDs
    Service XYZ Service Compliance Requirements
...
...
```
### Chris' Proposal 2 - Group all HLDs in one folder, all compliance requirements in another
In this format, all the HLDs are in one folder and compliance requirements in another folder, makint it easier to find all the documents at the same "level" of detail. As the complexity grows, this helps keep things organised according to "technical area of interest/expertise" (architesure/features vs. detailed requirements).
```
System Descriptions/HLDs
    General High-level Descriptions
    HA High-level Descriptions
    VNET service HLDs
    Load Balancer service HLDs
    Service XYZ service HLDs
    ...

Detailed Compliance Requirements
    General compliance Requirements (performance and scale...?)
    HA compliance Requirements
    VNET Service Compliance Requirements
    Load Balancer Service Compliance Requirements
    Service XYZ Service Compliance Requirements
    ...
```

## ToC
Needs to be reorganized per the choices made above.

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