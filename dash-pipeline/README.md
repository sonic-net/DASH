**[>> Can't wait? Jump to Quick-Start!](#quick-start)**

See also:
* [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets.
* [README-dash-ci](README-dash-ci.md) for CI pipelines.
* [README-dash-docker](README-dash-docker.md) for Docker usage.
# DASH Pipeline
This is a P4 model of the DASH overlay pipeline which uses the [bmv2](https://github.com/p4lang/behavioral-model) from [p4lang](https://github.com/p4lang). It includes the P4 program which models the DASH overlay dataplane; Dockerfiles; build and test infrastructure; and CI (Continuous Integration) spec files.

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
  - [Get the right branch](#get-the-right-branch)
  - [I feel lucky!](#i-feel-lucky)
  - [Build Artifacts](#build-artifacts)
  - [Run bmv2 software switch](#run-bmv2-software-switch)
  - [Run tests](#run-tests)
  - [Cleanup](#cleanup)
- [Installing Prequisites](#installing-prequisites)
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
Small items to complete given the exsting features and state, e.g. excluing major roadmap items.
* Update SAI submodule to upstream when PRs are merged (currently using dev branches for URLs)
* Produce "dev" and "distro" versions of docker images. Dev images mount to host FS and use artifacts built on the host. Distro images are entirely self-contained including all artifacts.
## Desired Optimizations
* Build a Docker image automatically when its Dockerfile changes, publish and pull from permanent repo
* Use Azure Container Registry (ACR) for Docker images instead of temporary Dockerhub registry
* Use dedicated higher-performance runners instead of [free Azure 2-core GitHub runner instances](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)

## Roadmap
These are significant feature or functionality work items.
* Use modified bmv2 which adds stateful processing. Current version is vanilla bmv2. This will require building it instead of using a prebuilt bmv2 docker image, see [Build Docker dev container](#build-docker-dev-container). [**WIP**]
* Integrate SAI-thrift server from [OCP/SAI](https://github.com/opencomputeproject/SAI) [**WIP**]
* Add DASH sevice test cases including SAI-thrift pipeline configuration and traffic tests

# Quick-start

## Prerequisites

See [Installing Prequisites](#installing-prequisites) for details.

* Ubuntu 20.04, bare-metal or VM
* 2 CPU cores minimum, 7GB RAM, 14Gb HD; same as [free Azure 2-core GitHub runner instances](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources), we'll try to live within these limits
* git - tested with version 2.25.1
* docker
* [docker-compose](#install-docker-compose) (**1.29.2 or later**)
* python3, pip3

## Clone this repo
```
git clone <repo URL>
git submodule update --init # NOTE --recursive not needed (yet)
```
## Get the right branch

**Optional** - if you require a particular dev branch.
```
git checkout <branch>
```
## I feel lucky!
Eager to see it work? Try this:

In first terminal (console will print bmv2 logs):
```
make clean && make all run-switch
```
In second terminal (console will print sai-thrift server logs):
```
make clean && make all network run-switch
```
In third terminal (console will print test results):
```
make run-all-tests clean
```
The final `clean` above will kill the switch, delete artifacts and veth pairs.

Below we break down the steps in more detail.

## Build Artifacts
```
make clean # optional, as needed
make all
```

## Run bmv2 software switch
This will also automatically ceate `veth` pairs as needed.
```
make run-switch     # willrun in foreground with logging
```

## Run tests
Use a different terminal:
```
make run-test          # Simple SAI table accessor, no traffic
```
Follow instructions for [Install docker-compose](#install-docker-compose), then:
```
make run-ixiac-test    # Uses SW traffic-generator
```
The setup for ixia-c traffic tests is as follows. More info is available [here](README-dash-workflows#about-snappi-and-ixia-c-traffic-generator).

![ixia-c setup](../test/third-party/traffic_gen/deployment/ixia-c.drawio.svg)

## Cleanup

This is a summary of most-often used commands, see [README-dash-workflows.md](README-dash-workflows.md) for more details.

* `CTRL-c` - kill the switch container from within the iteractive terminal
* `make kill-switch` - kills the switch container from another terminal
* `make network-clean` - delete veth pairs
* `make undeploy-ixiac` - kill ixia-c containers
* `make p4-clean` - delete P4 artifacts
* `make sai-clean` - delete SAI artifacts. Do this before committing code, see [Here](README-dash-workflows.md#typical-workflow-committing-new-code---ignoring-sai-submodule) 
* `make clean` - does all of the above

# Installing Prequisites

## Install git
```
sudo apt install -y git
```

## Install docker
Need for basically everything to build/test dash-pipeline.

See:
* https://docs.docker.com/desktop/linux/install/

## Install Python 3
This is probably already installed in your Linux OS, but if not:

See:
* https://docs.python-guide.org/starting/install3/linux/

```
sudo apt install -y python3
```
  
## Install pip3
See:
* https://pip.pypa.io/en/latest/installation/

You can probably use the following command for most cases:
```
sudo apt install -y python3-pip
```
## Install docker-compose
>**NOTE** Use docker-compose 1.29.2 or later! The `.yml` file format changed. Using an older version might result in an error such as: <br/> `ERROR: Invalid interpolation format for "controller" option in service "services": "ixiacom/ixia-c-controller:${CONTROLLER_VERSION:-latest}"`

It is assumed you already have Docker on your system.
The `docker-compose` command is used to orchestrate the ixia-c containers. You need to install it to run the ixia-c test scripts (`ixia-c` itself doesn't require docker-compose; it's merely convenient for instantiating it using a declarative `.yml` file).

See also:
* https://www.cyberithub.com/how-to-install-docker-compose-on-ubuntu-20-04-lts-step-by-step/
  

Installation of `docker-compose` has to be done just once. You can use another technique based on your platform and preferences. The following will download and install a linux executable under `/usr/local/bin`. You should have a PATH to this directory. You can edit the below command to locate it somewhere else as desired, just change the path as needed.


```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

To test installation, execute the following. The output on the second line is an example, yours may differ.
```
docker-compose --version
docker-compose version 1.29.2, build 5becea4c
```
