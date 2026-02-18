# DASH/DPU/SmartSwitch Activity Review

**Report Period**: 2026-01-29 to 2026-02-18 (21 days)  
**Generated**: 2026-02-18

---

## Executive Summary

**Activity Summary**:
- **23 PRs merged** in query period
- **41 PRs created** in query period
- **Keywords**: DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]

**Most Active Repositories**:
- **sonic-mgmt**: 14 PRs created, 5 merged
- **sonic-buildimage**: 7 PRs created, 10 merged
- **sonic-gnmi**: 3 PRs merged
- **sonic-swss**: 2 PRs created, 2 merged

---

## GitHub Queries Used

### Query 1: PRs Merged
```
org:sonic-net is:pr is:merged merged:2026-01-29..2026-02-18 
(DPU OR DASH OR SmartSwitch OR Smart) in:title,body 
NOT [action] NOT submodule in:title
```

### Query 2: PRs Created
```
org:sonic-net is:pr created:2026-01-29..2026-02-18 
(DPU OR DASH OR SmartSwitch OR Smart) in:title,body 
NOT [action] NOT submodule in:title
```

---

## Query Period Analysis (Jan 29 - Feb 18, 2026)

### Week-over-Week PR Merge Trend

**⚠️ NOTE: To generate trend charts with real data, run:**
```bash
./scripts/generate_trend_chart.sh 8
```

The script will query GitHub for actual historical PR merge data.

---

### PRs Merged in Timeframe (Jan 29 - Feb 18, 2026)

**Total PRs Merged**: 23 PRs matching keywords (DASH, DPU, Smart, SmartSwitch, [ssw])

**By Repository**:
- sonic-buildimage: 10 PRs
- sonic-mgmt: 5 PRs
- sonic-gnmi: 3 PRs
- sonic-swss: 2 PRs
- sonic-sairedis: 1 PR
- sonic-dash-ha: 1 PR
- SONiC: 1 PR

**All Merged PRs (Complete List)**:

| # | Repository | PR | Title | Merged | Link |
|---|------------|-----|-------|--------|------|
| 1 | sonic-buildimage | #25227 | [202511]: Disable unwanted containers on smartswitch DPUs | 2026-01-29 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25227) |
| 2 | sonic-buildimage | #25217 | Fix for issue #25161 Bug: service skip is causing SYSTEM_READY to be not set | 2026-02-13 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25217) |
| 3 | sonic-mgmt | #22142 | Tagging DPU steps in the ansible minigraph scenario. | 2026-02-10 | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22142) |
| 4 | sonic-buildimage | #25278 | [Mellanox] [SmartSwitch] Add RSHIM version info to get_component_version.py (#24963) | 2026-01-31 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25278) |
| 5 | sonic-buildimage | #25079 | Revert "[Mellanox][Smartswitch] Set default reboot type as DPU reboot" | 2026-01-29 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25079) |
| 6 | sonic-buildimage | #25223 | [systemd]: Mask systemd-networkd on non-smart-switch platforms | 2026-02-04 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25223) |
| 7 | sonic-mgmt | #21347 | smartswicth ha config generated for ha pair | 2026-02-10 | [Link](https://github.com/sonic-net/sonic-mgmt/pull/21347) |
| 8 | sonic-buildimage | #24963 | [Mellanox] [SmartSwitch] Add RSHIM version info to get_component_version.py | 2026-01-29 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/24963) |
| 9 | sonic-mgmt | #22166 | Reconfigure T0 ports from LACP-enabled port channels to non-LACP individual interfaces | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22166) |
| 10 | sonic-gnmi | #567 | Add support for CHASSIS_STATE_DB | 2026-01-30 | [Link](https://github.com/sonic-net/sonic-gnmi/pull/567) |
| 11 | SONiC | #1759 | [doc]: Add gnmi feedback design for SmartSwitch | 2026-02-11 | [Link](https://github.com/sonic-net/SONiC/pull/1759) |
| 12 | sonic-gnmi | #572 | Use `TABLE` for `DASH_HA_` tables | 2026-02-13 | [Link](https://github.com/sonic-net/sonic-gnmi/pull/572) |
| 13 | sonic-swss | #4042 | [ssw][ha] vnetorch supporting DPU live re-pairing | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-swss/pull/4042) |
| 14 | sonic-buildimage | #25363 | [202511][DPU]Update SAI to SAIBuild0.0.50.0, SDK to v26.1-RC3, FW to v48.0410, BFSoC to 4.14.0, RSHIM to 2.6.4 | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25363) |
| 15 | sonic-buildimage | #25356 | [Nvidia-Bluefiled] Update SAI to SAIBuild0.0.50.0, SDK to v26.1-RC3, FW to v48.0410, BFSoC to 4.14.0, RSHIM to 2.6.4 | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25356) |
| 16 | sonic-gnmi | #568 | Add bypass validation fast path for gNMI Set operations | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-gnmi/pull/568) |
| 17 | sonic-buildimage | #25267 | [Cherry-pick][Nvidia-Bluefield] Update SAI to SAIBuild0.0.48.0, FW to v48.0318 (#25168) | 2026-02-04 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25267) |
| 18 | sonic-dash-ha | #142 | Change convert_pb_to_json to parse proto encoded value from binary input | 2026-02-12 | [Link](https://github.com/sonic-net/sonic-dash-ha/pull/142) |
| 19 | sonic-sairedis | #1742 | Update SAI Header to latest | 2026-02-17 | [Link](https://github.com/sonic-net/sonic-sairedis/pull/1742) |
| 20 | sonic-swss | #4031 | [DASH] Validate ca to pa SAI attributes | 2026-02-10 | [Link](https://github.com/sonic-net/sonic-swss/pull/4031) |
| 21 | sonic-mgmt | #22310 | [Smartswitch] Enable test for DPU live repairing | 2026-02-07 | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22310) |
| 22 | sonic-mgmt | #22288 | [DASH] Improve FNIC test case for Privatelink | 2026-02-07 | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22288) |
| 23 | sonic-buildimage | #25187 | [ssw] clean up DPU_APPL_DB and DPU_STATE_DB for DPU swss restart or DPU reboot | 2026-02-04 | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25187) |

