**[>> Can't wait? Jump to Quick-Start!](#quick-start)**

See also:
* [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets.
* [README-dash-ci](README-dash-ci.md) for CI pipelines.
* [README-dash-docker](README-dash-docker.md) for Docker usage.
* [README-saithrift](README-saithrift.md) for saithrift client/server and test workflows.
* [README-ptftests](README-ptftests.md) for saithrift PTF test-case development and usage.
* [README-pytests](README-pytests.md) for saithrift Pytest test-case development and usage.
# DASH Pipeline
This is a P4 model of the DASH overlay pipeline which uses the [bmv2](https://github.com/p4lang/behavioral-model) from [p4lang](https://github.com/p4lang). It includes the P4 program which models the DASH overlay data plane; Dockerfiles; build and test infrastructure; and CI (Continuous Integration) spec files.

>**IMPORTANT:** Developers, read [Typical Workflow: Committing new code - ignoring SAI submodule](README-dash-workflows.md#typical-workflow-committing-new-code---ignoring-sai-submodule) before committing code.

**Table of Contents**
- [DASH Pipeline](#dash-pipeline)
- [Known Issues](#known-issues)
- [TODOs](#todos)
  - [Loose Ends](#loose-ends)
  - [Desired Optimizations](#desired-optimizations)
  - [Roadmap](#roadmap)
- [Quick-start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Clone this repo](#clone-this-repo)
  - [I feel lucky!](#i-feel-lucky)
  - [Cleanup](#cleanup)
  - [More Make Targets](#more-make-targets)
- [Installing Prerequisites](#installing-prerequisites)
  - [Install git](#install-git)
  - [Install docker](#install-docker)
  - [Install Python 3](#install-python-3)
  - [Install pip3](#install-pip3)
  - [Install docker-compose](#install-docker-compose)

# Known Issues
* P4 code doesn't loop packets back to same port.
* P4 code mark-to-drop not set when meta.drop is set.
* Permission and ownership issues in Docker images, permanent fix is needed.
# TODOs
## Loose Ends
Small items to complete given the existing features and state, e.g. excluding major roadmap items.
* Update SAI submodule to upstream when PRs are merged (currently using dev branches for URLs)
* Produce "dev" and "distro" versions of docker images. Dev images mount to host FS and use artifacts built on the host. Distro images are entirely self-contained including all artifacts.
## Desired Optimizations
* Build a Docker image automatically when its Dockerfile changes, publish and pull from permanent repo
* Use Azure Container Registry (ACR) for Docker images instead of temporary Dockerhub registry
* Use dedicated higher-performance runners instead of [free Azure 2-core GitHub runner instances](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)

## Roadmap
These are significant feature or functionality work items.
* Use modified bmv2 which adds stateful processing. Current version is vanilla bmv2. This will require building it instead of using a prebuilt bmv2 docker image, see [Build Docker dev container](#build-docker-dev-container). [**WIP**]
* Add DASH service test cases including SAI-thrift pipeline configuration and traffic tests

# Quick-start

## Prerequisites

See [Installing Prerequisites](#installing-prerequisites) for details.

* Ubuntu 20.04, bare-metal or VM
* 2 CPU cores minimum, 7GB RAM, 14Gb HD; same as [free Azure 2-core GitHub runner instances](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources), we'll try to live within these limits
* git - tested with version 2.25.1
* docker
* [docker-compose](#install-docker-compose) (**1.29.2 or later**)

## Clone this repo
```
git clone <repository URL>
cd DASH
```
**Optional** - if you require a particular dev branch:
```
git checkout <branch>
```
Init (clone) the SAI submodule:
```
git submodule update --init # NOTE --recursive not needed (yet)
```
## I feel lucky!
Eager to see it work? First [clone this repo](#clone-this-repo), then do the following:

In first terminal (console will print bmv2 logs):
```
cd dash-pipeline
make clean && make all run-switch
```
The above procedure takes awhile since it has to pull docker images (once) and build some code.

In second terminal (console will print saithrift server logs):
```
make run-saithrift-server
```
In third terminal (console will print test results):
```
make run-all-tests
```
When you're done, do:
```
make kill-all      # just to stop the daemons
                   # you can redo "run" commands w/o rebuilding
```
*OR*
```
make clean         # stop daemons and clean everything up
```
The final `clean` above will kill the switch, delete artifacts and veth pairs.


The tests may use a combination of SW packet generators:
* Scapy - well-known packet-at-a-time SW traffic generator/capture
* ixia-c - performant flow-based packet generator/capture
  
The setup for ixia-c -based traffic tests is as follows. More info is available [here](README-dash-workflows#about-snappi-and-ixia-c-traffic-generator).

![ixia-c setup](../test/third-party/traffic_gen/deployment/ixia-c.drawio.svg)


## Cleanup
This is a summary of most-often used commands, see [README-dash-workflows.md](README-dash-workflows.md) for more details.

* `CTRL-c` - kill the switch container from within the interactive terminal
* `make kill-all` - kill all the running containers
* `make clean` - clean up everything, kill containers

## More Make Targets
See [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets. There are many fine-grained Make targets to control your development workflow.
# Installing Prerequisites
## Install git
```
sudo apt install -y git
```
## Install docker
Need for basically everything to build/test dash-pipeline.

See:
* https://docs.docker.com/desktop/linux/install/

## Install docker-compose
>**NOTE** Use docker-compose 1.29.2 or later! The `.yml` file format changed. Using an older version might result in an error such as: <br/> `ERROR: Invalid interpolation format for "controller" option in service "services": "ixiacom/ixia-c-controller:${CONTROLLER_VERSION:-latest}"`

It is assumed you already have Docker on your system.
The `docker-compose` command is used to orchestrate the ixia-c containers. You need to install it to run the ixia-c test scripts (`ixia-c` itself doesn't require docker-compose; it's merely convenient for instantiating it using a declarative `.yml` file).

See also:
* https://www.cyberithub.com/how-to-install-docker-compose-on-ubuntu-20-04-lts-step-by-step/
  

Installation of `docker-compose` has to be done just once. You can use another technique based on your platform and preferences. The following will download and install a linux executable under `/usr/local/bin`. You should have a PATH to this directory. **You can edit the commands below to locate it somewhere else as desired; just change the path as needed.**


```
sudo mkdir -p /usr/local/bin
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

To test installation, execute the following. The output on the second line is an example, yours may differ.
```
docker-compose --version
docker-compose version 1.29.2, build 5becea4c
```
