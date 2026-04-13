# DASH/DPU/SmartSwitch Weekly Review
**Period:** March 26 – April 8, 2026 (14 days)
**Report Generated:** April 13, 2026
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **March 26 – April 8, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **54 PRs Created** during the period
- **35 PRs Merged** during the period
- **12 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Merge Rate:** 64.8% (35 merged out of 54 created)
- **Creation Velocity:** 3.9 PRs/day
- **Primary Focus Areas:** SmartSwitch HA infrastructure, DPU management tooling, DASH feature development, platform support

### Highlights
- Major HA cherry-pick batch landing in sonic-mgmt (202511 branch stabilization)
- DPU tooling improvements: single DPU config, factory default, gNOI reboot
- New DASH test scenarios: NVGRE encapsulation, CRM, Private Link, FNIC
- ZMQ keepalives for SmartSwitch reliability (sonic-swss-common)
- DPU HA Set Counters support added to sonic-swss
- AMD Elba DPU database migration logic added
- Platform fixes for Mellanox MST service hang and BFB installation

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during March 26 – April 8, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 166 | 569 | 523 | 20 PRs merged + 31 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 1,384 | 2,081 | 4,085 | 6 PRs merged + 7 PRs created | 🟢 High |
| sonic-net/sonic-sairedis | 142 | 408 | 208 | 0 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/sonic-gnmi | 46 | 95 | 28 | 1 PR merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss-common | 98 | 328 | 147 | 2 PRs merged + 1 PR created | 🟡 Moderate |
| sonic-net/sonic-platform-common | 18 | 57 | 30 | 2 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-utilities | 200 | 573 | 365 | 2 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss | 458 | 1,345 | 1,168 | 1 PR merged + 2 PRs created | 🟡 Moderate |
| sonic-net/SONiC | 2,300 | 1,100 | 65 | 0 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-dash-ha | 2 | 4 | 3 | 1 PR merged + 0 PRs created | 🟡 Low |
| sonic-net/sonic-host-services | 13 | 36 | 15 | 0 PRs merged + 1 PR created | 🟡 Low |
| sonic-net/sonic-platform-daemons | 11 | 32 | 50 | 0 PRs merged + 1 PR created | 🟡 Low |

**Note:** Repositories included only if they have PRs with DASH/DPU/SmartSwitch/Smart keywords in title or body during the query period.

---

## PRs Created (March 26 – April 8, 2026)

