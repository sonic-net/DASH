[<< Back to parent directory](../README.md) ]

[<< Back to DASH top-level Documents](../../README.md#contents) ]

>**NOTE**: This document is destined to be restructured into general- and per-service specifications.

# VNET to VNET scenario

This scenario is the starting point to design, implement and test the core DASH
mechanisms. In particular it allows the following features: VM to VM
communication in VNET, route support, LPM support, ACL support. This is to
verify the following performance propereies: CPS, flow, PPS, and rule scale. 

![vnet-to-vnet-one-dpu](../image/../design/images/vnet-to-vnet-one-dpu.svg)

<figcaption><i>Figure 1 - VNET to VNET one DPU</i></figcaption><br/><br/>