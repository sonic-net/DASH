# DASH/DPU/SmartSwitch Weekly Review
**Period:** May 14 – May 20, 2026 (7 days)
**Report Generated:** May 20, 2026
**Query Keywords:** DPU, DASH, SmartSwitch, Smart

---

## Executive Summary

This report covers activity from **May 14 – May 20, 2026** across the sonic-net organization, focusing on PRs containing DASH, DPU, SmartSwitch, or Smart keywords in titles or descriptions.

### Key Metrics
- **26 PRs Created** during the period
- **13 PRs Merged** during the period
- **10 Active Repositories** with DASH/DPU/SmartSwitch activity
- **Merge Rate:** 50.0% (13 merged out of 26 created)
- **Creation Velocity:** 3.7 PRs/day
- **Merge Velocity:** 1.9 PRs/day

### Highlights
- Highest PR creation volume: **sonic-buildimage** (6 created)
- Highest merge volume: **sonic-mgmt** (6 merged)
- Strong emphasis on SmartSwitch HA reliability, DPU lifecycle operations, and DASH scaling work
- Continued cross-repo coordination across mgmt, buildimage, gNMI, SWSS, and DASH HA components

---

## Repository Health

Overview of repositories with DASH/DPU/SmartSwitch activity during May 14 – May 20, 2026:

| Repository | Stars | Forks | Open Issues | Relevant Items | Activity Level |
|------------|-------|-------|-------------|----------------|----------------|
| sonic-net/sonic-mgmt | 261 | 1044 | 2266 | 6 PRs merged + 6 PRs created | 🟢 Very High |
| sonic-net/sonic-buildimage | 969 | 1837 | 2995 | 4 PRs merged + 6 PRs created | 🟢 Very High |
| sonic-net/sonic-sairedis | 80 | 394 | 166 | 0 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/sonic-dash-ha | 4 | 24 | 14 | 0 PRs merged + 3 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss-common | 58 | 347 | 114 | 1 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-swss | 228 | 704 | 691 | 0 PRs merged + 2 PRs created | 🟡 Moderate |
| sonic-net/sonic-dash-api | 5 | 34 | 1 | 1 PRs merged + 1 PRs created | 🟡 Moderate |
| sonic-net/sonic-gnmi | 45 | 113 | 80 | 1 PRs merged + 1 PRs created | 🟡 Moderate |
| sonic-net/sonic-utilities | 184 | 842 | 643 | 0 PRs merged + 1 PRs created | 🟡 Low |
| sonic-net/SONiC | 2802 | 1314 | 871 | 0 PRs merged + 1 PRs created | 🟡 Low |

**Note:** Repositories included only if they have PRs with DASH/DPU/SmartSwitch/Smart keywords in title or body during the query period.

---

## PRs Created (May 14 – May 20, 2026)

### Summary
- **Total:** 26 PRs
- **Top Repository:** sonic-buildimage (6 PRs created)
- **Key Themes:** SmartSwitch HA workflows, DPU recovery and reboot behavior, DASH data-path scaling, and ZMQ optimization

### All Created PRs (Complete List):

