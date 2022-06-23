# Sirius Pipeline
This is a P4 model of the DASH overlay pipeline which uses the [bmv2](https://github.com/p4lang/behavioral-model) from [p4lang](https://github.com/p4lang).

>**IMPORTANT:** Developers, read [Typical Workflow: Committing new code - ignoring SAI submodule](#typical-workflow-committing-new-code---ignoring-sai-submodule) before committing code.

- [Sirius Pipeline](#sirius-pipeline)
- [Known Issues](#known-issues)
- [TODOs](#todos)
  - [Loose Ends](#loose-ends)
  - [Desired Optimizations](#desired-optimizations)
  - [Roadmap](#roadmap)
- [Quick-start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Clone this repo](#clone-this-repo)
  - [Get the right branch](#get-the-right-branch)
  - [Build Artifacts](#build-artifacts)
  - [Run bmv2 software switch](#run-bmv2-software-switch)
  - [Run tests](#run-tests)
  - [Cleanup](#cleanup)
- [CI (Continuous Integration) Via Git Actions](#ci-continuous-integration-via-git-actions)
    - [CI Build log - Passing example](#ci-build-log---passing-example)
    - [CI Build log - Fail example](#ci-build-log---fail-example)
- [Detailed Build Workflow](#detailed-build-workflow)
  - [Build Workflow Diagram](#build-workflow-diagram)
  - [Build Docker dev container](#build-docker-dev-container)
  - [Optional - Manually Pull the pre-built Docker image](#optional---manually-pull-the-pre-built-docker-image)
  - [Optional - expert - build a new Docker image](#optional---expert---build-a-new-docker-image)
  - [Optional - Expert/Admin - Publish Docker Image](#optional---expertadmin---publish-docker-image)
  - [Optional - expert - `exec` a container shell](#optional---expert---exec-a-container-shell)
  - [Compile P4 Code](#compile-p4-code)
  - [Build libsai.so adaptor library](#build-libsaiso-adaptor-library)
    - [Restore SAI Submodule](#restore-sai-submodule)
  - [Build SAI client test program(s)](#build-sai-client-test-programs)
  - [Create veth pairs for bmv2](#create-veth-pairs-for-bmv2)
  - [Run software switch](#run-software-switch)
  - [Run simple SAI library test](#run-simple-sai-library-test)
  - [Run ixia-x traffic-generator test](#run-ixia-x-traffic-generator-test)
    - [ixia-c components and setup/teardown](#ixia-c-components-and-setupteardown)
    - [About snappi and ixia-c traffic-generator](#about-snappi-and-ixia-c-traffic-generator)
      - [Opensource Sites:](#opensource-sites)
      - [DASH-specific info:](#dash-specific-info)
- [Configuration Management](#configuration-management)
- [Installing Prequisites](#installing-prequisites)
  - [Install docker](#install-docker)
  - [Install Python 3](#install-python-3)
  - [Install pip3](#install-pip3)
  - [Install docker-compose](#install-docker-compose)
- [Developer Workflows](#developer-workflows)
  - [About Git Submodules](#about-git-submodules)
    - [Why use a submodule?](#why-use-a-submodule)
    - [Typical Workflow: Committing new code - ignoring SAI submodule](#typical-workflow-committing-new-code---ignoring-sai-submodule)
    - [Committing new SAI submodule version](#committing-new-sai-submodule-version)

# Known Issues
* The vnet_out test via `make run-test` needs to be run to allow `run-ixiac-test` to pass. Need to understand why this is so.
* Prebuilt Docker image is too large (> 12G), see [Desired Optimizations](#desired-optimizations).

# TODOs
## Loose Ends
These are work items to complete the project with existing features and functionality.

* Use specific tags on docker images (not `:latest`)
* Check for veths in run-switch, create automatically?

## Desired Optimizations
* Make smaller docker image or images to speed up downloading, reduce memory footprint, etc.
  * Make a smaller Docker image by stripping unneeded sources (e.g. grpc, p4c), apt caches etc. Current 12G image is large. Possibly use staged docker builds to permit precise copying of only necessary components. Consider contents of the base image (`p4lang/behavioral-model:no-pi`). For example, see:
    * https://devopscube.com/reduce-docker-image-size/
    * https://developers.redhat.com/articles/2022/01/17/reduce-size-container-images-dockerslim
  * Break the current docker image into multiple smaller images, one for each purpose in the build workflow. For example:
    * Compiling p4 code to produce .json outputs. Should we use [p4lang/p4c](https://hub.docker.com/r/p4lang/p4c) pre-built docker instead of building it into our current all-in-one image? 
    * Generating the SAI headers, P4Runtime adaptor and producing `libsai.so`
    * Running the bmv2 switch
    * Building the SAI-thrift server
    * Running the SAI-thrift server
* Consider building the behavioral-model base image from p4lang source at a known version, instead of pulling from Dockerhub, see [Configuration Management](#configuration-management). We might add p4lang/behavioral-model at a known commit level and build a docker image ourselves, so we can control the contents more precisely.
* Build Docker image automatically when Dockerfile changes, publish and pull from permanent repo
* Use Azure Container Registry (ACR) for Docker images instead of temporary Dockerhub registry
* Use dedicated higher-performance runners instead of [free Azure 2-core GitHub runner instances]((https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources))
* Explore use of [virtualenv](https://virtualenv.pypa.io/en/latest/) to avoid contaiminating the local environment with this project's particular Python requirements.

## Roadmap
These are significant feature or functionality work items.
* Use modified bmv2 which adds stateful processing. Current version is vanilla bmv2. This will require building it instead of using a prebuilt bmv2 docker image, see [Build Docker dev container](#build-docker-dev-container).
* Integrate SAI-thrift server from [OCP/SAI](https://github.com/opencomputeproject/SAI)
* Add DASH sevice test cases including SAI-thrift pipeline configuration and traffic tests

# Quick-start
## Prerequisites

See [Installing Prequisites](#installing-prequisites) for details.

* Ubuntu 20.04, bare-metal or VM
* docker, docker-compose (1.29.2 or later)
* python3, pip3

## Clone this repo
```
git clone <repo URL>
```
>**NOTE** You *don't* need to use `--recursive` even though we use git submodules; the `Makefile` takes care of initializing any submodules the first time (e.g. `SAI`) and avoids unnecessary recursion, which is slow but harmless.

If you prefer initializing the submodule manually, you can perform this step after `git clone`:
```
git submodule update --init # NOTE --recursive not needed (yet)
```
## Get the right branch

**Optional** - if you require a particular dev branch.
```
git checkout <branch>
```
## Build Artifacts
```
make clean # optional, as needed
make all
```

## Run bmv2 software switch
```
sudo make network   # once, to create veth pairs, etc.
make run-switch     # will run in foreground with logging
```

## Run tests
Use a different terminal:
```
make run-test          # Simple SAI table accessor, no traffic
```
Follow instructions for [Install docker-compose](#install-docker-compose), then:
```
make run-ixiac-test    # UDP traffic, by default it echos back
```
The setup for ixia-c traffic tests is as follows. More info is available [here](#about-ixia-x-traffic-generator).

![ixia-c setup](../test/third-party/traffic_gen/deployment/ixia-c.drawio.svg)
## Cleanup

* `CTRL-c` - kill the switch container
* `make network-clean` - delete veth pairs
* `make undeploy-ixiac` - kill ixia-c containers

# CI (Continuous Integration) Via Git Actions
This project contains [Git Actions](https://docs.github.com/en/actions) to perform continuous integration whenever certain actions are performed. These are specified in YAML files under [.github/workflows](../.github/workflows) directory.

* [sirius-ci.yml](../.github/workflows/sirius-ci.yml): A Commit or Pull Request of P4 code, Makefiles, scripts, etc.  will trigger a build of all artifacts and run tests, all in the Azure cloud. Status can be viewed on the Github repo using the "Actions" link in the top of the page. This will be true for forked repos as well as the main Azure/DASH repo.

  Two tests are currently executed in the CI pipeline. These will be increased extensively over time:
  * The `make run-test` target does a trivial SAI access using a c++ client program. This verifies the libsai-to-P4runtime adaptor over a socket. The test program acts as a P4Runtime client, and the bmv2 simple_switch process is the server.
  * The `make run-ixiac-test` target spins up a two-port software (DPDK) traffic-generator engine using the free version of [ixia-c](https://github.com/open-traffic-generator/ixia-c) controlled by a Python [snappi](https://github.com/open-traffic-generator/snappi) client. Using this approach allows the same scripts to eventually be scaled to line-rate using hardware-based traffic generators.
* [sirius-dev-docker.yml](../.github/workflows/sirius-dev-docker.yml): A commit of the [Dockerfile](Dockerfile) will trigger the [make docker](#build-docker-dev-container) build target and rebuild the `dash-bmv2` docker container. It will not publish it though, so it's ephemeral and disappears when the Git runner terminates. The main benefit of this is it may run much faster in the cloud than locally, allowing you to test for a successful build of changes more quickly.
* The CI badge will be updated according to the CI build status and appear on the front page of the repo (it's actually on the top-level README). You can click on this icon to drill down into the Git Actions history and view pass/fail details. Typical icons appear below:

  ![CI-badge-passing.svg](../assets/CI-badge-passing.svg)  ![CI-badge-failing.svg](../assets/CI-badge-failing.svg)  

Badges have flexibility, for example we could show the status of more than one branch at a time.

See:
* https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows
* https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)
### CI Build log - Passing example

A typical "Good" CI log appears below, this can be watched in real-time:

![CI-build-log-ok.png](../assets/CI-build-log-ok.png)  

### CI Build log - Fail example
A typical "Failed" CI log appears below. You can click on the arrow next to the red circled "X" and see details. In this example there is a (deliberate) P4 coding error.

![CI-build-log-fail.png](../assets/CI-build-log-fail.png)

Let's drill down into the Build P4 step which failed. We see a a bad statement. (There is no `#import` keyword for P4 or the C preprocessor).
```
#import DOH.h
```

![CI-build-log-fail-p4-drilldown.png](../assets/CI-build-log-fail-p4-drilldown.png)  

The main README for this repo shows the CI failing badge:

![CI-fail-README-badge](../assets/CI-fail-README-badge.png)
# Detailed Build Workflow
This explains the various build steps in more details. The CI pipeline does most of these steps as well. All filenames and directories mentioned in the sections below are relative to the `sirius-pipeline` directory (containing this README) unless otherwise specified. 

Building starts by retrieving a pre-built `dash-bmv2` Docker image from a Docker registry, then executing a series of targets in the main [Makefile](Makefile) via `make <target>`. It is designed to be run either manually; via user-supplied scripts; or from a CI pipeline in the cloud.

See the diagram below. You can read the [Dockerfile](Dockerfile) and all `Makefiles` to get a deeper understanding of the build process.

## Build Workflow Diagram

![dash-p4-bmv2-thrift-workflow](images/dash-p4-bmv2-thrift-workflow.svg)

## Build Docker dev container
The `make docker` target creates a docker image named `dash-bmv2`. This contains a build/compilation environment used to produce project artifacts. It also contains an execution environment to run the bmv2 model and test programs. It includes numerous Ubuntu packages.

During subsequent build steps, the docker image is used to spawn a container in which various `make` targets or other scripts are executed. So, the execution environment for most build steps is inside the docker container, not the normal user environment.

When the container is run, various local subdirectories are "mounted" as volumes in the container, for example local `./SAI/` is mounted as the container's `/SAI/` directory. The container thus reads and writes the local development environment directories and files.

>**NOTE** The base docker image is [p4lang/behavioral-model:no-pi](https://hub.docker.com/r/p4lang/behavioral-model). This is the vanilla bmv2. To use a modified bmv2 engine, it must be built from sources and this base container may need to change.

In addition it downloads several other OSS projects such as, `grpc`, `p4c`, etc. and builds them from source. The entire process can take one to several hours. It only needs to be built once per user environment.

>**TODO**  Build official versions and publish to a public Docker registry, and retrieve on demand.

## Optional - Manually Pull the pre-built Docker image
This is optional, the Docker image will be pulled automatically the first time you run `make p4`. This image contains all the build- and run-time components and packages. You can also do this to restore an image. If you want to use a substitute image, tag it with `dash-bmv2:latest`.

```
make docker-pull
```
## Optional - expert - build a new Docker image
This step builds a new Docker image on demand, but you shouldn't have to if you use the prebuilt one retrieved from a Docker registry. Note, this step can exceed one hour depending upon CPU speed and network bandwidth. 
```
make docker
```
## Optional - Expert/Admin - Publish Docker Image
This step publishes the local Docker image to the registry and requires credentials. It should be done selectively by repo maintainers. For now there is no `make` target to do this.

## Optional - expert - `exec` a container shell
This step runs a new container and executes `bash` shell, giving you a terminal in the container. It's primarily useful to examine the container contents or debug.
```
make dash-shell
```

## Compile P4 Code
```
make p4
```
The primary outputs of interest are:
 * `bmv2/sirius_pipeline.bmv2/sirius_pipeline.json` - the "P4 object code" which is actually metadata interpreted by the bmv2 "engine" to execute the P4 pipeline.
 * `bmv2/sirius_pipeline.bmv2/sirius_pipeline_p4rt.json` - the "P4Info" metadata which describes all the P4 entities (P4 tables, counters, etc.). This metadata is used downstream as follows:
    * P4Runtime controller used to manage the bmv2 program. The SAI API adaptor converts SAI library "c" code calls to P4Runtime socket calls.
    * P4-to-SAI header code generation (see next step below)

## Build libsai.so adaptor library
This library is the crucial item to allow integration with a Network Operating System (NOS) like SONiC. It wraps an implementtion specific "SDK" with standard Switch Abstraction Interface (SAI) APIs. In this case, an adaptor translates SAI API table/attribute CRUD operations into equivalent P4Runtime RPC calls, which is the native RPC API for bmv2.

```
make sai
```

This target generates SAI headers from the P4Info which was described above. It uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) which renders [SAI/templates](SAI/templates) into c++ source code for the SAI headers corresponding to the DASH API as defined in the P4 code. It then compiles this code into a shared library `libsai.so` which will later be used to link to a test server (Thrift) or `syncd` daemon for production.

This consists of two main steps
* Generate the SAI headers and implementation code via [SAI/generate_dash_api.sh](SAI/generate_dash_api.sh) script, which is merely a wrapper which calls the real workhorse: [SAI/sai_api_gen.py](SAI/sai_api_gen.py). This uses templates stored in [SAI/templates](SAI/templates).

  Headers are emitted into the imported `SAI` submodule (under `SAI/SAI`) under its `inc`, `meta` and `experimental` directories.

  Implementation code for each SAI accessor are emitted into the `SAI/lib` directory.
* Compile the implementation source code into `libsai.so`, providing the definitive DASH dataplane API. Note this `libsai` makes calls to bmv2's emdedded P4Runtime Server and must be linked with numerous libraries, see `tests/vnet_out/Makefile` to gain insights.

### Restore SAI Submodule
As mentioend above, the `make sai` target generates code into the `SAI` submodule (e.g. at `./SAI/SAI`). This "dirties" what is otherwise a cloned Git repo from `opencomputeproject/SAI`.
```
make sai-clean
```

To ensure the baseline code is restored prior to each run, the modified directories under SAI are deleted, then restored via `git checkout -- <path, path, ...>` . This retrieves the subtrees from the SAI submodule, which is stored intact in the local project's Git repo (e.g. under `DASH/.git/modules/sirius-pipeline/SAI/SAI`)

## Build SAI client test program(s)
This compiles a simple libsai client program to verify the libsai-to-p4runtime-to-bmv2 stack. It performs table access(es).

**TODO:** Write libsai client test programs which configure the dataplane and performs traffic tests.

```
make test
```

## Create veth pairs for bmv2
This needs to be run just once. It will create veth pairs, set their MTU, disable IPV6, etc.

```
make network
```

You can delete the veth pairs when you're done testing via this command:
```
make network-clean
```
## Run software switch
This will run an interactive docker container in the foreground. This will spew out verbose content when control APIs are called or packets are processed. Use additional terminals to run other test scripts.

>**NOTE:** Stop the process (CTRL-c) to shut down the switch container.

```
make run-switch   # launches bmv2 with P4Runtime server
```

## Run simple SAI library test
From a different terminal, run SAI client tests.
```
make run-test
```

## Run ixia-x traffic-generator test
Remeber to [Install docker-compose](#install-docker-compose).

From a different terminal, run [ixia-c](https://github.com/open-traffic-generator/ixia-c) traffic tests. The first time this runs, it will pull Python packages for the [snappi](https://github.com/open-traffic-generator/snappi) client as well as Docker images for the [ixia-c](https://github.com/open-traffic-generator/ixia-c) controller and traffic engines.

```
make run-ixiac-test
```
### ixia-c components and setup/teardown
The first time you run ixia-c traffic tests, the `ixiac-prereq` make target will run two dependent targets:
* `install-python-modules` - downloads and installs snappi Python client libraries
* `deploy-ixiac` - downloads two docker images (ixia-c controller, and ixia-c traffic engine or TE), then spins up one controller container and two traffic engines.

ixia-c always requires a dedicated CPU core for the receiver, capable of full DPDK performance, but can use dedicated or shared CPU cores for the transmitter and controller, at reduced performance. In this project, two cores total are required: one for the ixia-c receiver, and one shared core which handles the TE transmitters, controller, and all other processes including the P4 BMV2 switch, P4Runtime server, test clients, etc. This accommodates smaller cloud instances like the "free" Azure CI runners provided by Github [described here](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)


### About snappi and ixia-c traffic-generator
#### Opensource Sites:
* Vendor-neutral [Open Traffic Generator](https://github.com/open-traffic-generator) model and API
* [Ixia-c](https://github.com/open-traffic-generator/ixia-c), a powerful traffic generator based on Open Traffic Generator API
* [Ixia-c Slack support channel](https://github.com/open-traffic-generator/ixia-c/blob/main/docs/support.md)

#### DASH-specific info:
* [../test/test-cases/bmv2_model](../test/test-cases/bmv2_model) for ixia-c test cases
* [../test/third-party/traffic_gen/README.md](../test/third-party/traffic_gen/README.md) for ixia-c configuration info
* [../test/third-party/traffic_gen/deployment/README.md](../test/third-party/traffic_gen/deployment/README.md) for docker-compose configuration and diagram

# Configuration Management
"Configuration Management" here refers to maintaining version control over the various components used in the build and test workflows. It's mandatory to identify and lock down the versions of critical components, so that multiple versions and branches of the complete project can be built and tested in a reproducible and predictable way, at any point in the future.

Here are the critical components and description of their role, and how versions are controlled:
* DASH repo - controlled by Git source-code control, tracked by commit SHA, tag, branch, etc. This is the main project and its components should also be controlled.
* Docker image(s) - identified by the `repo/image_name:tag`, e.g. `repo/dash-bmv2:v1`. Note that `latest` is not a reliable way to control a Docker image. These images are used for building artifacts; and for running processes, e.g. the "P4 bmv2 switch."
  * Docker images which we pull from third-party repos, e.g. [p4lang/behavioral-model](https://hub.docker.com/r/p4lang/behavioral-model), may not have "version" tags in the strictest sense, but rather "variant" tags like `:no-pi` which is a build *option*, not a code version.
  * Docker images which we build, e.g. `dash-bmv2`, are controlled by us so we can specify their contents and tag images appropriately. Once built, the contents are fixed. However, rebuilding from the same Dockerfile in the future is not guaranteed to produce the same contents. In fact, it's very unlikely to be the same,  because the image may `apt install` the "latest" Ubuntu packages. So, every rebuild of a Docker image must be carefully retested. In some cases it may be necessary to specify the versions of consituent packages such as `grpc` etc.
  * Docker images which we build might be based `FROM` another Docker image, therefore it depends upon its content. Some might have ambiguous version tags  (e.g. `p4lang/behavioral-mode:no-pi` - it gets rebuilt and updated constantly, but what is its version?). Since Docker images are built in layers and a docker `pull` retrieves those layers from various registries, it might compose a final image which has surprising content if the base image changes.
* Git Submodules - these reference external Git repos as resources. They are controlled by the SHA commit of the submodule, which is "committed" to the top level project (see [About Git Submodules](#about-git-submodules)). The versions are always known and explicitly specified.


# Installing Prequisites

## Install docker
Need for basically everything to build/test sirius-pipeline.

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
It is assumed you already have Docker on your system.
The `docker-compose` command is used to orchestrate the ixia-c containers. You need to install it to run the ixia-c test scripts (`ixia-c` itself doesn't require docker-compose; it's merely convenient for instantiating it using a declarative `.yml` file).

See also:
* https://www.cyberithub.com/how-to-install-docker-compose-on-ubuntu-20-04-lts-step-by-step/
  

Installation of `docker-compose` has to be done just once. You can use another technique based on your platform and preferences. The following will download and install a linux executable under `/usr/local/bin`. You should have a PATH to this directory. You can edit the below command to locate it somewhere else as desired, just change the path as needed.

>**NOTE** Use docker-compose 1.29.2 or later!

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

To test installation, execute the following. The output on the second line is an example, yours may differ.
```
docker-compose --version
docker-compose version 1.29.2, build 5becea4c
```

# Developer Workflows
## About Git Submodules
See also:
* https://git-scm.com/book/en/v2/Git-Tools-Submodules
* https://www.atlassian.com/git/tutorials/git-submodule#:~:text=A%20git%20submodule%20is%20a,the%20host%20repository%20is%20updated

### Why use a submodule?
A Git submodule is like a symbolic link to another repo. It "points" to some other repo via a URL, and is also pinned to a specific revision of that repo. For example, the `DASH/sirius-pipeline/SAI` directory looks like this in Github. The `SAI @ fe69c82` means this is a submodule pointing to the SAI project (at the opencompute-project repo), in particular the `fe69c82` commit SHA.

![sai-submodule-in-repo](../assets/sai-submodule-in-repo.png)

Advantages of this approach:
* Don't need to "manually" clone another repo used by this project
* Precise configuration control - we want a specific revision, not "latest" which might break a DASH build if something under `SAI` changes.
* It's a well-known practice; for example the `SAI` project and the `sonic-buildimage` projects both use submodules to great advantage.

### Typical Workflow: Committing new code - ignoring SAI submodule

>**NOTE:** You **do not want to check in changes to the SAI/SAI submodule** unless you're deliberately upgrading to a new commit level of the SAI submodule.

Since the SAI/SAI directory gets modified in-place when bmv2 SAI artifacts are generated, it will "taint" the SAI/SAI submodule and appear as "dirty" when you invoke `git status`. This makes it inconvenient to  do `git commit -a`, which will commit everything which has changed. An easy remedy is to restore the SAI/SAI directory to pristine state as follows:
```
make sai-clean
```
Then you can do `git status`, `git commit -a` etc. and skip the modified SAI/SAI submodule.

### Committing new SAI submodule version
To upgrade to a newer version of `SAI`, for example following a SAI enhancement which the DASH project needs, or will benefit from, we need to change the commit SHA of the submodule. This requires the following steps, in abbreviated form:
* Inside the `SAI/SAI` directory, pull the desired version of SAI, e.g. to get latest:
  ```
  git pull
  ```
* Go to the top level in the DASH project
* Add the SAI submodule to the current commit stage; commit; and push:
  ```
  git add SAI/SAI
  git commit [-a]
  git push
  ```
  Since we haven't gone through this process yet, it is subject to more clarification or adjustments.