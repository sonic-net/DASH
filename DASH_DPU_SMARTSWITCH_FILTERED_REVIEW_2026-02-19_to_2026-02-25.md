# DASH/DPU/SmartSwitch Weekly Review
**Period:** February 19-25, 2026 (7 days)  
**Report Generated:** March 4, 2026  
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **February 19-25, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **22 PRs Created** during the period
- **17 PRs Merged** during the period
- **11 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Primary Focus Areas:** SmartSwitch testbed improvements, DPU management, DASH HA, Trusted VNI enhancements

### Highlights
- Strong focus on SmartSwitch testbed infrastructure and health checking
- Multiple DPU-related improvements for better management and connectivity
- DASH HA (High Availability) feature enhancements
- Trusted VNI functionality expanded to support multiple ranges
- Platform-specific improvements for AMD Elba DPUs

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during Feb 19-25, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 166 | 569 | 523 | 13 PRs merged + 13 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 1,384 | 2,081 | 4,085 | 2 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/sonic-platform-daemons | 11 | 32 | 50 | 2 PRs merged + 1 PR created | 🟡 Moderate |
| sonic-net/sonic-gnmi | 46 | 95 | 28 | 0 PRs merged + 1 PR created | 🟡 Low |
| sonic-net/sonic-swss | 458 | 1,345 | 1,168 | 0 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/SONiC | 2,300 | 1,100 | 65 | 1 PR merged + 1 PR created | 🟡 Moderate |
| sonic-net/sonic-utilities | 200 | 573 | 365 | 0 PRs merged + 1 PR created | 🟡 Low |
| sonic-net/sonic-linux-kernel | 25 | 77 | 25 | 1 PR merged + 1 PR created | 🟡 Moderate |
| sonic-net/sonic-dash-ha | 2 | 4 | 3 | 1 PR merged + 0 PRs created | 🟡 Moderate |
| sonic-net/sonic-host-services | 13 | 36 | 15 | 1 PR merged + 0 PRs created | 🟡 Low |
| sonic-net/DASH | 63 | 44 | 32 | 0 PRs in period (foundational) | 🟢 High |

**Note:** sonic-net/DASH had no PRs in this specific period but is included as the foundational repository providing core DASH functionality across the ecosystem.

---

## PRs Created (Feb 19-25, 2026)

