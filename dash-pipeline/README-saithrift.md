- [DASH saithrift client and server](#dash-saithrift-client-and-server)
  - [Overview](#overview)
  - [TODO](#todo)
- [Running DASH saithrift tests](#running-dash-saithrift-tests)
  - [Production - Launch container, run tests in one shot](#production---launch-container-run-tests-in-one-shot)
  - [Development - Launch container, run tests in one shot](#development---launch-container-run-tests-in-one-shot)
- [Developer: Run tests selectively from `bash` inside saithrift-client container](#developer-run-tests-selectively-from-bash-inside-saithrift-client-container)
  - [Select Directory - Container pre-built directory, or mounted from host](#select-directory---container-pre-built-directory-or-mounted-from-host)
- [Tips and techniques for writing tests](#tips-and-techniques-for-writing-tests)
  - [Workspace File Layout](#workspace-file-layout)
  - [saithrift Python client modules](#saithrift-python-client-modules)
- [Debugging saithrift Server with GDB](#debugging-saithrift-server-with-gdb)
  - [Run Interactive saithrift-server container](#run-interactive-saithrift-server-container)
# DASH saithrift client and server
## Overview

**TODO**
## TODO
* Select saithrift server IP address to allow running client remotely from target.
# Running DASH saithrift tests
## Production - Launch container, run tests in one shot
This will run all the tests built into the `dash-saithrift-client` docker image. This assumes you've already done `make docker-saithrift-client` which will bundle the current state of the `dash-pipeline/tests` directory into the image.
```
make run-saithrift-client-tests       # run all saithrift tests
make run-saithrift-client-pytests     # run Pytests
make run-saithrift-client-ptftests    # run PTF tests
```
## Development - Launch container, run tests in one shot
You can run tests based on the current state of the `dash-pipeline/tests/pytests` directory without rebuilding the `saithrift-client` docker image. Instead of running tests built into the container, a host volume is mounted (`dash-pipeline/tests` is mounted to container `/tests-dev`) and tests are run from there. This allows rapid incremental test-case development.
```
make run-saithrift-client-dev-tests
```

**TODO:** - pass params to the container to select tests etc.
# Developer: Run tests selectively from `bash` inside saithrift-client container
Enter the container, this will place you in the `/test-dev/` directory of the container which corresponds to the contents of the `DASH/dash-pipline/tests` directory on the host. In this way you can interactively run test-cases while you're editing them.
```
make run-saithrift-client-bash 
root@chris-z4:/tests-dev# 
```
The running container is also mounted via `-v $(PWD)/test:/test-dev`  which mounts the current developer workspace into the running container. You can thereby create and edit new tests "live" from a text editor and see the effect inside the container in real-time. Note, the container image also contains the `/tests` directory which was copied into the Docker image when `make docker-saithrift-client` was last run. This means you have a "production" copy of tests as well as live "development" host volume simultaneously in the container.

## Select Directory - Container pre-built directory, or mounted from host

* `cd /test/` - Enter directory which was prebuilt into container image; tests are not modifiable "live" from the host. This is good for canned tests.
* `cd /test-dev/` - Enter directory which is mounted to `dash-pipeline/tests` from the host allowing live editing in the host and running in the container. This is a convenient developer workflow.

To get the desired subdirectory for Pytests or PTF test, choose the appropriate path, e.g.:
* `cd /tests/saithrift/pytest`
* `cd /tests-dev/saithrift/ptf`

See the relevant documentation for running PTF or Pytests using `bash` commands.


# Tips and techniques for writing tests
The following information should apply equally well to writing any tests which utilize saithrift as the client library: PTF, Pytests, etc. Please refer to other READMEs for information specific to various frameworks.
## Workspace File Layout
Below is depicted a selected subset of the DASH repo pertinent to understanding source and build artifact locations needed for saithrift test development.

Note that the `SAI/SAI` directory is a Git submodule and its contents are modified during `make sai` and `make saithrift-server`.
```
DASH
  dash-pipeline
    SAI                   - top-level dir for SAI-related artifacts
                            This is the dash-pipeline SAI directory, not the SAI repo!
    rpc                   - output dir for saithrift code generator
                            contains client & server libraries & executable, see below
      SAI                 - Git submodule root, imported into DASH repo
        extensions        - DASH extension headers - mix of repo files + generated via "make sai"
        inc               - upstream sai headers
        meta              - generated SAI metadata, scripts, etc.
        test
          saithriftv2     - autogenerated saithrift tools, outputs
    tests                 - saithrift client/server test cases
      pytest              - DASH tests using Pytests with saithrift
      ptf                 - DASH tests using PTF with saithrift
```
## saithrift Python client modules
Here are the detailed contents of `DASH/dash-pipeline/SAI/rpc/usr/local/lib/python3.8/site-packages/sai_thrift`. You need to utilize the APIs and constants to write saithrift tests in PTF or Pytest.

When writing tests using particular SAI tables or attributes, use you editor to search the Python modules below to find functions, structures, attributes etc.

>**Note:** These artifacts are generated via the `make sai-thrift-server` target, they are not stored in the DASH repo.
```
constants.py     - wrapper for ttypes.py, not interesting
sai_adapter.py   - Main source of APIs for saithrift, e.g. create/remove/get/set
sai_headers.ph   - constants e.g. SAI_STATUS_SUCCESS
sai_rpc.py       - lower-level thrift marshalling/unmarshalling etc. Called by sai_adapter.py functions
ttypes.py        - SAI data types
```

Some typical examples of finding Python functions, classes, and constants:

**TODO**
         
# Debugging saithrift Server with GDB
`gdb` is built into the saithrift server image for easy debugging. Server code is compiled with the `-g` flag to include debug symbols. The saithrift server source code is available from withint the running DOcker container via volume mounts. Below is shown some a typical workflow:

## Run Interactive saithrift-server container
This starts the container and opens a bash session instead of running the server like normal. The working directory `/SAI/rpc/usr/sbin` contains the saiserver.
```
$ make run-saithrift-server-bash 
docker run --rm -it --net=host --name dash-saithrift-server-chris -v /home/chris/chris-DASH/DASH/dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline.json:/etc/dash/dash_pipeline.json -v /home/chris/chris-DASH/DASH/dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.txt:/etc/dash/dash_pipeline_p4rt.txt -v /home/chris/chris-DASH/DASH/dash-pipeline/SAI:/SAI -w /SAI/rpc/usr/sbin -v /home/chris/chris-DASH/DASH/dash-pipeline/SAI/SAI/meta:/meta -e LD_LIBRARY_PATH=/SAI/lib:/usr/local/lib chrissommers/dash-saithrift-bldr:220719 \
/bin/bash
chris@chris-z4:/SAI/rpc/usr/sbin$
```
Start gdb on the saiserver process:
```
chris@chris-z4:/SAI/rpc/usr/sbin$ gdb saiserver 
GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
Copyright (C) 2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.
--Type <RET> for more, q to quit, c to continue without paging--c

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from saiserver...
```
Point gdb to the mounted source directory which which must be build locally via `make saithrift-server`:
```
(gdb) dir /meta
Source directories searched: /meta:$cdir:$cwd
```
Set some breakpoints.
```
(gdb) b sai_api_query
Breakpoint 1 at 0x76d90
(gdb) b create_outbound_eni_to_vni_entry
Function "create_outbound_eni_to_vni_entry" not defined.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 2 (create_outbound_eni_to_vni_entry) pending.
```
Run the process:
```
(gdb) r
Starting program: /SAI/rpc/usr/sbin/saiserver 
warning: Error disabling address space randomization: Operation not permitted
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
[New Thread 0x7f2b50e25700 (LWP 15)]
[New Thread 0x7f2b48624700 (LWP 16)]
[New Thread 0x7f2b4bfff700 (LWP 17)]
GRPC call SetForwardingPipelineConfig 0.0.0.0:9559 => /etc/dash/dash_pipeline.json, /etc/dash/dash_pipeline_p4rt.txt
```
First breakoint is reached, it's a startup behavior. Enter `c` to resume:
```
Thread 1 "saiserver" hit Breakpoint 1, sai_api_query (api=SAI_API_UNSPECIFIED, api_method_table=0x558bad22dd30 <test_services>) at utils.cpp:217
217	        _Out_ void **api_method_table) {
(gdb) c
Continuing.
Starting SAI RPC server on port 9092
[New Thread 0x7f2b4b7fe700 (LWP 18)]
[New Thread 0x7f2b4affd700 (LWP 19)]
```