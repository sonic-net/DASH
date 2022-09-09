[[ << Back to DASH top-level README ](../README.md)]
# DASH Documentation 

Documentation comprises system descriptions, High-level design (HLD) documents and detailed compliance requirements. These are contained in the [DASH/documentation](./) directory and subdirectories.

The testing framework, methodology, documentation and testing artifacts are stored in the [DASH/test](../test) directory

See also DASH [FAQ](https://github.com/Azure/DASH/wiki/FAQ) and [Glossary](https://github.com/Azure/DASH/wiki/Glossary). 

# Contents

## Baseline Specifications and Requirements

All DASH devices shall conform to the following design specifications and compliance requirements:

| Topic                                 | Documents                                   |
| ------------------------------------- | --------------------------------------------|
| General Architecture and Requirements | [DASH general](./general/README.md)|        |
| Data plane                            | [Data plane](./dataplane/README.md)         |
| High-Availability (HA)                | [High-Availability](./high-avail/README.md) |
| gNMI Northbound API                   | [gNMI Northbound API](./gnmi/README.md)     |
| SAI Southbound API                    | [SAI Southbound API](./sai/README.md)       |

## Service Specifications and Requirements

DASH devices may implement one or more of the following services.

They shall conform to each service's design specifications and compliance requirements.

| Topic                                 | Documents                                                         |
| --------------------------------------| ------------------------------------------------------------------|
| Load Balancer Service                 | [Load Balancer Service](./load-bal-service/README.md)             |
| VNET-to-VNET Service                  | [VNET-to-VNET Service](./vnet2vnet-service/README.md)             |
| Service Tunnel & Private Link Service | [Service Tunnel & Private Link Service](./stpl-service/README.md) |
| VNET Peering Service                  | [VNET Peering Service ](./vnet-peering-service/README.md)         |
| Express Route (ER) Service            | [Express Route (ER) Service](./express-route-service/README.md)   |
| Encryption Gateway Service            | [Encryption Gateway Service](./encrypt-gw-service/README.md)      |


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


