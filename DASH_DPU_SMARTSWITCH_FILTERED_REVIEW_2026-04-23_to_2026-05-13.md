# DASH/DPU/SmartSwitch Weekly Review
**Period:** April 23 – May 13, 2026 (21 days)
**Report Generated:** May 14, 2026
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **April 23 – May 13, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **62 PRs Created** during the period
- **45 PRs Merged** during the period
- **9 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Merge Rate:** 72.6% (45 merged out of 62 created)
- **Creation Velocity:** 3.0 PRs/day
- **Merge Velocity:** 2.1 PRs/day

### Highlights
- Highest PR creation volume: **sonic-mgmt** (29 created)
- Highest merge volume: **sonic-mgmt** (18 merged)
- Strong multi-repo SmartSwitch/DPU delivery across test, platform, and orchestration components
- Continued HA, reboot flow, telemetry, and scale-path improvements across management and switch stacks

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during April 23 – May 13, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 261 | 1040 | 2244 | 18 PRs merged + 29 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 964 | 1832 | 2979 | 12 PRs merged + 11 PRs created | 🟢 Very High |
| sonic-net/sonic-gnmi | 45 | 113 | 80 | 5 PRs merged + 7 PRs created | 🟢 High |
| sonic-net/sonic-dash-ha | 4 | 24 | 10 | 4 PRs merged + 4 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss | 227 | 703 | 688 | 2 PRs merged + 5 PRs created | 🟡 Moderate |
| sonic-net/sonic-utilities | 184 | 837 | 638 | 1 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/sonic-sairedis | 79 | 391 | 164 | 2 PRs merged + 1 PRs created | 🟡 Moderate |
| sonic-net/SONiC | 2799 | 1312 | 871 | 1 PRs merged + 1 PRs created | 🟡 Low |
| sonic-net/DASH | 102 | 104 | 88 | 0 PRs merged + 1 PRs created | 🟡 Low |

**Note:** Repositories included only if they have PRs with DASH/DPU/SmartSwitch/Smart keywords in title or body during the query period.

---

## PRs Created (April 23 – May 13, 2026)

