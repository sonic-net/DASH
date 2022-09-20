See also:
* [README.md](README.md) Top-level README for dash-pipeline
* [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets.
* [README-ptftests](README-ptftests.md) for saithrift PTF test-case development and usage.
* [README-pytests](README-pytests.md) for saithrift Pytest test-case development and usage.

**Table of Contents**
- [DASH saithrift client and server](#dash-saithrift-client-and-server)
  - [Overview](#overview)
- [TODO](#todo)
- [Running DASH saithrift tests](#running-dash-saithrift-tests)
  - [Running/Stopping the saithrift server](#runningstopping-the-saithrift-server)
  - [Production - Launch container, run tests in one shot](#production---launch-container-run-tests-in-one-shot)
  - [Development - Launch container, run tests in one shot](#development---launch-container-run-tests-in-one-shot)
- [Developer: Run tests selectively from `bash` inside saithrift-client container](#developer-run-tests-selectively-from-bash-inside-saithrift-client-container)
  - [Select Directory - Container prebuilt directory, or mounted from host](#select-directory---container-prebuilt-directory-or-mounted-from-host)
- [Test aftermath and clearing the switch config](#test-aftermath-and-clearing-the-switch-config)
- [Tips and techniques for writing tests](#tips-and-techniques-for-writing-tests)
  - [Workspace File Layout](#workspace-file-layout)
  - [saithrift Python client modules](#saithrift-python-client-modules)
  - [Walk-through example of finding saithrift module entities](#walk-through-example-of-finding-saithrift-module-entities)
    - [How to create a local object?](#how-to-create-a-local-object)
    - [How to call the SAI create function for our local object?](#how-to-call-the-sai-create-function-for-our-local-object)
- [Debugging saithrift Server with GDB](#debugging-saithrift-server-with-gdb)
  - [Run Interactive saithrift-server container](#run-interactive-saithrift-server-container)
# DASH saithrift client and server
## Overview
The DASH saithrift API is used to configure and query a device under test (DUT) as described in [dash-test-workflow-saithrift](../test/docs/dash-test-workflow-saithrift.md) and [dash-test-workflow-saithrift-p4](../test/docs/dash-test-workflow-p4-saithrift.md).

This document describes how to run the saithrift server and client to run test suites. It also gives some advice for writing tests, debugging, etc.
# TODO
* Select saithrift server IP address to allow running client remotely from target.
# Running DASH saithrift tests
## Running/Stopping the saithrift server
```
make run-saithrift-server
make kill-saithrift-server
```
## Production - Launch container, run tests in one shot
This will run all the tests built into the `dash-saithrift-client` docker image. This assumes you've already done `make docker-saithrift-client` which will bundle the current state of the `dash-pipeline/tests` directory into the image.

Calling these make targets spins up a `saithrift-client` container on-the-fly, runs tests and kills the container. It's very lightweight.
```
make run-saithrift-client-pytests     # run Pytests from container's scripts
make run-saithrift-client-ptftests    # run PTF tests from container's scripts
make run-saithrift-client-tests       # run both suites above
```
## Development - Launch container, run tests in one shot
You can run tests based on the current state of the `dash-pipeline/tests/` directory without rebuilding the `saithrift-client` docker image. Instead of running tests built into the container and stored under `/tests`, a host volume `dash-pipeline/tests` is mounted to container `/tests-dev`) and tests are run from there. This allows rapid incremental test-case development. When doing so, the container's `/test` directory remains in-place with tests which were copied into the container at image build-time.

You can keep all containers running (switch, saithrift-server, ixia-c) and interactively write and execute test-cases without stopping the daemons. As stated, the saithrift-client container will start and stop each time you run the tests but the switch and saithrift-server will continue to run.
```
make run-saithrift-client-dev-pytests     # run Pytests from host mount
make run-saithrift-client-dev-ptftests    # run PTF tests from host mount
make run-saithrift-client-dev-tests       # run both suites above
```

**TODO:** - pass params to the container to select tests etc.
# Developer: Run tests selectively from `bash` inside saithrift-client container
Enter the container, this will place you in the `/tests-dev/` directory of the container which corresponds to the contents of the `DASH/dash-pipline/tests` directory on the host. In this way you can interactively run test-cases while you're editing them. When doing so, the container's `/tests` directory remains in-place with tests which were copied into the container at image build-time.
```
make run-saithrift-client-bash 
root@chris-z4:/tests-dev# 
```
The running container is also mounted via `-v $(PWD)/tests:/test-dev`  which mounts the current developer workspace into the running container. You can thereby create and edit new tests "live" from a text editor and see the effect inside the container in real-time. Note, the container image also contains the `/tests` directory which was copied into the Docker image when `make docker-saithrift-client` was last run. This means you have a "production" copy of tests as well as live "development" host volume simultaneously in the container.

## Select Directory - Container prebuilt directory, or mounted from host

* `cd /tests/` - Enter directory which was prebuilt into container image; tests are not modifiable "live" from the host. This is good for canned tests.
* `cd /tests-dev/` - Enter directory which is mounted to `dash-pipeline/tests` from the host, allowing live editing in the host and running in the container. This is a convenient developer workflow.

To get the desired subdirectory for Pytests or PTF test, choose the appropriate path, e.g.:
* `cd /tests/saithrift/pytest`
* `cd /tests-dev/saithrift/ptf`

You can run all tests inside each respective directory by entering the directory and running the `run-saithrift-xxx` bash scripts, e.g.:
```
DASH/DASH/dash-pipeline$ make run-saithrift-client-bash
...
root@chris-z4:/tests-dev/saithrift# cd ptf/
root@chris-z4:/tests-dev/saithrift/ptf# ./run-saithrift-ptftests.sh 
```
*OR*
```
DASH/DASH/dash-pipeline$ make run-saithrift-client-bash
...
root@chris-z4:/tests-dev/saithrift# cd pytest/
root@chris-z4:/tests-dev/saithrift/pytest# ./run-saithrift-pytests.sh 
```


See the relevant documentation for running select PTF or Pytests using `bash` commands. You can pass parameters via the command-line, to control which test groups are run using filenames, directories, or filtering on groups (PTF); or marks or match expressions (pytest).
# Test aftermath and clearing the switch config
Sometimes tests leave entries programmed into the switch, when they should have cleaned everything up. This can be caused by exceptions/assertions which fail and either inadvertently, or unavoidably, leave entries in tables. This might make a subsequent run of the same (or a different) test suite fail. In these cases, it might be best to execute the following sequence to restart the switch and saithrift server, then rerun test cases.
:
```
make kill-all run-switch              # console 1
make run-saithrift-server             # console 2
make run-saithrift-client-tests       # Console 3
make run-saithrift-client-dev-tests   # Alternative to above
```

It's strongly recommended to perform proper DUT config cleanup in the code for every test case and catch exceptions where possible, to ensure a complete cleanup, despite failures along the way.

# Tips and techniques for writing tests
The following information should apply equally well to writing any tests which utilize saithrift as the client library: PTF, Pytests, etc. Please refer to other READMEs for information specific to various frameworks.
## Workspace File Layout
Below is depicted a selected subset of the DASH repository pertinent to understanding source and build artifact locations needed for saithrift test development.

Note that the `SAI/SAI` directory is a Git submodule and its contents are modified during `make sai` and `make saithrift-server`.
```
DASH
  dash-pipeline
    SAI                   - top-level dir for SAI-related artifacts
                            This is the dash-pipeline SAI directory, not the SAI repo!
    rpc                   - output dir for saithrift code generator (1)
      SAI                 - Git submodule root, imported into DASH repo
        extensions        - DASH extension headers - mix of repo files + code from "make sai"
        inc               - upstream sai headers
        meta              - generated SAI metadata, scripts, etc.(2)
          sai_rpc_server.cpp - generated server source code(3)
        test
          saithriftv2     - autogenerated saithrift tools, outputs
    tests                 - saithrift client/server test cases
      pytest              - DASH tests using Pytests with saithrift
      ptf                 - DASH tests using PTF with saithrift
```
(1) Contains client & server libraries & executable, see [saithrift Python client modules](#saithrift-python-client-modules)<br>
(2) Mounted as `/meta` inside container<br>
(3) See [Debugging saithrift Server with GDB](#debugging-saithrift-server-with-gdb).
## saithrift Python client modules
Here are the detailed contents of `DASH/dash-pipeline/SAI/rpc/usr/local/lib/python3.8/site-packages/sai_thrift`. You need to utilize the APIs and constants inside these modules, to write saithrift tests in PTF or Pytest.

When writing tests using particular SAI tables or attributes, use your editor to search the Python modules below to find functions, structures, attributes etc. See [Walk-through example of finding saithrift module entities](#walk-through-example-of-finding-saithrift-module-entities) in the next section.

>**Note:** These artifacts are generated via the `make sai-thrift-server` target, they are not stored in the DASH repo.
```
constants.py     - wrapper for ttypes.py, not interesting
sai_adapter.py   - Main source of APIs for saithrift, e.g. create/remove/get/set
sai_headers.ph   - constants e.g. SAI_STATUS_SUCCESS
sai_rpc.py       - lower-level thrift marshalling/unmarshalling etc. Called by sai_adapter.py functions
ttypes.py        - SAI data types
```

## Walk-through example of finding saithrift module entities
See the following code snippet from a PTF test. A Pytest would look nearly identical. We'll briefly describe how you can find things in the Python saithrift library modules. Recall we'll be hunting inside `DASH/dash-pipeline/SAI/rpc/usr/local/lib/python3.8/site-packages/sai_thrift` as explained above.
```
  self.switch_id = 0
  self.eth_addr = '\xaa\xcc\xcc\xcc\xcc\xcc'
  self.vni = 60
  self.eni = 7
  self.dle = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=self.vni)
  self.eam = sai_thrift_eni_ether_address_map_entry_t(switch_id=self.switch_id, address = self.eth_addr)
  self.e2v = sai_thrift_outbound_eni_to_vni_entry_t(switch_id=self.switch_id, eni_id=self.eni)

  try:

      status = sai_thrift_create_direction_lookup_entry(self.client, self.dle,
                          action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
      assert(status == SAI_STATUS_SUCCESS)
      
      status = sai_thrift_create_eni_ether_address_map_entry(self.client,
                                                  eni_ether_address_map_entry=self.eam,
                                                  eni_id=self.eni)
      assert(status == SAI_STATUS_SUCCESS)

      status = sai_thrift_create_outbound_eni_to_vni_entry(self.client,
                                                                    outbound_eni_to_vni_entry=self.e2v,
                                                                    vni=self.vni)
```
### How to create a local object?
We want to determine the function signature to create the SAI object `direction_lookup_entry_t`.

**Understand the type:**

First, search for the data type itself inside `ttypes.py` to find:
```
# From ttypes.py:

class sai_thrift_direction_lookup_entry_t(object):
    """
    Attributes:
     - switch_id
     - vni
    """

    def __init__(self, switch_id=None, vni=None,):
        self.switch_id = switch_id
        self.vni = vni
```
Note the actual type is `sai_thrift_direction_lookup_entry_t` and it has two parameters to create it: `switch_id` and `vni`.

Looking further down into the `write()` method (which serializes into thrift) we get hints about the data types of these two parameters. We can see `switch_id` is 64 bits and `vni` is 32 bits:
```
# From ttypes.py:

      if self.switch_id is not None:
          oprot.writeFieldBegin('switch_id', TType.I64, 1)
          oprot.writeI64(self.switch_id)
          oprot.writeFieldEnd()
      if self.vni is not None:
          oprot.writeFieldBegin('vni', TType.I32, 2)
          oprot.writeI32(self.vni)
          oprot.writeFieldEnd()
```
**Call the sai_thrift_direction_lookup_entry_t constructor:**

Finally, we see the code in our test case is as below, using the name of the Python class `sai_thrift_direction_lookup_entry_t` and the attributes from the `__init__()` method to form the constructor call:
```
  self.dle = sai_thrift_direction_lookup_entry_t(switch_id=self.switch_id, vni=self.vni)
```
### How to call the SAI create function for our local object?
Now that we have a local object, we need to find the RPC call to remotely create it using saithrift.

Search `adaptor.py` for the string `direction_lookup_entry_t` and you'll find numerous instances. In particular you'll find the four accessors to `create()`, `remove()`, `set()` and `get()` these objects, as well as `bulk_create()` and `bulk_remove()` versions thereof. In our case, we want to `create()`. The method signature is:

```
# From adaptor.py:

def sai_thrift_create_direction_lookup_entry(client,
                                             direction_lookup_entry,
                                             action=None):
    """
    sai_create_direction_lookup_entry() - RPC client function implementation.

    Args:
        client (Client): SAI RPC client
        direction_lookup_entry(sai_thrift_direction_lookup_entry_t): direction_lookup_entry IN argument

        For the other parameters, see documentation of direction_lookup_entry CREATE attributes.
```
The `client` param is a handle to the already-established Thrift session.

The `direction_lookup_entry` was created by our previous steps.

The `action` is a SAI attribute enum which we can glean from the SAI header file. We need to find valid values.

**Find attribute enum values from SAI headers:**

We can examine `SAI/experimental/saiexperimentaldash.h` (which was autogenerated from our P4 code) to find:
```
// From saiexperimentaldash.h:

typedef enum _sai_direction_lookup_entry_action_t
{
    SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION,

    SAI_DIRECTION_LOOKUP_ENTRY_ACTION_DENY,

} sai_direction_lookup_entry_action_t;

```

Let's find the Python counterparts. Search for `SAI_DIRECTION_LOOKUP_ENTRY_ACTION` inside `saiheaders.py` to find the following, which are clearly the identical constant names from our sai headers.

```
# From saiheaders.py:

SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION = 0# /usr/include/sai/saiexperimentaldash.h: 45

SAI_DIRECTION_LOOKUP_ENTRY_ACTION_DENY = (SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION + 1)# /usr/include/sai/saiexperimentaldash.h: 45
```

**Call the remote create() method:**

We now have all the information needed to execute the RPC call:
```
  status = sai_thrift_create_direction_lookup_entry(self.client, self.dle,
                      action=SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION)
```

We can also find valid values for `status` inside `sai_headers.py`. Search for `SAI_STATUS` to find entries such as:
```
# From saiheaders.py:

# /usr/include/sai/saistatus.h: 50
try:
    SAI_STATUS_SUCCESS = 0
except:
    pass
```

Viola! You're ready to become a saithrift power-user. Rock on bruh!
# Debugging saithrift Server with GDB
`gdb` is built into the saithrift server image for easy debugging. Server code is compiled with the `-g` flag to include debug symbols. The saithrift server source code is available from within the running Docker container via volume mounts. Below is shown some a typical workflow:

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
Point gdb to the mounted source directory which which must be built locally via `make saithrift-server`:
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
First breakpoint is reached, it's a startup behavior. Enter `c` to resume:
```
Thread 1 "saiserver" hit Breakpoint 1, sai_api_query (api=SAI_API_UNSPECIFIED, api_method_table=0x558bad22dd30 <test_services>) at utils.cpp:217
217	        _Out_ void **api_method_table) {
(gdb) c
Continuing.
Starting SAI RPC server on port 9092
[New Thread 0x7f2b4b7fe700 (LWP 18)]
[New Thread 0x7f2b4affd700 (LWP 19)]
```