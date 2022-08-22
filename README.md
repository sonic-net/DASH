[![DASH-bmv2-CI](https://github.com/Azure/DASH/workflows/DASH-BMV2-CI/badge.svg?branch=main)](https://github.com/Azure/DASH/actions/workflows/dash-bmv2-ci.yml)

# SONiC-DASH - Disaggregated API for SONiC Hosts - DRAFT/Work in Progress

## SONiC-DASH is a new open source project that will "deliver enterprise network performance to critical cloud applications".  The project extends functionality to stateful workloads.  

We are developing set of APIs and object models describing network services for the cloud, and will work with all cloud providers and enterprise hybrid clouds to develop further functionality. We believe the DASH program describes a comprehensive set of services that are required by the vast majority of clouds. The goal of DASH is to be specific enough for SMART Programmable Technologies to optimize network performance and leverage commodity **hardware** technology to achieve 10x or even 100x stateful connection performance.

The technology has multiple applications such as 1) NIC on a host, 2) a Smart Switch, 3) Network Disaggregation, and 4) high performance Network Appliances. Many technology companies have committed to further developing this new open technology and its community. The best minds and practitioners are actively collaborating to optimize performance of the cloud by extending SONiC to include stateful workloads. 
 
Future innovations for in-service software upgrades and ultra-high availability for stateful connections will also be developed with the utmost importance. 

We hope that DASH will have the same success as SONiC for switches and will experience wide adoption as a major Open NOS for Programmable Technologies (including SmartNICs) to supercharge a variety of cloud and enterprise applications. 

## Where to Start?
Visit the [Documentation table of contents](documentation/README.md) for access to all design and requirements documents.

For a quick technical deep-dive, please begin with:

1. Peruse the [DASH high level design](documentation/general/design/dash-high-level-design.md) for an overview of DASH architecture. 
1. The [SDN Packet Transforms](documentation/general/design/sdn-features-packet-transforms.md) document, this facilitates understanding of the program goal and the 7 networking scenarios that Azure has defined.  
1. [Program Scale Testing Requirements - Draft](documentation/general/requirements/program-scale-testing-requirements-draft.md) for an example of a test to stress DPU/NIC hardware.

The API and Object Model for VNET<->VNET is in draft; the remaining services will be posted over as we move forward.

DASH Testing is covered  under the [test/](test/README.md) directory and is a work in progress.

## I Want To Contribute!

This project welcomes contributions and suggestions.  We are happy to have the Community involved via submission of **Issues and Pull Requests** (with substantive content or even just fixes). We are hoping for the documents, test framework, etc. to become a community process with active engagement.  PRs can be reviewed by by any number of people, and a maintainer may accept.

See [GitHub Basic Process](doc-github-rules.md).

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

<!-- dash icon -->
<div align="center">
<img src="documentation/images/icons/dash-icon-medium.svg" style="align:center;"/>
<div/> 
