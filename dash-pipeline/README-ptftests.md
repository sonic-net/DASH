* [README-dash-workflows.md](README-dash-workflows.md) for build workflows and Make targets.
* [README-saithrift](README-saithrift.md) for saithrift client/server and test workflows.
* [README-pytests](README-pytests.md) for saithrift Pytest test-case development and usage.


# PTF - Packet Test Framework
## PTF Overview
The Packet Test Framework (PTF) is a popular tool and is based on Pyunit, Scapy and some utilities to make testing data planes and switching devices easy and convenient.
- [PTF - Packet Test Framework](#ptf---packet-test-framework)
  - [PTF Overview](#ptf-overview)
  - [Learn By Example](#learn-by-example)
  - [Invoking Tests From Command-line](#invoking-tests-from-command-line)
  - [Locating PTF Packet Utilities](#locating-ptf-packet-utilities)
## Learn By Example
An excellent place to learn test-writing patterns is the existing SAI PTF tests located at https://github.com/opencomputeproject/SAI/tree/master/ptf and also expanded into the DASH workspace at `DASH/dash-pipeline/SAI/SAI/ptf`
## Invoking Tests From Command-line
You can exercise `ptf` manually by entering the saithrift-client container in a shell:

```
DASH/dash-pipeline$ make run-saithrift-client-bash 
...
root@chris-z4:/tests-dev# ptf -h
...
usage: usage: ptf [options] --test-dir TEST_DIR [tests]
PTF (Packet Test Framework) is a framework and set of tests to test a software switch.
...
```
Typical invocation:
```
sudo ptf --test-dir ./ptf --pypath /SAI/ptf \
	 --interface 0@veth1 --interface 1@veth3
```
Note that the container is launched with `/SAI/ptf` in the container mounted to the corresponding 
## Locating PTF Packet Utilities
The following directory contains source code for packet test utilities:
```
DASH/dash-pipeline/SAI/SAI/test/ptf/src/ptf
```
Note this directory won't be expanded into your workspace when you first clone DASH. You have to expand the GitSubmodules under SAI/SAI and SAI/SAI/test/ptf. This is done  part of the first DASH build (`git submodule update --init` and `make all`) as explained in other README's.

To clarify: the directory structure below is created after the `SAI/SAI` repository is cloned; then subsequently the `SAI/SAI/test/ptf` repository is cloned inside that repo.

You can also consult the source of PTF: https://github.com/p4lang/ptf. Note that SAI imports a specific commit SHA of PTF via the submodule so it's best to consult the code which is actually pulled into DASH. The way to check the version is to enter the PTF submodule directory and look at git branch:
```
DASH/dash-pipeline/SAI/SAI/test/ptf$ git branch 
* (HEAD detached at 10a2d4b)
  master
```

An example of utility functions you might find inside a typical PTF test is `verify_packets`. This function and many others are inside `DASH/dash-pipeline/SAI/SAI/test/ptf/src/ptf/testutils.py`. 
```
def verify_packets(test, pkt, ports=[], device_number=0, timeout=None):
    """
    Check that a packet is received on each of the specified port numbers for a
    given device (default device number is 0).

    Also verifies that the packet is not received on any other ports for this
    device, and that no other packets are received on the device (unless --relax
    is in effect).

    The parameter timeout will be passed as is for each individual verify calls.

    This covers the common and simplest cases for checking data plane outputs.
    For more complex usage, like multiple different packets being output, or
    multiple packets on the same port, use the primitive verify_packet,
    verify_no_packet, and verify_no_other_packets functions directly.
    """
```
