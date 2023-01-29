# Introduction

At the 2023-Jan-26 DASH Behavioral Model WG meeting, I (Andy
Fingerhut) volunteered to attempt to compile either the unmodified
DASH P4 reference code in this directory

+ https://github.com/sonic-net/DASH/tree/main/dash-pipeline/bmv2

using the open source p4c-dpdk compiler, or to make as few changes as
possible to it in order for it to compile.  The goal is to determine
whether there are any features missing in the p4c-dpdk compiler in
order to compile this P4 code.


# Results as of 2023-Jan-28

The good news is that with only a few changes in the code, it
compiles.

There are several warning messages output by p4c-dpdk that are
currently normal and exepcted.  These are warnings about the DPDK
implementation of this P4 program that causes extra data copies during
packet processing, with a minor effect on the packet processing
performance.

```
$ make
mkdir -p out
p4c-dpdk -DPNA_CONNTRACK --dump ./out --pp ./out/dash_pipeline.pp.p4 -o ./out/dash_pipeline.spec --arch pna --bf-rt-schema ./out/dash_pipeline.p4.bfrt.json --p4runtime-files ./out/dash_pipeline.p4.p4info.txt dash_pipeline.p4
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table outbound_ConntrackOut_conntrackOut. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table outbound_ConntrackIn_conntrackIn. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table outbound_outbound_ca_to_pa|dash_outbound_ca_to_pa. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table inbound_ConntrackIn_conntrackIn. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table inbound_ConntrackOut_conntrackOut. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table eni_meter. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table pa_validation. Copying all match fields to metadata
[--Wwarn=mismatch] warning: Mismatched header/metadata struct for key elements in table inbound_routing. Copying all match fields to metadata
```

I used the latest version of the open source p4c compiler as of
2023-Jan-26, but some earlier versions will likely work.  Given that
the DPDK back end of p4c is under active development, it is
recommended to use a p4c-dpdk binary compiled using recent versions of
the p4c source code.

One way to do that is to install p4c from the source code using the
instructions described here:
https://github.com/jafingerhut/p4-guide/blob/master/bin/README-install-troubleshooting.md


# Features known to be missing from p4c-dpdk


## PNA `send_to_port` extern function needs a small correction

See the comments in the block of code starting with:

```
#ifdef DPDK_PNA_SEND_TO_PORT_FIX_MERGED
```

I expect the change that enables this line of the P4 code to be
compiled via p4c-dpdk will be a very small effort for the p4c-dpdk
developers.  It is a one-line change in the pna.p4 include file.


## p4c-dpdk does not yet implement tables with direct counters and ternary match fields

See the comments in the blocks of code starting with:

```
#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
```

I do not know how much effort it would be for the p4c-dpdk developers
to make the enhancements required to enable this part of the DASH P4
code.  I have created the following public Github p4c issue to track
this:

+ https://github.com/p4lang/p4c/issues/3868
