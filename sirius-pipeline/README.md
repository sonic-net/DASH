# Sirius Pipeline
This is a P4 model of the DASH overlay pipeline which uses the [bmv2](https://github.com/p4lang/behavioral-model) from [p4lang](https://github.com/p4lang).

- [Sirius Pipeline](#sirius-pipeline)
- [TODO](#todo)
- [Quick-start](#quick-start)
  - [Get the right branch](#get-the-right-branch)
  - [Build Artifacts](#build-artifacts)
  - [Run bmv2 software switch](#run-bmv2-software-switch)
  - [Run tests](#run-tests)
- [CI (Continuous Integration) Via Git Actions](#ci-continuous-integration-via-git-actions)
- [Detailed Build Workflow](#detailed-build-workflow)
  - [Build Workflow Diagram](#build-workflow-diagram)
  - [Build Docker dev container](#build-docker-dev-container)
  - [Optional - Manually Pull the pre-built Docker image](#optional---manually-pull-the-pre-built-docker-image)
  - [Optional - expert - build a new Docker image](#optional---expert---build-a-new-docker-image)
  - [Optional - Expert/Admin - Publish Docker Image](#optional---expertadmin---publish-docker-image)
  - [Optional - expert - exec a container shell](#optional---expert---exec-a-container-shell)
  - [Compile P4 Code](#compile-p4-code)
  - [Build libsai.so adaptor library](#build-libsaiso-adaptor-library)
    - [Restore SAI Submodule](#restore-sai-submodule)
  - [Build SAI client test program(s)](#build-sai-client-test-programs)
  - [Configure networking for bmv2](#configure-networking-for-bmv2)
  - [Run software switch](#run-software-switch)
  - [Run simple SAI library test](#run-simple-sai-library-test)
  - [Install docker-compose](#install-docker-compose)
  - [Run ixia-x traffic-generator test](#run-ixia-x-traffic-generator-test)
  - [About ixia-x traffic-generator](#about-ixia-x-traffic-generator)
- [Developer Workflows](#developer-workflows)
  - [About Git Submodules](#about-git-submodules)
    - [Committing new code - submodule considerations](#committing-new-code---submodule-considerations)

# TODO
* Use modified bmv2 which adds stateful processing. Current version is vanilla bmv2. This will require building it instead of using a prebuilt bmv2 docker image, see [Build Docker dev container](#build-docker-dev-container).
* Integrate SAI-thrift server from [OCP/SAI](https://github.com/opencomputeproject/SAI)
* Add DASH sevice test cases including SAI-thrift pipeline configuration and traffic tests
* Build Docker image automatically when Dockerfile changes, publish and pull from permanent repo
* Use Azure Container Registry (ACR) for Docker images instead of temporary Dockerhub registry
* Use dedicated higher-performance runners instead of free Azure 2-core instances
* Make a smaller Docker image by stripping unneeded sources (e.g. grpc, p4c), apt caches etc. Current 12G image is large. Possibly use staged docker builds to permit precise copying of only necessary components.

# Quick-start
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
# CI (Continuous Integration) Via Git Actions
This project contains [Git Actions](https://docs.github.com/en/actions) to perform continuous integration whenever certain actions are performed. These are specified in YAML files under [.github/workflows](../.github/workflows) directory.

* [sirius-ci.yml](../.github/workflows/sirius-ci.yml): A Commit or Pull Request of P4 code, Makefiles, scripts, etc.  will trigger a build of all artifacts and run tests, all in the Azure cloud. Status can be viewed on the Github repo using the "Actions" link in the top of the page. This will be true for forked repos as well as the main Azure/DASH repo.

  Two tests are currently executed in the CI pipeline. These will be increased extensively over time:
  * The `make run-test` target does a trivial SAI access using a c++ client program. This verifies the libsai-to-P4runtime adaptor over a socket. The test program acts as a P4Runtime client, and the bmv2 simple_switch process is the server.
  * The `make run-ixiac-test` target spins up a two-port software (DPDK) traffic-generator engine using the free version of [ixia-c](https://github.com/open-traffic-generator/ixia-c) controlled by a Python [snappi](https://github.com/open-traffic-generator/snappi) client. Using this approach allows the same scripts to eventually be scaled to line-rate using hardware-based traffic generators.
* [sirius-dev-docker.yml](../.github/workflows/sirius-dev-docker.yml): A commit of the [Dockerfile](Dockerfile) will trigger the [make docker](#build-docker-dev-container) build target and rebuild the `dash-bmv2` docker container. It will not publish it though, so it's ephemeral and disappears when the Git runner terminates. The main benefit of this is it may run much faster in the cloud than locally, allowing you to test for a successful build of changes more quickly.
* The CI badge will be updated according to the CI build status and appear on the front page of the repo as well as the top-level README page. You can click on this icon to drill down into the Git Actions history and view pass/fail details. Typical icons appear below:

![CI-badge-passing.svg](../assets/CI-badge-passing.svg)  

A typical "Good" CI log appears below, this can be watched in real-time:

![CI-build-log-ok.png](../assets/CI-build-log-ok.png)  

A typical "Failed" CI log appears below. You can click on the arrow next to the red circled "X" and see details. In this example there is a (deliberate) P4 syntax error.

![CI-build-log-fail.png](../assets/CI-build-log-fail.png)  

# Detailed Build Workflow
This explains the various build steps in more details. The CI pipeline does most of these steps as well. All filenames and directories mentioned in the sections below are relative to the `sirius-pipeline` directory (containing this README) unless otherwise specified. 

Building starts by retrieving a pre-built `dash-bmv2` Docker image from a Docker registry, then executing a series of targets in the main [Makefile](Makefile) via `make <target>`. It is designed to be run either manually; via user-supplied scripts; or from a CI pipeline in the cloud.

See the diagram below. You can read the [Dockerfile](Dockerfile) and all `Makefiles` to get a deeper understanding of the build process.

## Build Workflow Diagram

![dash-p4-bmv2-thrift-workflow](images/dash-p4-bmv2-thrift-workflow.svg)

## Build Docker dev container
The `make docker` target creates a docker image named `dash-bmv2`. This contains a build/compilation environment used to produce project artifacts. It also contains an execution environment to run the bmv2 model and test programs. It includes numerous Ubuntu packages.

During subsequent build steps, the docker image is used to spawn a container in which various `make` targets or other scripts are executed. So, the execution environment for most build steps is inside the docker container, not the normal user environment.

When the container is run, various local subdirectories are "mounted" as volumes in the container, for example local `SAI/` is mounted as the container's `/SAI/` directory. The container thus reads and writes the local development environment directories and files.

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

## Optional - expert - exec a container shell
This step runs a container and executes `bash` shell, giving you a terminal in the container. It's primarily useful to examine the container contents or debug.
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

## Configure networking for bmv2
This needs to be run just once. It will create veth pairs, set their MTU, disable IPV6, etc.

**TODO:** Write a make target to undo the `make-network` modifications.

```
make network
```
## Run software switch
This will run an interactive docker container in the foreground. This will spew out verbose content when control APIs are called or packets are processed. Use additional terminals to run other test scripts.
```
make run-switch   # launches bmv2 with P4Runtime server
```

## Run simple SAI library test
From a different terminal, run SAI client tests.
```
make run-test
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

## Run ixia-x traffic-generator test
From a different terminal, run ixia-c traffic tests. The first time this runs, it will pull Python packages for the [snappi](https://github.com/open-traffic-generator/snappi) client as well as Docker images for the [ixia-c](https://github.com/open-traffic-generator/ixia-c) controller and traffic engines.
```
make run-ixiac-test
```
## About ixia-x traffic-generator

See also:
* [../test/test-cases/bmv2_model](../test/test-cases/bmv2_model) for ixia-c test cases
* [../test/third-party/traffic_gen/README.md](../test/third-party/traffic_gen/README.md) for ixia-c configuration info
* [../test/third-party/traffic_gen/deployment/README.md](../test/third-party/traffic_gen/deployment/README.md)

# Developer Workflows
## About Git Submodules
See also:
* https://git-scm.com/book/en/v2/Git-Tools-Submodules
* https://www.atlassian.com/git/tutorials/git-submodule#:~:text=A%20git%20submodule%20is%20a,the%20host%20repository%20is%20updated

### Committing new code - submodule considerations

Since the SAI/SAI directory gets modified in place when bmv2 SAI artifacts are generated, it will "taint" the SAI/SAI submodule and appear as "dirty" when you invoke `git status`. You do not want to check in changes to the SAI/SAI submodule. This makes it inconvenient to  do `git commit -a`. An easy remedy is to restore the SAI/SAI directory to pristine state as follows:
```
make sai-clean
```
Then you can do git status, git commit -a etc. and not involve the modified SAI/SAI submodule.