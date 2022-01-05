---
title: DASH test maturity stages
description: Describes DASH test maturity stages
last update: 01/04/2022
---

[[ << Test docs Table of Contents ]](./README.md)

[[ << DASH/test main README ]](../README.md)

[[ << DASH main README ]](../../README.md)

# DASH test maturity stages

This document describes the DASH test maturity stages. We show both a bottoms-up dataplane testing progression and a top-down full SONiC-stack testing progression. The intent is to articulate the various scenarios and show a set of reference diagrams in order to establish a common vocabulary and workflows. 

## Legend
In the diagrams below, the dashed "callout" notes indicate the prerequisites/dependencies needed to achieve this stage of testing, for example:

![dash-test-maturity-stages-prereq](../images/dash-test-maturity-stages-prereq.png) 

## Bottoms-Up, Dataplane Testing stages
The dataplane can be progressively tested by configuring the DUT through successive "API" layers, starting with the DASH-SAI API, which does not require use of the SONiC stack; then adding more and more SONiC layers; culminating with the use of an application-oriented northbound management API such as gNMI or other interface.

> **NOTE: Stage 3 - DUT Configuration via SAI-Thrift is deemed the minimum "gate" for DASH performance and conformance testing of a DUT's dataplane.** Community dataplane tests will focus on this stage.



### Dataplane Testing Stage 1: Manual/Ad-hoc Testing

![dash-test-maturity-stages-manual](../images/dash-test-maturity-stages-manual.png) 

This testing stage represents internal, vendor-specific testing approaches and probably precedes the use of any DASH community-specified tests. This stage is distinguished by:

* Proprietary DUT configuration mechanisms: e.g. gRPC/REST APIs, config files, utility programs etc. which are not slated for DASH produciton use
* Limited, manually-controlled, test traffic generation and analysis, using arbitrary, vendor-specific  traffic generation equipment, for example IXIA IxExplorer.

### Dataplane Testing Stage 2: Standardized, Automated Test Cases

![dash-test-maturity-stages-std-test-cases](../images/dash-test-maturity-stages-std-test-cases.png) 

This testing stage utilizes standardized, automated test cases which are used by the community. This stage is distinguished by:

* Proprietary DUT configuration mechanisms: e.g. gRPC/REST APIs, config files, utility programs etc. which are not slated for DASH production use
* Standardized, automated test suites (e.g. PyTest), primarly data-driven, which can be scaled out and parameterized to yield many different tests
* Standardized, model-based Traffic Generator config formats, e.g. [OpenTrafficGenerator](https://github.com/open-traffic-generator) using the [snappi](https://github.com/open-traffic-generator/snappi) client library
### Dataplane Testing Stage 3: DUT configuration via SAI-Thrift

![dash-test-maturity-stages-dut-config-sai](../images/dash-test-maturity-stages-dut-config-sai.png) 

This stage represents a crucial milestone for DASH-SONiC development because it verifies the ability to integrate with the SONIiC stack. LAter on, it allows comparing the performance and behavior of a DUT with and without SONiC, to identify potential issues. This stage is distinguished by:

* Vendor `libsai` implementation running on DUT with [saithrift](https://github.com/opencomputeproject/SAI/tree/master/test/saithrift) server endpoint. Note, saithrift is not a production component, it is used only for this test stage.
* Test scripts configure the DUT via saithrift

### Dataplane Testing Stage 4: DUT configuration via SAI-Redis

![dash-test-maturity-stages-dut-config-radis](../images/dash-test-maturity-stages-dut-config-sairedis.png) 

This stage tests integration with the "lower SONiC stack" which consists of the redis datastore `ASIC_DB` and the `syncd` daemon.
>**TODO** - identify other SONiC stack components required for/verified by this stage.

This stage is dinguished by:
* `syncd`, `redis` and sairedis thrift endpoint running on DUT. Note, the thrift-sairedis server is not a production component, it is used only for this test stage.
* Test scripts configure the DUT via saithrift
### Dataplane Testing Stage 5: DUT configuration via SONiC Northbound API

![dash-test-maturity-stages-dut-config-north](../images/dash-test-maturity-stages-dut-config-north.png) 

This stage is the culmination of DUT dataplane integrated with the SONiC stack and is distinguished by:

* Full SONiC stack integration of the [Switch State Services/SWSS](https://github.com/Azure/sonic-swss) (Redis, orchd, syncd, etc.)
* Northbound API endopint such as gNMI or other TBD-API with defined schema and backend
* Test scripts control the DUT via the northbound API

## Options - Fake libsai, P4 simulator
The figures below highlight various options which may be incorporated into various test stages to use a "Fake" libsai backend implementation, or a P4-simulated backend. This is a placeholder for future discussion.

![dash-test-maturity-stages-options](../images/dash-test-maturity-stages-options.png) 
<<<<<<< HEAD
=======

TBD
>>>>>>> dash-test-maturity-stages