### Summary
- **Total:** 62 PRs
- **Top Repository:** sonic-mgmt (29 PRs created)
- **Key Themes:** SmartSwitch HA testing, DPU upgrade/reboot behavior, DASH scale and infra updates, platform diagnostics

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-net/sonic-mgmt | [#24160](https://github.com/sonic-net/sonic-mgmt/pull/24160) | [gnmi] Fix gNOI reboot test failures on SmartSwitch platforms | Apr 23 | DPU SmartSwitch |
| 2 | sonic-net/sonic-dash-ha | [#156](https://github.com/sonic-net/sonic-dash-ha/pull/156) | Handling unplanned events in npu driven ha | Apr 23 | DPU |
| 3 | sonic-net/sonic-mgmt | [#24175](https://github.com/sonic-net/sonic-mgmt/pull/24175) | Bug fix: conditional mark stop working after Pytest 9.0 | Apr 23 | DPU |
| 4 | sonic-net/sonic-mgmt | [#24176](https://github.com/sonic-net/sonic-mgmt/pull/24176) | [HA][smartswitch] Ha test module9 | Apr 23 | DPU SmartSwitch |
| 5 | sonic-net/sonic-mgmt | [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) | Add route rule for backend IP for PL redirect | Apr 24 | DPU |
| 6 | sonic-net/sonic-dash-ha | [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) | Add support for new DPU pairing in-flight | Apr 24 | DPU |
| 7 | sonic-net/SONiC | [#2307](https://github.com/sonic-net/SONiC/pull/2307) | Update ssw ha hld | Apr 27 | [ssw] |
| 8 | sonic-net/sonic-mgmt | [#24229](https://github.com/sonic-net/sonic-mgmt/pull/24229) | [Smartswitch] Enable loganalyzer on DPUs | Apr 27 | DASH DPU SmartSwitch |
| 9 | sonic-net/sonic-mgmt | [#24245](https://github.com/sonic-net/sonic-mgmt/pull/24245) | [HA][smartswitch] Ha test repairing dpu | Apr 27 | DPU SmartSwitch |
| 10 | sonic-net/sonic-mgmt | [#24246](https://github.com/sonic-net/sonic-mgmt/pull/24246) | SmartSwitch upgrade test: follow-up fixes from PR #24005 review | Apr 27 | DPU SmartSwitch |
| 11 | sonic-net/sonic-gnmi | [#660](https://github.com/sonic-net/sonic-gnmi/pull/660) | Add OS.Verify and OS.Activate to DPU proxy forwardable methods | Apr 27 | DPU SmartSwitch |
| 12 | sonic-net/sonic-mgmt | [#24258](https://github.com/sonic-net/sonic-mgmt/pull/24258) | [SmartSwitch] Skip internal backplane ports in iface_namingmode tests | Apr 28 | DPU SmartSwitch |
| 13 | sonic-net/sonic-buildimage | [#27020](https://github.com/sonic-net/sonic-buildimage/pull/27020) | [aspeed][BMC] Do not mask sonic-hostservice.service on BMC images | Apr 28 | DPU |
| 14 | sonic-net/sonic-mgmt | [#24278](https://github.com/sonic-net/sonic-mgmt/pull/24278) | [smartswitch] re-enable the DASH tests on 202511 | Apr 28 | DASH DPU SmartSwitch |
| 15 | sonic-net/sonic-dash-ha | [#158](https://github.com/sonic-net/sonic-dash-ha/pull/158) | Hardening ActorCreator | Apr 28 | DASH |
| 16 | sonic-net/DASH | [#698](https://github.com/sonic-net/DASH/pull/698) | add eni attribute to get ha flow owner (DPU-driven HA) | Apr 28 | DPU |
| 17 | sonic-net/sonic-mgmt | [#24284](https://github.com/sonic-net/sonic-mgmt/pull/24284) | 202511: Add t2_single_node_max and t2_single_node_max_64p_v2 to q3d qos params | Apr 28 | DASH/DPU/SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#24292](https://github.com/sonic-net/sonic-mgmt/pull/24292) | [202511] Update the copp test for smartswitch(PR #22751 and # 21409) | Apr 29 | SmartSwitch |
| 19 | sonic-net/sonic-mgmt | [#24313](https://github.com/sonic-net/sonic-mgmt/pull/24313) | [SmartSwitch] Fix the generate smartswitch golden config flow | Apr 29 | DPU SmartSwitch |
| 20 | sonic-net/sonic-mgmt | [#24316](https://github.com/sonic-net/sonic-mgmt/pull/24316) | test_po_update.py - cannot remove the last IP entry of interface Port… | Apr 29 | DPU SmartSwitch |
| 21 | sonic-net/sonic-buildimage | [#27067](https://github.com/sonic-net/sonic-buildimage/pull/27067) | [sonic-yang-models] Migrate IP prefix typedefs; preserve host bits where needed | Apr 29 | DASH Smart |
| 22 | sonic-net/sonic-mgmt | [#24322](https://github.com/sonic-net/sonic-mgmt/pull/24322) | Refactor the activate_dash_ha_from_json fixture | Apr 29 | DASH/DPU/SmartSwitch |
| 23 | sonic-net/sonic-mgmt | [#24335](https://github.com/sonic-net/sonic-mgmt/pull/24335) | Remove the skip condition for test test_privatelink_udp_sport_range_negative | Apr 30 | SmartSwitch |
| 24 | sonic-net/sonic-mgmt | [#24344](https://github.com/sonic-net/sonic-mgmt/pull/24344) | Update 'dash' test skip condition to run on smartswitch HWSKUs | Apr 30 | DASH SmartSwitch |
| 25 | sonic-net/sonic-dash-ha | [#160](https://github.com/sonic-net/sonic-dash-ha/pull/160) | Fix state machine for forced shutdown and planned shutdown | Apr 30 | DPU |
| 26 | sonic-net/sonic-mgmt | [#24346](https://github.com/sonic-net/sonic-mgmt/pull/24346) | [HA][smartswitch] HA add flow compare to traffic tests | Apr 30 | SmartSwitch |
| 27 | sonic-net/sonic-gnmi | [#661](https://github.com/sonic-net/sonic-gnmi/pull/661) | [202511] Add OS.Verify and OS.Activate to DPU proxy forwardable methods | Apr 30 | DPU |
| 28 | sonic-net/sonic-mgmt | [#24351](https://github.com/sonic-net/sonic-mgmt/pull/24351) | [smartswitch]: Quiet retry-time noise in check_dpu_critical_processes | Apr 30 | DPU SmartSwitch |
| 29 | sonic-net/sonic-gnmi | [#662](https://github.com/sonic-net/sonic-gnmi/pull/662) | [202511] Fix too_many_pings + ARM64 CI + DPU proxy OS.Verify/Activate | May 1 | DPU |
| 30 | sonic-net/sonic-buildimage | [#27110](https://github.com/sonic-net/sonic-buildimage/pull/27110) | [Security] temporarily remove vpp test from sonic-mgmt docker image build | May 1 | DASH/DPU/SmartSwitch |
| 31 | sonic-net/sonic-sairedis | [#1881](https://github.com/sonic-net/sonic-sairedis/pull/1881) | zmq: reset ZMQ_REQ socket when zmq_poll times out | May 1 | DASH/DPU/SmartSwitch |
| 32 | sonic-net/sonic-gnmi | [#663](https://github.com/sonic-net/sonic-gnmi/pull/663) | Add OS.Verify and OS.Activate DPU proxy forwarding | May 1 | DPU SmartSwitch |
| 33 | sonic-net/sonic-swss | [#4540](https://github.com/sonic-net/sonic-swss/pull/4540) | [dash]: Add ENI OID mapping and DPU counter DB support | May 1 | DASH DPU |
| 34 | sonic-net/sonic-gnmi | [#664](https://github.com/sonic-net/sonic-gnmi/pull/664) | Add completeness test for DPU proxy ForwardToDPU handlers | May 1 | DPU |
| 35 | sonic-net/sonic-gnmi | [#665](https://github.com/sonic-net/sonic-gnmi/pull/665) | Add DPU_COUNTERS_DB virtual path handling for DASH_METER and ENI counters | May 1 | DASH/DPU/SmartSwitch |
| 36 | sonic-net/sonic-buildimage | [#27118](https://github.com/sonic-net/sonic-buildimage/pull/27118) | [Mellanox][Nvidia-bluefield] Upgrade syncd containers to Trixie | May 2 | DPU |
| 37 | sonic-net/sonic-gnmi | [#666](https://github.com/sonic-net/sonic-gnmi/pull/666) | Add System.RebootStatus DPU proxy forwarding | May 2 | DPU |
| 38 | sonic-net/sonic-mgmt | [#24376](https://github.com/sonic-net/sonic-mgmt/pull/24376) | [HA][smartswitch] HA add test FNIC steady state and planned shutdown | May 4 | SmartSwitch |
| 39 | sonic-net/sonic-mgmt | [#24402](https://github.com/sonic-net/sonic-mgmt/pull/24402) | Filter out dpu DUT in duts_list for npu ha config. | May 5 | DPU |
| 40 | sonic-net/sonic-buildimage | [#27176](https://github.com/sonic-net/sonic-buildimage/pull/27176) | Remove unnecessary config-engine dependency from docker-dash-engine | May 5 | DASH |
| 41 | sonic-net/sonic-mgmt | [#24412](https://github.com/sonic-net/sonic-mgmt/pull/24412) | [zmq] Add test_gnmi_zmq_mgmt_vrf and factor common helpers into gnmi_zmq_utils | May 5 | SmartSwitch |
| 42 | sonic-net/sonic-utilities | [#4521](https://github.com/sonic-net/sonic-utilities/pull/4521) | Validate config_db.json in reload path. | May 6 | DASH/DPU/SmartSwitch |
| 43 | sonic-net/sonic-buildimage | [#27206](https://github.com/sonic-net/sonic-buildimage/pull/27206) | [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 6 | DPU |
| 44 | sonic-net/sonic-buildimage | [#27207](https://github.com/sonic-net/sonic-buildimage/pull/27207) | [202511] [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 6 | DPU |
| 45 | sonic-net/sonic-utilities | [#4525](https://github.com/sonic-net/sonic-utilities/pull/4525) | [DPU] Add optional DPU flow dump to techsupport collection | May 6 | DPU |
| 46 | sonic-net/sonic-mgmt | [#24433](https://github.com/sonic-net/sonic-mgmt/pull/24433) | [qos]: Skip warm reboot on TH5 devices in DSCP queue mapping test | May 7 | SmartSwitch |
| 47 | sonic-net/sonic-buildimage | [#27247](https://github.com/sonic-net/sonic-buildimage/pull/27247) | [nvidia-bluefield] Remove legacy console=hvc0 from BF3 DPU kernel command line to fix IRQ open request error | May 7 | DPU |
| 48 | sonic-net/sonic-mgmt | [#24444](https://github.com/sonic-net/sonic-mgmt/pull/24444) | [HA] [smartswitch] add the HA reapairing test | May 7 | DPU SmartSwitch |
| 49 | sonic-net/sonic-buildimage | [#27248](https://github.com/sonic-net/sonic-buildimage/pull/27248) | [nvidia-bluefield] Remove legacy console=hvc0 from BF3 DPU kernel command line to fix IRQ open request error | May 7 | DPU |
| 50 | sonic-net/sonic-mgmt | [#24483](https://github.com/sonic-net/sonic-mgmt/pull/24483) | Fix test issues in test_gnoi_system_reboot.py | May 8 | SmartSwitch |
| 51 | sonic-net/sonic-mgmt | [#24488](https://github.com/sonic-net/sonic-mgmt/pull/24488) | [HA][dash] Add Flow comparison support using Flow API | May 8 | DASH DPU |
| 52 | sonic-net/sonic-swss | [#4557](https://github.com/sonic-net/sonic-swss/pull/4557) | [dashhaorch]: Update in-memory ha_role on HA scope set | May 8 | DASH/DPU/SmartSwitch |
| 53 | sonic-net/sonic-swss | [#4558](https://github.com/sonic-net/sonic-swss/pull/4558) | [dashhaorch]: Remove DPU_STATE_DB entries upon DEL of HA_SET/HA_SCOPE | May 8 | DASH/DPU/SmartSwitch |
| 54 | sonic-net/sonic-utilities | [#4536](https://github.com/sonic-net/sonic-utilities/pull/4536) | [show, clear]: add 'orchagent tasks' commands to surface per-Executor timing + scheduling latency | May 11 | DASH/DPU/SmartSwitch |
| 55 | sonic-net/sonic-swss | [#4564](https://github.com/sonic-net/sonic-swss/pull/4564) | [orchagent]: Add ZmqRouteServer for concurrent route updates | May 12 | DPU |
| 56 | sonic-net/sonic-mgmt | [#24534](https://github.com/sonic-net/sonic-mgmt/pull/24534) | Add ERSPAN mirror session plugin for NPU-DPU port packet capture (--enable-dpc-mirroring) | May 12 | DASH DPU SmartSwitch |
| 57 | sonic-net/sonic-swss | [#4566](https://github.com/sonic-net/sonic-swss/pull/4566) | [orchagent/dash]: Remove retry logic from DASH orchs | May 12 | DASH |
| 58 | sonic-net/sonic-mgmt | [#24564](https://github.com/sonic-net/sonic-mgmt/pull/24564) | [DASH] Update skip condition for DASH metering test on Nvidia | May 12 | DASH SmartSwitch |
| 59 | sonic-net/sonic-mgmt | [#24566](https://github.com/sonic-net/sonic-mgmt/pull/24566) | [HA] [smartswitch] limit the DPU parameters used by HA tests to first 2 | May 12 | DASH DPU SmartSwitch |
| 60 | sonic-net/sonic-mgmt | [#24573](https://github.com/sonic-net/sonic-mgmt/pull/24573) | [smartswitch]: Allow testbed.yaml to select which DPUs are admin-up | May 13 | DPU SmartSwitch |
| 61 | sonic-net/sonic-buildimage | [#27341](https://github.com/sonic-net/sonic-buildimage/pull/27341) | Fix interfaces-config missing first-boot transaction after image upgrade | May 13 | SmartSwitch |
| 62 | sonic-net/sonic-buildimage | [#27346](https://github.com/sonic-net/sonic-buildimage/pull/27346) | [vs] Add knob to skip DASH engine image install | May 13 | DASH |

---

## PRs Merged (April 23 – May 13, 2026)

### Summary
- **Total:** 45 PRs
- **Top Repository:** sonic-mgmt (18 PRs merged)
- **Key Themes:** HA execution stability, DPU/SmartSwitch lifecycle handling, DASH orchestration scale, and test enablement

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-net/sonic-sairedis | [#1844](https://github.com/sonic-net/sonic-sairedis/pull/1844) | [meta] Populate object_statuses on bulk validation failure; DASH entries use ITEM_NOT_FOUND for missing keys | Apr 23 | DASH |
| 2 | sonic-net/sonic-mgmt | [#20411](https://github.com/sonic-net/sonic-mgmt/pull/20411) | Adding scale tests for per vnet bgp | Apr 24 | SmartSwitch |
| 3 | sonic-net/sonic-utilities | [#4472](https://github.com/sonic-net/sonic-utilities/pull/4472) | Fix Pensando DPU reboot handling in smartswitch operations | Apr 24 | DPU SmartSwitch |
| 4 | sonic-net/sonic-buildimage | [#26878](https://github.com/sonic-net/sonic-buildimage/pull/26878) | Fix kea-dhcp4 startup failure after trixie upgrade | Apr 24 | DASH/DPU/SmartSwitch |
| 5 | sonic-net/sonic-swss | [#4468](https://github.com/sonic-net/sonic-swss/pull/4468) | [dash]: Fix bulk remove post-processing for inbound/outbound routing entries | Apr 24 | DASH |
| 6 | sonic-net/sonic-mgmt | [#23545](https://github.com/sonic-net/sonic-mgmt/pull/23545) | Add error ignore in fpga update | Apr 26 | DASH/DPU/SmartSwitch |
| 7 | sonic-net/sonic-mgmt | [#24015](https://github.com/sonic-net/sonic-mgmt/pull/24015) | [SmartSwitch] Update the auto techsupport test for DPU | Apr 26 | DPU SmartSwitch |
| 8 | sonic-net/sonic-gnmi | [#643](https://github.com/sonic-net/sonic-gnmi/pull/643) | [SmartSwitch] Support maximum gnmi message size of 125k messages | Apr 27 | DASH SmartSwitch |
| 9 | sonic-net/sonic-mgmt | [#24005](https://github.com/sonic-net/sonic-mgmt/pull/24005) | Add smart switch full upgrade test all DPUs then reboot NPU | Apr 27 | DPU SmartSwitch |
| 10 | sonic-net/sonic-buildimage | [#26614](https://github.com/sonic-net/sonic-buildimage/pull/26614) | [Smartswitch][Mellanox]Increase shutdown timeout for smartswitch | Apr 28 | DPU SmartSwitch |
| 11 | sonic-net/sonic-mgmt | [#24138](https://github.com/sonic-net/sonic-mgmt/pull/24138) | [HA][smartswitch] enable running HA tests with any DPU pair | Apr 28 | DPU SmartSwitch |
| 12 | sonic-net/sonic-dash-ha | [#156](https://github.com/sonic-net/sonic-dash-ha/pull/156) | Handling unplanned events in npu driven ha | Apr 28 | DPU |
| 13 | sonic-net/sonic-mgmt | [#24049](https://github.com/sonic-net/sonic-mgmt/pull/24049) | console servers: Skip warm and fast reboots for C0. | Apr 29 | SmartSwitch |
| 14 | sonic-net/sonic-dash-ha | [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) | Add support for new DPU pairing in-flight | Apr 29 | DPU |
| 15 | sonic-net/sonic-mgmt | [#24322](https://github.com/sonic-net/sonic-mgmt/pull/24322) | Refactor the activate_dash_ha_from_json fixture | Apr 30 | DASH/DPU/SmartSwitch |
| 16 | sonic-net/SONiC | [#2307](https://github.com/sonic-net/SONiC/pull/2307) | Update ssw ha hld | Apr 30 | [ssw] |
| 17 | sonic-net/sonic-buildimage | [#27110](https://github.com/sonic-net/sonic-buildimage/pull/27110) | [Security] temporarily remove vpp test from sonic-mgmt docker image build | May 1 | DASH/DPU/SmartSwitch |
| 18 | sonic-net/sonic-gnmi | [#660](https://github.com/sonic-net/sonic-gnmi/pull/660) | Add OS.Verify and OS.Activate to DPU proxy forwardable methods | May 1 | DPU SmartSwitch |
| 19 | sonic-net/sonic-mgmt | [#23438](https://github.com/sonic-net/sonic-mgmt/pull/23438) | update _upgrade_one_dpu_via_gnoi to use perform_gnoi_reboot_dpu | May 1 | DPU SmartSwitch |
| 20 | sonic-net/sonic-buildimage | [#26933](https://github.com/sonic-net/sonic-buildimage/pull/26933) | [Smartswitch][Mellanox] Updated module to initialize without connector | May 4 | DPU SmartSwitch |
| 21 | sonic-net/sonic-buildimage | [#26871](https://github.com/sonic-net/sonic-buildimage/pull/26871) | [Mellanox][SmartSwitch] Convert sonic-bfb-installer.sh to python | May 4 | DPU SmartSwitch |
| 22 | sonic-net/sonic-mgmt | [#23518](https://github.com/sonic-net/sonic-mgmt/pull/23518) | Fix an issue in get_vlan_brief() | May 4 | SmartSwitch |
| 23 | sonic-net/sonic-mgmt | [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) | Add route rule for backend IP for PL redirect | May 4 | DPU |
| 24 | sonic-net/sonic-gnmi | [#663](https://github.com/sonic-net/sonic-gnmi/pull/663) | Add OS.Verify and OS.Activate DPU proxy forwarding | May 4 | DPU SmartSwitch |
| 25 | sonic-net/sonic-gnmi | [#662](https://github.com/sonic-net/sonic-gnmi/pull/662) | [202511] Fix too_many_pings + ARM64 CI + DPU proxy OS.Verify/Activate | May 5 | DPU |
| 26 | sonic-net/sonic-mgmt | [#24402](https://github.com/sonic-net/sonic-mgmt/pull/24402) | Filter out dpu DUT in duts_list for npu ha config. | May 5 | DPU |
| 27 | sonic-net/sonic-buildimage | [#26586](https://github.com/sonic-net/sonic-buildimage/pull/26586) | Added db migration logic to Pensando-Elba dpu | May 6 | DPU |
| 28 | sonic-net/sonic-buildimage | [#26475](https://github.com/sonic-net/sonic-buildimage/pull/26475) | [Mellanox] relocate udev-manager, add SN4280 mgmt PCI binding | May 6 | DPU SmartSwitch |
| 29 | sonic-net/sonic-buildimage | [#26929](https://github.com/sonic-net/sonic-buildimage/pull/26929) | [Cherry-pick] [Nvidia]: relocate udev-manager, add SN4280 mgmt PCI binding (#26475) | May 6 | DPU SmartSwitch |
| 30 | sonic-net/sonic-mgmt | [#24433](https://github.com/sonic-net/sonic-mgmt/pull/24433) | [qos]: Skip warm reboot on TH5 devices in DSCP queue mapping test | May 7 | SmartSwitch |
| 31 | sonic-net/sonic-dash-ha | [#158](https://github.com/sonic-net/sonic-dash-ha/pull/158) | Hardening ActorCreator | May 7 | DASH |
| 32 | sonic-net/sonic-dash-ha | [#160](https://github.com/sonic-net/sonic-dash-ha/pull/160) | Fix state machine for forced shutdown and planned shutdown | May 7 | DPU |
| 33 | sonic-net/sonic-buildimage | [#27118](https://github.com/sonic-net/sonic-buildimage/pull/27118) | [Mellanox][Nvidia-bluefield] Upgrade syncd containers to Trixie | May 7 | DPU |
| 34 | sonic-net/sonic-mgmt | [#24344](https://github.com/sonic-net/sonic-mgmt/pull/24344) | Update 'dash' test skip condition to run on smartswitch HWSKUs | May 8 | DASH SmartSwitch |
| 35 | sonic-net/sonic-mgmt | [#23211](https://github.com/sonic-net/sonic-mgmt/pull/23211) | Ignore expected error from DPU conosle minicom session disconnection. | May 8 | DPU |
| 36 | sonic-net/sonic-gnmi | [#664](https://github.com/sonic-net/sonic-gnmi/pull/664) | Add completeness test for DPU proxy ForwardToDPU handlers | May 8 | DPU |
| 37 | sonic-net/sonic-sairedis | [#1835](https://github.com/sonic-net/sonic-sairedis/pull/1835) | Runtime knob for Southbound ZMQ | May 8 | DPU |
| 38 | sonic-net/sonic-buildimage | [#27176](https://github.com/sonic-net/sonic-buildimage/pull/27176) | Remove unnecessary config-engine dependency from docker-dash-engine | May 11 | DASH |
| 39 | sonic-net/sonic-buildimage | [#27206](https://github.com/sonic-net/sonic-buildimage/pull/27206) | [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 11 | DPU |
| 40 | sonic-net/sonic-mgmt | [#24346](https://github.com/sonic-net/sonic-mgmt/pull/24346) | [HA][smartswitch] HA add flow compare to traffic tests | May 11 | SmartSwitch |
| 41 | sonic-net/sonic-buildimage | [#26549](https://github.com/sonic-net/sonic-buildimage/pull/26549) | [Mellanox] Fix MST service hang when DPUs are powered off | May 12 | DPU |
| 42 | sonic-net/sonic-swss | [#4558](https://github.com/sonic-net/sonic-swss/pull/4558) | [dashhaorch]: Remove DPU_STATE_DB entries upon DEL of HA_SET/HA_SCOPE | May 12 | DASH/DPU/SmartSwitch |
| 43 | sonic-net/sonic-mgmt | [#24566](https://github.com/sonic-net/sonic-mgmt/pull/24566) | [HA] [smartswitch] limit the DPU parameters used by HA tests to first 2 | May 12 | DASH DPU SmartSwitch |
| 44 | sonic-net/sonic-mgmt | [#24488](https://github.com/sonic-net/sonic-mgmt/pull/24488) | [HA][dash] Add Flow comparison support using Flow API | May 13 | DASH DPU |
| 45 | sonic-net/sonic-mgmt | [#24176](https://github.com/sonic-net/sonic-mgmt/pull/24176) | [HA][smartswitch] Ha test module9 | May 13 | DPU SmartSwitch |

---

## Key Development Areas

1. **SmartSwitch HA and Test Maturity**
   - Ongoing HA test execution improvements, module-level coverage, and reboot/upgrade validation.
2. **DPU Platform and Lifecycle Handling**
   - Work spans DPU reboot logic, upgrade paths, diagnostics, and service readiness behavior.
3. **DASH Scale and Data-Path Support**
   - Continued updates in orchestration and data-plane repositories to support scale and robustness.
4. **Cross-Repository Integration**
   - Activity remains distributed across mgmt, buildimage, sairedis, swss/common, SONiC, and utilities.

---

## Community Meeting Notes (Applied Where Applicable)

> ⚠️ **Note:** The following section is derived from AI-generated meeting recap notes and mapped to this date range where matching PR evidence exists.

| Topic from Meeting Notes | Applicability in Apr 23 – May 13 Data | Evidence in This Report |
|---|---|---|
| Backend IP route rule for PL redirect | **Applicable** | sonic-mgmt [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) (created Apr 24, merged May 4) |
| Smart Switch HA HLD update | **Applicable** | SONiC [#2307](https://github.com/sonic-net/SONiC/pull/2307) (created Apr 27, merged Apr 30) |
| DPU pairing support update | **Applicable** | sonic-dash-ha [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) (created Apr 24, merged Apr 29) |
| Floating NIC steady-state/planned-shutdown test | **Applicable** | sonic-mgmt [#24376](https://github.com/sonic-net/sonic-mgmt/pull/24376) (created May 4) |
| gNMI-ZMQ management VRF test path | **Applicable** | sonic-mgmt [#24412](https://github.com/sonic-net/sonic-mgmt/pull/24412) (created May 5) |
| ENI OID mapping + DPU counter/virtual path handling | **Applicable** | sonic-swss [#4540](https://github.com/sonic-net/sonic-swss/pull/4540), sonic-gnmi [#665](https://github.com/sonic-net/sonic-gnmi/pull/665) |
| ZMQ socket timeout reset fix | **Applicable** | sonic-sairedis [#1881](https://github.com/sonic-net/sonic-sairedis/pull/1881) (created May 1) |
| gNMI client placement in sonic-management docker | **Partially applicable (discussion/planning)** | No single merged placement PR clearly identified in this window; keep as follow-up track item |
| HA module progress (8 committed, module 9 in review) | **Applicable** | sonic-mgmt [#24176](https://github.com/sonic-net/sonic-mgmt/pull/24176) (Module 9) merged May 13 |
| DASH architecture walkthrough request | **Planning item** | No direct PR mapping required; community onboarding/documentation follow-up |

### Meeting Follow-up Tasks

| Action Item | Owner(s) | Tracking in This Report |
|---|---|---|
| Respond to DASH walkthrough email | Kristina | Community/onboarding action; no direct PR required |
| Coordinate gNMI client integration location (sonic-management docker) | Michael, Mircea | Track under cross-repo infra/testing PRs in upcoming reports |
| Share involved-routing examples and diagrams | Michal | Expected to drive follow-on test PRs; monitor sonic-mgmt activity |

---

## Recommendations

### High Priority
1. Keep merge throughput aligned with creation volume in the highest-traffic repositories.
2. Continue HA/DPU validation coverage for reboot and upgrade scenarios across platform variants.
3. Prioritize follow-up on scale-related changes with targeted stress and regression runs.
4. Track meeting follow-up items explicitly on the project board (gNMI client placement, routing examples, walkthrough/onboarding).

### Medium Priority
1. Track time-to-merge for high-volume repos to identify review bottlenecks.
2. Maintain cross-repo traceability for related SmartSwitch/DASH changes in stacked PR sets.
3. Continue validation of ZMQ and DPU proxy test paths as GNMI/SAIRedis fixes land.

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Period | April 23 – May 13, 2026 (21 days) |
| PRs Created | 62 |
| PRs Merged | 45 |
| Merge Rate | 72.6% |
| Creation Velocity | 3.0 PRs/day |
| Merge Velocity | 2.1 PRs/day |
| Active Repositories | 9 |
| Top Created Repo | sonic-mgmt (29) |
| Top Merged Repo | sonic-mgmt (18) |

---

## Conclusion

The April 23 – May 13 window shows sustained multi-repository execution for SmartSwitch/DPU/DASH development, with strong merge throughput and broad cross-team activity. The dataset indicates continued emphasis on HA quality, DPU lifecycle operations, and scalable DASH enablement.

Meeting recap items were integrated where PR evidence exists in this window (HA HLD, backend IP route rule, FNIC and ZMQ test-path additions, ENI/DPU counter work, and ZMQ timeout handling). Remaining meeting actions are captured as planning tracks for follow-up in subsequent reports.

---

### Query Used
```
org:sonic-net is:pr created:2026-04-23..2026-05-13 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
org:sonic-net is:pr is:merged merged:2026-04-23..2026-05-13 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```

*Data source: GitHub Search API results retrieved on 2026-05-13.*
