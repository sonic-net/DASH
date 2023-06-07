# Table of Contents - DASH Test Documentation

| Document | Description |
|----------|-------------|
| [High-Level Description (HLD) Test Specification](dash-test-HLD.md) | High-level design for the testing of devices which conform to the SONiC-DASH requirements.|
| [Dash Test Maturity Stages](dash-test-maturity-stages.md) | Describes a progressive approach to DASH testing.|
| [DASH SAI-Thrift Test Workflow](dash-test-workflow-saithrift.md) | DASH test workflow with SAI-thrift. |
| [SAI PTF Design](https://github.com/opencomputeproject/SAI/blob/master/doc/SAI-Proposal-SAI-PTF.md) | SAI Thrift auto-generated Python based testing framework doc. |
| [SAI PTF User Guides](https://github.com/opencomputeproject/SAI/tree/master/ptf/docs) | SAI Thrift Server User Guide to autogenerate test frame work. |
| [DASH P4 SAI-Thrift Test Workflow](dash-test-workflow-p4-saithrift.md) | Use of P4-based simulators or SW data planes to verify DASH behavior, using saithrift API. |
| [Keysight Testbed](testbed/README.md) | Describes the setup and configuration of a DASH testbed using Keysight hardware traffic generators.|
| [DASH PTF Testbed](dash-ptf-testbed.md) | Describes the integration of [SAI PTF](https://github.com/opencomputeproject/SAI/tree/master/ptf) into a DASH Test Framework
| [DASH SAI Challenger Testbed](dash-saichallenger-testbed.md) | Describes the integration of [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) and [dpugen](https://pypi.org/project/dpugen/) into a DASH Test Framework |
| [SAI Challenger DASH Schema](README-SAIC-DASH-config-spec.md) | High-level schema to generate scaled configurations (e.g. via [dpugen](https://pypi.org/project/dpugen/)) as well as the DASH "SAI Record" format which comprises SAI "CRUD" operations.
| [SAI Challenger Tutorials](../test-cases/functional/saic/tutorial/README.md) | Guided tour of SAI Challenger for DASH
| [SAI Challenger Test Workflows](dash-test-sai-challenger.md) | How to run scalable tests using SAI-Challenger and snappi. |
| [Testbed](testbed/README.md) | Describes the setup and configuration of a DASH testbed.|
| [snappi and SAI-Challenger based tests](dash-test-sai-challenger.md) | How to run scalable tests using SAI-Challenger and snappi. The scalability is achieved with additional DASH/SAI abstraction level in test code to simplify high scale DUT configuration. |
| [Test Plans](testplans/README.md) |  Home of DASH features test plans including test plan template |
