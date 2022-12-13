<h1>Contents</h1>

- [Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`](#tutorial---writing-dash-pytests-using-sai-challenger-and-dpugen)
  - [Overview](#overview)
  - [General Instructions for running tests](#general-instructions-for-running-tests)
    - [Preparation: Build and Run bmv2 and saithrift-server](#preparation-build-and-run-bmv2-and-saithrift-server)
    - [Running tests from outside the container using `make`](#running-tests-from-outside-the-container-using-make)
    - [Running tests from inside the container](#running-tests-from-inside-the-container)
- [Device Configuration Tutorials](#device-configuration-tutorials)
  - [Configuration Tutorial Overview](#configuration-tutorial-overview)
  - [Device Configuration Test Case Walk-through](#device-configuration-test-case-walk-through)
    - [test\_sai\_vnet\_vips\_config\_via\_literal.py](#test_sai_vnet_vips_config_via_literalpy)
    - [test\_sai\_vnet\_vips\_config\_via\_list\_comprehension.py](#test_sai_vnet_vips_config_via_list_comprehensionpy)
    - [test\_sai\_vnet\_vips\_config\_via\_list\_comprehension\_files.py](#test_sai_vnet_vips_config_via_list_comprehension_filespy)
    - [test\_sai\_vnet\_vips\_config\_via\_custom\_gen.py](#test_sai_vnet_vips_config_via_custom_genpy)
    - [test\_sai\_vnet\_vips\_config\_via\_custom\_gen\_files.py](#test_sai_vnet_vips_config_via_custom_gen_filespy)
    - [test\_sai\_vnet\_outbound\_small\_scale\_config\_via\_dpugen.py](#test_sai_vnet_outbound_small_scale_config_via_dpugenpy)
    - [test\_sai\_vnet\_outbound\_small\_scale\_config\_via\_dpugen\_files.py](#test_sai_vnet_outbound_small_scale_config_via_dpugen_filespy)
- [Traffic Generation Tutorials - TODO](#traffic-generation-tutorials---todo)
- [Appendix - Common Themes and design patterns](#appendix---common-themes-and-design-patterns)
  - [Common Design Patterns for Device Configuration](#common-design-patterns-for-device-configuration)
    - [Pattern: Command-line mode to create JSON files for select test-cases](#pattern-command-line-mode-to-create-json-files-for-select-test-cases)
    - [Pattern: `make_create_cmds()` helper](#pattern-make_create_cmds-helper)
    - [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper)
    - [Pattern: reading JSON config files and applying them](#pattern-reading-json-config-files-and-applying-them)
    - [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands)

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
* Complex configuration generated using [dpugen](https://pypi.org/project/dpugen/) with streaming records.

Along the way we're refer to some common design patterns and themes which we've collected in an [Appendix](#appendix---common-themes-and-design-patterns). You can jump ahead and read that now, or refer to it as you walk through examples.

## Device Configuration Test Case Walk-through
A variety of techniques are illustrated by a series of test files.
### [test_sai_vnet_vips_config_via_literal.py](test_sai_vnet_vips_config_via_literal.py)

This very simple test-case shows how to define a configuration using the "DASH Config" format expressed as an array of Python dictionaries, each one corresponding to one SAI "record."

The simple helper method `make_create_cmds()` returns a hard-coded array of records:
```
def make_create_cmds():
    """ Return some configuration entries expressed literally"""
    return [
        {
            "name": "vip_entry#1",
            "op": "create",
            "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
            "key": {
            "switch_id": "$SWITCH_ID",
            "vip": "192.168.0.1"
            },
            "attributes": [
            "SAI_VIP_ENTRY_ATTR_ACTION",
            "SAI_VIP_ENTRY_ACTION_ACCEPT"
            ]
        },
        ...etc.
        ]
```

It is applied to the device using this simple technique:
```
result = [*dpu.process_commands( (make_create_cmds()) )]
```
See [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands) to understand how the commands are applied to the DUT.

We could have just defined the array in a variable and passed it to `process_commands()` but we wrapped it in `make_create_cmds()` as explained in [Pattern: `make_create_cmds()` helper](#pattern-make_create_cmds-helper).

The helper method `make_remove_cmds()` makes a list of commands to teardown the configuration, see [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper).

We then apply the remove commands the same way as create commands:
```
result = [*dpu.process_commands(make_remove_cmds())]
```
### [test_sai_vnet_vips_config_via_list_comprehension.py](test_sai_vnet_vips_config_via_list_comprehension.py)
This test case shows how to easily generate an array of similar "config" commands by using Python list-comprehension syntax. It's not unique to this framework but it fits in nicely for some cases, like making many iterations of an object with concise code.

This example builds on [test_sai_vnet_vips_config_via_literal.py](test_sai_vnet_vips_config_via_literal.py) but replaces a statically-defined list of SAI records with a list-comprehension expression, e.g.:
```
def make_create_cmds(vip_start=1,d1=1,d2=1):
    """
    Return a populated array of vip dictionary entries using list comprehension
    with IP address 192.168.0.[d1..d2] and incrementing vip starting at vip_start
    """
    return [
        {
            "name": "vip_entry#%02d" % (x-d1+1),
            "op": "create",
            "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
            "key": {
            "switch_id": "$SWITCH_ID",
            "vip": "192.168.0.%d" % x
            },
            "attributes": [
            "SAI_VIP_ENTRY_ATTR_ACTION",
            "SAI_VIP_ENTRY_ACTION_ACCEPT"
            ]
        } for x in range (d1,d2+1)]
```
This generates a list where the VIP IPv4 address cycles through values from `192.168.0.<d1>` through `192.168.0.<d2>`, where d1 and d2 are parameters.

>**NOTE:** While generating many VIPs may not be very useful, it's a simple test-case to teach some techniques.

The create commands are applied to the device using this simple technique:
```
result = [*dpu.process_commands( (make_create_cmds()) )]
```
See [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands) to understand how the commands are applied to the DUT.

The helper method `make_remove_cmds()` makes a list of commands to teardown the configuration, see [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper).

We then apply the remove commands the same way as create commands:
```
result = [*dpu.process_commands(make_remove_cmds())]
```

### [test_sai_vnet_vips_config_via_list_comprehension_files.py](test_sai_vnet_vips_config_via_list_comprehension_files.py)
This test case uses JSON files created by [test_sai_vnet_vips_config_via_list_comprehension.py](test_sai_vnet_vips_config_via_list_comprehension.py) used in command-line mode. Using static JSON files can be useful for using fixed configurations which are also easy to read for reference, edit manually, etc. This technique is not recommended for extremely large configurations, which might be better served using a streaming generator technique.

The commands used to create the files are as follows:
```
./test_sai_vnet_vips_config_via_list_comprehension.py -c -d1 1 -d2 16 > test_sai_vnet_vips_config_via_list_comprehension_create.json

./test_sai_vnet_vips_config_via_list_comprehension.py -r -d1 1 -d2 16 > test_sai_vnet_vips_config_via_list_comprehension_remove.json
```

The test case code to apply the create and remove commands consists merely of reading JSON into a variable, and feeding that variable (an array of SAI records) to the `process_commands()` method. We explain this technique in [Pattern: reading JSON config files and applying them](#pattern-reading-json-config-files-and-applying-them).

### [test_sai_vnet_vips_config_via_custom_gen.py](test_sai_vnet_vips_config_via_custom_gen.py)
This test-case illustrates how to write a custom config "generator" which uses the Python `yield` command to emit a series of "SAI records" via an iterator. The custom config generator uses a series of nested loops to cycle through all four octets of a VIP IPv4 address.

This case is conceptually similar to [test_sai_vnet_vips_config_via_list_comprehension.py](test_sai_vnet_vips_config_via_list_comprehension.py) but differs in a few ways:
* There are four nested loops, one per octet in the IPv4 address
* The nested loops are easier to read than a complex nested list comprehension expression would be
* The use of `yield` instead of an expanded array "saves memory" because only one element of the array (a dictionary) exists at a time; it is fed ("streamed") to the `dpu.process-commands()` method; and is applied to the device. In contrast, the list comprehension technique, or other non-generator technique, expands the entire array in-memory before it is consumed. This can have a profound effect upon memory consumption for huge configurations with potentially millions of entries! (This generator technique is used extensively in `dpugen`.)

As mentioned, these config entries are applied to the DUT using the SAI Challenger `dpu.process_commands()` method to read the commands one at a time in "streaming" mode.  This one line of code illustrates the simplicity:
```
result = [*dpu.process_commands( (make_create_cmds()) )]
```
where `make_create_cmds()` is a wrapper around our custom generator. `make_create_cmds()` returns an iterator which emits items from the generator.

See [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands) to understand how the commands are applied to the DUT.

Likewise, removing the config is equally simple:
```
result = [*dpu.process_commands( (make_remove_cmds()) )]
```
where `make_remove_cmds()` again is a simple method which we explain in [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper). Unfortunately, because we chose to reverse the output of `make_create_cmds()`, we need to build the list in-place, which temporarily consumes memory store the entire list. (One *could* make a generator to produce reversed records on the fly.)
### [test_sai_vnet_vips_config_via_custom_gen_files.py](test_sai_vnet_vips_config_via_custom_gen_files.py)
This test-case illustrates reading previously-stored JSON files and applying them to the DUT.
The [test_sai_vnet_vips_config_via_custom_gen_files.py](test_sai_vnet_vips_config_via_custom_gen_files.py) test case was run in command-line mode to emit JSON to stdout and store into files, as follows. The create and remove commands were stored in separate files to be used by this test-case.

The following commands were used to generate 256 unique vip entries. See the code or run the file in command-line mode to understand the parameters.

```
./test_sai_vnet_vips_config_via_custom_gen.py -c -a1 192 -a2 193 -b1 168 -b2 169 -c1 1 -c2 2 -d1 1 -d2 32 > test_sai_vnet_vips_config_via_custom_gen_create.json

./test_sai_vnet_vips_config_via_custom_gen.py -r -a1 192 -a2 193 -b1 168 -b2 169 -c1 1 -c2 2 -d1 1 -d2 32 > test_sai_vnet_vips_config_via_custom_gen_remove.json
```
We used the tecnique described in [Pattern: reading JSON config files and applying them](#pattern-reading-json-config-files-and-applying-them) to read the JSON files and apply them to the DUT.
### [test_sai_vnet_outbound_small_scale_config_via_dpugen.py](test_sai_vnet_outbound_small_scale_config_via_dpugen.py)
This test builds upon earlier lessons. It demonstrates the use of [dpugen](https://pypi.org/project/dpugen/) for generating a small-scale, yet complete DASH VNET service configuration. Several high-level scaling parameters are fed to dpugen and it emits a sequence of SAI records corresponding to the requested configuration. We then apply these records using SAI Challenger.

Looking at the code, we see some high-level scaling parameters such as:
```
NUMBER_OF_VIP = 1
NUMBER_OF_DLE = 1
NUMBER_OF_ENI = 1
...etc
```

These are then referenced in a more detailed configuration structure which is used by the generator, e.g.:
```
TEST_VNET_OUTBOUND_CONFIG_SCALE = {
    'DASH_VIP':                 {'vpe': {'count': NUMBER_OF_VIP,'SWITCH_ID': '$SWITCH_ID','IPV4': 	{'count': NUMBER_OF_VIP,'start': '221.0.0.2','step': '0.1.0.0'}}},
    'DASH_DIRECTION_LOOKUP':    {'dle': {'count': NUMBER_OF_DLE,'SWITCH_ID': '$SWITCH_ID','VNI': 	{'count': NUMBER_OF_DLE,'start': 5000,'step': 1000},'ACTION': 'SET_OUTBOUND_DIRECTION'}},
    
...etc.
```
This structure gives you fine-grained control over such things as starting addresses, increment values, etc. Most of the time you can just copy this boilerplate and change the high-level scale parameters to achieve different-sized configurations.

To "generate" the configuration, we instantiate a generator initialized with the parameters:
```
def make_create_commands(self):
    """ Generate a configuration
        returns iterator (generator) of SAI records
    """
    conf = dpugen.sai.SaiConfig(params=TEST_VNET_OUTBOUND_CONFIG_SCALE)
    conf.generate()
    return conf.items()
```

We then apply these to the DUT as follows:
```
  results = [*dpu.process_commands( (self.make_create_commands()) )]
```

The `process_commands()` method calls the generator's `items()` iterator (returned by our helper `make_create_commands()`). See [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands).

Under the hood, SAI Challenger calls the generator's `items()` iterator (returned by our helper `make_create_commands()`) and processes the returned records one by one.

Here is a typical sequence of records as you can view in [test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json):
```
[
  {
    "name": "vip_#1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "vip": "221.0.0.2"
    },
    "attributes": [
      "SAI_VIP_ENTRY_ATTR_ACTION",
      "SAI_VIP_ENTRY_ACTION_ACCEPT"
    ]
  },
  {
    "name": "direction_lookup_entry_#5000",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "vni": "5000"
    },
    "attributes": [
      "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
      "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
    ]
  },
  
  ... etc.
```
For each record, SAI Challenger invokes a parser, makes DUT API calls over the chosen RPC interface (e.g. sai-thrift), checks the return values and   
stores the OIDs of the created objects in a dictionary which can be referred to by the `name` in each record, e.g. `vip_#1`.

To teardown the configuration, we convert the *create* records into *remove* records containing just the `op` and name. We made a helper to do this as described in [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper).

A list of remove records, taken from [test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json), looks like this:
```
[
  {
    "name": "outbound_ca_to_pa_#2",
    "op": "remove"
  },
  {
    "name": "outbound_ca_to_pa_#1",
    "op": "remove"
  },
  
  ...etc.
```

SAI Challenger looks up the OIDs it received from the DUT when it created the objects and performs a `remove()` request one at a time.

### [test_sai_vnet_outbound_small_scale_config_via_dpugen_files.py](test_sai_vnet_outbound_small_scale_config_via_dpugen_files.py)

This test-case illustrates reading previously-stored JSON files and applying them to the DUT.
The [test_sai_vnet_outbound_small_scale_config_via_dpugen.py](test_sai_vnet_outbound_small_scale_config_via_dpugen.py) test case was run in command-line mode to emit JSON to stdout and store into files, as follows. The create and remove commands were stored in separate files to be used by this test-case.

The following commands were used to generate the configuration. See the code or run the file in command-line mode to understand the parameters.

```
PYTHONPATH=.. ./test_sai_vnet_outbound_small_scale_config_via_dpugen.py -c  > test_sai_vnet_outbound_small_scale_config_via_dpugen_files_create.json

PYTHONPATH=.. ./test_sai_vnet_outbound_small_scale_config_via_dpugen.py -r  > test_sai_vnet_outbound_small_scale_config_via_dpugen_files_create.json
```
(Some hand clean-up was done to the above JSON files, to remove some superfluous content produced while the generator was running.)

We describe how to read and apply JSON files in [Pattern: reading JSON config files and applying them](#pattern-reading-json-config-files-and-applying-them).
# Traffic Generation Tutorials - TODO
To be added in the future...
# Appendix - Common Themes and design patterns
## Common Design Patterns for Device Configuration
Here we present some recurring themes used not only in our in tutorial examples, but in "real" test cases elsewhere in this repo.
### Pattern: Command-line mode to create JSON files for select test-cases
This pattern was developed to make the tuorials more useful, but is equally applicable for production tests.

Some of the examples use DUT configuration files containing SAI records in JSON format, which are loaded and applied to the device via a  SAI-Challenger DUT API driver, e.g. SAI-thrift. Some of these JSON files were themselves generated  using one of the example `.py` files, some of which are dual-purpose Pytest scripts:
* They can be executed by the Pytest framework to test the DUT.
* They can be run in command-line mode to emit the generated configurations as JSON text, saved to a file, and reused in tests.

For example, we use the [test_sai_vnet_outbound_small_scale_config_via_dpugen.py](test_sai_vnet_outbound_small_scale_config_via_dpugen.py) test-case in command-line mode to generate two JSON files:
* [test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json)
* [test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json](test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json)

This is useful to create persistent copies of generated configurations, or simply to examine the configuration and make adjustments during development. Only selected scripts have a command-line mode. (Check the files for a `__main__` section.) Each such file has a `-h` option to show usage and available options.

>**NOTE:** The output might contain diagnostic messages captured from `stdout`, so some hand-trimming of JSON may be needed. Check the file contents and edit as requires.

**Example:**

To generate JSON containing SAI records to **create** the vnet config and redirect to a file:
```
PYTHONPATH=.. ./test_sai_vnet_outbound_small_scale_config_via_dpugen.py -c > test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json
```
To generate JSON containing SAI records to **remove** the vnet config and redirect to a file:
```
PYTHONPATH=.. ./test_sai_vnet_outbound_small_scale_config_via_dpugen.py -r > test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json
```

### Pattern: `make_create_cmds()` helper
Generating device setup commands can be simple or complex, as the tutorials and production test cases illustrate. These are run at the start of a test case.

In our tutorials, we use a wrapper method to get the configuration as an iterator, even if the configuration is a simple list containing one entry. This allows us to make a corresponding `remove()` helper as described ahead, in a consistent and concise way. It also makes it easy to implement the command-line mode which prints the configurations in JSON format.
>**NOTE:** Some of the examples have parameterized `make_create_cmds()` 
### Pattern: `make_remove_cmds()` helper

At the end of a test, device configuration is "torn down" to prepare for a subsequent test, leaving the DUT in a clean, known state. It is advisable to remove the config entries in the exact reverse order of their creation, in order to avoid dependency errors in the device. For example, some items are contained in other items, and the proper removal order might be enforced.

SAI Challenger, plus a simple design pattern, makes it easy to construct the remove commands and apply them.

The tutorials all implement a `make_remove_cmds()` helper which relies on the `make_create_cmds()` helper. The beauty of this is you don't have to write any original code to remove the config, you can just copy this pattern.
>**NOTE:** Some of the examples have parameterized `make_remove_cmds()` to match the parameterized `make_create_cmds()`.
```
def make_remove_cmds():
    """ Return an array of remove commands """
    cleanup_commands = [{'name': cmd['name'], 'op': 'remove'} for cmd in make_create_cmds()]
    for cmd in reversed(cleanup_commands):
        yield cmd
    return
```

Here's how this works:
* Make an array of remove commands containing just the symbolic name of the entry (which SAI challenger automatically translates into OIDs when it calls the actual APIs, see [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands)), and the operation code `remove`
* Reverse the order of the array
* Provide an iterator (generator) to this array as return value

### Pattern: reading JSON config files and applying them
One technique is to create static JSON files representing create and remove commands, reading them in a test-case and applying them to the DUT.

For example, here is the complete code from a test-case which does this. We  read create (setup) and remove (teardown) commands stored in separate files and apply them. Another possiblity would be to store only the create commands as a file, and generate the remove commands from the create commands at runtime, using techniques described in [Pattern: `make_remove_cmds()` helper](#pattern-make_remove_cmds-helper).
```
import json
from pathlib import Path
from pprint import pprint

import pytest

current_file_dir = Path(__file__).parent

def test_sai_vnet_vips_config_create_file(dpu):
    with (current_file_dir / f'test_sai_vnet_vips_config_via_list_comprehension_create.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)
        result = [*dpu.process_commands(setup_commands)]
        # pprint(result)

def test_sai_vnet_outbound_small_scale_config_remove_file(dpu):
    with (current_file_dir / f'test_sai_vnet_vips_config_via_list_comprehension_remove.json').open(mode='r') as config_file:
        teardown_commands = json.load(config_file)
        result = [*dpu.process_commands(teardown_commands)]
        # pprint(result)
```

The behavior of `process_commands()` is described in [Pattern: The magic of dpu.process\_commmands()](#pattern-the-magic-of-dpuprocess_commmands).
### Pattern: The magic of dpu.process_commmands()
The `process_commands()` method which is in the SAI Challenger framework performs a lot of magic under the hood, including:
* Reading through the entries one by one
* Translating into the appropriate device API calls, in this case sai-thrift RPC calls.
* Checking for errors
* Storing the returned Object ID (OID) in a dictionary, keyed by the arbitrary entry name chosen by the test developer, e.g. `vip_entry#1`. This key can be used in subsequent calls, such as:
  * Creating another object which uses this OID as a parameter
  * Removing the object later, by name (not OID)

This unburdens the test developer from pesky details.