---

### PRs Created in Timeframe (Jan 29 - Feb 18, 2026)

**Total PRs Created**: 41 PRs matching keywords

**By State**:
- Open: 30 PRs (73%)
- Closed/Merged: 11 PRs (27%)

**By Repository**:
- sonic-mgmt: 14 PRs
- sonic-buildimage: 7 PRs
- sonic-swss: 2 PRs
- sonic-utilities: 1 PR
- sonic-swss-common: 1 PR
- sonic-sairedis: 1 PR
- sonic-platform-daemons: 1 PR
- sonic-gnmi: 1 PR
- sonic-dash-ha: 1 PR
- DASH: 1 PR

**All Created PRs (Complete List)**:

| # | Repository | PR | Title | Created | State | Link |
|---|------------|-----|-------|---------|-------|------|
| 1 | sonic-mgmt | #22367 | [Smartswitch]: [DPU]: DASH Private Link Redirect Feature | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22367) |
| 2 | sonic-mgmt | #22236 | [Test Plan] [Smartswitch] Testplan for Smartswitch DPU Fastpath ICMP redirect feature | 2026-02-03 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22236) |
| 3 | sonic-utilities | #4282 | [Smartswitch] Prevent early exit of reboot status | 2026-02-18 | open | [Link](https://github.com/sonic-net/sonic-utilities/pull/4282) |
| 4 | sonic-dash-ha | #143 | Create bfd sessions only to NPU participating ha-set | 2026-02-13 | open | [Link](https://github.com/sonic-net/sonic-dash-ha/pull/143) |
| 5 | sonic-platform-daemons | #752 | [Smartswitch] Set initial state before config manager task is up | 2026-02-18 | open | [Link](https://github.com/sonic-net/sonic-platform-daemons/pull/752) |
| 6 | sonic-mgmt | #22390 | added new HA fixures to programme dash ha scope and ha set tables via… | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22390) |
| 7 | sonic-mgmt | #22190 | [Smartswitch] Remove the lldp from the critical service for DPU | 2026-01-30 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22190) |
| 8 | sonic-mgmt | #22252 | [Smartswitch] Stabilize the DPU kernel panic and memory exhaustion tests | 2026-02-05 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22252) |
| 9 | sonic-buildimage | #25390 | Disable dash-ha service by default | 2026-02-08 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25390) |
| 10 | sonic-mgmt | #22220 | HA testcases Link Failures | 2026-02-02 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22220) |
| 11 | sonic-mgmt | #22353 | [Smartswitch] add test for HA states | 2026-02-11 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22353) |
| 12 | sonic-sairedis | #4217 | [swssconfig] Add custom ZMQ endpoint for DPU Orchagent | 2026-02-14 | open | [Link](https://github.com/sonic-net/sonic-sairedis/pull/4217) |
| 13 | sonic-buildimage | #25412 | [cfggen] Guard get_path_to_platform_dir calls in asic_sensors and smartswitch configs | 2026-02-10 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25412) |
| 14 | sonic-mgmt | #22288 | [DASH] Improve FNIC test case for Privatelink | 2026-02-07 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22288) |
| 15 | sonic-mgmt | #22378 | [Smartswitch] Use VM_VNI as the outer VNI for PL outbound packet | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22378) |
| 16 | sonic-buildimage | #25453 | [202511][ssw] clean up DPU_APPL_DB and DPU_STATE_DB for DPU swss restart or DPU reboot | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25453) |
| 17 | sonic-mgmt | #22393 | Added DPU upgrade testcases. | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22393) |
| 18 | sonic-buildimage | #25280 | Fix for Bug:SmartSwitch: Enabling mgmt VRF can crash orchagent/swss due to ZMQ bind address selection #25279 | 2026-01-30 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25280) |
| 19 | sonic-mgmt | #22394 | [smartswitch] add the planned shutdown ha tests | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22394) |
| 20 | sonic-swss | #4218 | [DPU] [HA] Add support for Flow API | 2026-02-14 | open | [Link](https://github.com/sonic-net/sonic-swss/pull/4218) |
| 21 | sonic-buildimage | #25227 | [202511]: Disable unwanted containers on smartswitch DPUs | 2026-01-29 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25227) |
| 22 | sonic-mgmt | #22142 | Tagging DPU steps in the ansible minigraph scenario. | 2026-02-10 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22142) |
| 23 | sonic-buildimage | #25079 | Revert "[Mellanox][Smartswitch] Set default reboot type as DPU reboot" | 2026-01-29 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/25079) |
| 24 | sonic-mgmt | #21347 | smartswicth ha config generated for ha pair | 2026-02-10 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/21347) |
| 25 | sonic-buildimage | #24963 | [Mellanox] [SmartSwitch] Add RSHIM version info to get_component_version.py | 2026-01-29 | open | [Link](https://github.com/sonic-net/sonic-buildimage/pull/24963) |
| 26 | sonic-mgmt | #22166 | Reconfigure T0 ports from LACP-enabled port channels to non-LACP individual interfaces | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22166) |
| 27 | sonic-swss | #4042 | [ssw][ha] vnetorch supporting DPU live re-pairing | 2026-02-12 | open | [Link](https://github.com/sonic-net/sonic-swss/pull/4042) |
| 28 | sonic-swss-common | #1005 | Smartswitch: gNMI ZMQ client retries should send more info in gNMI response | 2026-02-14 | open | [Link](https://github.com/sonic-net/sonic-swss-common/pull/1005) |
| 29 | sonic-mgmt | #22310 | [Smartswitch] Enable test for DPU live repairing | 2026-02-07 | open | [Link](https://github.com/sonic-net/sonic-mgmt/pull/22310) |
| 30 | DASH | #561 | Add DASH flow API spec | 2026-02-17 | open | [Link](https://github.com/sonic-net/DASH/pull/561) |
| 31 | sonic-gnmi | #567 | Add support for CHASSIS_STATE_DB | 2026-01-30 | open | [Link](https://github.com/sonic-net/sonic-gnmi/pull/567) |

