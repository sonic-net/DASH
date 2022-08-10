[[ << Back to DASH top-level README ](../README.md)]
# DASH Documentation 

Documentation comprises system descriptions, High-level design (HLD) documents and detailed compliance requirements. These are contained in the [DASH/documentation](./) directory and subdirectories.

The testing framework, methodology, documentation and testing artifacts are stored in the [DASH/test](../test) directory

See also DASH [FAQ](https://github.com/Azure/DASH/wiki/FAQ) and [Glossary](https://github.com/Azure/DASH/wiki/Glossary). 

# Contents
## Baseline Specifications and Requirements
All DASH devices shall conform to the following design specifications and compliance requirements:

| Topic   | Links to Folders |
| ------- | ---------|
| General Architecture and Requirements| [Parent Folder](general/README.md) \| [ Design](general/design/README.md) \| [Compliance Requirements](general/requirements/README.md)|
| Data plane                           | [Parent Folder](dataplane/README.md) \| [ Design](dataplane/design/README.md) \| [Compliance Requirements](dataplane/requirements/README.md)|
| High-Availability (HA)                                                    | [Parent Folder](high-avail/README.md) \| [ Design](high-avail/design/README.md) \| [Compliance Requirements](high-avail/requirements/README.md)|
| gNMI Northbound API                  | [Parent Folder](gnmi/README.md) \| [ Design](gnmi/design/README.md) \| [Compliance Requirements](gnmi/requirements/README.md)|
| SAI Southbound API                   | [Parent Folder](sai/README.md) \| [ Design](sai/design/README.md) \| [Compliance Requirements](sai/requirements/README.md)|

## Service Specifications and Requirements
DASH devices may implement one or more of the following services.
They shall conform to each service's design specifications and compliance requirements.
| Topic   | Links to Folders |
| ------- | ---------|
| Load Balancer Service                | [Parent Folder](load-bal-service/README.md) \| [ Design](load-bal-service/design/README.md) \| [Compliance Requirements](load-bal-service/requirements/README.md)|
| VNET-to-VNET Service                         | [Parent Folder](vnet2vnet-service/README.md) \| [ Design](vnet2vnet-service/design/README.md) \| [Compliance Requirements](vnet2vnet-service/requirements/README.md)|
| Service Tunnel & Private Link Service                          | [Parent Folder](stpl-service/README.md) \| [ Design](stpl-service/design/README.md) \| [Compliance Requirements](stpl-service/requirements/README.md)|
| VNET Peering Service                          | [Parent Folder](vnet-peering-service/README.md) \| [ Design](vnet-peering-service/design/README.md) \| [Compliance Requirements](vnet-peering-service/requirements/README.md)|
| Express Route (ER) Service                    |  [Parent Folder](express-route-service/README.md) \| [ Design](express-route-service/design/README.md) \| [Compliance Requirements](express-route-service/requirements/README.md)|
| Encryption Gateway Service                    |  [Parent Folder](encrypt-gw-service/README.md) \| [ Design](encrypt-gw-service/design/README.md) \| [Compliance Requirements](encrypt-gw-service/requirements/README.md)|


# Organization of Design & Requirements Documents
Documentation consists of separate, but related *System Descriptions* (HLDs, architecture, theory of operations, etc.) and *Compliance Requirements* (hard specifications, typically numerical  but also behavioral). These two types of documents are deliberately kept separated, see [Relationships and Flow of Documents](#relationships-and-flow-of-documents).

Documentation is organized into folders as follows. Each feature or topic has all the high-level specs  and the compliance requirements in the same parent folder, e.g. General, High-Availability, etc., making it easier to access related information about one topic. As the complexity grows, this helps keep things organized according to "functional topic." 
```
topic1
    design
        topic1 High-level Descriptions and architecture
    requirements
        topic1 compliance Requirements

topic2
    design
        topic2 High-level Descriptions
    requirements
        topic2 compliance Requirements

etc
...
```

# Relationships and Flow of Documents
The diagram below shows how High-Level Descriptions beget Compliance requirements, compliance requirements beget test cases, and test cases are executed by test scripts to produce Test Results.

![dash-specs-flow](images/general/dash-specs-flow.svg).

Some of the guiding principles for this approach are:
* Define the objectives and the design or proposal separately from performance and requirement details.
* Describe **hard requirements** separately from the design and architecture descriptions This allows the requirements to be easily defined, maintained, and referenced from other downstream "consumers," e.g., **test cases**. All requirements must be identified with some designator which allows traceability in test cases, scripts and results.
* We encourage the creation of simultaneous **human** and **machine-readable** data which can **drive test cases**.  
* We must avoid burying test parameters into the test scripts. This allows the requirements to be maintained/defined independently from the (often complex) code which executes tests. 
* Many projects exist where only a programmer can locate and ferret out actual test criteria, often expressed as hard-coded constants buried within thousands of lines of test automation code. For quality control, these criteria must be easily accessible, reviewable and maintainable, to anyone familiar with the project.
* We advocate complete auditability and traceability of tests cases, test results, associated specs and DUT/SUT configuration. This means a test run will record versions of every item including GitHub repository commit SHA ids, branches, tags, SW versions, API versions, etc.
* Clear, concise and to the point human-readable reports, plus machine-readable results allowing dashboards, rolling-up of results, etc.

## Related Repositories

- [SONiC](https://github.com/Azure/SONiC)
- [SAI](https://github.com/opencomputeproject/SAI)
- [P4](https://opennetworking.org/p4) and [P4 working group](https://p4.org/working-groups)
- [PINS](opennetworking.org/pins)
- [PNA Consortium Spec](https://p4.org/p4-spec/docs/PNA-v0.5.0.html)
- [IPDK](https://ipdk.io/) and [IPDK GitHub](https://github.com/ipdk-io/ipdk-io.github.io)
- [bmv2 - behavioral model v2](https://github.com/p4lang/behavioral-model)
- [DPDK](https://www.dpdk.org)


## References

- [Glossary](https://github.com/Azure/DASH/wiki/Glossary)
- [FAQ](https://github.com/Azure/DASH/wiki/FAQ)


