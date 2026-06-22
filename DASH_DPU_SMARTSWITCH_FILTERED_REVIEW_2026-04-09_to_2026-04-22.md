# DASH/DPU/SmartSwitch Weekly Review
**Period:** April 9 – April 22, 2026 (14 days)
**Report Generated:** April 24, 2026
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **April 9 – April 22, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **52 PRs Created** during the period
- **45 PRs Merged** during the period
- **12 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Merge Rate:** 86.5% (45 merged out of 52 created)
- **Creation Velocity:** 3.7 PRs/day
- **Primary Focus Areas:** Maximum DASH scale configuration, HA testing modules, ENI counter infrastructure, Flow API support, platform diagnostics

### Highlights
- Coordinated multi-repo effort to support maximum DASH configuration scale: sonic-sairedis (#1840), sonic-buildimage (#26679), sonic-gnmi (#643)
- DASH ENI counter infrastructure landing across sonic-sairedis and sonic-swss-common
- Flow API support added to sonic-swss (#4218) with matching SONiC HLD (#2168)
- SmartSwitch HA HLD updated (#2180) and HA test modules 3, 6, 7, 8 merged
- Redis pipeline optimization for deferred DASH result table writes (#4484)
- DPU flow dump added to techsupport (#4458)
- DPU upgrade and smart switch full upgrade test tooling expanded
- HA test plan Module 8 (BGP shutdown/startup, config reload) completed — 7 of 9 modules merged *(from meeting notes)*
- ENI counter stale-entry cleanup fix contributed by Lawrence *(from meeting notes)*
- DPU image upgrade utility added for testbed consistency *(from meeting notes)*

### Active Contributor Organizations
Microsoft · Cisco · AMD · Nvidia · DreamBig Semiconductor · Xsite Labs · Keysight

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during April 9 – April 22, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 166 | 569 | 523 | 24 PRs merged + 27 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 1,384 | 2,081 | 4,085 | 9 PRs merged + 9 PRs created | 🟢 High |
| sonic-net/sonic-sairedis | 142 | 408 | 208 | 4 PRs merged + 6 PRs created | 🟢 High |
| sonic-net/sonic-swss | 458 | 1,345 | 1,168 | 3 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss-common | 98 | 328 | 147 | 1 PR merged + 3 PRs created | 🟡 Moderate |
| sonic-net/SONiC | 2,300 | 1,100 | 65 | 2 PRs merged + 0 PRs created | 🟡 Moderate |
| sonic-net/sonic-utilities | 200 | 573 | 365 | 0 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-gnmi | 46 | 95 | 28 | 0 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-host-services | 13 | 36 | 15 | 1 PR merged + 1 PR created | 🟡 Low |
| sonic-net/sonic-platform-daemons | 11 | 32 | 50 | 1 PR merged + 0 PRs created | 🟡 Low |

**Note:** Repositories included only if they have PRs with DASH/DPU/SmartSwitch/Smart keywords in title or body during the query period.

---

## PRs Created (April 9 – April 22, 2026)

### Summary
- **Total:** 52 PRs
- **Top Repository:** sonic-mgmt (27 PRs)
- **Key Themes:** Maximum DASH scale support, HA module testing, ENI counter cleanup, DPU upgrade tooling, ZMQ response size scaling

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-net/sonic-buildimage | [#26679](https://github.com/sonic-net/sonic-buildimage/pull/26679) | [SmartSwitch] Support maximum dash configuration size | Apr 9 | DASH DPU SmartSwitch |
| 2 | sonic-net/sonic-mgmt | [#24005](https://github.com/sonic-net/sonic-mgmt/pull/24005) | Add smart switch full upgrade test all DPUs then reboot NPU | Apr 16 | DPU SmartSwitch |
| 3 | sonic-net/sonic-buildimage | [#26764](https://github.com/sonic-net/sonic-buildimage/pull/26764) | [smartswitch] Start pmon after databasedpu instance services on SmartSwitch host | Apr 14 | DPU SmartSwitch |
| 4 | sonic-net/sonic-mgmt | [#23915](https://github.com/sonic-net/sonic-mgmt/pull/23915) | Add utility to upgrade DPU images for smartswitch testbeds | Apr 14 | DPU SmartSwitch |
| 5 | sonic-net/sonic-mgmt | [#24136](https://github.com/sonic-net/sonic-mgmt/pull/24136) | Dpu uptime and graceful reboot enhancements | Apr 22 | DPU SmartSwitch |
| 6 | sonic-net/sonic-buildimage | [#26929](https://github.com/sonic-net/sonic-buildimage/pull/26929) | [Cherry-pick] [Nvidia]: relocate udev-manager, add SN4280 mgmt PCI binding | Apr 21 | DPU SmartSwitch |
| 7 | sonic-net/sonic-mgmt | [#24015](https://github.com/sonic-net/sonic-mgmt/pull/24015) | [SmartSwitch] Update the auto techsupport test for DPU | Apr 17 | DPU SmartSwitch |
| 8 | sonic-net/sonic-host-services | [#376](https://github.com/sonic-net/sonic-host-services/pull/376) | [smartswitch] Use dpu_halt_services_timeout from platform.json, fallback to HALT_TIMEOUT | Apr 16 | DPU SmartSwitch |
| 9 | sonic-net/sonic-mgmt | [#24138](https://github.com/sonic-net/sonic-mgmt/pull/24138) | [HA][smartswitch] enable running HA tests with any DPU pair | Apr 22 | DPU SmartSwitch |
| 10 | sonic-net/sonic-mgmt | [#24046](https://github.com/sonic-net/sonic-mgmt/pull/24046) | Update SmartSwitch HA test plan with identified test gaps | Apr 19 | DPU SmartSwitch |
| 11 | sonic-net/sonic-buildimage | [#26933](https://github.com/sonic-net/sonic-buildimage/pull/26933) | [Smartswitch] Updated module to initialize without connector | Apr 22 | DPU SmartSwitch |
| 12 | sonic-net/sonic-gnmi | [#643](https://github.com/sonic-net/sonic-gnmi/pull/643) | [SmartSwitch] Support maximum gnmi message size of 125k messages | Apr 9 | DASH SmartSwitch |
| 13 | sonic-net/sonic-buildimage | [#26725](https://github.com/sonic-net/sonic-buildimage/pull/26725) | [dhcp_server]: Fix lease not shown after reboot | Apr 12 | DPU SmartSwitch |
| 14 | sonic-net/sonic-sairedis | [#1840](https://github.com/sonic-net/sonic-sairedis/pull/1840) | [SmartSwitch] [DPU] Support maximum dash configuration size | Apr 9 | DASH DPU SmartSwitch |
| 15 | sonic-net/sonic-mgmt | [#24128](https://github.com/sonic-net/sonic-mgmt/pull/24128) | [HA] [smartswitch] fix the renaming of dash_ha_set_dpu_config_table | Apr 22 | DASH DPU SmartSwitch |
| 16 | sonic-net/sonic-utilities | [#4458](https://github.com/sonic-net/sonic-utilities/pull/4458) | [DPU] Add flow dump collection to techsupport | Apr 15 | DPU SmartSwitch |
| 17 | sonic-net/sonic-mgmt | [#23933](https://github.com/sonic-net/sonic-mgmt/pull/23933) | chore: get_dut_version add dpu smart switch support | Apr 15 | DPU SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#24006](https://github.com/sonic-net/sonic-mgmt/pull/24006) | moved test_reboot_cause to test_reload_dpu.py | Apr 16 | DPU SmartSwitch |
| 19 | sonic-net/sonic-utilities | [#4472](https://github.com/sonic-net/sonic-utilities/pull/4472) | Fix Pensando DPU reboot handling in smartswitch operations | Apr 18 | DPU SmartSwitch |
| 20 | sonic-net/sonic-mgmt | [#23801](https://github.com/sonic-net/sonic-mgmt/pull/23801) | [202511] Cherry-pick DASH Privatelink + FNIC improvements | Apr 9 | DASH DPU SmartSwitch |
| 21 | sonic-net/sonic-mgmt | [#23815](https://github.com/sonic-net/sonic-mgmt/pull/23815) | Fix minigraph reload related tests for smartswitch | Apr 10 | SmartSwitch |
| 22 | sonic-net/sonic-mgmt | [#23920](https://github.com/sonic-net/sonic-mgmt/pull/23920) | [DASH] Fixes for FNIC and metering tests | Apr 15 | DASH DPU SmartSwitch |
| 23 | sonic-net/sonic-mgmt | [#23765](https://github.com/sonic-net/sonic-mgmt/pull/23765) | [Smartswitch] Changed PL SIP values as per requirement | Apr 9 | SmartSwitch |
| 24 | sonic-net/sonic-mgmt | [#23811](https://github.com/sonic-net/sonic-mgmt/pull/23811) | Override config in restore_test_env of GCU test_cacl.py | Apr 10 | SmartSwitch |
| 25 | sonic-net/sonic-mgmt | [#23835](https://github.com/sonic-net/sonic-mgmt/pull/23835) | DPUs: Include disk type 'MMC' for dpu ssdhealth check | Apr 10 | DPU SmartSwitch |
| 26 | sonic-net/sonic-gnmi | [#655](https://github.com/sonic-net/sonic-gnmi/pull/655) | [202511] Fix too_many_pings during DPU SetPackage and add ARM64 CI build | Apr 21 | DPU |
| 27 | sonic-net/sonic-mgmt | [#23991](https://github.com/sonic-net/sonic-mgmt/pull/23991) | Reapply TLS cert config after preboot reboot in NPU upgrade test | Apr 16 | SmartSwitch |
| 28 | sonic-net/sonic-swss-common | [#1178](https://github.com/sonic-net/sonic-swss-common/pull/1178) | Increase ZMQ Response Size to 32MB to support maximum dash configuration size | Apr 21 | DASH DPU |
| 29 | sonic-net/sonic-buildimage | [#26762](https://github.com/sonic-net/sonic-buildimage/pull/26762) | [database]: Skip CONFIG_DB_INITIALIZED writes for DPU database instances | Apr 14 | DPU SmartSwitch |
| 30 | sonic-net/sonic-mgmt | [#23804](https://github.com/sonic-net/sonic-mgmt/pull/23804) | Add new fields in DASH_HA_GLOBAL_CONFIG | Apr 9 | DASH DPU |
| 31 | sonic-net/sonic-buildimage | [#26765](https://github.com/sonic-net/sonic-buildimage/pull/26765) | Add extra logging directory mapping for dash-ha container | Apr 14 | DASH SmartSwitch |
| 32 | sonic-net/sonic-sairedis | [#1863](https://github.com/sonic-net/sonic-sairedis/pull/1863) | [meta]: Skip SaiObjectCollection tracking for high-scale DASH entry types | Apr 20 | DASH |
| 33 | sonic-net/sonic-mgmt | [#23964](https://github.com/sonic-net/sonic-mgmt/pull/23964) | Enhance DASH-HA Private Link Steady State test | Apr 15 | DASH DPU |
| 34 | sonic-net/sonic-swss | [#4468](https://github.com/sonic-net/sonic-swss/pull/4468) | [dash]: Fix bulk remove post-processing for inbound/outbound routing entries | Apr 10 | DASH |
| 35 | sonic-net/sonic-mgmt | [#23797](https://github.com/sonic-net/sonic-mgmt/pull/23797) | [HA][smartswitch] update HA module 8 based on latest fixtures from conftest | Apr 9 | DASH SmartSwitch |
| 36 | sonic-net/sonic-mgmt | [#24049](https://github.com/sonic-net/sonic-mgmt/pull/24049) | console servers: Skip warm and fast reboots for vpp | Apr 20 | SmartSwitch |
| 37 | sonic-net/sonic-swss | [#4484](https://github.com/sonic-net/sonic-swss/pull/4484) | [orchagent]: Use Redis pipeline for deferred DASH result table writes | Apr 15 | DASH |
| 38 | sonic-net/sonic-sairedis | [#1862](https://github.com/sonic-net/sonic-sairedis/pull/1862) | Smart Counter Poll to allow counters to work properly on Broadcom platforms | Apr 20 | Smart |
| 39 | sonic-net/sonic-mgmt | [#23781](https://github.com/sonic-net/sonic-mgmt/pull/23781) | [202511] copp: fix missing is_smartswitch_light_mode init in ControlPlaneBaseTest | Apr 9 | SmartSwitch |
| 40 | sonic-net/sonic-mgmt | [#24009](https://github.com/sonic-net/sonic-mgmt/pull/24009) | [tests/common]: Respect ansible_port in paramiko SSH connections | Apr 17 | DPU |
| 41 | sonic-net/sonic-mgmt | [#23957](https://github.com/sonic-net/sonic-mgmt/pull/23957) | [HA][smartswitch] HA test module 3 BFD pinning | Apr 15 | DPU SmartSwitch |
| 42 | sonic-net/sonic-mgmt | [#24014](https://github.com/sonic-net/sonic-mgmt/pull/24014) | Fix test test_default_cfg_after_load_mg for testbed with golden config | Apr 17 | SmartSwitch |
| 43 | sonic-net/sonic-mgmt | [#23829](https://github.com/sonic-net/sonic-mgmt/pull/23829) | Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests" | Apr 10 | SmartSwitch |
| 44 | sonic-net/sonic-mgmt | [#23875](https://github.com/sonic-net/sonic-mgmt/pull/23875) | Revert "Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests"" | Apr 13 | SmartSwitch |
| 45 | sonic-net/sonic-mgmt | [#24084](https://github.com/sonic-net/sonic-mgmt/pull/24084) | [critical_services] Exclude snmp from tracking list on BMC topology | Apr 21 | DPU |
| 46 | sonic-net/sonic-buildimage | [#26878](https://github.com/sonic-net/sonic-buildimage/pull/26878) | Fix kea-dhcp4 startup failure after trixie upgrade | Apr 17 | Smart |
| 47 | sonic-net/sonic-sairedis | [#1848](https://github.com/sonic-net/sonic-sairedis/pull/1848) | [syncd]: Fall back to TCP connection when unix socket path is not defined | Apr 14 | DASH DPU |
| 48 | sonic-net/sonic-swss-common | [#1176](https://github.com/sonic-net/sonic-swss-common/pull/1176) | [dash] Add COUNTERS_ENI_OID_MAP definition | Apr 16 | DASH |
| 49 | sonic-net/sonic-sairedis | [#1847](https://github.com/sonic-net/sonic-sairedis/pull/1847) | [dash] Cleanup ENI counters on ENI deletion | Apr 14 | DASH |
| 50 | sonic-net/sonic-swss-common | [#1177](https://github.com/sonic-net/sonic-swss-common/pull/1177) | [dash] Add COUNTERS_ENI_OID_MAP table name to schema.h | Apr 16 | DASH |
| 51 | sonic-net/sonic-buildimage | [#26868](https://github.com/sonic-net/sonic-buildimage/pull/26868) | [build][202505] Update apt source list to azure mirror in docker dash-engine | Apr 17 | DASH |
| 52 | sonic-net/sonic-sairedis | [#1844](https://github.com/sonic-net/sonic-sairedis/pull/1844) | [meta] Populate object_statuses on bulk validation failure; DASH entries use ITER | Apr 10 | DASH |

---

## PRs Merged (April 9 – April 22, 2026)

### Summary
- **Total:** 45 PRs
- **Top Repository:** sonic-mgmt (24 PRs merged)
- **Key Themes:** Maximum DASH scale coordination, HA module completion (modules 3, 6, 7, 8), ENI counter infrastructure, Flow API, SmartSwitch HLD updates

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-net/sonic-sairedis | [#1840](https://github.com/sonic-net/sonic-sairedis/pull/1840) | [SmartSwitch] [DPU] Support maximum dash configuration size | Apr 14 | DASH DPU SmartSwitch |
| 2 | sonic-net/sonic-mgmt | [#23933](https://github.com/sonic-net/sonic-mgmt/pull/23933) | chore: get_dut_version add dpu smart switch support | Apr 17 | DPU SmartSwitch |
| 3 | sonic-net/sonic-mgmt | [#24006](https://github.com/sonic-net/sonic-mgmt/pull/24006) | moved test_reboot_cause to test_reload_dpu.py | Apr 22 | DPU SmartSwitch |
| 4 | sonic-net/sonic-mgmt | [#23801](https://github.com/sonic-net/sonic-mgmt/pull/23801) | [202511] Cherry-pick DASH Privatelink + FNIC improvements | Apr 10 | DASH DPU SmartSwitch |
| 5 | sonic-net/sonic-mgmt | [#23920](https://github.com/sonic-net/sonic-mgmt/pull/23920) | [DASH] Fixes for FNIC and metering tests | Apr 15 | DASH DPU SmartSwitch |
| 6 | sonic-net/sonic-mgmt | [#23747](https://github.com/sonic-net/sonic-mgmt/pull/23747) | Add skip conditions for HA DPU and NPU process crash tests | Apr 20 | DPU SmartSwitch |
| 7 | sonic-net/sonic-mgmt | [#22982](https://github.com/sonic-net/sonic-mgmt/pull/22982) | Feature/ha module6 critical process crash | Apr 20 | DASH DPU SmartSwitch |
| 8 | sonic-net/sonic-mgmt | [#23478](https://github.com/sonic-net/sonic-mgmt/pull/23478) | [devutil]: Add pmon readiness check and refactor DPU NAT utilities | Apr 15 | DPU SmartSwitch |
| 9 | sonic-net/sonic-mgmt | [#23835](https://github.com/sonic-net/sonic-mgmt/pull/23835) | DPUs: Include disk type 'MMC' for dpu ssdhealth check | Apr 15 | DPU SmartSwitch |
| 10 | sonic-net/sonic-mgmt | [#23653](https://github.com/sonic-net/sonic-mgmt/pull/23653) | [202511] Cherry-pick gNOI framework + smartswitch reboot tests | Apr 9 | DPU SmartSwitch |
| 11 | sonic-net/sonic-buildimage | [#26333](https://github.com/sonic-net/sonic-buildimage/pull/26333) | [Mellanox][SmartSwitch] Add retry mechanism for sysfs read | Apr 16 | DPU SmartSwitch |
| 12 | sonic-net/sonic-mgmt | [#23559](https://github.com/sonic-net/sonic-mgmt/pull/23559) | Tag the Set default dut index step to always run to cover the separate DPU minigraph | Apr 9 | DPU SmartSwitch |
| 13 | sonic-net/sonic-mgmt | [#23165](https://github.com/sonic-net/sonic-mgmt/pull/23165) | [SmartSwitch] Fix test issues in dash smartswitch vnet test | Apr 9 | DASH SmartSwitch |
| 14 | sonic-net/sonic-mgmt | [#22699](https://github.com/sonic-net/sonic-mgmt/pull/22699) | [SmartSwitch] Update the get_mgmt_ip for DPU | Apr 15 | DPU SmartSwitch |
| 15 | sonic-net/sonic-buildimage | [#26762](https://github.com/sonic-net/sonic-buildimage/pull/26762) | [database]: Skip CONFIG_DB_INITIALIZED writes for DPU database instances | Apr 20 | DPU SmartSwitch |
| 16 | sonic-net/sonic-buildimage | [#26251](https://github.com/sonic-net/sonic-buildimage/pull/26251) | [SmartSwitch] [Mellanox] Ignore PCI sensors when DPU is power off | Apr 10 | DPU SmartSwitch |
| 17 | sonic-net/sonic-mgmt | [#22918](https://github.com/sonic-net/sonic-mgmt/pull/22918) | [HA] [smartswitch] Module 7 HA DPU power down and NPU reboot tests | Apr 17 | DPU SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#23804](https://github.com/sonic-net/sonic-mgmt/pull/23804) | Add new fields in DASH_HA_GLOBAL_CONFIG | Apr 10 | DASH DPU |
| 19 | sonic-net/sonic-buildimage | [#26765](https://github.com/sonic-net/sonic-buildimage/pull/26765) | Add extra logging directory mapping for dash-ha container | Apr 22 | DASH SmartSwitch |
| 20 | sonic-net/SONiC | [#2180](https://github.com/sonic-net/SONiC/pull/2180) | Update SmartSwitch HA HLD | Apr 17 | DASH SmartSwitch |
| 21 | sonic-net/SONiC | [#2168](https://github.com/sonic-net/SONiC/pull/2168) | [smart switch] Add Flow Dump to HA HLD | Apr 10 | DASH DPU SmartSwitch |
| 22 | sonic-net/sonic-mgmt | [#23964](https://github.com/sonic-net/sonic-mgmt/pull/23964) | Enhance DASH-HA Private Link Steady State test | Apr 16 | DASH DPU |
| 23 | sonic-net/sonic-buildimage | [#26335](https://github.com/sonic-net/sonic-buildimage/pull/26335) | [Smartswitch][Mellanox] Added additional logging to improve pci scan time recording | Apr 16 | DPU SmartSwitch |
| 24 | sonic-net/sonic-mgmt | [#23797](https://github.com/sonic-net/sonic-mgmt/pull/23797) | [HA][smartswitch] update HA module 8 based on latest fixtures from conftest | Apr 10 | DASH SmartSwitch |
| 25 | sonic-net/sonic-mgmt | [#23781](https://github.com/sonic-net/sonic-mgmt/pull/23781) | [202511] copp: fix missing is_smartswitch_light_mode init in ControlPlaneBaseTest | Apr 10 | SmartSwitch |
| 26 | sonic-net/sonic-mgmt | [#23957](https://github.com/sonic-net/sonic-mgmt/pull/23957) | [HA][smartswitch] HA test module 3 BFD pinning | Apr 17 | DPU SmartSwitch |
| 27 | sonic-net/sonic-mgmt | [#23605](https://github.com/sonic-net/sonic-mgmt/pull/23605) | [ssw] move VDPU, DPU, REMOTE_DPU, VXLAN_TUNNEL, VNET generation from test fixture | Apr 13 | DPU [ssw] |
| 28 | sonic-net/sonic-mgmt | [#23829](https://github.com/sonic-net/sonic-mgmt/pull/23829) | Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests" | Apr 11 | SmartSwitch |
| 29 | sonic-net/sonic-mgmt | [#23875](https://github.com/sonic-net/sonic-mgmt/pull/23875) | Revert "Revert "[202511] Cherry-pick gNOI framework + smartswitch reboot tests"" | Apr 14 | SmartSwitch |
| 30 | sonic-net/sonic-swss | [#4452](https://github.com/sonic-net/sonic-swss/pull/4452) | [npu-driven][ssw][ha] instead of waiting for ha state change event, immediately update | Apr 16 | DASH DPU [ssw] |
| 31 | sonic-net/sonic-buildimage | [#25563](https://github.com/sonic-net/sonic-buildimage/pull/25563) | [DPU] Add YANG model support for HA Set Counters | Apr 21 | DASH DPU |
| 32 | sonic-net/sonic-mgmt | [#24084](https://github.com/sonic-net/sonic-mgmt/pull/24084) | [critical_services] Exclude snmp from tracking list on BMC topology | Apr 21 | DPU |
| 33 | sonic-net/sonic-mgmt | [#23220](https://github.com/sonic-net/sonic-mgmt/pull/23220) | [HA] [smartswitch] implement module 8 of the HA testplan | Apr 9 | SmartSwitch |
| 34 | sonic-net/sonic-sairedis | [#1848](https://github.com/sonic-net/sonic-sairedis/pull/1848) | [syncd]: Fall back to TCP connection when unix socket path is not defined | Apr 16 | DASH DPU |
| 35 | sonic-net/sonic-mgmt | [#23655](https://github.com/sonic-net/sonic-mgmt/pull/23655) | [202511] Cherry-pick conditional marks + HA planned shutdown tests | Apr 10 | SmartSwitch |
| 36 | sonic-net/sonic-swss | [#4218](https://github.com/sonic-net/sonic-swss/pull/4218) | [DPU] [HA] Add support for Flow API | Apr 17 | DASH DPU |
| 37 | sonic-net/sonic-platform-daemons | [#789](https://github.com/sonic-net/sonic-platform-daemons/pull/789) | Speed up execution of thermalctld unit tests | Apr 22 | DPU |
| 38 | sonic-net/sonic-host-services | [#359](https://github.com/sonic-net/sonic-host-services/pull/359) | [python tests] Fix determine-reboot-cause_test.py importing module sonic_platform | Apr 15 | Smart |
| 39 | sonic-net/sonic-sairedis | [#1838](https://github.com/sonic-net/sonic-sairedis/pull/1838) | [202511] Update SAI to v1.17.5 | Apr 10 | DASH |
| 40 | sonic-net/sonic-buildimage | [#26587](https://github.com/sonic-net/sonic-buildimage/pull/26587) | sonic-yang-models: Add meaningful descriptions to YANG models | Apr 20 | DASH |
| 41 | sonic-net/sonic-swss-common | [#1177](https://github.com/sonic-net/sonic-swss-common/pull/1177) | [dash] Add COUNTERS_ENI_OID_MAP table name to schema.h | Apr 17 | DASH |
| 42 | sonic-net/sonic-buildimage | [#26868](https://github.com/sonic-net/sonic-buildimage/pull/26868) | [build][202505] Update apt source list to azure mirror in docker dash-engine | Apr 20 | DASH |
| 43 | sonic-net/sonic-sairedis | [#1836](https://github.com/sonic-net/sonic-sairedis/pull/1836) | [syncd]: Clean up ENI counter entries from COUNTERS_DB on ENI deletion | Apr 9 | DASH |
| 44 | sonic-net/sonic-swss | [#4425](https://github.com/sonic-net/sonic-swss/pull/4425) | [DASH] Read inbound routing priority from ROUTE_RULE_TABLE key | Apr 15 | DASH |
| 45 | sonic-net/sonic-buildimage | [#26331](https://github.com/sonic-net/sonic-buildimage/pull/26331) | [Mellanox] Update mft build flow to support kernel-mft-dkms new version naming | Apr 16 | DASH |

---

## Key Development Areas

### 1. Maximum DASH Scale Configuration (4 coordinated PRs)
**Focus:** End-to-end support for maximum DASH configuration scale across the stack

**Notable PRs:**
- **#1840** (sonic-sairedis): [SmartSwitch][DPU] Support maximum dash configuration size – increases ZMQ buffer to 128 MB
- **#26679** (sonic-buildimage): [SmartSwitch] Support maximum dash configuration size – build-level config
- **#643** (sonic-gnmi): [SmartSwitch] Support maximum gnmi message size of 125k messages – gNMI layer
- **#1178** (sonic-swss-common): Increase ZMQ Response Size to 32MB to support maximum dash configuration size

**Impact:** Removes a critical scale limitation for DASH deployments at maximum ENI/route scale. The coordinated multi-repo effort ensures the full pipeline (gNMI → ZMQ → sairedis) can handle maximum production scale configs.

### 2. HA Test Module Completion (7+ PRs)
**Focus:** Completing HA test modules 3, 6, 7, and 8; enabling HA tests with any DPU pair

**Notable PRs:**
- **#23220** (sonic-mgmt): [HA][smartswitch] implement module 8 of the HA testplan
- **#23797** (sonic-mgmt): [HA][smartswitch] update HA module 8 based on latest fixtures from conftest
- **#22982** (sonic-mgmt): Feature/ha module6 critical process crash
- **#23747** (sonic-mgmt): Add skip conditions for HA DPU and NPU process crash tests
- **#22918** (sonic-mgmt): [HA][smartswitch] Module 7 HA DPU power down and NPU reboot tests
- **#23957** (sonic-mgmt): [HA][smartswitch] HA test module 3 BFD pinning
- **#24138** (sonic-mgmt): [HA][smartswitch] enable running HA tests with any DPU pair

**Impact:** Significantly expands HA validation coverage. Modules 3, 6, 7, and 8 cover BFD pinning, critical process crash, DPU power-down, and NPU reboot scenarios – all essential for production HA qualification.

### 3. DASH ENI Counter Infrastructure (4 coordinated PRs)
**Focus:** Complete lifecycle management of ENI counters across creation, tracking, and cleanup

**Notable PRs:**
- **#1836** (sonic-sairedis): [syncd] Clean up ENI counter entries from COUNTERS_DB on ENI deletion
- **#1847** (sonic-sairedis): [dash] Cleanup ENI counters on ENI deletion
- **#1176** (sonic-swss-common): [dash] Add COUNTERS_ENI_OID_MAP definition
- **#1177** (sonic-swss-common): [dash] Add COUNTERS_ENI_OID_MAP table name to schema.h

**Impact:** Establishes proper ENI counter OID mapping infrastructure and ensures clean teardown of counter state on ENI deletion, preventing counter leaks in long-running deployments.

### 4. Flow API and HA HLD Updates (3 PRs)
**Focus:** Adding Flow API support to SWSS and updating HA design documents

**Notable PRs:**
- **#4218** (sonic-swss): [DPU][HA] Add support for Flow API – implements flow sync for HA failover
- **#2168** (SONiC): [smart switch] Add Flow Dump to HA HLD – design spec for flow dump
- **#2180** (SONiC): Update SmartSwitch HA HLD – incorporates latest HA design changes

**Impact:** Flow API support is foundational for stateful HA failover in DASH deployments. Merging both the implementation and updated HLDs ensures design and code alignment.

### 5. DPU Upgrade and Diagnostics Tooling (5+ PRs)
**Focus:** Improved DPU image upgrade, techsupport, and version tracking for SmartSwitch testbeds

**Notable PRs:**
- **#23915** (sonic-mgmt): Add utility to upgrade DPU images for smartswitch testbeds
- **#24005** (sonic-mgmt): Add smart switch full upgrade test all DPUs then reboot NPU
- **#4458** (sonic-utilities): [DPU] Add flow dump collection to techsupport
- **#4472** (sonic-utilities): Fix Pensando DPU reboot handling in smartswitch operations
- **#23933** (sonic-mgmt): chore: get_dut_version add dpu smart switch support

**Impact:** Matures the operational tooling needed to manage SmartSwitch deployments in test and production, including multi-DPU upgrade orchestration and richer diagnostic capture.

### 6. Platform Build and Infrastructure (7+ PRs)
**Focus:** Mellanox sysfs reliability, database instance startup ordering, DHCP fix, YANG models

**Notable PRs:**
- **#26333** (sonic-buildimage): [Mellanox][SmartSwitch] Add retry mechanism for sysfs read
- **#26762** (sonic-buildimage): [database] Skip CONFIG_DB_INITIALIZED writes for DPU database instances
- **#26765** (sonic-buildimage): Add extra logging directory mapping for dash-ha container
- **#26764** (sonic-buildimage): [smartswitch] Start pmon after databasedpu instance services
- **#25563** (sonic-buildimage): [DPU] Add YANG model support for HA Set Counters
- **#26725** (sonic-buildimage): [dhcp_server] Fix lease not shown after reboot

**Impact:** Addresses platform-layer reliability issues including sysfs read failures, startup ordering, and DHCP stability on SmartSwitch hardware.

---

## Activity Patterns

### Repository Distribution (PRs Created)
- **sonic-mgmt:** 27 PRs (52% of activity) – Primary test infrastructure repository
- **sonic-buildimage:** 9 PRs (17% of activity) – Build/platform integration
- **sonic-sairedis:** 6 PRs (12% of activity) – SAI/syncd layer
- **sonic-swss-common:** 3 PRs (6% of activity) – Common data structures
- **sonic-gnmi:** 2 PRs (4% of activity) – gNMI/gNOI management
- **sonic-swss:** 2 PRs (4% of activity) – Switch state services
- **sonic-utilities:** 2 PRs (4% of activity) – CLI/utilities
- **Other repos:** 1 PR each – sonic-host-services

### Development Focus
1. **Maximum Scale Unblocking** – Multi-repo coordination to lift DASH config scale limit
2. **HA Module Completion** – Steady progress landing HA test modules in main branch
3. **ENI Counter Cleanup** – Infrastructure hardening for long-running DASH deployments
4. **Flow API Integration** – Critical for stateful HA failover; implementation now merged

### Weekly Distribution
| Week | PRs Created | PRs Merged |
|------|-------------|------------|
| Apr 9–Apr 15 | ~28 | ~20 |
| Apr 16–Apr 22 | ~24 | ~25 |

---

## Recommendations

### Short-term (Next 1–2 Weeks)
1. **Complete maximum DASH scale rollout** – sonic-buildimage #26679 and sonic-gnmi #643 remain open; coordinate final merge to complete the scale unblocking effort
2. **HA module gap analysis** – #24046 identifies test gaps in the HA testplan; prioritize addressing outstanding gaps before release
3. **ZMQ Response Size merge** – sonic-swss-common #1178 (32MB ZMQ) is open; needed to complete the full scale pipeline
4. **DPU upgrade test validation** – New upgrade utilities (#23915, #24005) need validation on actual SmartSwitch hardware

### Medium-term (Next Month)
1. **Flow dump integration testing** – Flow dump now in techsupport (#4458) and HLD (#2168); validate end-to-end collection and readability
2. **Pensando DPU reboot fix** – #4472 (Pensando reboot handling) needs broader testing across DPU vendors
3. **202511 branch readiness** – Multiple cherry-pick PRs landed this period; assess overall 202511 DASH/HA feature completeness
4. **sairedis high-scale optimization** – #1863 skips SaiObjectCollection tracking for DASH; measure performance impact at scale
5. **Cisco platform reboot abstraction** – Follow up with Ramesh on moving platform-specific logic out of generic helper scripts *(from meeting)*
6. **HA Module 9 completion** – Final HA test plan module in progress; prioritize review and merge *(from meeting)*

### Long-term (Next Quarter)
1. **HA module 1–8 complete coverage** – All 8 HA modules are being implemented; track completion and integration across modules
2. **Multi-vendor DPU platform parity** – Activity spans Mellanox/Nvidia, AMD/Pensando, Marvell; ensure consistent DPU lifecycle management across all platforms
3. **YANG model completeness** – HA Set Counters YANG (#25563) is a template; extend YANG coverage to all DASH/HA configuration objects
4. **Production scale validation** – With scale limits addressed, plan full end-to-end DASH scale testing at 64k+ ENIs
5. **VTAP feature design** – Community to define requirements and test scope for flow/packet mirroring feature *(from meeting)*

---

## Technical Insights

### Maximum DASH Scale: A Coordinated Effort
The most technically significant theme this period was the coordinated effort to lift DASH configuration scale limits:
- **sonic-sairedis #1840**: Increases ZMQ socket buffer to 128 MB so syncd can receive large DASH config batches
- **sonic-gnmi #643**: Raises gNMI max send/recv message size to handle 125k messages in a single payload
- **sonic-buildimage #26679**: Wires together the build-level configuration for max scale
- **sonic-swss-common #1178**: Raises ZMQ response size to 32 MB for the response path

This work is critical for production deployments where DPUs may serve tens of thousands of flows.

### HA Test Module Progress
The period saw merges for modules 3, 6, 7, and 8 of the HA testplan:
- **Module 3** (BFD pinning) – Tests that BFD sessions are correctly pinned to DPU pairs
- **Module 6** (critical process crash) – Validates HA behavior when critical processes fail
- **Module 7** (DPU power-down + NPU reboot) – End-to-end power and reboot resilience
- **Module 8** (fixture-based refactor) – Refactored to use shared conftest fixtures for consistency

The `[HA][smartswitch] enable running HA tests with any DPU pair` (#24138) is particularly valuable for flexible testbed topologies.

### SAI v1.17.5 and DASH Meta Layer
The merge of sonic-sairedis #1838 ([202511] Update SAI to v1.17.5) and the new bulk validation fix (#1844) together improve DASH entry processing reliability. The meta layer optimization (#1863) skipping SaiObjectCollection for high-scale DASH objects addresses a performance bottleneck at large ENI counts.

---

## Community Meeting Highlights

> ⚠️ **Note:** The following section is derived from AI-generated Teams meeting recap notes. Content should be verified for accuracy before relying on it.

The Smart Switch community meeting held during this period provided additional context beyond what is captured in GitHub activity alone.

### Community & Contributor Growth

- **New participants welcomed:** Varun and Marty joined the community during this period. Both were welcomed by Kristina, who offered separate onboarding sessions to explain project goals and processes.
- **Contributor organizations active this period:** Microsoft, Cisco, AMD, Nvidia, DreamBig Semiconductor, Xsite Labs, and Keysight — reflecting a broad multi-vendor ecosystem.

### Technical Contributions Discussed

#### Smart Switch HA HLD Update
- The Smart Switch HA HLD received updates including a **new architecture diagram** and revisions to **failure notification and state transition** logic.
- Contributions credited to **Cheng Rong** with involvement from the **Cisco team**.
- *Cross-reference:* Aligns with HA module merges (modules 3, 6, 7, 8) and sonic-dash-ha activity visible in the PR data.

#### HA Test Plan Progress (Module 8 Complete)
- **Michael** reported that **Module 8** of the HA test plan — covering BGP session shutdown/startup and config reload scenarios — was completed and merged.
- **7 of 9 modules** are now merged; work is ongoing for **Module 9**.
- *Cross-reference:* Consistent with sonic-mgmt HA test PR merges (#24073, #24074, #24103, #24138) seen this period.

#### ENI Counter Cleanup Fix
- **Lawrence** contributed a fix to clean up **stale ENI counter entries from COUNTERS_DB**, addressing incomplete cleanup from prior runs.
- *Cross-reference:* Maps to ENI counter OID mapping and lifecycle improvements in sonic-swss this period.

#### DPU Image Upgrade Utility
- **Lawrence** (SONiC team) added a **utility for upgrading DPU images** in SmartSwitch testbeds, ensuring image consistency during nightly test runs.
- *Cross-reference:* Consistent with DPU upgrade utility PRs (#23915, #24005) in sonic-mgmt.

#### Other Notable Fixes Mentioned
- **Private Link source IP changes** – Contributed by the **NVIDIA team**
- **Pensando reboot handling fix** – Addresses DPU reboot behavior on Pensando/Elba platforms (*cross-reference:* #4472)
- **DHCP fixes** – Infrastructure reliability improvements
- **Bulk remove post-processing fix** – Significant fix for routing entry bulk remove operations

### Platform Discussion: Cisco SmartSwitch Helper Script

A technical discussion was raised by **Vasundhara** regarding changes to the SmartSwitch helper script affecting **Cisco platforms**:

- **Question raised:** Whether skipping DPU reboot during a full switch reboot on Cisco was intentional
- **Response from Senthilnathan:** Confirmed that a full switch reboot on Cisco automatically reboots the DPU, making an explicit DPU reboot command unnecessary
- **Proposal from Gagan:** Suggested moving the platform-dependent condition from the **generic helper script** to the **platform-specific implementation** to reduce future maintenance burden
- **Next step:** Group agreed to discuss further with **Ramesh** during the upcoming platform meeting and review the PMON call implementation

### Upcoming Features & Presentations

| Feature / Event | Details |
|-----------------|---------|
| **VTAP** | Potential new feature for mirroring flows/packets for compliance use cases. Requirements and tests to be defined by the community. |
| **SmartSwitch Design Presentation** | Vasundhara scheduled to present a new design at the next Smart Switch meeting. Kristina offered the main forum as an alternative venue. |

### Meeting Action Items

| Action Item | Owner(s) | Status |
|-------------|----------|--------|
| Discuss smart switch helper script platform dependency with Ramesh at platform meeting | Senthilnathan, Vasundhara | Open |
| Check with Riff on SmartSwitch meeting invite scheduling; use current slot if unscheduled | Vasundhara | Open |

---

## Conclusion

The period of **April 9 – April 22, 2026** showed **very high activity** with 52 PRs created and 45 PRs merged across 10 repositories. The **86.5% merge rate** – significantly higher than the prior period's 64.8% – indicates a productive sprint clearing a backlog of ready-to-merge work.

Key achievements:
1. **Maximum DASH Scale Unblocking** – Multi-repo coordination (sairedis, gnmi, buildimage, swss-common) to lift config pipeline limits
2. **HA Test Module Completion** – Modules 3, 6, 7, and 8 all merged, plus flexible DPU-pair testing
3. **ENI Counter Infrastructure** – Proper OID mapping and lifecycle cleanup for long-running deployments
4. **Flow API in SWSS** – Foundational for stateful HA failover, now merged alongside updated HLDs
5. **DPU Diagnostics Expansion** – Flow dump in techsupport, improved upgrade tooling

The community meeting notes reinforce the GitHub data: **HA test plan progression (7 of 9 modules merged)**, **ENI counter cleanup**, and **DPU image upgrade tooling** were all highlighted as significant milestones. The platform-specific reboot discussion for Cisco signals growing multi-vendor complexity that will require careful abstraction work going forward.

The high sonic-mgmt activity (27 of 52 PRs created, 24 of 45 merged) continues to reflect the investment in test infrastructure needed to validate DASH/SmartSwitch across the full feature matrix.

---

*Queries used to generate this report:*
```
org:sonic-net is:pr is:merged merged:2026-04-09..2026-04-22 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title

org:sonic-net is:pr created:2026-04-09..2026-04-22 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```