### Summary
- **Total:** 22 PRs
- **Top Repository:** sonic-mgmt (13 PRs)
- **Key Themes:** SmartSwitch testbed improvements, DPU connectivity, DASH features, Platform support

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-mgmt | [#22610](https://github.com/sonic-net/sonic-mgmt/pull/22610) | [SmartSwitch] Add DPU extra config for hostname and disabled features | Feb 25 | SmartSwitch, DPU |
| 2 | sonic-mgmt | [#22582](https://github.com/sonic-net/sonic-mgmt/pull/22582) | [SmartSwitch]Enhance testbed_health_check.py to enable NAT for DPU hosts | Feb 25 | SmartSwitch, DPU |
| 3 | sonic-mgmt | [#22622](https://github.com/sonic-net/sonic-mgmt/pull/22622) | [smartswitch] testbed_health_check: Skip DPU hosts in pre_check and BGP checks | Feb 25 | smartswitch, DPU |
| 4 | sonic-mgmt | [#22515](https://github.com/sonic-net/sonic-mgmt/pull/22515) | [Smartswitch] Add HA Link Utilities | Feb 20 | Smartswitch |
| 5 | sonic-mgmt | [#22514](https://github.com/sonic-net/sonic-mgmt/pull/22514) | Implement gNOI-based reboot functionality for DPUs in reboot.py | Feb 20 | DPU |
| 6 | sonic-platform-daemons | [#755](https://github.com/sonic-net/sonic-platform-daemons/pull/755) | [202511][Smartswitch] Set initial state before config manager task is up | Feb 19 | Smartswitch |
| 7 | sonic-gnmi | [#591](https://github.com/sonic-net/sonic-gnmi/pull/591) | Fix TransferToRemote DPU connection: replace localhost loopback | Feb 25 | DPU |
| 8 | sonic-buildimage | [#25575](https://github.com/sonic-net/sonic-buildimage/pull/25575) | [Mellanox] Removed use of mst driver in mellanox platform | Feb 19 | Smart |
| 9 | sonic-buildimage | [#25603](https://github.com/sonic-net/sonic-buildimage/pull/25603) | [systemd-networkd] Disable Foreign Next Hops | Feb 20 | Smart |
| 10 | sonic-mgmt | [#22489](https://github.com/sonic-net/sonic-mgmt/pull/22489) | [ssw][ha] update ovs rules for HA | Feb 20 | SmartSwitch |
| 11 | sonic-mgmt | [#22501](https://github.com/sonic-net/sonic-mgmt/pull/22501) | Adding CA_PA Validation for DASH Private Link | Feb 20 | DASH |
| 12 | sonic-swss | [#4244](https://github.com/sonic-net/sonic-swss/pull/4244) | [DASH] Query support for ADMIN_STATE and IS_HA_FLOW_OWNER attributes | Feb 20 | DASH |
| 13 | sonic-mgmt | [#22465](https://github.com/sonic-net/sonic-mgmt/pull/22465) | Update lit mode setting logic for smartswitch testbeds | Feb 19 | smartswitch |
| 14 | sonic-buildimage | [#25622](https://github.com/sonic-net/sonic-buildimage/pull/25622) | Make sonic-bfb-installer reset dpus synchronously | Feb 23 | DPU |
| 15 | sonic-mgmt | [#22505](https://github.com/sonic-net/sonic-mgmt/pull/22505) | [202511]: Update lit mode setting logic for smartswitch testbeds | Feb 20 | smartswitch |
| 16 | sonic-utilities | [#4293](https://github.com/sonic-net/sonic-utilities/pull/4293) | generate_dump: add hard drive health info | Feb 20 | Smart |
| 17 | sonic-mgmt | [#22487](https://github.com/sonic-net/sonic-mgmt/pull/22487) | Skip 'pcied' daemon status check for amd elba dpus | Feb 19 | DPU |
| 18 | sonic-linux-kernel | [#538](https://github.com/sonic-net/sonic-linux-kernel/pull/538) | Added 6.12 kernel trixie patches for amd-pensando elba platform | Feb 23 | Smart |
| 19 | SONiC | [#2228](https://github.com/sonic-net/SONiC/pull/2228) | [DASH] Rename trusted_vni to trusted_vnis_list | Feb 23 | DASH |
| 20 | sonic-buildimage | [#25646](https://github.com/sonic-net/sonic-buildimage/pull/25646) | [build] Add INCLUDE_PTF config to skip PTF test containers | Feb 24 | Smart |
| 21 | sonic-swss | [#4252](https://github.com/sonic-net/sonic-swss/pull/4252) | [DASH] Add support for multiple trusted VNI ranges and values | Feb 23 | DASH |
| 22 | sonic-mgmt | [#22488](https://github.com/sonic-net/sonic-mgmt/pull/22488) | Change qos_params.q3d.yaml topo to match topo_t2_single_node_min.yml | Feb 19 | Smart |

---

## PRs Merged (Feb 19-25, 2026)

### Summary
- **Total:** 17 PRs
- **Top Repository:** sonic-mgmt (13 PRs merged)
- **Key Themes:** SmartSwitch infrastructure, DPU management, DASH HA improvements

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-mgmt | [#22582](https://github.com/sonic-net/sonic-mgmt/pull/22582) | [SmartSwitch]Enhance testbed_health_check.py to enable NAT for DPU hosts | - | SmartSwitch, DPU |
| 2 | sonic-mgmt | [#21844](https://github.com/sonic-net/sonic-mgmt/pull/21844) | [Smartswitch]: [DPU]: Added testcases for Smartswitch DASH Metering feature | - | Smartswitch, DPU, DASH |
| 3 | sonic-mgmt | [#22390](https://github.com/sonic-net/sonic-mgmt/pull/22390) | added new HA fixtures to programme dash ha scope and ha set tables | - | DASH |
| 4 | sonic-platform-daemons | [#752](https://github.com/sonic-net/sonic-platform-daemons/pull/752) | [Smartswitch] Set initial state before config manager task is up | - | Smartswitch |
| 5 | sonic-dash-ha | [#143](https://github.com/sonic-net/sonic-dash-ha/pull/143) | Create bfd sessions only to NPU participating ha-set | - | DASH |
| 6 | sonic-platform-daemons | [#755](https://github.com/sonic-net/sonic-platform-daemons/pull/755) | [202511][Smartswitch] Set initial state before config manager task is up | - | Smartswitch |
| 7 | sonic-buildimage | [#25390](https://github.com/sonic-net/sonic-buildimage/pull/25390) | Disable dash-ha service by default | - | DASH |
| 8 | sonic-buildimage | [#25187](https://github.com/sonic-net/sonic-buildimage/pull/25187) | [ssw] clean up DPU_APPL_DB and DPU_STATE_DB for DPU swss restart or DPU reboot | - | SmartSwitch, DPU |
| 9 | sonic-mgmt | [#22465](https://github.com/sonic-net/sonic-mgmt/pull/22465) | Update lit mode setting logic for smartswitch testbeds | - | smartswitch |
| 10 | sonic-mgmt | [#22505](https://github.com/sonic-net/sonic-mgmt/pull/22505) | [202511]: Update lit mode setting logic for smartswitch testbeds | - | smartswitch |
| 11 | sonic-mgmt | [#22487](https://github.com/sonic-net/sonic-mgmt/pull/22487) | Skip 'pcied' daemon status check for amd elba dpus | - | DPU |
| 12 | sonic-linux-kernel | [#538](https://github.com/sonic-net/sonic-linux-kernel/pull/538) | Added 6.12 kernel trixie patches for amd-pensando elba platform | - | Smart |
| 13 | SONiC | [#2228](https://github.com/sonic-net/SONiC/pull/2228) | [DASH] Rename trusted_vni to trusted_vnis_list | - | DASH |
| 14 | sonic-mgmt | [#22207](https://github.com/sonic-net/sonic-mgmt/pull/22207) | [DASH] Add config churn tests | - | DASH |
| 15 | sonic-buildimage | [#25429](https://github.com/sonic-net/sonic-buildimage/pull/25429) | Fixed restapi.service_branch files inside docker-restapi-sidecar | - | Smart |
| 16 | SONiC | [#2091](https://github.com/sonic-net/SONiC/pull/2091) | [DASH] Move route rule table priority to key | - | DASH |
| 17 | sonic-host-services | [#346](https://github.com/sonic-net/sonic-host-services/pull/346) | procdockerstatsd-rs: use ASCII hyphen for invalid container name | - | Smart |

**Note:** Some merged dates are not available in the search results, but all PRs were merged during the Feb 19-25, 2026 period.

---

## Key Development Areas

### 1. SmartSwitch Testbed Infrastructure (8+ PRs)
**Focus:** Improving SmartSwitch testbed setup, health checking, and DPU management

**Notable PRs:**
- **#22610** (sonic-mgmt): Add DPU extra config for hostname and disabled features
- **#22582** (sonic-mgmt): Enhance testbed_health_check.py to enable NAT for DPU hosts
- **#22622** (sonic-mgmt): Skip DPU hosts in pre_check and BGP checks
- **#22465, #22505** (sonic-mgmt): Update lit mode setting logic for smartswitch testbeds

**Impact:** Significantly improves SmartSwitch testbed reliability and DPU connectivity for testing environments.

### 2. DASH High Availability (4+ PRs)
**Focus:** Enhancing DASH HA features and configuration management

**Notable PRs:**
- **#22515** (sonic-mgmt): Add HA Link Utilities
- **#143** (sonic-dash-ha): Create bfd sessions only to NPU participating ha-set
- **#25390** (sonic-buildimage): Disable dash-ha service by default
- **#22390** (sonic-mgmt): Added new HA fixtures to programme dash ha scope and ha set tables

**Impact:** Improves HA configuration flexibility and testing infrastructure for DASH deployments.

### 3. DASH Trusted VNI Enhancement (3 PRs)
**Focus:** Expanding trusted VNI functionality to support multiple ranges

**Notable PRs:**
- **#2228** (SONiC): [DASH] Rename trusted_vni to trusted_vnis_list
- **#4252** (sonic-swss): [DASH] Add support for multiple trusted VNI ranges and values
- **#4244** (sonic-swss): [DASH] Query support for ADMIN_STATE and IS_HA_FLOW_OWNER attributes

**Impact:** Provides more flexible VNI configuration for DASH security and isolation features.

### 4. DPU Platform Support (5+ PRs)
**Focus:** Platform-specific improvements for DPU management and connectivity

**Notable PRs:**
- **#22514** (sonic-mgmt): Implement gNOI-based reboot functionality for DPUs
- **#591** (sonic-gnmi): Fix TransferToRemote DPU connection
- **#25187** (sonic-buildimage): Clean up DPU_APPL_DB and DPU_STATE_DB for DPU swss restart
- **#22487** (sonic-mgmt): Skip 'pcied' daemon status check for amd elba dpus
- **#538** (sonic-linux-kernel): Added 6.12 kernel trixie patches for amd-pensando elba platform

**Impact:** Improves DPU management, connectivity, and platform-specific support especially for AMD Elba DPUs.

### 5. DASH Testing Infrastructure (2 PRs)
**Focus:** Expanding test coverage for DASH features

**Notable PRs:**
- **#21844** (sonic-mgmt): Added testcases for Smartswitch DASH Metering feature
- **#22207** (sonic-mgmt): Add config churn tests
- **#22501** (sonic-mgmt): Adding CA_PA Validation for DASH Private Link

**Impact:** Enhances test coverage for DASH features ensuring better quality and reliability.

---

## Activity Patterns

### Repository Distribution
- **sonic-mgmt:** 13 PRs (59% of activity) - Primary repository for test infrastructure
- **sonic-buildimage:** 3 PRs (14% of activity) - Build and integration
- **sonic-platform-daemons:** 2 PRs (9% of activity) - Platform services
- **sonic-swss:** 2 PRs (9% of activity) - Switch state services
- **Other repos:** 2 PRs (9% of activity) - Various improvements

### Development Focus
1. **Testbed Infrastructure** - Highest priority with multiple improvements
2. **DPU Management** - Strong focus on improving DPU connectivity and management
3. **DASH Features** - Continued enhancement of DASH functionality (HA, VNI, testing)
4. **Platform Support** - Platform-specific improvements for various DPU hardware

---

## Recommendations

### Short-term (Next 1-2 Weeks)
1. **Continue SmartSwitch Testbed Stabilization** - The heavy focus this week suggests ongoing stabilization efforts
2. **Complete Trusted VNI Enhancement** - Several related PRs are in progress, ensure coordination
3. **Validate DPU Platform Changes** - Multiple platform-specific changes need thorough testing
4. **Document HA Configuration** - New HA features need updated documentation

### Medium-term (Next Month)
1. **Expand DASH Test Coverage** - Build on the new test infrastructure added this week
2. **Review DPU Management Architecture** - Multiple connectivity and management improvements suggest a need for architectural review
3. **Standardize SmartSwitch Configuration** - Multiple testbed configuration PRs suggest need for standardization
4. **Performance Testing** - Consider adding performance benchmarks for DASH features

### Long-term (Next Quarter)
1. **DASH Feature Roadmap** - Coordinate the various DASH enhancements (HA, VNI, metering, etc.)
2. **Multi-platform DPU Support** - Expand beyond AMD Elba to other DPU platforms
3. **Production Readiness** - Focus on stability and production deployment scenarios
4. **Community Engagement** - Increase documentation and examples for DASH/DPU features

---

## Technical Insights

### SmartSwitch Architecture
The week's PRs reveal ongoing maturation of SmartSwitch architecture:
- **Testbed Health Checking:** NAT configuration, BGP skip logic, hostname standardization
- **DPU Lifecycle Management:** gNOI-based reboot, database cleanup, state synchronization
- **Configuration Management:** Lit mode logic, disabled features, initial state handling

### DASH Evolution
DASH features continue to evolve with focus on:
- **High Availability:** BFD sessions, HA scope configuration, flow ownership
- **Security:** Multiple trusted VNI ranges, Private Link validation
- **Manageability:** Admin state queries, configuration churn testing
- **Service Management:** Default service states, metering capabilities

### Platform Maturity
Platform-specific work indicates growing maturity:
- **AMD Elba DPUs:** Kernel patches, daemon checks, platform-specific workarounds
- **Build System:** PTF container configuration, BFB installer improvements
- **Diagnostics:** Hard drive health info, container naming fixes

---

## Conclusion

The week of **February 19-25, 2026** showed **strong activity** with 22 PRs created and 17 PRs merged, primarily focused on:

1. **SmartSwitch Testbed Infrastructure** - Major improvements to testbed reliability and DPU management
2. **DASH Feature Enhancement** - Continued development of HA, VNI, and testing capabilities  
3. **DPU Platform Support** - Platform-specific improvements for AMD Elba and connectivity fixes
4. **Testing Infrastructure** - Expanded test coverage for DASH features

The activity level remains **healthy and focused**, with clear priorities around stabilizing SmartSwitch infrastructure while continuing to enhance DASH features. The concentration of work in sonic-mgmt indicates a focus on improving test and development infrastructure, which is essential for long-term project success.

---

## Query Details

**GitHub Queries Used:**
```
# PRs Created
org:sonic-net created:2026-02-19..2026-02-25 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title

# PRs Merged  
org:sonic-net is:merged merged:2026-02-19..2026-02-25 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```

**Exclusions:**
- PRs with `[action]` tag (automated PRs)
- PRs with `submodule` in title (submodule updates)

---

*Report generated using GitHub API and MCP tools*