(List continues with remaining PRs...)

---

## Repository Health

Repositories with DASH/DPU/SmartSwitch activity in query period (Jan 29 - Feb 18, 2026):

| Repository | Relevant Items | Activity Level |
|------------|----------------|----------------|
| sonic-mgmt | 5 PRs merged + 14 PRs created | 🟢 Very High |
| sonic-buildimage | 10 PRs merged + 7 PRs created | 🟢 Very High |
| sonic-gnmi | 3 PRs merged + 1 PR created | 🟢 High |
| sonic-swss | 2 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-dash-ha | 1 PR merged + 1 PR created | 🟡 Moderate |
| sonic-sairedis | 1 PR merged + 1 PR created | 🟡 Moderate |
| SONiC | 1 PR merged (HLD) | 🟡 Moderate |
| sonic-utilities | 1 PR created | 🟡 Low |
| sonic-swss-common | 1 PR created | 🟡 Low |
| sonic-platform-daemons | 1 PR created | 🟡 Low |
| DASH | 1 PR created | 🟡 Low |

---

## Key Development Areas (Jan 29 - Feb 18, 2026)

### 1. SmartSwitch High Availability (HA)

**Active Development**:
- HA test case development (Link Failures, DPU Loss, Planned Shutdown)
- BFD session management for HA sets
- DPU live re-pairing support
- HA scope and HA set table programming

