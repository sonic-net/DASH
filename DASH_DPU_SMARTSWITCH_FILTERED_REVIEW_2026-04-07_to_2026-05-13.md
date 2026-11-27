# DASH/DPU/SmartSwitch Weekly Review
**Period:** April 7 – May 13, 2026 (37 days)
**Report Generated:** May 14, 2026
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **April 7 – May 13, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **125 PRs Created** during the period
- **104 PRs Merged** during the period
- **13 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Merge Rate:** 83.2%
- **Creation Velocity:** 3.4 PRs/day
- **Merge Velocity:** 2.8 PRs/day

### Highlights
- Highest PR creation volume: **sonic-mgmt** (60 created)
- Highest merge volume: **sonic-mgmt** (46 merged)
- Strong SmartSwitch/HA and DPU lifecycle focus across management, buildimage, and GNMI repositories
- High cross-repository execution cadence with sustained merge throughput over a 37-day span

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during April 7 – May 13, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 261 | 1042 | 2236 | 46 PRs merged + 60 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 965 | 1833 | 2987 | 25 PRs merged + 21 PRs created | 🟢 Very High |
| sonic-net/sonic-sairedis | 79 | 391 | 161 | 6 PRs merged + 10 PRs created | 🟢 High |
| sonic-net/sonic-gnmi | 45 | 113 | 80 | 5 PRs merged + 9 PRs created | 🟢 High |
| sonic-net/sonic-swss | 227 | 703 | 685 | 6 PRs merged + 8 PRs created | 🟢 High |
| sonic-net/sonic-dash-ha | 4 | 24 | 10 | 5 PRs merged + 4 PRs created | 🟡 Moderate |
| sonic-net/sonic-utilities | 184 | 839 | 636 | 2 PRs merged + 5 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss-common | 58 | 346 | 113 | 3 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/SONiC | 2801 | 1314 | 869 | 3 PRs merged + 1 PRs created | 🟡 Moderate |
| sonic-net/sonic-host-services | 5 | 156 | 61 | 1 PRs merged + 1 PRs created | 🟡 Low |
| sonic-net/sonic-platform-common | 53 | 224 | 53 | 1 PRs merged + 1 PRs created | 🟡 Low |
| sonic-net/sonic-platform-daemons | 35 | 215 | 100 | 1 PRs merged + 1 PRs created | 🟡 Low |
| sonic-net/DASH | 102 | 104 | 88 | 0 PRs merged + 1 PRs created | 🟡 Low |

**Note:** Repositories are included only if they have PRs with DASH/DPU/SmartSwitch/Smart keywords in title or body during this query period.

---

## PRs Created (April 7 – May 13, 2026)