| # | Repository | PR | Title | Created | Keywords |
|---|------------|-----|-------|---------|----------|
| 1 | sonic-net/sonic-swss-common | [#1188](https://github.com/sonic-net/sonic-swss-common/pull/1188) | swsscommon: expose batched ZmqProducerStateTable APIs to SWIG | May 14 | DASH |
| 2 | sonic-net/sonic-gnmi | [#675](https://github.com/sonic-net/sonic-gnmi/pull/675) | MixedDbClient: batch ZMQ Set/Del for multi-key gNMI updates (#27250) | May 14 | DASH DPU |
| 3 | sonic-net/sonic-buildimage | [#27382](https://github.com/sonic-net/sonic-buildimage/pull/27382) | NH-5010 - Set GRUB timeout_style=countdown | May 14 | Smart |
| 4 | sonic-net/sonic-buildimage | [#27384](https://github.com/sonic-net/sonic-buildimage/pull/27384) | NH-5010 - Set GRUB timeout_style=countdown | May 14 | Smart |
| 5 | sonic-net/sonic-buildimage | [#27385](https://github.com/sonic-net/sonic-buildimage/pull/27385) | [build]: Add dpu-auto-recovery feature to init_cfg.json.j2 | May 14 | DPU SmartSwitch |
| 6 | sonic-net/sonic-dash-ha | [#164](https://github.com/sonic-net/sonic-dash-ha/pull/164) | Add brainsplit_recovered | May 14 | DASH DPU Smart |
| 7 | sonic-net/sonic-buildimage | [#27387](https://github.com/sonic-net/sonic-buildimage/pull/27387) | [FC] Move DPU counter defaults to init_cfg.json (#20492) | May 14 | DASH DPU |
| 8 | sonic-net/SONiC | [#2336](https://github.com/sonic-net/SONiC/pull/2336) | [HLD] Add handling of role activation and bulk sync failures in HA state machine. | May 14 | DASH DPU |
| 9 | sonic-net/sonic-swss-common | [#1189](https://github.com/sonic-net/sonic-swss-common/pull/1189) | [202511][DASH] Add COUNTERS_ENI_OID_MAP table name to schema.h (#1177) | May 15 | DASH |
| 10 | sonic-net/sonic-swss | [#4574](https://github.com/sonic-net/sonic-swss/pull/4574) | Skip swss.rec updates for high volume dash child objects | May 15 | DASH |
| 11 | sonic-net/sonic-mgmt | [#24640](https://github.com/sonic-net/sonic-mgmt/pull/24640) | Fix: gNOI upgrade set_package fails when target_version is not provided | May 15 | DPU Smart |
| 12 | sonic-net/sonic-mgmt | [#24641](https://github.com/sonic-net/sonic-mgmt/pull/24641) | [BMC] Skip test_orchagent_heartbeat on BMC (no orchagent) | May 15 | SmartSwitch |
| 13 | sonic-net/sonic-utilities | [#4545](https://github.com/sonic-net/sonic-utilities/pull/4545) | Remove trailing dash from tunnelstat cache directory name | May 15 | DASH |
| 14 | sonic-net/sonic-swss | [#4578](https://github.com/sonic-net/sonic-swss/pull/4578) | [zmqorch]: Restore drain-until-empty consumer for non-DPU/fabric | May 15 | DASH DPU |
| 15 | sonic-net/sonic-buildimage | [#27411](https://github.com/sonic-net/sonic-buildimage/pull/27411) | [mellanox] Remove force power off during ONIE upgrade | May 15 | DPU SmartSwitch |
| 16 | sonic-net/sonic-mgmt | [#24701](https://github.com/sonic-net/sonic-mgmt/pull/24701) | [HA] Enhance planned SWO and shutdown tests | May 18 | DPU |
| 17 | sonic-net/sonic-mgmt | [#24703](https://github.com/sonic-net/sonic-mgmt/pull/24703) | [smartswitch]: Skip admin-down DPUs in sanity check and health_checker | May 18 | DPU SmartSwitch |
| 18 | sonic-net/sonic-mgmt | [#24704](https://github.com/sonic-net/sonic-mgmt/pull/24704) | [202511][ssw] move VDPU, DPU, REMOTE_DPU, VXLAN_TUNNEL, VNET generation from test fixture to golden config gen (#23605) | May 18 | DPU SmartSwitch |
| 19 | sonic-net/sonic-buildimage | [#27436](https://github.com/sonic-net/sonic-buildimage/pull/27436) | Nebius SmartSwitch SKU | May 18 | SmartSwitch |
| 20 | sonic-net/sonic-mgmt | [#24706](https://github.com/sonic-net/sonic-mgmt/pull/24706) | [ssw] fix PORT lanes validation | May 18 | DPU SmartSwitch |
| 21 | sonic-net/sonic-sairedis | [#1893](https://github.com/sonic-net/sonic-sairedis/pull/1893) | [DPU] Optimize Flow Sync Notification and fix cleanup for flow dumps | May 18 | DASH DPU |
| 22 | sonic-net/sonic-dash-ha | [#165](https://github.com/sonic-net/sonic-dash-ha/pull/165) | Improve Bulk Sync Workflow | May 18 | DPU |
| 23 | sonic-net/sonic-sairedis | [#1897](https://github.com/sonic-net/sonic-sairedis/pull/1897) | Improve smartswitch memory scaling by conditionally caching high volu… | May 19 | DASH SmartSwitch |
| 24 | sonic-net/sonic-dash-api | [#67](https://github.com/sonic-net/sonic-dash-api/pull/67) | Update the order of keys in ha_scope_config | May 19 | DASH |
| 25 | sonic-net/sonic-sairedis | [#1898](https://github.com/sonic-net/sonic-sairedis/pull/1898) | Improve SmartSwitch memory scaling | May 19 | DASH SmartSwitch |
| 26 | sonic-net/sonic-dash-ha | [#167](https://github.com/sonic-net/sonic-dash-ha/pull/167) | Add version to npu DASH_HA_SCOPE_STATE | May 20 | DASH DPU |

---

## PRs Merged (May 14 – May 20, 2026)

### Summary
- **Total:** 13 PRs
- **Top Repository:** sonic-mgmt (6 PRs merged)
- **Key Themes:** max-scale DASH enablement, SmartSwitch platform boot/reboot stability, and DPU telemetry/counter plumbing

### All Merged PRs (Complete List):

| # | Repository | PR | Title | Merged | Keywords |
|---|------------|-----|-------|--------|----------|
| 1 | sonic-net/sonic-mgmt | [#24136](https://github.com/sonic-net/sonic-mgmt/pull/24136) | Dpu uptime and graceful reboot enhancements | May 14 | DPU SmartSwitch |
| 2 | sonic-net/sonic-mgmt | [#24573](https://github.com/sonic-net/sonic-mgmt/pull/24573) | [smartswitch]: Allow testbed.yaml to select which DPUs are admin-up | May 14 | DPU SmartSwitch |
| 3 | sonic-net/sonic-buildimage | [#27207](https://github.com/sonic-net/sonic-buildimage/pull/27207) | [202511] [Mellanox] [DPU] Update FW to 48.1000, BFSoC to 4.14.0-13938, RSHIM to 2.6.6 | May 14 | DPU |
| 4 | sonic-net/sonic-buildimage | [#26679](https://github.com/sonic-net/sonic-buildimage/pull/26679) | [SmartSwitch] Support maximum dash configuration size | May 15 | DASH DPU SmartSwitch |
| 5 | sonic-net/sonic-mgmt | [#24564](https://github.com/sonic-net/sonic-mgmt/pull/24564) | [DASH] Update skip condition for DASH metering test on Nvidia | May 15 | DASH SmartSwitch |
| 6 | sonic-net/sonic-swss-common | [#1189](https://github.com/sonic-net/sonic-swss-common/pull/1189) | [202511][DASH] Add COUNTERS_ENI_OID_MAP table name to schema.h (#1177) | May 15 | DASH |
| 7 | sonic-net/sonic-buildimage | [#26764](https://github.com/sonic-net/sonic-buildimage/pull/26764) | [smartswitch] Start pmon after databasedpu instance services on SmartSwitch host (Fixes #26760) | May 15 | DPU SmartSwitch |
| 8 | sonic-net/sonic-mgmt | [#24229](https://github.com/sonic-net/sonic-mgmt/pull/24229) | [Smartswitch] Enable loganalyzer on DPUs | May 18 | DASH DPU SmartSwitch |
| 9 | sonic-net/sonic-mgmt | [#24046](https://github.com/sonic-net/sonic-mgmt/pull/24046) |  Update SmartSwitch HA test plan with identified test gaps | May 18 | DPU SmartSwitch |
| 10 | sonic-net/sonic-mgmt | [#23915](https://github.com/sonic-net/sonic-mgmt/pull/23915) | Add utility to upgrade DPU images for smartswitch testbeds | May 18 | DPU SmartSwitch |
| 11 | sonic-net/sonic-buildimage | [#27020](https://github.com/sonic-net/sonic-buildimage/pull/27020) | [aspeed][BMC] Do not mask sonic-hostservice.service on BMC images | May 19 | DPU |
| 12 | sonic-net/sonic-dash-api | [#67](https://github.com/sonic-net/sonic-dash-api/pull/67) | Update the order of keys in ha_scope_config | May 19 | DASH |
| 13 | sonic-net/sonic-gnmi | [#665](https://github.com/sonic-net/sonic-gnmi/pull/665) | Add DPU_COUNTERS_DB virtual path handling for DASH_METER and ENI counters | May 20 | DASH DPU |

---

## Recommendations

### High Priority
1. Continue tracking SmartSwitch HA and DPU reboot-path changes with focused regression coverage.
2. Monitor merge latency for high-volume repos to keep merge throughput aligned with incoming PR volume.
3. Maintain cross-repo linkage for DASH scale-path updates spanning buildimage, gNMI, SWSS, and management tests.

### Medium Priority
1. Keep validating ZMQ and bulk-update paths under scale to reduce orchestration hot-path overhead.
2. Capture follow-up risks for open SmartSwitch/DPU PRs in the next weekly report window.

---

## Metrics Summary

| Metric | Value |
|--------|-------|
| Period | May 14 – May 20, 2026 (7 days) |
| PRs Created | 26 |
| PRs Merged | 13 |
| Merge Rate | 50.0% |
| Creation Velocity | 3.7 PRs/day |
| Merge Velocity | 1.9 PRs/day |
| Active Repositories | 10 |
| Top Created Repo | sonic-buildimage (6) |
| Top Merged Repo | sonic-mgmt (6) |

---

## Conclusion

The May 14 – May 20 window shows focused delivery on SmartSwitch/DPU reliability and DASH scale plumbing, with steady merge execution across multiple repositories. The period includes several high-impact merges in buildimage/mgmt/gnmi plus a healthy queue of newly opened SmartSwitch and DASH work for subsequent weeks.

---

### Query Used
```
org:sonic-net is:pr created:2026-05-14..2026-05-20 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
org:sonic-net is:pr is:merged merged:2026-05-14..2026-05-20 (DPU OR DASH OR SmartSwitch OR Smart) in:title,body NOT [action] NOT submodule in:title
```

*Data source: GitHub Search API results retrieved on 2026-05-20.*