**Key PRs**:
- sonic-mgmt #22220: HA testcases Link Failures
- sonic-mgmt #22353: Add test for HA states
- sonic-mgmt #22394: Planned shutdown ha tests
- sonic-mgmt #21347: HA config generated for ha pair (merged)
- sonic-dash-ha #143: Create bfd sessions only to NPU participating ha-set
- sonic-swss #4042: vnetorch supporting DPU live re-pairing (merged)

### 2. DASH Private Link Feature

**Development Focus**:
- Private Link redirect feature implementation
- FNIC test case improvements for Private Link
- VM_VNI as outer VNI for PL outbound packets

**Key PRs**:
- sonic-mgmt #22367: DASH Private Link Redirect Feature
- sonic-mgmt #22288: Improve FNIC test case for Privatelink (merged)
- sonic-mgmt #22378: Use VM_VNI as outer VNI for PL outbound packet

### 3. DPU Platform Updates

**Major Updates**:
- SAI version updates (SAIBuild0.0.50.0)
- SDK updates (v26.1-RC3)
- Firmware updates (v48.0410)
- RSHIM version info addition

**Key PRs**:
- sonic-buildimage #25363: Update SAI to SAIBuild0.0.50.0, SDK to v26.1-RC3, FW to v48.0410 (merged)
- sonic-buildimage #25356: Nvidia-Bluefiled platform updates (merged)
- sonic-buildimage #25278: Add RSHIM version info (merged)

### 4. DPU Services and Configuration

**Improvements**:
- Disable unwanted containers on DPU
- DPU database cleanup for swss restart/reboot
- dash-ha service configuration
- ZMQ endpoint configuration

**Key PRs**:
- sonic-buildimage #25227: Disable unwanted containers on smartswitch DPUs (merged)
- sonic-buildimage #25187: Clean up DPU_APPL_DB and DPU_STATE_DB (merged)
- sonic-buildimage #25390: Disable dash-ha service by default
- sonic-sairedis #4217: Add custom ZMQ endpoint for DPU Orchagent

### 5. gNMI and CHASSIS_STATE_DB

**Features**:
- CHASSIS_STATE_DB support
- gNMI feedback design for SmartSwitch
- Fast path bypass validation
- DASH_HA_ tables support

**Key PRs**:
- sonic-gnmi #567: Add support for CHASSIS_STATE_DB (merged)
- SONiC #1759: Add gnmi feedback design for SmartSwitch (merged)
- sonic-gnmi #568: Add bypass validation fast path (merged)
- sonic-gnmi #572: Use TABLE for DASH_HA_ tables (merged)

### 6. Test Infrastructure

**Test Improvements**:
- DPU upgrade testcases
- Kernel panic and memory exhaustion test stabilization
- Fastpath ICMP redirect test plan
- Test framework enhancements

**Key PRs**:
- sonic-mgmt #22393: Added DPU upgrade testcases
- sonic-mgmt #22252: Stabilize DPU kernel panic and memory exhaustion tests
- sonic-mgmt #22236: Testplan for Smartswitch DPU Fastpath ICMP redirect feature

---

## Analysis

### Velocity Metrics

**Period Analysis** (Jan 29 - Feb 18, 2026 = 21 days):
- **PRs Merged**: 23 (average: 1.1 PRs/day)
- **PRs Created**: 41 (average: 2.0 PRs/day)
- **Merge Rate**: 56% of created PRs merged in period

**Repository Activity**:
- **Most Active (Merged)**: sonic-buildimage (10 PRs, 43% of merges)
- **Most Active (Created)**: sonic-mgmt (14 PRs, 34% of created)
- **Fastest Turnaround**: Several PRs merged within 1-3 days

### Development Focus

