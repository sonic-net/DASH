- [Detailed DASH Behavioral Model Build Workflow](#detailed-dash-behavioral-model-build-workflow)
  - [Docker Image(s)](#docker-images)
  - [Build Workflow Diagram](#build-workflow-diagram)
  - [Compile P4 Code](#compile-p4-code)
  - [Build libsai.so adaptor library](#build-libsaiso-adaptor-library)
    - [Restore SAI Submodule](#restore-sai-submodule)
  - [Build SAI client test program(s)](#build-sai-client-test-programs)
  - [Create veth pairs for bmv2](#create-veth-pairs-for-bmv2)
  - [Run software switch](#run-software-switch)
  - [Run simple SAI library test](#run-simple-sai-library-test)
  - [Run ixia-c traffic-generator test](#run-ixia-c-traffic-generator-test)
    - [ixia-c components and setup/teardown](#ixia-c-components-and-setupteardown)
    - [About snappi and ixia-c traffic-generator](#about-snappi-and-ixia-c-traffic-generator)
      - [Opensource Sites:](#opensource-sites)
      - [DASH-specific info:](#dash-specific-info)
  - [About Git Submodules](#about-git-submodules)
    - [Why use a submodule?](#why-use-a-submodule)
    - [Typical Workflow: Committing new code - ignoring SAI submodule](#typical-workflow-committing-new-code---ignoring-sai-submodule)
    - [Committing new SAI submodule version](#committing-new-sai-submodule-version)
- [Configuration Management](#configuration-management)
# Detailed DASH Behavioral Model Build Workflow

This explains the various build steps in more details. The CI pipeline does most of these steps as well. All filenames and directories mentioned in the sections below are relative to the `dash-pipeline` directory (containing this README) unless otherwise specified. 

The workflows described here are primarily driven by a [Makefile](Makefile) and are suitable for a variety of use-cases:
* Manual execution by developers - edit, build, test; commit and push to GitHub
* Automated script-based execution in a development or production environment, e.g. regression testing
* Cloud-based CI (Continuous Integration) build and test, every time code is pushed to GitHub or a Pull Request is submitted to the upstream repository.

See the diagram below. You can read the [dockerfiles](dockerfiles) and all `Makefiles` in various directories to get a deeper understanding of the build process.
## Docker Image(s)
Several docker images are used to compile artifacts, such as P4 code, or run processses, such as the bmv2 simple switch. These Dockerfiles should not change often and are stored/retrieved from an external docker registry. See [README-dash.docker](README-dash.docker.md) for details. When a Dockerfile does change, it needs to be published in the resgistry. Dockerfile changes also trigger rebuilds of the docker images in the CI pipeline.

See the diagram below. You can read the [Dockerfile](Dockerfile) and all `Makefiles` to get a deeper understanding of the build process.

## Build Workflow Diagram

![dash-p4-bmv2-thrift-workflow](images/dash-p4-bmv2-thrift-workflow.svg)

## Compile P4 Code
```
make p4
```
The primary outputs of interest are:
 * `bmv2/dash_pipeline.bmv2/dash_pipeline.json` - the "P4 object code" which is actually metadata interpreted by the bmv2 "engine" to execute the P4 pipeline.
 * `bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.json` - the "P4Info" metadata which describes all the P4 entities (P4 tables, counters, etc.). This metadata is used downstream as follows:
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
As mentioned above, the `make sai` target generates code into the `SAI` submodule (e.g. at `./SAI/SAI`). This "dirties" what is otherwise a cloned Git repo from `opencomputeproject/SAI`.
```
make sai-clean
```

To ensure the baseline code is restored prior to each run, the modified directories under SAI are deleted, then restored via `git checkout -- <path, path, ...>` . This retrieves the subtrees from the SAI submodule, which is stored intact in the local project's Git repo (e.g. under `DASH/.git/modules/dash-pipeline/SAI/SAI`)

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

## Run ixia-c traffic-generator test
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

## About Git Submodules
See also:
* https://git-scm.com/book/en/v2/Git-Tools-Submodules
* https://www.atlassian.com/git/tutorials/git-submodule#:~:text=A%20git%20submodule%20is%20a,the%20host%20repository%20is%20updated

### Why use a submodule?
A Git submodule is like a symbolic link to another repo. It "points" to some other repo via a URL, and is also pinned to a specific revision of that repo. For example, the `DASH/dash-pipeline/SAI` directory looks like this in Github. The `SAI @ fe69c82` means this is a submodule pointing to the SAI project (at the opencompute-project repo), in particular the `fe69c82` commit SHA.

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
  # Configuration Management

>**TODO** Needs updating

"Configuration Management" here refers to maintaining version control over the various components used in the build and test workflows. It's mandatory to identify and lock down the versions of critical components, so that multiple versions and branches of the complete project can be built and tested in a reproducible and predictable way, at any point in the future.

Below are the critical components and description of their role, and how versions are controlled:
* DASH repo - controlled by Git source-code control, tracked by commit SHA, tag, branch, etc. This is the main project and its components should also be controlled.
* Docker image(s) - identified by the `repo/image_name:tag`, e.g. `repo/dash-bmv2:v1`. Note that `latest` is not a reliable way to control a Docker image. These images are used for building artifacts; and for running processes, e.g. the "P4 bmv2 switch."
  * Docker images which we pull from third-party repos, e.g. [p4lang/behavioral-model](https://hub.docker.com/r/p4lang/behavioral-model), may not have "version" tags in the strictest sense, but rather "variant" tags like `:no-pi` which is a build *option*, not a code version.
  * Docker images which we build, e.g. `dash-bmv2`, are controlled by us so we can specify their contents and tag images appropriately. Once built, the contents are fixed. However, rebuilding from the same Dockerfile in the future is not guaranteed to produce the same contents. In fact, it's very unlikely to be the same,  because the image may `apt install` the "latest" Ubuntu packages. So, every rebuild of a Docker image must be carefully retested. In some cases it may be necessary to specify the versions of consituent packages such as `grpc` etc.
  * Docker images which we build might be based `FROM` another Docker image, therefore it depends upon its content. Some might have ambiguous version tags  (e.g. `p4lang/behavioral-mode:no-pi` - it gets rebuilt and updated constantly, but what is its version?). Since Docker images are built in layers and a docker `pull` retrieves those layers from various registries, it might compose a final image which has surprising content if the base image changes.
* Git Submodules - these reference external Git repos as resources. They are controlled by the SHA commit of the submodule, which is "committed" to the top level project (see [About Git Submodules](#about-git-submodules)). The versions are always known and explicitly specified.

See:
* [Why you should pin your docker images with SHA instead of tags](https://rockbag.medium.com/why-you-should-pin-your-docker-images-with-sha-instead-of-tags-fd132443b8a6)