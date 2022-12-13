<h1>Contents</h1>

- [Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`](#tutorial---writing-dash-pytests-using-sai-challenger-and-dpugen)
  - [Overview](#overview)
  - [General Instructions for running tests](#general-instructions-for-running-tests)
    - [Preparation: Build and Run bmv2 and saithrift-server](#preparation-build-and-run-bmv2-and-saithrift-server)
    - [Running tests from outside the container using `make`](#running-tests-from-outside-the-container-using-make)
    - [Running tests from inside the container](#running-tests-from-inside-the-container)
- [Device Configuration Tutorials](#device-configuration-tutorials)
  - [Configuration Tutorial Overview](#configuration-tutorial-overview)
  - [Preface: Command-line mode to create JSON files for select test-cases](#preface-command-line-mode-to-create-json-files-for-select-test-cases)
  - [Device Configuration Test Case Walk-through](#device-configuration-test-case-walk-through)
    - [test\_sai\_vnet\_vips\_config\_via\_literal.py](#test_sai_vnet_vips_config_via_literalpy)
    - [test\_sai\_vnet\_vips\_config\_via\_custom\_gen\_files.py](#test_sai_vnet_vips_config_via_custom_gen_filespy)
    - [test\_sai\_vnet\_vips\_config\_via\_custom\_gen\_files.py](#test_sai_vnet_vips_config_via_custom_gen_filespy-1)
- [Traffic Generation Tutorials](#traffic-generation-tutorials)

# Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`
## Overview
This document takes you through several aspects of writing test-cases using the [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) test framework. This framework and its DASH enhancements are described [here](../../../../docs/dash-saichallenger-testbed.md).

We present simple, incremental examples which demonstrate key concepts. Once you understand these, the best way to become an expert is to study existing "production" test-cases and copy/borrow/adapt to your own test cases.

>**NOTE:** The example scripts presented here are run as part of the automatic CI/CD testing pipeline, to help catch regressions and ensure they are always current.

## General Instructions for running tests
All tests must be run from within a `dash-saichallenger-client` container. You can run the tests in a variety of ways. We will assume you will run these tests on the bmv2 software switch, but the instructions can be adapted to run on other targets including real hardware.

### Preparation: Build and Run bmv2 and saithrift-server
Fetch and build bmv2 and collaterals. You may skip if you've already done this.
```
git clone https://github.com/Azure/DASH.git
cd dash-pipeline
make clean && make all
```
Launch the switch (console #1):
```
make run-switch
```
Launch the saithrift server (console #2):
```
make run-saithrift-server
```
### Running tests from outside the container using `make`
Here are some ways to run tutorial test-cases from outside the container, using `make` targets. Use console #3.

Run all tutorials:
```
make run-saichallenger-tutorials
```

Run tutorials, specifying Pytest setup file and tutorial directory explicitly (i.e. run all tutorials):
```
make run-saichallenger-tests sai_dpu_client_server_snappi.json tutorial
```

Run tutorials, specifying Pytest setup file and test script file explicitly:
```
make run-saichallenger-tests sai_dpu_client_server_snappi.json tutorial/test_sai_vnet_vips_config_gen.py
```
### Running tests from inside the container
This workflow is good for interactive development and also gives you direct access to Pytest command options.

Enter the container (console #3):
```
make run-saichallenger-client-bash
```
Enter the tutorial directory and list contents:
```
root@chris-z4:/sai-challenger/dash_tests# cd tutorial/
root@chris-z4:/sai-challenger/dash_tests/tutorial# ls
...
```
Run all tests:
```
./run_tests.sh
```

Run specific test file:
```
./run_tests.sh test_sai_vnet_vips_config_gen.py
```

Run using specific test-fixture setup file:
```
SETUP=../sai_dpu_client_server_snappi.json ./run_tests.sh
```

Run specific test case:
```
./run_tests.sh test_sai_vnet_vips_config_gen.py
```

Run test cases containing Pytest mark `snappi` using Pytest `-m` flag:
```
./run_tests.sh -m snappi
```

Run test cases matching a pattern using Pytest `-k` flag:
```
./run_tests.sh -k vip
```

# Device Configuration Tutorials
## Configuration Tutorial Overview
We'll show how to configure devices using the following techniques. Traffic testing is not part of these tutorials.
* Simple configurations using "SAI Records" expressed as inline code in a test script
* Simple and complex configurations using "SAI Records" stored in JSON files
* Simple example using a custom generator with streaming records
* Complex configuration generated using dpugen with streaming records.
## Preface: Command-line mode to create JSON files for select test-cases
Some of the examples use DUT configuration files containing SAI records in JSON format, which are loaded and applied to the device via a  SAI-Challenger DUT API driver, e.g. SAI-thrift. Some of these JSON files were themselves generated  using one of the example `.py` files, some of which are dual-purpose Pytest scripts:
* They can be executed by the Pytest framework using either bespoke code or [dpugen](https://pypi.org/project/dpugen/)  to generate scaled configurations, and apply them to the device.
* They can be run in command-line mode to emit the generated configurations as JSON text which, which we saved to the example `.json` files.

For example, we use the [test_sai_vnet_outbound_small_scale_config_via_dpugen.py](test_sai_vnet_outbound_small_scale_config_via_dpugen.py) test-case in command-line mode to generate two JSON files:
* [test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json)
* [test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json)

This is useful to create persistent copies of generated configurations, or simply to examine the configuration and make adjustments during development. Only selected scripts have a command-line mode. (Check the files for a `__main__` section.) Each such file has a `-h` option to show usage and available options.

>**NOTE:** The output might contain diagnostic messages captured from `stdout`, so some hand-trimming of JSON may be needed. Check the file contents and edit as requires.

**Example:**

To generate JSON containing SAI records to **create** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_via_dpugen.py -c > test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json
```
To generate JSON containing SAI records to **remove** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_via_dpugen.py -r > test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json
```
## Device Configuration Test Case Walk-through
A variety of techniques are illustrated by a progressive series of test files.
### [test_sai_vnet_vips_config_via_literal.py](test_sai_vnet_vips_config_via_literal.py)

This very simple test-case shows how to define a configuration using the "DASH Config" format expressed as an array of Python dictionaries, each one corresponding to one SAI "record."

The simple helper method `make_create_cmds()` returns the array of records. It is applied to the device using this simple technique:
```
result = [*dpu.process_commands( (make_create_cmds()) )]
```
The `process_commands()` method which is in the SAI Challenger framework performs a lot of magic under the hood, including:
* Reading through the entries one by one
* Translating into the appropriate device API calls, in this case sai-thrift RPC calls.
* Checking for errors
* Storing the returned Object ID (OID) in a dictionary, keyed by the arbtrary entry name chosen by the test developer, e.g. `vip_entry#1`. This key can be used in subsequent calls, such as:
* creating another object which uses this OID as a parameter
* Removing the object later, by name (not OID)

This unburdens the test developer from pesky details.

The helper method `make_remove_cmds()` converts the initial "create" array into a corresponding "remove" array of commands using this simple bit of code:
```
def make_remove_cmds():
    cleanup_commands = [{'name': vip['name'], 'op': 'remove'} for vip in make_create_cmds()]
    return reversed(cleanup_commands)
```
The idea here is we only need the objects' OIDs, which we can reference by `name`, and the operation or `op` set to remove.

The ideas described above appear in various forms in all the other test cases.
### [test_sai_vnet_vips_config_via_custom_gen_files.py](test_sai_vnet_vips_config_via_custom_gen_files.py)
This test-case illustrates how to write a custom config "generator" which uses the Python `yield` command to emit a series of "SAI records" via an interator. The custom config generator uses a series of nested loops to cycle through all four octets of a VIP IPv4 address.

These are applied to the DUT using the SAI Challenger `dpu.process_commands()` method to read the commands one at a time in "streaming" mode.  This one line of code illustrates the simplicity:
```
result = [*dpu.process_commands( (make_create_cmds()) )]
```
where `make_create_cmds()` is a wrapper around our custom generator. Likewise, removing the config is equally simple:
```
result = [*dpu.process_commands( (make_remove_cmds()) )]
```
where `make_remove_cmds()` again is a simple method which generates a list of remove commands by reversing the create list of commands and supplying only the object entry's "name."
### [test_sai_vnet_vips_config_via_custom_gen_files.py](test_sai_vnet_vips_config_via_custom_gen_files.py)
This test-case illustrates reading previously-stored JSON files and applying them to the DUT.
The [test_sai_vnet_vips_config_via_custom_gen_files.py](test_sai_vnet_vips_config_via_custom_gen_files.pytest case was run in command-line more to emit JSON to stdout and store into files, as follows. The create and remove commands were stored in separate files to be used by this test-case.

The following commands were used to generate 256 unique vip entries. See the code or run the file in command-line mode to understand the parameters.

```
./test_sai_vnet_vips_config_via_custom_gen.py -c -a1 192 -a2 193 -b1 168 -b2 169 -c1 1 -c2 2 -d1 1 -d2 32 > test_sai_vnet_vips_config_via_custom_gen_create.json

./test_sai_vnet_vips_config_via_custom_gen.py -r -a1 192 -a2 193 -b1 168 -b2 169 -c1 1 -c2 2 -d1 1 -d2 32 > test_sai_vnet_vips_config_via_custom_gen_remove.json
```
# Traffic Generation Tutorials
**TODO**