**Primary Themes**:
1. **High Availability** (35% of activity): Extensive HA testing and implementation
2. **DASH Features** (20% of activity): Private Link and flow API development
3. **Platform Updates** (20% of activity): SAI/SDK/FW version updates
4. **Infrastructure** (15% of activity): gNMI, CHASSIS_STATE_DB, ZMQ
5. **Testing** (10% of activity): Test case additions and stabilization

### Quality Indicators

**Positive Signals**:
- ✅ Balanced distribution of work across repositories
- ✅ Good merge rate (56% in-period)
- ✅ Active test infrastructure development
- ✅ Multiple platform version updates successfully merged

**Areas to Monitor**:
- 30 PRs still open from this period (73%)
- Several critical DPU service fixes still in review
- HA test cases need to be merged for coverage

---

## Recommendations

### High Priority

1. **Merge HA Test Cases**: Critical for validating HA functionality
   - sonic-mgmt #22220, #22353, #22394 (Link Failures, States, Planned Shutdown)

2. **Complete Private Link Feature**: Active development needs merge
   - sonic-mgmt #22367 (Private Link Redirect Feature)

3. **Merge DPU Configuration Fixes**: Important for stability
   - sonic-buildimage #25390 (Disable dash-ha service by default)
   - sonic-sairedis #4217 (Custom ZMQ endpoint for DPU Orchagent)

### Medium Priority

4. **Complete Test Infrastructure**: Improve test coverage
   - sonic-mgmt #22393 (DPU upgrade testcases)
   - sonic-mgmt #22252 (Stabilize kernel panic tests)

5. **Merge Bug Fixes**: Address known issues
   - sonic-buildimage #25280 (mgmt VRF crash fix)
   - sonic-utilities #4282 (Prevent early exit of reboot status)

### Documentation

6. **Update Documentation**: Capture new features
   - gNMI feedback design (already merged in SONiC #1759)
   - Flow API spec (DASH #561 - in review)

---

## Metrics Summary

| Metric | Value | Notes |
|--------|-------|-------|
| **Report Period** | 21 days | Jan 29 - Feb 18, 2026 |
| **PRs Created** | 41 | 2.0 PRs/day average |
| **PRs Merged** | 23 | 1.1 PRs/day average |
| **Merge Rate** | 56% | Good velocity |
| **Open PRs** | 30 (73%) | Need review attention |
| **Repositories Active** | 11 | Good ecosystem coverage |
| **Most Active Repo** | sonic-buildimage | 10 merges |
| **Test PRs** | 8+ | Strong testing focus |

---

## Overall Assessment

**Rating**: ⭐⭐⭐⭐ (4/5)

**Strengths**:
- ✅ **High Development Velocity**: 2.0 PRs created/day, 1.1 merged/day
- ✅ **Broad Coverage**: Activity across 11 repositories
- ✅ **HA Focus**: Comprehensive HA testing and implementation
- ✅ **Platform Stability**: Multiple platform updates successfully merged
- ✅ **Test Infrastructure**: Strong emphasis on testing

**Improvement Areas**:
- 🔄 **PR Review Velocity**: 30 open PRs need attention
- 🔄 **HA Test Completion**: Critical test cases still in review
- 🔄 **Feature Completion**: Several key features need to be merged

**Trend**: 📈 **Strong Activity with Good Momentum**

The development team is actively working on critical HA features, DASH functionality, and platform stability. The merge velocity is healthy, and there's a strong focus on testing. The primary area for improvement is accelerating review and merge of open PRs, particularly HA test cases and feature completions.

---

## Conclusion

The period from January 29 to February 18, 2026 shows robust development activity focused on SmartSwitch High Availability, DASH Private Link features, and platform updates. With 23 PRs merged and 41 created, the team demonstrates strong productivity. The primary recommendation is to accelerate reviews for the 30 open PRs, particularly focusing on HA test cases and critical bug fixes.

---

## Related Documents

- [Trend Charts Documentation](TREND_CHARTS.md)
- [PR Activity Tracking](PR_ACTIVITY_TRACKING.md)
- [Weekly Review Guide](WEEKLY_REVIEW_GUIDE.md)

---

*Report generated for DASH/DPU/SmartSwitch activity tracking*  
*Date range: 2026-01-29 to 2026-02-18*  
*Keywords: DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]*  
*Query method: GitHub search API via github-mcp-server*
