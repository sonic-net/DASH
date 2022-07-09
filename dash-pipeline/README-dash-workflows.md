See also:
* [README.md](README.md) Top-level README for dash-pipeline
* [README-dash-ci](README-dash-ci.md) for CI pipelines.
* [README-dash-docker](README-dash-docker.md) for Docker usage.

**Table of Contents**
- [Detailed DASH Behavioral Model Build Workflow](#detailed-dash-behavioral-model-build-workflow)
  - [Docker Image(s)](#docker-images)
  - [Build Workflow Diagram](#build-workflow-diagram)
  - [Compile P4 Code](#compile-p4-code)
  - [Build libsai.so adaptor library](#build-libsaiso-adaptor-library)
    - [Restore SAI Submodule](#restore-sai-submodule)
  - [Build SAI client test program(s)](#build-sai-client-test-programs)
  - [Create veth pairs for bmv2](#create-veth-pairs-for-bmv2)
  - [Run software switch](#run-software-switch)
  - [Initialize software switch](#initialize-software-switch)
    - [Use wireshark to decode P4Runtime messages in the SAI-P4RT adaptor](#use-wireshark-to-decode-p4runtime-messages-in-the-sai-p4rt-adaptor)
  - [Run simple SAI library test](#run-simple-sai-library-test)
  - [Run ixia-c traffic-generator test](#run-ixia-c-traffic-generator-test)
    - [ixia-c components and setup/teardown](#ixia-c-components-and-setupteardown)
    - [About snappi and ixia-c traffic-generator](#about-snappi-and-ixia-c-traffic-generator)
      - [Opensource Sites](#opensource-sites)
      - [DASH-specific info](#dash-specific-info)
  - [About Git Submodules](#about-git-submodules)
    - [Why use a submodule?](#why-use-a-submodule)
    - [Typical Workflow: Committing new code - ignoring SAI submodule](#typical-workflow-committing-new-code---ignoring-sai-submodule)
    - [Committing new SAI submodule version](#committing-new-sai-submodule-version)
- [Configuration Management](#configuration-management)
  - [DASH Repo Versioning](#dash-repo-versioning)
  - [Submodules](#submodules)
  - [Docker Image Versioning](#docker-image-versioning)
    - [Project-Specific Images](#project-specific-images)
    - [Third-party Docker Images](#third-party-docker-images)
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
make p4-clean # optional
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
make sai-clean  # optional
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
This will run an interactive docker container in the foreground. The main process is `simple_switch_grpc` which  includes an embedded P4Runtime server. This will spew out verbose content when control APIs are called or packets are processed. Use additional terminals to run other test scripts.

>**NOTE:** Stop the process (CTRL-c) to shut down the switch container. You can also invoke `make kill-switch` from another terminal or script.

```
make run-switch   # launches bmv2 with P4Runtime server
```
## Initialize software switch
The `bmv2` switch does not start up loaded with your P4 program; it is a "blank slate" awaiting a
`SetForwardingPipelineConfigRequest` gRPC message which contains the output of the p4c compiler (P4 bmv2 JSON) and P4Info), as described in [Compile P4 Code](#compile-p4-code). In our current implementation, this is done via a static initializer in the`libsai.so` shared library, which won't get loaded and activated (by the Linux loader) until an API call is made to the library. This can be triggered by e.g. a SAI table accessor. What if we want to initialize the switch without calling any SAI table APIs?

The `init_switch` test program and corresponding make target shown below makes a benign dummy call to the library to cause it to load and perform a `SetForwardingPipelineConfigRequest`.
```
make init-switch
```
A message similar to the following will be emitted in the running switch's console:
```
GRPC call SetForwardingPipelineConfig 0.0.0.0:9559 => /etc/dash/dash_pipeline.json, /etc/dash/dash_pipeline_p4rt.txt
Switch is initialized.
```
### Use wireshark to decode P4Runtime messages in the SAI-P4RT adaptor
>**Hint:** You can monitor P4Runtime messages using Wireshark or similar. Select interface `lo`, filter on `tcp.port==9559`. Right-click on a captured packet and select "Decode as..." and configure port 9559 to decode as HTTP2 (old versions of Wireshark might lack this choice).

## Run simple SAI library test
From a different terminal, run SAI client tests. This exercises the `libsai.so` shared library including P4Runtime client adaptor, which communicates to the running `simple_switch_grpc` process over a socket.
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
#### Opensource Sites
* Vendor-neutral [Open Traffic Generator](https://github.com/open-traffic-generator) model and API
* [Ixia-c](https://github.com/open-traffic-generator/ixia-c), a powerful traffic generator based on Open Traffic Generator API
* [Ixia-c Slack support channel](https://github.com/open-traffic-generator/ixia-c/blob/main/docs/support.md)

#### DASH-specific info
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

"Configuration Management" here refers to maintaining version control over the various components used in the build and test workflows. It's mandatory to identify and lock down the versions of critical components, so that multiple versions and branches of the complete project can be built and tested in a reproducible and predictable way, at any point in the future.

The sections below discuss version control of critical components.
## DASH Repo Versioning
The DASH GitHub repo, i.e. [https://github.com/Azure/DASH](https://github.com/Azure/DASH) is controlled by Git source-code control, tracked by commit SHA, tag, branch, etc. This is the main project and its components should also be controlled.
## Submodules
As discussed in [About Git Submodules](#about-git-submodules), submodules are controlled by the SHA commit of the submodule, which is "committed" to the top level project (see [About Git Submodules](#about-git-submodules)). The versions are always known and explicitly specified.
## Docker Image Versioning
Docker image(s) are identified by their `repo/image_name:tag`, e.g. `p4lang/dp4c:latest`.
### Project-Specific Images
Docker images which we build, e.g. `dash-bmv2-bldr`, are controlled by us so we can specify their contents and tag images appropriately. It is important to version-control the contents of these images so that future builds of these images produce the same desired behavior. This meains controlling the versions of base Docker images, OS packages added via `apt install` etc.
### Third-party Docker Images
Docker images which we pull from third-party repos, e.g. [p4lang/behavioral-model](https://hub.docker.com/r/p4lang/behavioral-model) may have "version" tags like `:latest`, `:stable`, `:no-pi`. Such tags are not reliable as packages are often updated, so `:latest` and even `:stable` change over time. We use such images directly or as base images in our own Dockerfiles, e.g. in `FROM` statements.

Similarly, common OS base images like [amd64/ubuntu:20.04](https://hub.docker.com/layers/ubuntu/amd64/ubuntu/20.04/images/sha256-b2339eee806d44d6a8adc0a790f824fb71f03366dd754d400316ae5a7e3ece3e?context=explore) have the tag `20.04` but this does not guarantee that the image won't suddenly change, which could break our builds.

To ensure predictable and stable behavior, we should use SHA values for tags, e.g. `@sha256:ce45720e...` instead of `:latest`.

Example:

***Not reliable:***
```
# Can change daily:
FROM p4lang/behavioral-model:latest
```
***Reliable:***
```
# p4lang/behavioral-model:latest on 2022-07-03:
FROM p4lang/behavioral-model@sha256:ce45720e28a96a50f275c1b511cd84c2558b62f2cf7a7e506765183bc3fb2e32
```
The screencap below shows how to obtain the SAH digest of a docker image on Dockerhub, corresponding to the example above.

![dockerhub-p4lang-bm-latest](images/dockerhub-p4lang-bm-latest.png)

See:
* [Why you should pin your docker images with SHA instead of tags](https://rockbag.medium.com/why-you-should-pin-your-docker-images-with-sha-instead-of-tags-fd132443b8a6)