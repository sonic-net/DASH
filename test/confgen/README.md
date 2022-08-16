# Overview
The intention of the dash config generator is to provide a way to build a large scale dash config. and to provide some insight into the actual values used in the test.

The dash config format is close to [dash-reference-config-example.md](../../../documentation/gnmi/design/dash-reference-config-example.md) with small changes.

This is not yet a config that can be deployed, but intends to be morphed into one as DASH standards get ratified and implemented

## Features
* Generate complex DASH configurations
* Custom input parameters for scale and other options.
* Output to file or stdio
* Select output format: `JSON` [future: `yaml`?]
* Generate all config (uber-generator) or just selected items (e.g. `aclgroups`)
* Potential to create custom apps to transform streaming data e.g into device API calls w/o intermediate text rendering
## High-level Diagram

![confgen-hld-diag](images/confgen-hld-diag.svg)

## Design
The uber-generator `generate.d.py` instantiates sub-generators and produces a composite output stream which can be rendered into text files (JSON) or sent to stdout for custom pipelines.

The uber-generator and sub-generators all derive from a base-class `ConfBase`. They all share a common `main` progam with CLI command-line options, which allows them to be used independently yet consistently.

The generators produce Python data structures which can be rendered into output text (e.g. JSON) or used to feed custom applications such as a saithrift API driver, to directly configure a device. Likewise a custom API driver can be developed for vendor-specific APIs.

Default parameters allow easy operations with no complex input. All parameters can be selectively overridden via cmd-line, input file or both.
## Confgen Applications
Two anticipated applications (see Figure below):
* Generate a configuration file, e.g. JSON, and use this to feed downstream tools such as a DUT configuration utility.
* Use the output of the config data stream generators to perform on-the-fly DUT configuration without intermediate JSON file rendering; also configure traffic-generators using data in the config info itself.

![confgen-apps](images/confgen-apps.svg)

## Sample CLI Usage
This may not be current; check latest for actual content.
```
$ ./generate.d.py -h
usage: generate.d.py [-h] [-f {json}] [-c {dict,list}] [-d] [-m] [-M "MSG"] [-P "{PARAMS}"] [-p PARAM_FILE]
                     [-o OFILE]

Generate DASH Configs

optional arguments:
  -h, --help            show this help message and exit
  -f {json}, --format {json}
                        Config output format.
  -c {dict,list}, --content {dict,list}
                        Emit dictionary (with inner lists), or list items only
  -d, --dump-params     Just dump parameters (defaults with user-defined merged in
  -m, --meta            Include metadata in output (only if "-c dict" used)
  -M "MSG", --msg "MSG"
                        Put MSG in metadata (only if "-m" used)
  -P "{PARAMS}", --set-params "{PARAMS}"
                        supply parameters as a dict, partial is OK; defaults and file-provided (-p)
  -p PARAM_FILE, --param-file PARAM_FILE
                        use parameter dict from file, partial is OK; overrides defaults
  -o OFILE, --output OFILE
                        Output file (default: standard output)

Usage:
=========
./generate.d.py                - generate output to stdout using uber-generator
./generate.d.py -o tmp.json    - generate output to file tmp.json
./generate.d.py -o /dev/null   - generate output to nowhere (good for testing)
./generate.d.py -c list        - generate just the list items w/o parent dictionary
dashgen/aclgroups.py [options] - run one sub-generator, e.g. acls, routetables, etc.
                               - many different subgenerators available, support same options as uber-generator

Passing parameters. Provided as Python dict, see dflt_params.py for available items
================
./generate.d.py -d                          - display default parameters and quit
./generate.d.py -d -P PARAMS                - override given parameters, display and quit; see dflt_params.py for template
./generate.d.py -d -p PARAM_FILE            - override parameters in file; display only
./generate.d.py -d -p PARAM_FILE -P PARAMS  - override params from file, then override params from cmdline; display only
./generate.d.py -p PARAM_FILE -P PARAMS     - override params from file, then override params from cmdline, generate output

Examples:
./generate.d.py -d -p params_small.py -P "{'ENI_COUNT': 16}"  - use params_small.py but override ENI_COUNT; display params
./generate.d.py -p params_hero.py -o tmp.json                 - generate full "hero test" scale config as json file
dashgen/vpcmappingtypes.py -m -M "Kewl Config!"               - generate dict of vpcmappingtypes, include meta with message            
```

# TODO
* Reconcile the param dicts vs. param attributes obtained via Munch, use of scalar variables inside performance-heavy loops etc. There is a tradeoff between elegance, expressiveness and performance.
# IDEAS/Wish-List
* Expose yaml format, need to work on streaming output (bulk output was working, but slow).
* Use logger instead of print to stderr
* logging levels -v, -vv, -vvv etc., otherwise silent on stderr
* -O, --optimize flags for speed or memory (for speed - expand lists in-memory and use orjson serializer, like original code)
* Use nested generators inside each sub-generator, instead of nested loops, to reduce in-memory usage; may require enhancing JSON output streaming to use recursion etc.
# Logic
ACLs and Routes should not be summarized.

```
we start with the `ENI_COUNT`
for each eni we allocate a `MAC_L_START` and `IP_L_START`
  when moving to next ENI we increment the mac by `ENI_MAC_STEP` and the ip by `IP_STEP4`
  each eni has `ACL_TABLE_COUNT` inbound and `ACL_TABLE_COUNT` outbound NSGs
  
  ACLs:
    each NSG has `ACL_RULES_NSG` acl rules 
    each acl rule has `IP_PER_ACL_RULE` ip prefixes
    the acl rules priorities are alternating allow and deny
    odd/even ip's are allocated to allow/deny rules
    no ips from inbound are repeated in outbound rules or other way around  except a last rule in the last table of each direction that will allow the traffic to flow

  Static VxLAN map:
    not all ips will have a map entry only the first `IP_MAPPED_PER_ACL_RULE` ips from each acl rule will have a ip/mac map entry.
  
  Routing:
    all allow ips will have a route as well as some deny ips.
    route allocation is controlled by `IP_ROUTE_DIVIDER_PER_ACL_RULE`
    the ips of each acl will be divided in groups of `IP_ROUTE_DIVIDER_PER_ACL_RULE`
    there will be routes for all but one ip in each group in such a way to prevent route summarization.

    lets say `IP_ROUTE_DIVIDER_PER_ACL_RULE` is 8
    we will have a route for:
        1.128.0.0/30
        1.128.0.4/31
        1.128.0.7/32
        and then it repeats
        1.128.0.8/30......
    this way there is no route for 1.128.0.6
```

# Scale

| 8 ENI Scenario  |  required |   generated config number |
| ----------------| --------- |---------------------------|
| ENI's/VPorts    | 8         | ENI_COUNT                            |
| NSGs            | 48        | ENI_COUNT * 2[^1] * ACL_TABLE_COUNT  |
| ACL rules       | 48000     | NSG * ACL_RULES_NSG                  |
| Prefixes        | 9.6M      | ACL * IP_PER_ACL_RULE                |
| Mapping Table   | 2M        | ACL * IP_MAPPED_PER_ACL_RULE         |
| Routes          | 1.6M      | ACL * (IP_PER_ACL_RULE / IP_ROUTE_DIVIDER_PER_ACL_RULE) *  log(IP_ROUTE_DIVIDER_PER_ACL_RULE, 2)  |

# Sample (low scale)
[sample_dash_conf.json](sample_dash_conf.json)


[^1]: we multiply by 2 because we have inbound and outbound