### Summary
- **Total:** 54 PRs
- **Top Repository:** sonic-mgmt (31 PRs)
- **Key Themes:** SmartSwitch HA cherry-picks, DPU management tooling, DASH testing, gNOI framework, platform improvements

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-mgmt | [#23456](https://github.com/sonic-net/sonic-mgmt/pull/23456) | [Smartswitch] [DPU] DASH Fastpath feature testcases | Mar 31 | SmartSwitch, DPU, DASH |
| 2 | sonic-buildimage | [#26614](https://github.com/sonic-net/sonic-buildimage/pull/26614) | [Smartswitch][Mellanox]Increase shutdown timeout for smartswitch | Apr 7 | SmartSwitch |
| 3 | sonic-mgmt | [#23747](https://github.com/sonic-net/sonic-mgmt/pull/23747) | Add skip conditions for HA DPU and NPU process crash tests | Apr 8 | DPU, DASH |
| 4 | sonic-mgmt | [#23478](https://github.com/sonic-net/sonic-mgmt/pull/23478) | [devutil]: Add pmon readiness check and refactor DPU NAT utilities | Mar 31 | DPU |
| 5 | sonic-mgmt | [#23656](https://github.com/sonic-net/sonic-mgmt/pull/23656) | HA privatelink support when running snappi_tests | Apr 6 | DASH |
| 6 | sonic-buildimage | [#26475](https://github.com/sonic-net/sonic-buildimage/pull/26475) | [Nvidia] relocate udev-manager, add SN4280 mgmt PCI binding | Mar 30 | Smart |
| 7 | sonic-mgmt | [#23438](https://github.com/sonic-net/sonic-mgmt/pull/23438) | update _upgrade_one_dpu_via_gnoi to use perform_gnoi_reboot_dpu | Mar 30 | DPU |
| 8 | sonic-mgmt | [#23650](https://github.com/sonic-net/sonic-mgmt/pull/23650) | smartswitch: migrate test_cold_reboot_dpus to use gnmi_tls fixture | Apr 6 | SmartSwitch, DPU |
| 9 | sonic-host-services | [#367](https://github.com/sonic-net/sonic-host-services/pull/367) | Replace docker exec gnoi_client with native Python gRPC calls | Mar 30 | Smart |
| 10 | sonic-mgmt | [#23727](https://github.com/sonic-net/sonic-mgmt/pull/23727) | Add a new testcase test_dash_smartswitch_crm | Apr 8 | DASH, SmartSwitch |
| 11 | sonic-mgmt | [#23345](https://github.com/sonic-net/sonic-mgmt/pull/23345) | [conditional_mark] Skip features and scripts on lossy topologies | Mar 26 | Smart |
| 12 | sonic-mgmt | [#23518](https://github.com/sonic-net/sonic-mgmt/pull/23518) | Fix an issue in get_vlan_brief() | Apr 1 | Smart |
| 13 | sonic-mgmt | [#23654](https://github.com/sonic-net/sonic-mgmt/pull/23654) | [202511] Cherry-pick HA core infrastructure | Apr 6 | DASH, SmartSwitch |
| 14 | SONiC | [#2282](https://github.com/sonic-net/SONiC/pull/2282) | Adding a draft version of smartswitch system-health HLD | Apr 2 | SmartSwitch |
| 15 | sonic-gnmi | [#634](https://github.com/sonic-net/sonic-gnmi/pull/634) | Fix too_many_pings during DPU SetPackage and add ARM64 CI build | Mar 31 | DPU |
| 16 | sonic-mgmt | [#23605](https://github.com/sonic-net/sonic-mgmt/pull/23605) | [ssw] move VDPU, DPU, REMOTE_DPU, VXLAN_TUNNEL, VNET generation from test fixture | Apr 3 | DPU, ssw |
| 17 | sonic-swss | [#4452](https://github.com/sonic-net/sonic-swss/pull/4452) | [npu-driven][ssw][ha] instead of waiting for ha state change event, immediately | Apr 7 | DASH, ssw |
| 18 | sonic-mgmt | [#23569](https://github.com/sonic-net/sonic-mgmt/pull/23569) | Inner-src mac rewrite 9k scale test | Apr 2 | Smart |
| 19 | sonic-mgmt | [#23352](https://github.com/sonic-net/sonic-mgmt/pull/23352) | [DASH] Use VLAN intf for DPU dataplane intf when available | Mar 26 | DASH, DPU |
| 20 | sonic-buildimage | [#26586](https://github.com/sonic-net/sonic-buildimage/pull/26586) | Added db migration logic to Pensando-Elba dpu | Apr 6 | DPU |
| 21 | sonic-mgmt | [#23653](https://github.com/sonic-net/sonic-mgmt/pull/23653) | [202511] Cherry-pick gNOI framework + smartswitch reboot tests | Apr 6 | SmartSwitch |
| 22 | sonic-buildimage | [#26549](https://github.com/sonic-net/sonic-buildimage/pull/26549) | [Mellanox] Fix MST service hang when DPUs are powered off | Apr 3 | DPU |
| 23 | sonic-mgmt | [#23472](https://github.com/sonic-net/sonic-mgmt/pull/23472) | [HA] [smartswitch] call the flow compare utility | Mar 31 | SmartSwitch, DASH |
| 24 | sonic-mgmt | [#23748](https://github.com/sonic-net/sonic-mgmt/pull/23748) | Bug fix: add extra sleep before startup DPU to avoid deadlock | Apr 8 | DPU |
| 25 | sonic-sairedis | [#1819](https://github.com/sonic-net/sonic-sairedis/pull/1819) | Enable async ASIC_DB writes for Southbound-ZMQ | Mar 27 | Smart |
| 26 | sonic-mgmt | [#23559](https://github.com/sonic-net/sonic-mgmt/pull/23559) | Tag the Set default dut index step to always run to cover the separate DPU minigrph | Apr 2 | DPU |
| 27 | sonic-gnmi | [#637](https://github.com/sonic-net/sonic-gnmi/pull/637) | Improve DPU file transfer throughput and reliability | Apr 1 | DPU |
| 28 | sonic-mgmt | [#23360](https://github.com/sonic-net/sonic-mgmt/pull/23360) | [ssw] adding tooling to config one single DPU | Mar 26 | DPU, ssw |
| 29 | sonic-mgmt | [#23387](https://github.com/sonic-net/sonic-mgmt/pull/23387) | Feature: add MMC to supported disk, skip psustatus check on DPU | Mar 27 | DPU |
| 30 | sonic-platform-daemons | [#789](https://github.com/sonic-net/sonic-platform-daemons/pull/789) | Speed up execution of thermalctld unit tests | Apr 7 | Smart |
| 31 | sonic-mgmt | [#23329](https://github.com/sonic-net/sonic-mgmt/pull/23329) | [SmartSwitch] [HA] disable northbound route zmq flag for ha topology | Mar 26 | SmartSwitch, DASH |
| 32 | sonic-buildimage | [#26592](https://github.com/sonic-net/sonic-buildimage/pull/26592) | [Mellanox][202511] Fix get component versions script to fetch correct asic fw | Apr 6 | Smart |
| 33 | sonic-mgmt | [#23545](https://github.com/sonic-net/sonic-mgmt/pull/23545) | Add error ignore in fpga update | Apr 2 | Smart |
| 34 | SONiC | [#2279](https://github.com/sonic-net/SONiC/pull/2279) | HLD for Southbound ZMQ | Apr 2 | Smart |
| 35 | sonic-buildimage | [#26587](https://github.com/sonic-net/sonic-buildimage/pull/26587) | sonic-yang-models: Add meaningful descriptions to YANG models | Apr 6 | Smart |
| 36 | sonic-platform-common | [#652](https://github.com/sonic-net/sonic-platform-common/pull/652) | [Smartswitch] Fix device base path for platform file | Apr 7 | SmartSwitch |
| 37 | sonic-mgmt | [#23596](https://github.com/sonic-net/sonic-mgmt/pull/23596) | [HA][smartswitch] HA reconfigure test | Apr 3 | SmartSwitch, DASH |
| 38 | sonic-buildimage | [#26473](https://github.com/sonic-net/sonic-buildimage/pull/26473) | [sonic-py-common] Add gRPC framework with gNOI client | Mar 30 | Smart |
| 39 | sonic-swss | [#4425](https://github.com/sonic-net/sonic-swss/pull/4425) | [DASH] Read inbound routing priority from ROUTE_RULE_TABLE key | Apr 1 | DASH |
| 40 | sonic-platform-common | [#649](https://github.com/sonic-net/sonic-platform-common/pull/649) | [module_base]: Fix nested lock deadlock in get_module_state_transition | Apr 2 | Smart |
| 41 | sonic-mgmt | [#23528](https://github.com/sonic-net/sonic-mgmt/pull/23528) | [HA][smartswitch] add the HA reconfigure test | Apr 1 | SmartSwitch, DASH |
| 42 | sonic-utilities | [#4405](https://github.com/sonic-net/sonic-utilities/pull/4405) | [config reload] Skip routeCheck monit calls on DPU platforms | Mar 31 | DPU |
| 43 | sonic-mgmt | [#23417](https://github.com/sonic-net/sonic-mgmt/pull/23417) | [gnmi] Add retry logic to test_gnmi_appldb_01 gNMI GET operations | Mar 30 | Smart |
| 44 | sonic-mgmt | [#23403](https://github.com/sonic-net/sonic-mgmt/pull/23403) | copp: fix DHCPTopoT1Test/DHCP6TopoT1Test false failure from background traffic | Mar 30 | Smart |
| 45 | sonic-swss-common | [#1170](https://github.com/sonic-net/sonic-swss-common/pull/1170) | [202511]: Introduce keepalives for ZmqClient and ZmqServer | Mar 31 | Smart |
| 46 | sonic-mgmt | [#23655](https://github.com/sonic-net/sonic-mgmt/pull/23655) | [202511] Cherry-pick conditional marks + HA planned shutdown tests | Apr 6 | DASH, SmartSwitch |
| 47 | sonic-mgmt | [#23711](https://github.com/sonic-net/sonic-mgmt/pull/23711) | fix pre/post tests errors in run_tests.sh | Apr 8 | Smart |
| 48 | sonic-mgmt | [#23632](https://github.com/sonic-net/sonic-mgmt/pull/23632) | [DASH] Test NVGRE encapsulation for FNIC scenario | Apr 3 | DASH |
| 49 | sonic-mgmt | [#23514](https://github.com/sonic-net/sonic-mgmt/pull/23514) | Fix default_pfcwd_status KeyError in pfcwd_feature_enabled() when zebra_nexthop_t | Apr 1 | Smart |
| 50 | sonic-mgmt | [#23364](https://github.com/sonic-net/sonic-mgmt/pull/23364) | [DASH] Match VM_VNI to VNET_VNI | Mar 26 | DASH |
| 51 | sonic-sairedis | [#1836](https://github.com/sonic-net/sonic-sairedis/pull/1836) | [syncd]: Clean up ENI counter entries from COUNTERS_DB on ENI deletion | Apr 7 | DASH |
| 52 | sonic-mgmt | [#23361](https://github.com/sonic-net/sonic-mgmt/pull/23361) | [vm_set]: Add fallback default for VM_targets when VMs are not required | Mar 26 | Smart |
| 53 | sonic-sairedis | [#1838](https://github.com/sonic-net/sonic-sairedis/pull/1838) | [202511] Update SAI to v1.17.5 | Apr 8 | Smart |
| 54 | sonic-utilities | [#4407](https://github.com/sonic-net/sonic-utilities/pull/4407) | Enable express boot support for Marvell Teralynx platform | Mar 31 | Smart |

---

## PRs Merged (March 26 – April 8, 2026)

### Summary
- **Total:** 35 PRs
- **Top Repository:** sonic-mgmt (20 PRs merged)
- **Key Themes:** SmartSwitch HA infrastructure, DPU platform management, DASH feature completion, ZMQ reliability

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-mgmt | [#23654](https://github.com/sonic-net/sonic-mgmt/pull/23654) | [202511] Cherry-pick HA core infrastructure | Apr 7 | DASH, SmartSwitch |
| 2 | sonic-mgmt | [#23323](https://github.com/sonic-net/sonic-mgmt/pull/23323) | [smartswitch] fix the errors from command execution on DPU | Mar 26 | SmartSwitch, DPU |
| 3 | sonic-gnmi | [#634](https://github.com/sonic-net/sonic-gnmi/pull/634) | Fix too_many_pings during DPU SetPackage and add ARM64 CI build | Apr 2 | DPU |
| 4 | sonic-mgmt | [#23177](https://github.com/sonic-net/sonic-mgmt/pull/23177) | Treating the return values separately from log perform reboot | Apr 1 | Smart |
| 5 | sonic-mgmt | [#23352](https://github.com/sonic-net/sonic-mgmt/pull/23352) | [DASH] Use VLAN intf for DPU dataplane intf when available | Mar 30 | DASH, DPU |
| 6 | sonic-buildimage | [#26334](https://github.com/sonic-net/sonic-buildimage/pull/26334) | [Smartswitch][Mellanox] Fix BFB installation based on waiting for chassisd retry | Apr 7 | SmartSwitch |
| 7 | sonic-mgmt | [#23472](https://github.com/sonic-net/sonic-mgmt/pull/23472) | [HA] [smartswitch] call the flow compare utility | Apr 6 | SmartSwitch, DASH |
| 8 | sonic-mgmt | [#22864](https://github.com/sonic-net/sonic-mgmt/pull/22864) | [smartswitch]: Fix IndexError in dpuhosts access for DPU platform tests | Apr 7 | SmartSwitch, DPU |
| 9 | sonic-buildimage | [#26406](https://github.com/sonic-net/sonic-buildimage/pull/26406) | [yang][ssw] add dpu_vnet and dpu_vnet to global config table, allow underscore | Apr 8 | DPU, ssw |
| 10 | sonic-mgmt | [#23360](https://github.com/sonic-net/sonic-mgmt/pull/23360) | [ssw] adding tooling to config one single DPU | Apr 3 | DPU, ssw |
| 11 | sonic-mgmt | [#23329](https://github.com/sonic-net/sonic-mgmt/pull/23329) | [SmartSwitch] [HA] disable northbound route zmq flag for ha topology | Mar 27 | SmartSwitch, DASH |
| 12 | sonic-buildimage | [#26592](https://github.com/sonic-net/sonic-buildimage/pull/26592) | [Mellanox][202511] Fix get component versions script to fetch correct asic fw | Apr 8 | Smart |
| 13 | sonic-mgmt | [#23048](https://github.com/sonic-net/sonic-mgmt/pull/23048) | [ssw] add port table and step to set dpu config to factory default | Apr 3 | DPU, ssw |
| 14 | sonic-buildimage | [#26348](https://github.com/sonic-net/sonic-buildimage/pull/26348) | [Mellanox] Fix get component versions script to fetch correct asic fw | Apr 7 | Smart |
| 15 | sonic-mgmt | [#23207](https://github.com/sonic-net/sonic-mgmt/pull/23207) | [SmartSwitch] Adding backward compatibility for feature "enable/disable vxlan spl" | Apr 1 | SmartSwitch |
| 16 | sonic-platform-common | [#652](https://github.com/sonic-net/sonic-platform-common/pull/652) | [Smartswitch] Fix device base path for platform file | Apr 7 | SmartSwitch |
| 17 | sonic-mgmt | [#23596](https://github.com/sonic-net/sonic-mgmt/pull/23596) | [HA][smartswitch] HA reconfigure test | Apr 7 | SmartSwitch, DASH |
| 18 | sonic-platform-common | [#649](https://github.com/sonic-net/sonic-platform-common/pull/649) | [module_base]: Fix nested lock deadlock in get_module_state_transition | Apr 6 | Smart |
| 19 | sonic-utilities | [#4405](https://github.com/sonic-net/sonic-utilities/pull/4405) | [config reload] Skip routeCheck monit calls on DPU platforms | Apr 1 | DPU |
| 20 | sonic-mgmt | [#23403](https://github.com/sonic-net/sonic-mgmt/pull/23403) | copp: fix DHCPTopoT1Test/DHCP6TopoT1Test false failure from background traffic | Apr 1 | Smart |
| 21 | sonic-swss-common | [#1170](https://github.com/sonic-net/sonic-swss-common/pull/1170) | [202511]: Introduce keepalives for ZmqClient and ZmqServer | Apr 8 | Smart |
| 22 | sonic-mgmt | [#23324](https://github.com/sonic-net/sonic-mgmt/pull/23324) | iface_namemode: add new port role of Dpc | Mar 27 | DPU |
| 23 | sonic-swss-common | [#1162](https://github.com/sonic-net/sonic-swss-common/pull/1162) | Introduce keepalives for ZmqClient and ZmqServer | Apr 7 | Smart |
| 24 | sonic-buildimage | [#26214](https://github.com/sonic-net/sonic-buildimage/pull/26214) | Disable routeCheck, dualtorNeighborCheck and vnetRouteCheck in monit config on DPU | Apr 1 | DPU |
| 25 | sonic-mgmt | [#22952](https://github.com/sonic-net/sonic-mgmt/pull/22952) | Remove generate_vlan_config from HA conftest | Mar 27 | DASH |
| 26 | sonic-buildimage | [#26234](https://github.com/sonic-net/sonic-buildimage/pull/26234) | Modified reboot pre-shutdown script to handle dpu side reboot | Apr 3 | DPU |
| 27 | sonic-swss | [#4232](https://github.com/sonic-net/sonic-swss/pull/4232) | [DPU] Add support for HA Set Counters | Apr 7 | DPU, DASH |
| 28 | sonic-mgmt | [#23632](https://github.com/sonic-net/sonic-mgmt/pull/23632) | [DASH] Test NVGRE encapsulation for FNIC scenario | Apr 7 | DASH |
| 29 | sonic-mgmt | [#23276](https://github.com/sonic-net/sonic-mgmt/pull/23276) | [DASH] Revert test_fnic name change | Apr 3 | DASH |
| 30 | sonic-mgmt | [#23514](https://github.com/sonic-net/sonic-mgmt/pull/23514) | Fix default_pfcwd_status KeyError in pfcwd_feature_enabled() when zebra_nexthop_t | Apr 2 | Smart |
| 31 | sonic-mgmt | [#23364](https://github.com/sonic-net/sonic-mgmt/pull/23364) | [DASH] Match VM_VNI to VNET_VNI | Mar 28 | DASH |
| 32 | sonic-mgmt | [#23361](https://github.com/sonic-net/sonic-mgmt/pull/23361) | [vm_set]: Add fallback default for VM_targets when VMs are not required | Mar 27 | Smart |
| 33 | sonic-mgmt | [#23199](https://github.com/sonic-net/sonic-mgmt/pull/23199) | [BMC] Add is_bmc() and get_bmc_host() SonicHost extensions | Mar 26 | Smart |
| 34 | sonic-dash-ha | [#146](https://github.com/sonic-net/sonic-dash-ha/pull/146) | Add a dedicated always-on logging file for hamgrd | Apr 7 | DASH |
| 35 | sonic-utilities | [#4407](https://github.com/sonic-net/sonic-utilities/pull/4407) | Enable express boot support for Marvell Teralynx platform | Apr 8 | Smart |

---

## Key Development Areas

### 1. SmartSwitch HA Infrastructure (10+ PRs)
**Focus:** Stabilizing HA functionality across branches, reconfigure testing, flow comparison

**Notable PRs:**
- **#23654** (sonic-mgmt): [202511] Cherry-pick HA core infrastructure (9 PRs backported)
- **#23653** (sonic-mgmt): [202511] Cherry-pick gNOI framework + smartswitch reboot tests
- **#23655** (sonic-mgmt): [202511] Cherry-pick conditional marks + HA planned shutdown tests
- **#23596** (sonic-mgmt): [HA][smartswitch] HA reconfigure test
- **#23472** (sonic-mgmt): [HA][smartswitch] call the flow compare utility
- **#23329** (sonic-mgmt): [SmartSwitch][HA] disable northbound route zmq flag for ha topology
- **#146** (sonic-dash-ha): Add a dedicated always-on logging file for hamgrd

**Impact:** Major branch stabilization effort for 202511 release, with core HA functionality now available on the release branch.

### 2. DPU Management Tooling (8+ PRs)
**Focus:** Improving DPU configuration, factory reset, gNOI-based management

**Notable PRs:**
- **#23048** (sonic-mgmt): [ssw] add port table and step to set dpu config to factory default
- **#23360** (sonic-mgmt): [ssw] adding tooling to config one single DPU
- **#23605** (sonic-mgmt): [ssw] move VDPU, DPU, REMOTE_DPU, VXLAN_TUNNEL, VNET generation
- **#23438** (sonic-mgmt): update _upgrade_one_dpu_via_gnoi to use perform_gnoi_reboot_dpu
- **#26406** (sonic-buildimage): [yang][ssw] add dpu_vnet to global config table
- **#26234** (sonic-buildimage): Modified reboot pre-shutdown script to handle DPU side reboot
- **#634** (sonic-gnmi): Fix too_many_pings during DPU SetPackage
- **#637** (sonic-gnmi): Improve DPU file transfer throughput and reliability

**Impact:** Significantly improves DPU lifecycle management, configuration and diagnostics capabilities.

### 3. DASH Feature Development (8+ PRs)
**Focus:** NVGRE encapsulation, route rules, VNI matching, CRM, Private Link

**Notable PRs:**
- **#23632** (sonic-mgmt): [DASH] Test NVGRE encapsulation for FNIC scenario
- **#23727** (sonic-mgmt): Add a new testcase test_dash_smartswitch_crm
- **#4425** (sonic-swss): [DASH] Read inbound routing priority from ROUTE_RULE_TABLE key
- **#4232** (sonic-swss): [DPU] Add support for HA Set Counters
- **#23364** (sonic-mgmt): [DASH] Match VM_VNI to VNET_VNI
- **#23352** (sonic-mgmt): [DASH] Use VLAN intf for DPU dataplane intf when available
- **#23656** (sonic-mgmt): HA privatelink support when running snappi_tests
- **#4452** (sonic-swss): [npu-driven][ssw][ha] immediate ha state handling

**Impact:** Expands DASH test coverage and feature completeness for production deployments.

### 4. ZMQ Reliability for SmartSwitch (3 PRs)
**Focus:** Keepalive support for ZmqClient and ZmqServer to prevent silent failures

**Notable PRs:**
- **#1162** (sonic-swss-common): Introduce keepalives for ZmqClient and ZmqServer
- **#1170** (sonic-swss-common): [202511] Introduce keepalives for ZmqClient and ZmqServer
- **#1819** (sonic-sairedis): Enable async ASIC_DB writes for Southbound-ZMQ
- **#2279** (SONiC): HLD for Southbound ZMQ (design document)

**Impact:** Improves reliability of SmartSwitch/DPU communication infrastructure and provides async DB write support.

### 5. Platform and Build Improvements (7+ PRs)
**Focus:** Mellanox MST fix, AMD Elba DPU DB migration, BFB installer, gRPC framework

**Notable PRs:**
- **#26549** (sonic-buildimage): [Mellanox] Fix MST service hang when DPUs are powered off
- **#26334** (sonic-buildimage): [Smartswitch][Mellanox] Fix BFB installation for chassisd retry
- **#26586** (sonic-buildimage): Added db migration logic to Pensando-Elba DPU
- **#26473** (sonic-buildimage): [sonic-py-common] Add gRPC framework with gNOI client
- **#26475** (sonic-buildimage): [Nvidia] relocate udev-manager, add SN4280 mgmt PCI binding
- **#1836** (sonic-sairedis): [syncd] Clean up ENI counter entries from COUNTERS_DB on ENI deletion
- **#2282** (SONiC): Adding a draft version of smartswitch system-health HLD

**Impact:** Resolves platform-specific issues and adds foundational infrastructure for new gRPC/gNOI capabilities.

---

## Activity Patterns

### Repository Distribution (PRs Created)
- **sonic-mgmt:** 31 PRs (57% of activity) – Primary test infrastructure repository
- **sonic-buildimage:** 7 PRs (13% of activity) – Build/platform integration
- **sonic-sairedis:** 3 PRs (6% of activity) – SAI/syncd layer
- **sonic-gnmi:** 2 PRs (4% of activity) – gNMI/gNOI management
- **sonic-swss:** 2 PRs (4% of activity) – Switch state services
- **sonic-platform-common:** 2 PRs (4% of activity) – Platform abstractions
- **sonic-utilities:** 2 PRs (4% of activity) – CLI/utilities
- **SONiC:** 2 PRs (4% of activity) – HLD/design documents
- **Other repos:** 3 PRs (5% of activity) – sonic-swss-common, sonic-host-services, sonic-platform-daemons

### Development Focus
1. **HA Branch Stabilization** – High priority with 202511 cherry-pick batch
2. **DPU Management** – Strong focus on tooling, gNOI, configuration management
3. **DASH Feature Completion** – Continued work on testing, VNI, routing, counters
4. **Infrastructure Reliability** – ZMQ keepalives, gRPC framework, DB migrations

### Weekly Distribution
| Week | PRs Created | PRs Merged |
|------|-------------|------------|
| Mar 26–Apr 1 | ~25 | ~14 |
| Apr 2–Apr 8  | ~29 | ~21 |

---

## Recommendations

### Short-term (Next 1–2 Weeks)
1. **Review open HA cherry-pick PRs** – Several 202511 cherry-picks landed; verify remaining backport coverage
2. **gNOI framework adoption** – New gRPC framework added; ensure sonic-host-services and sonic-gnmi updates are aligned
3. **DPU DB migration validation** – AMD Elba DB migration logic needs integration testing
4. **ZMQ keepalive rollout** – Verify keepalive behavior under SmartSwitch stress scenarios

### Medium-term (Next Month)
1. **SmartSwitch CRM testing** – New CRM testcase (#23727) needs end-to-end validation
2. **NVGRE FNIC production readiness** – Expand NVGRE encapsulation test coverage beyond FNIC
3. **Platform health HLD review** – Draft SmartSwitch system-health HLD (#2282) needs community feedback
4. **Southbound ZMQ design review** – HLD #2279 needs acceptance before implementation proceeds

### Long-term (Next Quarter)
1. **DASH HA production hardening** – Merge rate of 64.8% suggests items in flight; prioritize completion
2. **Multi-DPU platform support** – Work spans AMD Elba, Mellanox/Nvidia, Marvell; standardize abstractions
3. **gNOI adoption roadmap** – gRPC/gNOI framework emerging as management standard; plan full rollout
4. **Documentation** – Several HLDs in draft; ensure finalization before implementation scales

---

## Technical Insights

### 202511 Branch Stabilization
The period saw a concentrated effort to backport HA functionality to the 202511 release branch:
- **#23654**: HA core infrastructure (BFD, gNMI, state_db, conftest chain)
- **#23653**: gNOI framework + smartswitch reboot tests
- **#23655**: Conditional marks + HA planned shutdown tests
This indicates the 202511 release is actively being hardened for DASH/HA production use.

### DPU Management Maturity
Multiple DPU management improvements signal growing operational maturity:
- **Factory reset** – DPU config can now be reset to factory defaults via test framework
- **Single-DPU tooling** – Tools to configure one DPU independently from the full topology
- **gNOI-based reboot** – Standardizing DPU reboot via gNOI rather than platform-specific methods
- **DB cleanup** – Pensando-Elba DB migration and VDPU/DPU fixture refactoring

### DASH FNIC / NVGRE Progress
New test scenarios highlight expanding DASH deployment models:
- **NVGRE encapsulation for FNIC** – Extends DASH to Fiber Channel over IP scenarios
- **Private Link with snappi** – Traffic generator-based Private Link validation
- **CRM for SmartSwitch** – Critical Resource Monitoring extended to DPU/DASH contexts

---

## Conclusion

The period of **March 26 – April 8, 2026** showed **high activity** with 54 PRs created and 35 PRs merged across 12 repositories. The **64.8% merge rate** and **3.9 PRs/day** velocity reflect a busy two-week sprint focused on:

1. **202511 Branch Stabilization** – HA cherry-pick batches ensuring release readiness
2. **DPU Management Tooling** – Significant improvements to single-DPU configuration and lifecycle management
3. **DASH Feature Completion** – NVGRE, CRM, Private Link, counters, and routing improvements
4. **Platform Infrastructure** – ZMQ reliability, gRPC/gNOI framework, Mellanox/AMD platform fixes

The high PR creation rate in sonic-mgmt (31 of 54) continues to reflect the importance of the test infrastructure layer for validating DASH/SmartSwitch functionality across platforms.

---

*Queries used to generate this report:*
```
org:sonic-net is:pr is:merged merged:2026-03-26..2026-04-08 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title

org:sonic-net is:pr created:2026-03-26..2026-04-08 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```