### Summary
- **Total:** 125 PRs
- **Top Repository:** sonic-net/sonic-mgmt (60 PRs created)
- **Key Themes:** SmartSwitch HA test expansion, DPU reboot/upgrade handling, DASH orchestration and scale-path updates

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-net/sonic-platform-common | [#652](https://github.com/sonic-net/sonic-platform-common/pull/652) | [Smartswitch] Fix device base path for platform file | Apr 7 | SmartSwitch |
| 2 | sonic-net/sonic-buildimage | [#26614](https://github.com/sonic-net/sonic-buildimage/pull/26614) | [Smartswitch][Mellanox]Increase shutdown timeout for smartswitch | Apr 7 | DPU SmartSwitch |
| 3 | sonic-net/sonic-platform-daemons | [#789](https://github.com/sonic-net/sonic-platform-daemons/pull/789) | Speed up execution of thermalctld unit tests | Apr 7 | - |
| 4 | sonic-net/sonic-sairedis | [#1835](https://github.com/sonic-net/sonic-sairedis/pull/1835) | Runtime knob for Southbound ZMQ | Apr 7 | DPU |
| 5 | sonic-net/sonic-swss | [#4452](https://github.com/sonic-net/sonic-swss/pull/4452) | [npu-driven][ssw][ha] instead of waiting for ha state change event, immediately update dpu_state_db and in-memory ha state, and create bfd software sessions accordingly | Apr 7 | DPU SmartSwitch |
| 6 | sonic-net/sonic-sairedis | [#1836](https://github.com/sonic-net/sonic-sairedis/pull/1836) | [syncd]: Clean up ENI counter entries from COUNTERS_DB on ENI deletion | Apr 7 | DASH |
| 7 | sonic-net/sonic-mgmt | [#23711](https://github.com/sonic-net/sonic-mgmt/pull/23711) | fix pre/post tests errors in run_tests.sh | Apr 8 | DPU |
| 8 | sonic-net/sonic-mgmt | [#23727](https://github.com/sonic-net/sonic-mgmt/pull/23727) | Add a new testcase test_dash_smartswitch_crm | Apr 8 | SmartSwitch |
| 9 | sonic-net/sonic-sairedis | [#1838](https://github.com/sonic-net/sonic-sairedis/pull/1838) | [202511] Update SAI to v1.17.5 | Apr 8 | DASH |
| 10 | sonic-net/sonic-mgmt | [#23747](https://github.com/sonic-net/sonic-mgmt/pull/23747) | Add skip conditions for HA DPU and NPU process crash tests | Apr 8 | DPU SmartSwitch |
| 11 | sonic-net/sonic-mgmt | [#23748](https://github.com/sonic-net/sonic-mgmt/pull/23748) | Bug fix: add extra sleep before startup DPU to avoid deadlock | Apr 8 | DPU |
| 12 | sonic-net/sonic-mgmt | [#23765](https://github.com/sonic-net/sonic-mgmt/pull/23765) | [Smartswitch] Changed PL SIP values as per requirement | Apr 9 | SmartSwitch |
| 13 | sonic-net/sonic-mgmt | [#23781](https://github.com/sonic-net/sonic-mgmt/pull/23781) | [202511] copp: fix missing is_smartswitch_light_mode init in ControlPlaneBaseTest | Apr 9 | SmartSwitch |
| 14 | sonic-net/sonic-buildimage | [#26679](https://github.com/sonic-net/sonic-buildimage/pull/26679) | [SmartSwitch] Support maximum dash configuration size | Apr 9 | DASH DPU SmartSwitch |
| 15 | sonic-net/sonic-gnmi | [#643](https://github.com/sonic-net/sonic-gnmi/pull/643) | [SmartSwitch] Support maximum gnmi message size of 125k messages | Apr 9 | DASH SmartSwitch |
| 16 | sonic-net/sonic-sairedis | [#1840](https://github.com/sonic-net/sonic-sairedis/pull/1840) | [SmartSwitch] [DPU] Support maximum dash configuration size | Apr 9 | DASH DPU SmartSwitch |
| 17 | sonic-net/sonic-mgmt | [#23797](https://github.com/sonic-net/sonic-mgmt/pull/23797) | [HA][smartswitch] update HA module 8 based on latest fixtures from conftest | Apr 9 | SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#23801](https://github.com/sonic-net/sonic-mgmt/pull/23801) | [202511] Cherry-pick DASH Privatelink + FNIC improvements | Apr 9 | DASH DPU SmartSwitch |
| 19 | sonic-net/sonic-mgmt | [#23804](https://github.com/sonic-net/sonic-mgmt/pull/23804) | Add new fields in DASH_HA_GLOBAL_CONFIG | Apr 9 | - |
| 20 | sonic-net/sonic-mgmt | [#23811](https://github.com/sonic-net/sonic-mgmt/pull/23811) | Override config in restore_test_env of GCU test_cacl.py | Apr 10 | SmartSwitch |
| 21 | sonic-net/sonic-mgmt | [#23815](https://github.com/sonic-net/sonic-mgmt/pull/23815) | Fix minigraph reload related tests for smartswitch | Apr 10 | SmartSwitch |
| 22 | sonic-net/sonic-sairedis | [#1844](https://github.com/sonic-net/sonic-sairedis/pull/1844) | [meta] Populate object_statuses on bulk validation failure; DASH entries use ITEM_NOT_FOUND for missing keys | Apr 10 | DASH |
| 23 | sonic-net/sonic-mgmt | [#23829](https://github.com/sonic-net/sonic-mgmt/pull/23829) | Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests" | Apr 10 | SmartSwitch |
| 24 | sonic-net/sonic-swss | [#4468](https://github.com/sonic-net/sonic-swss/pull/4468) | [dash]: Fix bulk remove post-processing for inbound/outbound routing entries | Apr 10 | DASH |
| 25 | sonic-net/sonic-mgmt | [#23835](https://github.com/sonic-net/sonic-mgmt/pull/23835) | DPUs: Include disk type 'MMC' for dpu ssdhealth check . Also fix for PR: 23641  | Apr 10 | DPU SmartSwitch |
| 26 | sonic-net/sonic-buildimage | [#26725](https://github.com/sonic-net/sonic-buildimage/pull/26725) | [dhcp_server]: Fix lease not shown after reboot (#24178) | Apr 12 | SmartSwitch |
| 27 | sonic-net/sonic-mgmt | [#23875](https://github.com/sonic-net/sonic-mgmt/pull/23875) | Revert "Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests"" | Apr 13 | SmartSwitch |
| 28 | sonic-net/sonic-sairedis | [#1847](https://github.com/sonic-net/sonic-sairedis/pull/1847) | [dash] Cleanup ENI counters on ENI deletion | Apr 14 | DASH |
| 29 | sonic-net/sonic-sairedis | [#1848](https://github.com/sonic-net/sonic-sairedis/pull/1848) | [syncd]: Fall back to TCP connection when unix socket path is not defined | Apr 14 | DPU |
| 30 | sonic-net/sonic-buildimage | [#26762](https://github.com/sonic-net/sonic-buildimage/pull/26762) | [database]: Skip CONFIG_DB_INITIALIZED writes for DPU database instances | Apr 14 | DPU SmartSwitch |
| 31 | sonic-net/sonic-buildimage | [#26764](https://github.com/sonic-net/sonic-buildimage/pull/26764) | [smartswitch] Start pmon after databasedpu instance services on SmartSwitch host (Fixes #26760) | Apr 14 | DPU SmartSwitch |
| 32 | sonic-net/sonic-buildimage | [#26765](https://github.com/sonic-net/sonic-buildimage/pull/26765) | Add extra logging directory mapping for dash-ha container | Apr 14 | DASH SmartSwitch |
| 33 | sonic-net/sonic-mgmt | [#23915](https://github.com/sonic-net/sonic-mgmt/pull/23915) | Add utility to upgrade DPU images for smartswitch testbeds | Apr 14 | DPU SmartSwitch |
| 34 | sonic-net/sonic-mgmt | [#23920](https://github.com/sonic-net/sonic-mgmt/pull/23920) | [DASH] Fixes for FNIC and metering tests | Apr 15 | DASH DPU SmartSwitch |
| 35 | sonic-net/sonic-utilities | [#4458](https://github.com/sonic-net/sonic-utilities/pull/4458) | [DPU] Add flow dump collection to techsupport | Apr 15 | DPU SmartSwitch |
| 36 | sonic-net/sonic-mgmt | [#23933](https://github.com/sonic-net/sonic-mgmt/pull/23933) | chore: get_dut_version add dpu smart switch support | Apr 15 | DPU SmartSwitch Smart |
| 37 | sonic-net/sonic-swss | [#4484](https://github.com/sonic-net/sonic-swss/pull/4484) | [orchagent]: Use Redis pipeline for deferred DASH result table writes | Apr 15 | DASH |
| 38 | sonic-net/sonic-mgmt | [#23957](https://github.com/sonic-net/sonic-mgmt/pull/23957) | [HA][smartswitch] HA test module 3 BFD pinning | Apr 15 | SmartSwitch |
| 39 | sonic-net/sonic-mgmt | [#23964](https://github.com/sonic-net/sonic-mgmt/pull/23964) | Enhance DASH-HA Private Link Steady State test | Apr 15 | DASH |
| 40 | sonic-net/sonic-mgmt | [#23991](https://github.com/sonic-net/sonic-mgmt/pull/23991) | Reapply TLS cert config after preboot reboot in NPU upgrade test | Apr 16 | SmartSwitch Smart |
| 41 | sonic-net/sonic-swss-common | [#1176](https://github.com/sonic-net/sonic-swss-common/pull/1176) | [dash] Add COUNTERS_ENI_OID_MAP definition | Apr 16 | DASH |
| 42 | sonic-net/sonic-swss-common | [#1177](https://github.com/sonic-net/sonic-swss-common/pull/1177) | [dash] Add COUNTERS_ENI_OID_MAP table name to schema.h | Apr 16 | DASH |
| 43 | sonic-net/sonic-host-services | [#376](https://github.com/sonic-net/sonic-host-services/pull/376) | [smartswitch] Use dpu_halt_services_timeout from platform.json, fallback to HALT_TIMEOUT=60 | Apr 16 | DPU SmartSwitch |
| 44 | sonic-net/sonic-mgmt | [#24005](https://github.com/sonic-net/sonic-mgmt/pull/24005) | Add smart switch full upgrade test all DPUs then reboot NPU | Apr 16 | DPU SmartSwitch Smart |
| 45 | sonic-net/sonic-mgmt | [#24006](https://github.com/sonic-net/sonic-mgmt/pull/24006) | moved test_reboot_cause to test_reload_dpu.py | Apr 16 | DPU SmartSwitch |
| 46 | sonic-net/sonic-mgmt | [#24009](https://github.com/sonic-net/sonic-mgmt/pull/24009) | [tests/common]: Respect ansible_port in paramiko SSH connections | Apr 17 | DPU |
| 47 | sonic-net/sonic-mgmt | [#24014](https://github.com/sonic-net/sonic-mgmt/pull/24014) | Fix test test_default_cfg_after_load_mg for testbed with golden config | Apr 17 | SmartSwitch |
| 48 | sonic-net/sonic-mgmt | [#24015](https://github.com/sonic-net/sonic-mgmt/pull/24015) | [SmartSwitch] Update the auto techsupport test for DPU | Apr 17 | DPU SmartSwitch |
| 49 | sonic-net/sonic-buildimage | [#26868](https://github.com/sonic-net/sonic-buildimage/pull/26868) | [build][202505] Update apt source list to azure mirror in docker dash-engine | Apr 17 | DASH |
| 50 | sonic-net/sonic-buildimage | [#26871](https://github.com/sonic-net/sonic-buildimage/pull/26871) | [Mellanox][SmartSwitch] Convert sonic-bfb-installer.sh to python | Apr 17 | DPU SmartSwitch |
| 51 | sonic-net/sonic-buildimage | [#26878](https://github.com/sonic-net/sonic-buildimage/pull/26878) | Fix kea-dhcp4 startup failure after trixie upgrade | Apr 17 | - |
| 52 | sonic-net/sonic-utilities | [#4472](https://github.com/sonic-net/sonic-utilities/pull/4472) | Fix Pensando DPU reboot handling in smartswitch operations | Apr 18 | DPU SmartSwitch |
| 53 | sonic-net/sonic-mgmt | [#24046](https://github.com/sonic-net/sonic-mgmt/pull/24046) |  Update SmartSwitch HA test plan with identified test gaps | Apr 19 | DPU SmartSwitch |
| 54 | sonic-net/sonic-mgmt | [#24049](https://github.com/sonic-net/sonic-mgmt/pull/24049) | console servers: Skip warm and fast reboots for C0. | Apr 20 | SmartSwitch |
| 55 | sonic-net/sonic-sairedis | [#1862](https://github.com/sonic-net/sonic-sairedis/pull/1862) | Smart Counter Poll to allow counters to work properly on Broadcom platforms. | Apr 20 | Smart |
| 56 | sonic-net/sonic-sairedis | [#1863](https://github.com/sonic-net/sonic-sairedis/pull/1863) | [meta]: Skip SaiObjectCollection tracking for high-scale DASH entry t… | Apr 20 | DASH |
| 57 | sonic-net/sonic-swss-common | [#1178](https://github.com/sonic-net/sonic-swss-common/pull/1178) | Increase ZMQ Response Size to 32MB to support maximum dash configuration size | Apr 21 | DASH DPU |
| 58 | sonic-net/sonic-mgmt | [#24084](https://github.com/sonic-net/sonic-mgmt/pull/24084) | [critical_services] Exclude snmp from tracking list on BMC topology | Apr 21 | DPU |
| 59 | sonic-net/sonic-gnmi | [#655](https://github.com/sonic-net/sonic-gnmi/pull/655) | [202511] Fix too_many_pings during DPU SetPackage and add ARM64 CI build (#634) | Apr 21 | DPU |
| 60 | sonic-net/sonic-buildimage | [#26929](https://github.com/sonic-net/sonic-buildimage/pull/26929) | [Cherry-pick] [Nvidia]: relocate udev-manager, add SN4280 mgmt PCI binding (#26475) | Apr 21 | DPU SmartSwitch Smart |
| 61 | sonic-net/sonic-buildimage | [#26933](https://github.com/sonic-net/sonic-buildimage/pull/26933) | [Smartswitch][Mellanox] Updated module to initialize without connector | Apr 22 | DPU SmartSwitch |
| 62 | sonic-net/sonic-mgmt | [#24128](https://github.com/sonic-net/sonic-mgmt/pull/24128) | [HA] [smartswitch] fix the renaming of dash_ha_set_dpu_config_table | Apr 22 | SmartSwitch |
| 63 | sonic-net/sonic-mgmt | [#24136](https://github.com/sonic-net/sonic-mgmt/pull/24136) | Dpu uptime and graceful reboot enhancements | Apr 22 | DPU SmartSwitch |
| 64 | sonic-net/sonic-mgmt | [#24138](https://github.com/sonic-net/sonic-mgmt/pull/24138) | [HA][smartswitch] enable running HA tests with any DPU pair | Apr 22 | DPU SmartSwitch |
| 65 | sonic-net/sonic-mgmt | [#24160](https://github.com/sonic-net/sonic-mgmt/pull/24160) | [gnmi] Fix gNOI reboot test failures on SmartSwitch platforms | Apr 23 | DPU SmartSwitch |
| 66 | sonic-net/sonic-dash-ha | [#156](https://github.com/sonic-net/sonic-dash-ha/pull/156) | Handling unplanned events in npu driven ha | Apr 23 | DPU |
| 67 | sonic-net/sonic-mgmt | [#24175](https://github.com/sonic-net/sonic-mgmt/pull/24175) | Bug fix: conditional mark stop working after Pytest 9.0 | Apr 23 | DPU |
| 68 | sonic-net/sonic-mgmt | [#24176](https://github.com/sonic-net/sonic-mgmt/pull/24176) | [HA][smartswitch] Ha test module9 | Apr 23 | DPU SmartSwitch |
| 69 | sonic-net/sonic-mgmt | [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) | Add route rule for backend IP for PL redirect | Apr 24 | DPU |
| 70 | sonic-net/sonic-dash-ha | [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) | Add support for new DPU pairing in-flight | Apr 24 | DPU |
| 71 | sonic-net/SONiC | [#2307](https://github.com/sonic-net/SONiC/pull/2307) | Update ssw ha hld | Apr 27 | - |
| 72 | sonic-net/sonic-mgmt | [#24229](https://github.com/sonic-net/sonic-mgmt/pull/24229) | [Smartswitch] Enable loganalyzer on DPUs | Apr 27 | DASH DPU SmartSwitch |
| 73 | sonic-net/sonic-mgmt | [#24245](https://github.com/sonic-net/sonic-mgmt/pull/24245) | [HA][smartswitch] Ha test repairing dpu | Apr 27 | DPU SmartSwitch |
| 74 | sonic-net/sonic-mgmt | [#24246](https://github.com/sonic-net/sonic-mgmt/pull/24246) | SmartSwitch upgrade test: follow-up fixes from PR #24005 review | Apr 27 | DPU SmartSwitch |
| 75 | sonic-net/sonic-gnmi | [#660](https://github.com/sonic-net/sonic-gnmi/pull/660) | Add OS.Verify and OS.Activate to DPU proxy forwardable methods | Apr 27 | DPU SmartSwitch Smart |
| 76 | sonic-net/sonic-mgmt | [#24258](https://github.com/sonic-net/sonic-mgmt/pull/24258) | [SmartSwitch] Skip internal backplane ports in iface_namingmode tests | Apr 28 | DPU SmartSwitch |
| 77 | sonic-net/sonic-buildimage | [#27020](https://github.com/sonic-net/sonic-buildimage/pull/27020) | [aspeed][BMC] Do not mask sonic-hostservice.service on BMC images | Apr 28 | DPU |
| 78 | sonic-net/sonic-mgmt | [#24278](https://github.com/sonic-net/sonic-mgmt/pull/24278) | [smartswitch] re-enable the DASH tests on 202511 | Apr 28 | DASH DPU SmartSwitch |
| 79 | sonic-net/sonic-dash-ha | [#158](https://github.com/sonic-net/sonic-dash-ha/pull/158) | Hardening ActorCreator | Apr 28 | DASH |
| 80 | sonic-net/DASH | [#698](https://github.com/sonic-net/DASH/pull/698) | add eni attribute to get ha flow owner (DPU-driven HA) | Apr 28 | DPU |
| 81 | sonic-net/sonic-mgmt | [#24284](https://github.com/sonic-net/sonic-mgmt/pull/24284) | 202511: Add t2_single_node_max and t2_single_node_max_64p_v2 to q3d qos params | Apr 28 | - |
| 82 | sonic-net/sonic-mgmt | [#24292](https://github.com/sonic-net/sonic-mgmt/pull/24292) | [202511] Update the copp test for smartswitch(PR #22751 and # 21409) | Apr 29 | SmartSwitch |
| 83 | sonic-net/sonic-mgmt | [#24313](https://github.com/sonic-net/sonic-mgmt/pull/24313) | [SmartSwitch] Fix the generate smartswitch golden config flow | Apr 29 | DPU SmartSwitch |
| 84 | sonic-net/sonic-mgmt | [#24316](https://github.com/sonic-net/sonic-mgmt/pull/24316) | test_po_update.py - cannot remove the last IP entry of interface Port… | Apr 29 | DPU SmartSwitch |
| 85 | sonic-net/sonic-buildimage | [#27067](https://github.com/sonic-net/sonic-buildimage/pull/27067) | [sonic-yang-models] Migrate IP prefix typedefs; preserve host bits where needed | Apr 29 | DASH Smart |
| 86 | sonic-net/sonic-mgmt | [#24322](https://github.com/sonic-net/sonic-mgmt/pull/24322) | Refactor the activate_dash_ha_from_json fixture | Apr 29 | - |
| 87 | sonic-net/sonic-mgmt | [#24335](https://github.com/sonic-net/sonic-mgmt/pull/24335) | Remove the skip condition for test test_privatelink_udp_sport_range_negative | Apr 30 | SmartSwitch |
| 88 | sonic-net/sonic-mgmt | [#24344](https://github.com/sonic-net/sonic-mgmt/pull/24344) | Update 'dash' test skip condition to run on smartswitch HWSKUs | Apr 30 | DASH SmartSwitch |
| 89 | sonic-net/sonic-dash-ha | [#160](https://github.com/sonic-net/sonic-dash-ha/pull/160) | Fix state machine for forced shutdown and planned shutdown | Apr 30 | DPU |
| 90 | sonic-net/sonic-mgmt | [#24346](https://github.com/sonic-net/sonic-mgmt/pull/24346) | [HA][smartswitch] HA add flow compare to traffic tests | Apr 30 | SmartSwitch |
| 91 | sonic-net/sonic-gnmi | [#661](https://github.com/sonic-net/sonic-gnmi/pull/661) | [202511] Add OS.Verify and OS.Activate to DPU proxy forwardable methods | Apr 30 | DPU |
| 92 | sonic-net/sonic-mgmt | [#24351](https://github.com/sonic-net/sonic-mgmt/pull/24351) | [smartswitch]: Quiet retry-time noise in check_dpu_critical_processes | Apr 30 | DPU SmartSwitch |
| 93 | sonic-net/sonic-gnmi | [#662](https://github.com/sonic-net/sonic-gnmi/pull/662) | [202511] Fix too_many_pings + ARM64 CI + DPU proxy OS.Verify/Activate | May 1 | DPU |
| 94 | sonic-net/sonic-buildimage | [#27110](https://github.com/sonic-net/sonic-buildimage/pull/27110) | [Security] temporarily remove vpp test from sonic-mgmt docker image build | May 1 | - |
| 95 | sonic-net/sonic-sairedis | [#1881](https://github.com/sonic-net/sonic-sairedis/pull/1881) | zmq: reset ZMQ_REQ socket when zmq_poll times out | May 1 | - |
| 96 | sonic-net/sonic-gnmi | [#663](https://github.com/sonic-net/sonic-gnmi/pull/663) | Add OS.Verify and OS.Activate DPU proxy forwarding | May 1 | DPU SmartSwitch |
| 97 | sonic-net/sonic-swss | [#4540](https://github.com/sonic-net/sonic-swss/pull/4540) | [dash]: Add ENI OID mapping and DPU counter DB support | May 1 | DASH DPU |
| 98 | sonic-net/sonic-gnmi | [#664](https://github.com/sonic-net/sonic-gnmi/pull/664) | Add completeness test for DPU proxy ForwardToDPU handlers | May 1 | DPU |
| 99 | sonic-net/sonic-gnmi | [#665](https://github.com/sonic-net/sonic-gnmi/pull/665) | Add DPU_COUNTERS_DB virtual path handling for DASH_METER and ENI counters | May 1 | - |
| 100 | sonic-net/sonic-buildimage | [#27118](https://github.com/sonic-net/sonic-buildimage/pull/27118) | [Mellanox][Nvidia-bluefield] Upgrade syncd containers to Trixie | May 2 | DPU |
| 101 | sonic-net/sonic-gnmi | [#666](https://github.com/sonic-net/sonic-gnmi/pull/666) | Add System.RebootStatus DPU proxy forwarding | May 2 | DPU |
| 102 | sonic-net/sonic-mgmt | [#24376](https://github.com/sonic-net/sonic-mgmt/pull/24376) | [HA][smartswitch] HA add test FNIC steady state and planned shutdown | May 4 | SmartSwitch |
| 103 | sonic-net/sonic-mgmt | [#24402](https://github.com/sonic-net/sonic-mgmt/pull/24402) | Filter out dpu DUT in duts_list for npu ha config. | May 5 | DPU |
| 104 | sonic-net/sonic-buildimage | [#27176](https://github.com/sonic-net/sonic-buildimage/pull/27176) | Remove unnecessary config-engine dependency from docker-dash-engine | May 5 | DASH |
| 105 | sonic-net/sonic-mgmt | [#24412](https://github.com/sonic-net/sonic-mgmt/pull/24412) | [zmq] Add test_gnmi_zmq_mgmt_vrf and factor common helpers into gnmi_zmq_utils | May 5 | SmartSwitch |
| 106 | sonic-net/sonic-utilities | [#4521](https://github.com/sonic-net/sonic-utilities/pull/4521) | Validate config_db.json in reload path. | May 6 | - |
| 107 | sonic-net/sonic-buildimage | [#27206](https://github.com/sonic-net/sonic-buildimage/pull/27206) | [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 6 | DPU |
| 108 | sonic-net/sonic-buildimage | [#27207](https://github.com/sonic-net/sonic-buildimage/pull/27207) | [202511] [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 6 | DPU |
| 109 | sonic-net/sonic-utilities | [#4525](https://github.com/sonic-net/sonic-utilities/pull/4525) | [DPU] Add optional DPU flow dump to techsupport collection | May 6 | DPU |
| 110 | sonic-net/sonic-mgmt | [#24433](https://github.com/sonic-net/sonic-mgmt/pull/24433) | [qos]: Skip warm reboot on TH5 devices in DSCP queue mapping test | May 7 | SmartSwitch |
| 111 | sonic-net/sonic-buildimage | [#27247](https://github.com/sonic-net/sonic-buildimage/pull/27247) | [nvidia-bluefield] Remove legacy console=hvc0 from BF3 DPU kernel command line to fix IRQ open request error | May 7 | DPU |
| 112 | sonic-net/sonic-mgmt | [#24444](https://github.com/sonic-net/sonic-mgmt/pull/24444) | [HA] [smartswitch] add the HA reapairing test | May 7 | DPU SmartSwitch |
| 113 | sonic-net/sonic-buildimage | [#27248](https://github.com/sonic-net/sonic-buildimage/pull/27248) | [nvidia-bluefield] Remove legacy console=hvc0 from BF3 DPU kernel command line to fix IRQ open request error | May 7 | DPU |
| 114 | sonic-net/sonic-mgmt | [#24483](https://github.com/sonic-net/sonic-mgmt/pull/24483) | Fix test issues in test_gnoi_system_reboot.py | May 8 | SmartSwitch |
| 115 | sonic-net/sonic-mgmt | [#24488](https://github.com/sonic-net/sonic-mgmt/pull/24488) | [HA][dash] Add Flow comparison support using Flow API | May 8 | DASH DPU |
| 116 | sonic-net/sonic-swss | [#4557](https://github.com/sonic-net/sonic-swss/pull/4557) | [dashhaorch]: Update in-memory ha_role on HA scope set | May 8 | - |
| 117 | sonic-net/sonic-swss | [#4558](https://github.com/sonic-net/sonic-swss/pull/4558) | [dashhaorch]: Remove DPU_STATE_DB entries upon DEL of HA_SET/HA_SCOPE | May 8 | - |
| 118 | sonic-net/sonic-utilities | [#4536](https://github.com/sonic-net/sonic-utilities/pull/4536) | [show, clear]: add 'orchagent tasks' commands to surface per-Executor timing + scheduling latency | May 11 | - |
| 119 | sonic-net/sonic-swss | [#4564](https://github.com/sonic-net/sonic-swss/pull/4564) | [orchagent]: Add ZmqRouteServer for concurrent route updates | May 12 | DPU |
| 120 | sonic-net/sonic-mgmt | [#24534](https://github.com/sonic-net/sonic-mgmt/pull/24534) | Add ERSPAN mirror session plugin for NPU-DPU port packet capture (--enable-dpc-mirroring) | May 12 | DASH DPU SmartSwitch |
| 121 | sonic-net/sonic-swss | [#4566](https://github.com/sonic-net/sonic-swss/pull/4566) | [orchagent/dash]: Remove retry logic from DASH orchs | May 12 | DASH |
| 122 | sonic-net/sonic-mgmt | [#24564](https://github.com/sonic-net/sonic-mgmt/pull/24564) | [DASH] Update skip condition for DASH metering test on Nvidia | May 12 | DASH SmartSwitch |
| 123 | sonic-net/sonic-mgmt | [#24566](https://github.com/sonic-net/sonic-mgmt/pull/24566) | [HA] [smartswitch] limit the DPU parameters used by HA tests to first 2 | May 12 | DASH DPU SmartSwitch |
| 124 | sonic-net/sonic-mgmt | [#24573](https://github.com/sonic-net/sonic-mgmt/pull/24573) | [smartswitch]: Allow testbed.yaml to select which DPUs are admin-up | May 13 | DPU SmartSwitch |
| 125 | sonic-net/sonic-buildimage | [#27346](https://github.com/sonic-net/sonic-buildimage/pull/27346) | [vs] Add knob to skip DASH engine image install | May 13 | DASH |

---

## PRs Merged (April 7 – May 13, 2026)

### Summary
- **Total:** 104 PRs
- **Top Repository:** sonic-net/sonic-mgmt (46 PRs merged)
- **Key Themes:** HA module progression, DPU platform stabilization, GNMI/ZMQ reliability, and SmartSwitch test enablement

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-net/sonic-mgmt | [#23596](https://github.com/sonic-net/sonic-mgmt/pull/23596) | [HA][smartswitch] HA reconfigure test  | Apr 7 | SmartSwitch |
| 2 | sonic-net/sonic-buildimage | [#26334](https://github.com/sonic-net/sonic-buildimage/pull/26334) | [Smartswitch][Mellanox] Fix BFB installation based on waiting for chassisd retry mechanism | Apr 7 | DPU SmartSwitch Smart |
| 3 | sonic-net/sonic-buildimage | [#26348](https://github.com/sonic-net/sonic-buildimage/pull/26348) | [Mellanox] Fix get component versions script to fetch correct asic fw | Apr 7 | DPU SmartSwitch |
| 4 | sonic-net/sonic-mgmt | [#22864](https://github.com/sonic-net/sonic-mgmt/pull/22864) | [smartswitch]: Fix IndexError in dpuhosts access for DPU platform tests | Apr 7 | DPU SmartSwitch |
| 5 | sonic-net/sonic-swss-common | [#1162](https://github.com/sonic-net/sonic-swss-common/pull/1162) | Introduce keepalives for ZmqClient and ZmqServer | Apr 7 | DPU |
| 6 | sonic-net/sonic-mgmt | [#23632](https://github.com/sonic-net/sonic-mgmt/pull/23632) | [DASH] Test NVGRE encapsulation for FNIC scenario | Apr 7 | DASH |
| 7 | sonic-net/sonic-platform-common | [#652](https://github.com/sonic-net/sonic-platform-common/pull/652) | [Smartswitch] Fix device base path for platform file | Apr 7 | SmartSwitch |
| 8 | sonic-net/sonic-mgmt | [#23654](https://github.com/sonic-net/sonic-mgmt/pull/23654) | [202511] Cherry-pick HA core infrastructure | Apr 7 | DASH SmartSwitch |
| 9 | sonic-net/sonic-dash-ha | [#146](https://github.com/sonic-net/sonic-dash-ha/pull/146) | Add a dedicated always-on logging file for hamgrd | Apr 7 | DASH |
| 10 | sonic-net/sonic-swss | [#4232](https://github.com/sonic-net/sonic-swss/pull/4232) | [DPU] Add support for HA Set Counters | Apr 7 | DPU |
| 11 | sonic-net/sonic-utilities | [#4407](https://github.com/sonic-net/sonic-utilities/pull/4407) | Enable express boot support for Marvell Teralynx platform | Apr 8 | DASH |
| 12 | sonic-net/sonic-swss-common | [#1170](https://github.com/sonic-net/sonic-swss-common/pull/1170) | [202511]: Introduce keepalives for ZmqClient and ZmqServer | Apr 8 | DPU |
| 13 | sonic-net/sonic-buildimage | [#26592](https://github.com/sonic-net/sonic-buildimage/pull/26592) | [Mellanox][202511] Fix get component versions script to fetch correct asic fw | Apr 8 | DPU SmartSwitch |
| 14 | sonic-net/sonic-buildimage | [#26406](https://github.com/sonic-net/sonic-buildimage/pull/26406) | [yang][ssw] add dpu_vnet and dpu_vnet to global config table, allow underscore in dpu name, change main_dpu_ids to string | Apr 8 | DPU SmartSwitch |
| 15 | sonic-net/sonic-mgmt | [#23220](https://github.com/sonic-net/sonic-mgmt/pull/23220) | [HA] [smartswitch] implement module 8 of the HA testplan | Apr 9 | SmartSwitch |
| 16 | sonic-net/sonic-mgmt | [#23165](https://github.com/sonic-net/sonic-mgmt/pull/23165) | [SmartSwitch] Fix test issues in dash smartswitch vnet test | Apr 9 | DASH SmartSwitch |
| 17 | sonic-net/sonic-mgmt | [#23559](https://github.com/sonic-net/sonic-mgmt/pull/23559) | Tag the Set default dut index step to always run to cover the separate DPU minigraph case | Apr 9 | DPU SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#23653](https://github.com/sonic-net/sonic-mgmt/pull/23653) | [202511] Cherry-pick gNOI framework + smartswitch reboot tests | Apr 9 | DPU SmartSwitch |
| 19 | sonic-net/sonic-sairedis | [#1836](https://github.com/sonic-net/sonic-sairedis/pull/1836) | [syncd]: Clean up ENI counter entries from COUNTERS_DB on ENI deletion | Apr 9 | DASH |
| 20 | sonic-net/sonic-mgmt | [#23781](https://github.com/sonic-net/sonic-mgmt/pull/23781) | [202511] copp: fix missing is_smartswitch_light_mode init in ControlPlaneBaseTest | Apr 10 | SmartSwitch |
| 21 | sonic-net/sonic-sairedis | [#1838](https://github.com/sonic-net/sonic-sairedis/pull/1838) | [202511] Update SAI to v1.17.5 | Apr 10 | DASH |
| 22 | sonic-net/sonic-mgmt | [#23801](https://github.com/sonic-net/sonic-mgmt/pull/23801) | [202511] Cherry-pick DASH Privatelink + FNIC improvements | Apr 10 | DASH DPU SmartSwitch |
| 23 | sonic-net/sonic-mgmt | [#23655](https://github.com/sonic-net/sonic-mgmt/pull/23655) | [202511] Cherry-pick conditional marks + HA planned shutdown tests | Apr 10 | SmartSwitch |
| 24 | sonic-net/SONiC | [#2168](https://github.com/sonic-net/SONiC/pull/2168) | [smart switch] Add Flow Dump to HA HLD | Apr 10 | DPU SmartSwitch Smart |
| 25 | sonic-net/sonic-mgmt | [#23804](https://github.com/sonic-net/sonic-mgmt/pull/23804) | Add new fields in DASH_HA_GLOBAL_CONFIG | Apr 10 | - |
| 26 | sonic-net/sonic-mgmt | [#23797](https://github.com/sonic-net/sonic-mgmt/pull/23797) | [HA][smartswitch] update HA module 8 based on latest fixtures from conftest | Apr 10 | SmartSwitch |
| 27 | sonic-net/sonic-buildimage | [#26251](https://github.com/sonic-net/sonic-buildimage/pull/26251) | [SmartSwitch] [Mellanox] Ignore PCI sensors when DPU is power off | Apr 10 | DPU SmartSwitch |
| 28 | sonic-net/sonic-mgmt | [#23829](https://github.com/sonic-net/sonic-mgmt/pull/23829) | Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests" | Apr 11 | SmartSwitch |
| 29 | sonic-net/sonic-mgmt | [#23605](https://github.com/sonic-net/sonic-mgmt/pull/23605) | [ssw] move VDPU, DPU, REMOTE_DPU, VXLAN_TUNNEL, VNET generation from test fixture to golden config gen | Apr 13 | DPU SmartSwitch |
| 30 | sonic-net/sonic-sairedis | [#1840](https://github.com/sonic-net/sonic-sairedis/pull/1840) | [SmartSwitch] [DPU] Support maximum dash configuration size | Apr 14 | DASH DPU SmartSwitch |
| 31 | sonic-net/sonic-mgmt | [#23875](https://github.com/sonic-net/sonic-mgmt/pull/23875) | Revert "Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests"" | Apr 14 | SmartSwitch |
| 32 | sonic-net/sonic-host-services | [#359](https://github.com/sonic-net/sonic-host-services/pull/359) | [python tests] Fix determine-reboot-cause_test.py importing module sonic_platform | Apr 15 | - |
| 33 | sonic-net/sonic-mgmt | [#22699](https://github.com/sonic-net/sonic-mgmt/pull/22699) | [SmartSwitch] Update the get_mgmt_ip for DPU | Apr 15 | DPU SmartSwitch |
| 34 | sonic-net/sonic-mgmt | [#23835](https://github.com/sonic-net/sonic-mgmt/pull/23835) | DPUs: Include disk type 'MMC' for dpu ssdhealth check . Also fix for PR: 23641  | Apr 15 | DPU SmartSwitch |
| 35 | sonic-net/sonic-mgmt | [#23478](https://github.com/sonic-net/sonic-mgmt/pull/23478) | [devutil]: Add pmon readiness check and refactor DPU NAT utilities | Apr 15 | DPU SmartSwitch |
| 36 | sonic-net/sonic-mgmt | [#23920](https://github.com/sonic-net/sonic-mgmt/pull/23920) | [DASH] Fixes for FNIC and metering tests | Apr 15 | DASH DPU SmartSwitch |
| 37 | sonic-net/sonic-swss | [#4425](https://github.com/sonic-net/sonic-swss/pull/4425) | [DASH] Read inbound routing priority from ROUTE_RULE_TABLE key | Apr 15 | DASH |
| 38 | sonic-net/sonic-mgmt | [#23964](https://github.com/sonic-net/sonic-mgmt/pull/23964) | Enhance DASH-HA Private Link Steady State test | Apr 16 | DASH |
| 39 | sonic-net/sonic-buildimage | [#26335](https://github.com/sonic-net/sonic-buildimage/pull/26335) | [Smartswitch][Mellanox] Added additional logging to improve pci scan time record | Apr 16 | DPU SmartSwitch |
| 40 | sonic-net/sonic-buildimage | [#26333](https://github.com/sonic-net/sonic-buildimage/pull/26333) | [Mellanox][SmartSwitch] Add retry mechanism for sysfs read | Apr 16 | SmartSwitch |
| 41 | sonic-net/sonic-buildimage | [#26331](https://github.com/sonic-net/sonic-buildimage/pull/26331) | [Mellanox] Update mft build flow to support kernel-mft-dkms new version naming format. | Apr 16 | DASH |
| 42 | sonic-net/sonic-sairedis | [#1848](https://github.com/sonic-net/sonic-sairedis/pull/1848) | [syncd]: Fall back to TCP connection when unix socket path is not defined | Apr 16 | DPU |
| 43 | sonic-net/sonic-swss | [#4452](https://github.com/sonic-net/sonic-swss/pull/4452) | [npu-driven][ssw][ha] instead of waiting for ha state change event, immediately update dpu_state_db and in-memory ha state, and create bfd software sessions accordingly | Apr 16 | DPU SmartSwitch |
| 44 | sonic-net/sonic-swss-common | [#1177](https://github.com/sonic-net/sonic-swss-common/pull/1177) | [dash] Add COUNTERS_ENI_OID_MAP table name to schema.h | Apr 17 | DASH |
| 45 | sonic-net/sonic-mgmt | [#23933](https://github.com/sonic-net/sonic-mgmt/pull/23933) | chore: get_dut_version add dpu smart switch support | Apr 17 | DPU SmartSwitch Smart |
| 46 | sonic-net/sonic-mgmt | [#23957](https://github.com/sonic-net/sonic-mgmt/pull/23957) | [HA][smartswitch] HA test module 3 BFD pinning | Apr 17 | SmartSwitch |
| 47 | sonic-net/sonic-mgmt | [#22918](https://github.com/sonic-net/sonic-mgmt/pull/22918) | [HA] [smartswitch] Module 7 HA DPU power down and NPU reboot tests | Apr 17 | DPU SmartSwitch |
| 48 | sonic-net/SONiC | [#2180](https://github.com/sonic-net/SONiC/pull/2180) | Update SmartSwitch HA HLD | Apr 17 | DASH SmartSwitch |
| 49 | sonic-net/sonic-swss | [#4218](https://github.com/sonic-net/sonic-swss/pull/4218) | [DPU] [HA] Add support for Flow API | Apr 17 | DPU |
| 50 | sonic-net/sonic-buildimage | [#26868](https://github.com/sonic-net/sonic-buildimage/pull/26868) | [build][202505] Update apt source list to azure mirror in docker dash-engine | Apr 20 | DASH |
| 51 | sonic-net/sonic-mgmt | [#22982](https://github.com/sonic-net/sonic-mgmt/pull/22982) | Feature/ha module6 critical process crash | Apr 20 | DASH DPU SmartSwitch |
| 52 | sonic-net/sonic-mgmt | [#23747](https://github.com/sonic-net/sonic-mgmt/pull/23747) | Add skip conditions for HA DPU and NPU process crash tests | Apr 20 | DPU SmartSwitch |
| 53 | sonic-net/sonic-buildimage | [#26762](https://github.com/sonic-net/sonic-buildimage/pull/26762) | [database]: Skip CONFIG_DB_INITIALIZED writes for DPU database instances | Apr 20 | DPU SmartSwitch |
| 54 | sonic-net/sonic-buildimage | [#26587](https://github.com/sonic-net/sonic-buildimage/pull/26587) | sonic-yang-models: Add meaningful descriptions to YANG models | Apr 20 | DASH Smart |
| 55 | sonic-net/sonic-mgmt | [#24084](https://github.com/sonic-net/sonic-mgmt/pull/24084) | [critical_services] Exclude snmp from tracking list on BMC topology | Apr 21 | DPU |
| 56 | sonic-net/sonic-buildimage | [#25563](https://github.com/sonic-net/sonic-buildimage/pull/25563) | [DPU] Add YANG model support for HA Set Counters | Apr 21 | DASH DPU |
| 57 | sonic-net/sonic-mgmt | [#24006](https://github.com/sonic-net/sonic-mgmt/pull/24006) | moved test_reboot_cause to test_reload_dpu.py | Apr 22 | DPU SmartSwitch |
| 58 | sonic-net/sonic-platform-daemons | [#789](https://github.com/sonic-net/sonic-platform-daemons/pull/789) | Speed up execution of thermalctld unit tests | Apr 22 | - |
| 59 | sonic-net/sonic-buildimage | [#26765](https://github.com/sonic-net/sonic-buildimage/pull/26765) | Add extra logging directory mapping for dash-ha container | Apr 22 | DASH SmartSwitch |
| 60 | sonic-net/sonic-sairedis | [#1844](https://github.com/sonic-net/sonic-sairedis/pull/1844) | [meta] Populate object_statuses on bulk validation failure; DASH entries use ITEM_NOT_FOUND for missing keys | Apr 23 | DASH |
| 61 | sonic-net/sonic-mgmt | [#20411](https://github.com/sonic-net/sonic-mgmt/pull/20411) | Adding scale tests for per vnet bgp | Apr 24 | SmartSwitch |
| 62 | sonic-net/sonic-utilities | [#4472](https://github.com/sonic-net/sonic-utilities/pull/4472) | Fix Pensando DPU reboot handling in smartswitch operations | Apr 24 | DPU SmartSwitch |
| 63 | sonic-net/sonic-buildimage | [#26878](https://github.com/sonic-net/sonic-buildimage/pull/26878) | Fix kea-dhcp4 startup failure after trixie upgrade | Apr 24 | - |
| 64 | sonic-net/sonic-swss | [#4468](https://github.com/sonic-net/sonic-swss/pull/4468) | [dash]: Fix bulk remove post-processing for inbound/outbound routing entries | Apr 24 | DASH |
| 65 | sonic-net/sonic-mgmt | [#23545](https://github.com/sonic-net/sonic-mgmt/pull/23545) | Add error ignore in fpga update | Apr 26 | - |
| 66 | sonic-net/sonic-mgmt | [#24015](https://github.com/sonic-net/sonic-mgmt/pull/24015) | [SmartSwitch] Update the auto techsupport test for DPU | Apr 26 | DPU SmartSwitch |
| 67 | sonic-net/sonic-gnmi | [#643](https://github.com/sonic-net/sonic-gnmi/pull/643) | [SmartSwitch] Support maximum gnmi message size of 125k messages | Apr 27 | DASH SmartSwitch |
| 68 | sonic-net/sonic-mgmt | [#24005](https://github.com/sonic-net/sonic-mgmt/pull/24005) | Add smart switch full upgrade test all DPUs then reboot NPU | Apr 27 | DPU SmartSwitch Smart |
| 69 | sonic-net/sonic-buildimage | [#26614](https://github.com/sonic-net/sonic-buildimage/pull/26614) | [Smartswitch][Mellanox]Increase shutdown timeout for smartswitch | Apr 28 | DPU SmartSwitch |
| 70 | sonic-net/sonic-mgmt | [#24138](https://github.com/sonic-net/sonic-mgmt/pull/24138) | [HA][smartswitch] enable running HA tests with any DPU pair | Apr 28 | DPU SmartSwitch |
| 71 | sonic-net/sonic-dash-ha | [#156](https://github.com/sonic-net/sonic-dash-ha/pull/156) | Handling unplanned events in npu driven ha | Apr 28 | DPU |
| 72 | sonic-net/sonic-mgmt | [#24049](https://github.com/sonic-net/sonic-mgmt/pull/24049) | console servers: Skip warm and fast reboots for C0. | Apr 29 | SmartSwitch |
| 73 | sonic-net/sonic-dash-ha | [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) | Add support for new DPU pairing in-flight | Apr 29 | DPU |
| 74 | sonic-net/sonic-mgmt | [#24322](https://github.com/sonic-net/sonic-mgmt/pull/24322) | Refactor the activate_dash_ha_from_json fixture | Apr 30 | - |
| 75 | sonic-net/SONiC | [#2307](https://github.com/sonic-net/SONiC/pull/2307) | Update ssw ha hld | Apr 30 | - |
| 76 | sonic-net/sonic-buildimage | [#27110](https://github.com/sonic-net/sonic-buildimage/pull/27110) | [Security] temporarily remove vpp test from sonic-mgmt docker image build | May 1 | - |
| 77 | sonic-net/sonic-gnmi | [#660](https://github.com/sonic-net/sonic-gnmi/pull/660) | Add OS.Verify and OS.Activate to DPU proxy forwardable methods | May 1 | DPU SmartSwitch Smart |
| 78 | sonic-net/sonic-mgmt | [#23438](https://github.com/sonic-net/sonic-mgmt/pull/23438) | update _upgrade_one_dpu_via_gnoi to use perform_gnoi_reboot_dpu | May 1 | DPU SmartSwitch |
| 79 | sonic-net/sonic-buildimage | [#26933](https://github.com/sonic-net/sonic-buildimage/pull/26933) | [Smartswitch][Mellanox] Updated module to initialize without connector | May 4 | DPU SmartSwitch |
| 80 | sonic-net/sonic-buildimage | [#26871](https://github.com/sonic-net/sonic-buildimage/pull/26871) | [Mellanox][SmartSwitch] Convert sonic-bfb-installer.sh to python | May 4 | DPU SmartSwitch |
| 81 | sonic-net/sonic-mgmt | [#23518](https://github.com/sonic-net/sonic-mgmt/pull/23518) | Fix an issue in get_vlan_brief() | May 4 | SmartSwitch |
| 82 | sonic-net/sonic-mgmt | [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) | Add route rule for backend IP for PL redirect | May 4 | DPU |
| 83 | sonic-net/sonic-gnmi | [#663](https://github.com/sonic-net/sonic-gnmi/pull/663) | Add OS.Verify and OS.Activate DPU proxy forwarding | May 4 | DPU SmartSwitch |
| 84 | sonic-net/sonic-gnmi | [#662](https://github.com/sonic-net/sonic-gnmi/pull/662) | [202511] Fix too_many_pings + ARM64 CI + DPU proxy OS.Verify/Activate | May 5 | DPU |
| 85 | sonic-net/sonic-mgmt | [#24402](https://github.com/sonic-net/sonic-mgmt/pull/24402) | Filter out dpu DUT in duts_list for npu ha config. | May 5 | DPU |
| 86 | sonic-net/sonic-buildimage | [#26586](https://github.com/sonic-net/sonic-buildimage/pull/26586) | Added db migration logic to Pensando-Elba dpu | May 6 | DPU |
| 87 | sonic-net/sonic-buildimage | [#26475](https://github.com/sonic-net/sonic-buildimage/pull/26475) | [Mellanox] relocate udev-manager, add SN4280 mgmt PCI binding | May 6 | DPU SmartSwitch Smart |
| 88 | sonic-net/sonic-buildimage | [#26929](https://github.com/sonic-net/sonic-buildimage/pull/26929) | [Cherry-pick] [Nvidia]: relocate udev-manager, add SN4280 mgmt PCI binding (#26475) | May 6 | DPU SmartSwitch Smart |
| 89 | sonic-net/sonic-mgmt | [#24433](https://github.com/sonic-net/sonic-mgmt/pull/24433) | [qos]: Skip warm reboot on TH5 devices in DSCP queue mapping test | May 7 | SmartSwitch |
| 90 | sonic-net/sonic-dash-ha | [#158](https://github.com/sonic-net/sonic-dash-ha/pull/158) | Hardening ActorCreator | May 7 | DASH |
| 91 | sonic-net/sonic-dash-ha | [#160](https://github.com/sonic-net/sonic-dash-ha/pull/160) | Fix state machine for forced shutdown and planned shutdown | May 7 | DPU |
| 92 | sonic-net/sonic-buildimage | [#27118](https://github.com/sonic-net/sonic-buildimage/pull/27118) | [Mellanox][Nvidia-bluefield] Upgrade syncd containers to Trixie | May 7 | DPU |
| 93 | sonic-net/sonic-mgmt | [#24344](https://github.com/sonic-net/sonic-mgmt/pull/24344) | Update 'dash' test skip condition to run on smartswitch HWSKUs | May 8 | DASH SmartSwitch |
| 94 | sonic-net/sonic-mgmt | [#23211](https://github.com/sonic-net/sonic-mgmt/pull/23211) | Ignore expected error from DPU conosle minicom session disconnection. | May 8 | DPU |
| 95 | sonic-net/sonic-gnmi | [#664](https://github.com/sonic-net/sonic-gnmi/pull/664) | Add completeness test for DPU proxy ForwardToDPU handlers | May 8 | DPU |
| 96 | sonic-net/sonic-sairedis | [#1835](https://github.com/sonic-net/sonic-sairedis/pull/1835) | Runtime knob for Southbound ZMQ | May 8 | DPU |
| 97 | sonic-net/sonic-buildimage | [#27176](https://github.com/sonic-net/sonic-buildimage/pull/27176) | Remove unnecessary config-engine dependency from docker-dash-engine | May 11 | DASH |
| 98 | sonic-net/sonic-buildimage | [#27206](https://github.com/sonic-net/sonic-buildimage/pull/27206) | [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 11 | DPU |
| 99 | sonic-net/sonic-mgmt | [#24346](https://github.com/sonic-net/sonic-mgmt/pull/24346) | [HA][smartswitch] HA add flow compare to traffic tests | May 11 | SmartSwitch |
| 100 | sonic-net/sonic-buildimage | [#26549](https://github.com/sonic-net/sonic-buildimage/pull/26549) | [Mellanox] Fix MST service hang when DPUs are powered off | May 12 | DPU |
| 101 | sonic-net/sonic-swss | [#4558](https://github.com/sonic-net/sonic-swss/pull/4558) | [dashhaorch]: Remove DPU_STATE_DB entries upon DEL of HA_SET/HA_SCOPE | May 12 | - |
| 102 | sonic-net/sonic-mgmt | [#24566](https://github.com/sonic-net/sonic-mgmt/pull/24566) | [HA] [smartswitch] limit the DPU parameters used by HA tests to first 2 | May 12 | DASH DPU SmartSwitch |
| 103 | sonic-net/sonic-mgmt | [#24488](https://github.com/sonic-net/sonic-mgmt/pull/24488) | [HA][dash] Add Flow comparison support using Flow API | May 13 | DASH DPU |
| 104 | sonic-net/sonic-mgmt | [#24176](https://github.com/sonic-net/sonic-mgmt/pull/24176) | [HA][smartswitch] Ha test module9 | May 13 | DPU SmartSwitch |

---

## Key Development Areas

1. **SmartSwitch HA maturity in sonic-mgmt**: sustained module/test additions and topology hardening across HA and reboot scenarios.
2. **DPU lifecycle and platform reliability in sonic-buildimage**: firmware/container updates and platform behavior fixes remained high-volume.
3. **DASH data path and state handling in sonic-swss / sonic-sairedis / sonic-gnmi**: ENI counter/OID mapping, HA state updates, and ZMQ path improvements.
4. **Cross-repo execution**: 125 created and 104 merged PRs over 37 days across 13 repos indicates broad, sustained engineering throughput.

---

## Community Meeting Notes (Applied Where Applicable)

> ⚠️ **Note:** The following section is derived from AI-generated meeting recap notes and mapped to this date range where matching PR evidence exists.

| Topic from Meeting Notes | Applicability in Apr 7 – May 13 Data | Evidence in This Report |
|---|---|---|
| Backend IP route rule for PL redirect | **Applicable** | sonic-mgmt [#24181](https://github.com/sonic-net/sonic-mgmt/pull/24181) (created Apr 24, merged May 4) |
| Smart Switch HA HLD update | **Applicable** | SONiC [#2307](https://github.com/sonic-net/SONiC/pull/2307) merged Apr 30 |
| DPU pairing support update | **Applicable** | sonic-dash-ha [#157](https://github.com/sonic-net/sonic-dash-ha/pull/157) merged Apr 29 |
| Floating NIC steady-state/planned-shutdown test | **Applicable** | sonic-mgmt [#24376](https://github.com/sonic-net/sonic-mgmt/pull/24376) created May 4 |
| gNMI-ZMQ management VRF test path | **Applicable** | sonic-mgmt [#24412](https://github.com/sonic-net/sonic-mgmt/pull/24412) created May 5 |
| ENI OID mapping + DPU counter/virtual path handling | **Applicable** | sonic-swss [#4540](https://github.com/sonic-net/sonic-swss/pull/4540), sonic-gnmi [#665](https://github.com/sonic-net/sonic-gnmi/pull/665) |
| ZMQ socket timeout reset fix | **Applicable** | sonic-sairedis [#1881](https://github.com/sonic-net/sonic-sairedis/pull/1881) created May 1 |
| gNMI client placement in sonic-management docker | **Partially applicable (discussion/planning)** | No single merged placement PR clearly identified in this window; keep as follow-up track item |
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
- Continue weekly triage of high-volume sonic-mgmt and sonic-buildimage PR queues to keep merge latency controlled.
- Track meeting follow-up items explicitly on the project board (gNMI client placement, routing examples, walkthrough/onboarding).

### Medium Priority
- Add explicit labels for HA module phase and SmartSwitch platform-specific changes to improve board classification and reporting.
- Keep validating ZMQ and DPU proxy path reliability as GNMI and SAI redis changes continue to land.

---

## Metrics Summary

| Metric | Value |
|---|---:|
| Date Range | Apr 7 – May 13, 2026 (37 days) |
| PRs Created | 125 |
| PRs Merged | 104 |
| Active Repositories | 13 |
| Creation Velocity | 3.4 PRs/day |
| Merge Velocity | 2.8 PRs/day |
| Merge Rate | 83.2% |

---

## Conclusion

The period of **April 7 – May 13, 2026** shows **very high development throughput**: 125 PRs created and 104 merged across 13 repositories. Work remained concentrated in sonic-mgmt and sonic-buildimage while substantial changes continued in sonic-gnmi, sonic-swss, sonic-sairedis, and sonic-dash-ha.

Meeting recap items were integrated where PR evidence exists in this window (HA HLD, backend IP route rule, FNIC and ZMQ test-path additions, ENI/DPU counter work, and ZMQ timeout handling). Remaining meeting actions are captured as planning tracks for follow-up in subsequent reports.

---

*Queries used to generate this report:*
```
org:sonic-net is:pr is:merged merged:2026-04-07..2026-05-13 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title

org:sonic-net is:pr created:2026-04-07..2026-05-13 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```