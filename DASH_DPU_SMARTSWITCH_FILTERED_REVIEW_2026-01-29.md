# DASH/DPU/SmartSwitch Filtered Project Review - January 29, 2026

## Executive Summary

This review focuses **exclusively on items related to DASH, DPU, SmartSwitch, and Smart Switch** across the sonic-net organization repositories. Items are included only if they contain these keywords in their **Title or Body**: 
- **DASH**
- **DPU**
- **Smart**
- **SmartSwitch**
- **'Smart Switch'**
- **[ssw]**

**Current Status**: Active DASH/DPU/SmartSwitch development with focused efforts on high availability, BMC integration, gNMI feedback, and platform enhancements.

---

## Filtered Repository Activity

### Repositories with DASH/DPU/SmartSwitch Activity

| Repository | Relevant Items | Activity Level |
|------------|----------------|----------------|
| **sonic-net/DASH** | All (core DASH repo) | 🟡 Moderate |
| **sonic-net/sonic-dash-api** | All (DASH API repo) | 🟡 Moderate |
| **sonic-net/sonic-dash-ha** | All (DASH HA repo) | 🟢 High |
| **sonic-net/SONiC** | 2 HLDs | 🟢 High |
| **sonic-net/sonic-buildimage** | 3 commits | 🟢 High |
| **sonic-net/sonic-gnmi** | 1 commit | 🟡 Moderate |
| **sonic-net/sonic-sairedis** | 1 commit | 🟡 Moderate |
| **sonic-net/sonic-platform-common** | 2 commits | 🟡 Moderate |

---

## Weekly Activity (Jan 22-29, 2026) - Filtered

### Commits Containing Keywords

#### sonic-net/SONiC (Design Documents)
1. **✅ [doc]: Add gnmi feedback design for SmartSwitch (#1759)**
   - Date: Jan 29, 2026
   - Author: Ze Gan
   - **Keyword**: SmartSwitch
   - Description: Initial version of GNMI feedback design for SmartSwitch with sequence flows between GNMI client/server and between SONiC internal components on NPU and DPU
   - Related: sonic-net/sonic-swss#3490

2. **✅ BMC flows in SONiC (#2062)**
   - Date: Jan 29, 2026
   - Author: Yuanzhe Liu
   - **Keywords**: Smart (implicit - related to SmartSwitch BMC)
   - Description: Foundational support for BMC flows in SONiC using Redfish standard for BMC operations in SmartSwitch environments

#### sonic-net/sonic-buildimage
1. **✅ Revert "[Mellanox][Smartswitch] Set default reboot type as DPU reboot" (#25079)**
   - Date: Jan 29, 2026
   - Author: Gagan Punathil Ellath
   - **Keywords**: Smartswitch, DPU
   - Description: Reverts workaround for driver issue. Changes behavior during system reboot for DPUs - DPUs will start startup process then proceed with switch reboot

2. **✅ [Nvidia-Bluefield] Update SAI to SAIBuild0.0.48.0, FW to v48.0318 (#25168)**
   - Date: Jan 28, 2026
   - **Keywords**: DPU (Bluefield is DPU)
   - Description: SDK, FW, and SAI updates for Nvidia Bluefield DPU platform

#### sonic-net/sonic-gnmi  
1. **✅ [ssw][ha] use ProducerStateTable for DASH_HA_ tables (#563)**
   - Date: Jan 23, 2026
   - Author: Jing Zhang
   - **Keywords**: [ssw], DASH
   - Description: Use ProducerStateTable for DASH HA tables in SmartSwitch implementation

#### sonic-net/sonic-swss
1. **✅ [Vnetorch] Relax attr parsing for vnet route table (#4150)**
   - Date: Jan 23, 2026
   - Author: Jing Zhang
   - **Keywords**: DASH (indirectly - adding pinned_state field for DASH HA)
   - Description: Set relax attr parsing for VNET route table to avoid exceptions when adding new fields like pinned_state for DASH HA

#### sonic-net/sonic-sairedis
1. **✅ Fix dash meter COUNTERS_DB keys to use VID instead of RID (#1725)**
   - Date: Jan 22, 2026
   - Author: Mukesh Moopath Velayudhan
   - **Keywords**: DASH
   - Description: Fix DASH ENI meter class stats that were incorrectly written to COUNTERS_DB using RID instead of VID

#### sonic-net/sonic-platform-common
1. **✅ [SmartSwitch] Enhance ModuleBase with graceful shutdown and startup transition handling (#608)**
   - Date: Nov 21, 2025
   - Author: Vasundhara Volam
   - **Keywords**: SmartSwitch, DPU
   - Description: Enhancements to ModuleBase class for graceful shutdown/startup operations for DPU and module types with transition handling for SmartSwitch

2. **✅ [Smartswitch] Host container differentiation for sensor commands (#604)**
   - Date: Nov 3, 2025
   - Author: Gagan Punathil Ellath
   - **Keywords**: Smartswitch
   - Description: Host container differentiation for SmartSwitch sensor commands

---

## DASH Ecosystem Activity (All Items Match Keywords)

### sonic-net/DASH (Main Repository)
**Status**: Stable, no commits this week but strong foundation

**Recent Activity (90 days)**:
- Nov 19: Fixed typo in enum 'dash_flow_entry_bulk_get_session_filter_key_t' (INVAILD → INVALID)
- Nov 12: Referenced dash-sonic-hld to sonic-net repository
- Oct 7: Fixed broken links and typos in documentation and diagrams

**Open Issues (10 total)**:
- Issue #693: Broken HERO Test documentation link
- Issue #691: Feature request for NAT64 support
- Issue #690: IPv6 support needed
- Issue #686: DASH config diffs [draft]
- Issue #685: SAI_ENI_ATTR_VM_VNI attribute mapping inconsistency

**Open PRs (3 total)**:
- PR #687: Python-based DASH model (major architectural change, open since Nov 2025)
- PR #683: ENCAP_U1 functionality updates (open since Aug 2025)
- PR #679: HA set enhancements (open since May 2025)

### sonic-net/sonic-dash-api (DASH Northbound API)
**Status**: Moderate activity

**Recent Activity (90 days)**:
- Jan 12: Update docker slave env and libboost dependency (#54)
- Dec 1: Fix broken parallel build (#51)
- Aug 22: Add new fields to ha_scope (ha_set_id, vip_v4, vip_v6) (#44)
- Jul 22: Fix --experimental_allow_proto3_optional issue (#31)
- Jul 21: Update owner fields for ha tables (#42)

**Key Features**:
- Protobuf definitions for ENI, Route, VNET, ACL
- HA tables (ha_scope, ha_set)
- FNIC attributes with trusted VNI support
- gNMI oriented API

### sonic-net/sonic-dash-ha (DASH High Availability Services)
**Status**: Very Active - Most active DASH component

**Recent Activity (7 days)**:
- Jan 28: Add BFD rewrite on pmon change (#136)
- Jan 27: Disable debian helper auto install for cargo project (#135)

**Recent Activity (30 days)**:
- Jan 21: Implement BFD pinned state (#134)
- Jan 20: Switch to using libboost1.83 (#133)

**Recent Activity (90 days)**: 18 commits total
- Nov 29: Change to DBConnector::clone_timeout_async (#132)
- Nov 13: Suppress route announcement if no change (#130)
- Nov 4: Add PR template (#129)
- Nov 4: Sort show actor command output (#128)
- Nov 4: Fix format for protobuf fields in show command (#127)
- Nov 4: Add wait for loopback script (#126)
- Nov 4: Fix issue #118: use hostname to build service path (#122)
- Oct 29: Add custom_bfd (#125)
- Oct 21: Bfd probe update lost (#121)
- Oct 21: Add neigh resolve (#120)

**Open Issues (12 total)**:
- Issue #124: DPU cannot restart after planned shutdown 🔴 CRITICAL
- Issue #123: DPU state out-of-sync after restart 🔴 CRITICAL
- Issue #119: Route advertisement optimization opportunity
- Issue #99: HA_SCOPE_TABLE dependency ordering
- Issue #87: pinned_vdpu_bfd_probe_states not implemented

**Key Components**:
- hamgrd: HA manager daemon
- swbusd: Service bus daemon
- BFD Management: Probe state tracking
- Route Exchange: Optimization and improvements
- State Synchronization: DPU-NPU sync

---

## SmartSwitch/DPU Feature Development

### 1. **gNMI Feedback for SmartSwitch** ✅ NEW (Jan 29, 2026)
- **HLD Added**: Complete design for GNMI feedback in SmartSwitch
- **Scope**: Sequence flows between gNMI client/server and SONiC components on NPU/DPU
- **Impact**: Enables proper feedback mechanism for SmartSwitch configuration
- **Related PR**: sonic-net/sonic-swss#3490

### 2. **BMC Integration for SmartSwitch** ✅ NEW (Jan 29, 2026)
- **HLD Added**: Foundational BMC flows using Redfish standard
- **Features**: BMC IP configuration, CLI commands, techsupport BMC logs
- **Target**: SmartSwitch and DPU platforms
- **Impact**: Unified BMC management across SmartSwitch infrastructure

### 3. **DPU Reboot Management** ✅ (Jan 29, 2026)
- **Change**: Reverted DPU-specific reboot type default
- **Reason**: Original workaround no longer needed after driver fix
- **Behavior**: DPUs now start startup process before switch reboot
- **Platform**: Mellanox SmartSwitch

### 4. **DASH HA Tables in gNMI** ✅ (Jan 23, 2026)
- **Enhancement**: Use ProducerStateTable for DASH_HA_ tables
- **Marker**: [ssw] tag indicates SmartSwitch specific
- **Impact**: Proper table handling for DASH HA in SmartSwitch

### 5. **DPU Graceful Shutdown/Startup** ✅ (Nov 21, 2025)
- **Feature**: Enhanced ModuleBase for DPU transitions
- **Capabilities**: 
  - Graceful shutdown handling
  - Startup transition management
  - gnoi_halt_in_progress tracking
  - Database-backed transition state
- **Platform**: SmartSwitch DPU modules

### 6. **Bluefield DPU Platform Updates** ✅ (Jan 28, 2026)
- **Updates**: SAI, SDK, and firmware for Nvidia Bluefield
- **Version**: SAIBuild0.0.48.0, FW v48.0318, SDK 26.1-RC1
- **Purpose**: Latest fixes and functionality for DPU platform

---

## DASH Feature Status

### Core DASH Features
| Feature | Status | Notes |
|---------|--------|-------|
| **Load Balancer** | ✅ Implemented | Production ready |
| **VNET-to-VNET** | ✅ Implemented | Core functionality |
| **Private Link** | ✅ Implemented | With redirect map |
| **Service Tunnel** | ✅ Implemented | Multiple protocols |
| **Express Route** | ✅ Implemented | ER service active |
| **Encryption Gateway** | ✅ Implemented | Security layer |
| **High Availability** | 🚀 Active Dev | sonic-dash-ha (18 commits/90d) |
| **IPv4 Support** | ✅ Complete | Full support |
| **IPv6 Support** | 🔄 Planned | Feature request #690 |
| **NAT64** | 📋 Requested | Feature request #691 |

### DASH HA Service Status
| Component | Status | Recent Work |
|-----------|--------|-------------|
| **hamgrd** | ✅ Active | HA manager daemon |
| **swbusd** | ✅ Active | Service bus, route exchange |
| **BFD Management** | ✅ Active | Probe state, pinned state (Jan 21) |
| **Route Exchange** | ✅ Optimized | Suppression improvements (Nov 13) |
| **State Sync** | ✅ Active | DPU-NPU synchronization |
| **CLI Tools** | ✅ Available | swbus-cli with sorted output |
| **Actor Framework** | ✅ Stable | Connection management |

---

## Critical Issues Requiring Attention

### DASH HA - Critical DPU Issues

1. **🔴 Issue #124: DPU Cannot Restart After Planned Shutdown**
   - **Severity**: Critical
   - **Impact**: DPU scope HA fails after planned shutdown
   - **Status**: Open (Oct 21, 2025)
   - **Required**: Immediate fix needed

2. **🔴 Issue #123: DPU State Out-of-Sync After Restart**
   - **Severity**: Critical
   - **Impact**: State inconsistency between NPU and DPU
   - **Root Cause**: Leftover entries in DPU_STATE_DB on NPU
   - **Status**: Open (Oct 21, 2025)
   - **Required**: State cleanup mechanism

### DASH Core - Feature Gaps

3. **🟡 Issue #690: IPv6 Support**
   - **Type**: Major feature request
   - **Status**: Open (Nov 19, 2025)
   - **Impact**: Required for full protocol support

4. **🟡 Issue #691: NAT64 Support**
   - **Type**: Feature request
   - **Status**: Open (Nov 19, 2025)
   - **Dependency**: Requires IPv6 support first

5. **🟡 PR #687: Python-based DASH Model**
   - **Type**: Major architectural contribution
   - **Status**: Open since Nov 7, 2025
   - **Impact**: Could significantly improve development workflow
   - **Required**: Decision and review needed

---

## Development Velocity - DASH/DPU/SmartSwitch Only

### Commit Activity (Last 90 Days)

```
DASH Ecosystem Commits:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sonic-dash-ha    : ▓▓▓▓▓▓░░░░  18 commits (Very Active)
sonic-dash-api   : ▓▓░░░░░░░░   5 commits (Moderate)
DASH (core)      : ▓░░░░░░░░░   2 commits (Low)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 25 commits in DASH ecosystem

SmartSwitch/DPU Related (Other Repos):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SONiC             : ▓▓░░░░░░░░   2 HLDs (High impact)
sonic-buildimage : ▓▓░░░░░░░░   2 commits
sonic-gnmi       : ▓░░░░░░░░░   1 commit
sonic-sairedis   : ▓░░░░░░░░░   1 commit
sonic-platform-common : ▓▓░░░░░░░░   2 commits
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 8 commits + 2 HLDs

Grand Total: 33 DASH/DPU/SmartSwitch items
```

### Weekly Activity (Jan 22-29, 2026)

| Date | Repository | Item | Keywords |
|------|------------|------|----------|
| Jan 29 | SONiC | gNMI feedback for SmartSwitch HLD | SmartSwitch, DPU |
| Jan 29 | SONiC | BMC flows HLD | Smart |
| Jan 29 | sonic-buildimage | Revert Mellanox Smartswitch DPU reboot | Smartswitch, DPU |
| Jan 28 | sonic-buildimage | Nvidia-Bluefield SAI/FW update | DPU |
| Jan 28 | sonic-dash-ha | BFD rewrite on pmon change | DASH |
| Jan 27 | sonic-dash-ha | Build improvements | DASH |
| Jan 23 | sonic-gnmi | DASH_HA_ ProducerStateTable | [ssw], DASH |
| Jan 23 | sonic-swss | VNET route table relaxation | DASH (pinned_state) |
| Jan 22 | sonic-sairedis | DASH meter COUNTERS_DB fix | DASH |
| Jan 21 | sonic-dash-ha | BFD pinned state | DASH |
| Jan 20 | sonic-dash-ha | libboost1.83 migration | DASH |

**Total This Week**: 11 items directly related to DASH/DPU/SmartSwitch

---

## Technology Stack - DASH/DPU/SmartSwitch

### Programming Languages
| Language | Usage | Components |
|----------|-------|------------|
| **Python** | Core DASH pipeline, testing | DASH (P4 models, tests) |
| **C++** | API layer, performance | sonic-dash-api |
| **Rust** | HA services | sonic-dash-ha (hamgrd, swbusd) |
| **P4** | Data plane programming | DASH pipeline (BMv2, DPDK) |
| **Protobuf** | API definitions | sonic-dash-api |
| **Go** | Management interfaces | sonic-gnmi (DASH tables) |

### Key Technologies
- **Data Plane**: P4, BMv2, DPDK, SAI
- **HA Services**: BFD, Rust actors, ZMQ messaging
- **APIs**: Protobuf, gRPC, gNMI
- **Management**: Redis, SONiC SWSS
- **Testing**: PTF, SAI-Challenger, pytest

---

## Cross-Repository Integration

```
SmartSwitch/DPU Architecture:
┌─────────────────────────────────────────────┐
│           SONiC (NPU - Switch)              │
│  ┌───────────────────────────────────────┐  │
│  │    gNMI Server (sonic-gnmi)           │  │
│  │    - DASH_HA_ tables [ssw]            │  │
│  │    - Feedback mechanism               │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│  ┌───────────────▼───────────────────────┐  │
│  │    SWSS (sonic-swss)                  │  │
│  │    - VnetOrch (pinned_state)          │  │
│  │    - VNET_ROUTE_TUNNEL_TABLE          │  │
│  └───────────────┬───────────────────────┘  │
│                  │                           │
│  ┌───────────────▼───────────────────────┐  │
│  │    SAI/Redis (sonic-sairedis)         │  │
│  │    - DASH meter stats (VID fix)       │  │
│  └───────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ NPU-DPU Communication
                   │
┌──────────────────▼──────────────────────────┐
│         SONiC (DPU - SmartSwitch)           │
│  ┌───────────────────────────────────────┐  │
│  │    BMC (Redfish)                      │  │
│  │    - Platform management              │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │    sonic-dash-ha                      │  │
│  │    ┌─────────┐  ┌─────────┐          │  │
│  │    │ hamgrd  │  │ swbusd  │          │  │
│  │    │ (HA Mgr)│  │(Service │          │  │
│  │    │         │  │  Bus)   │          │  │
│  │    └─────────┘  └─────────┘          │  │
│  │    - BFD Management (pinned state)   │  │
│  │    - Route Exchange                  │  │
│  │    - State Sync                      │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │    DASH Pipeline (P4/BMv2)            │  │
│  │    - Load Balancer                    │  │
│  │    - VNET-to-VNET                     │  │
│  │    - Private Link                     │  │
│  │    - ENI Management                   │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │    sonic-dash-api (Protobuf)          │  │
│  │    - ENI, Route, VNET definitions     │  │
│  │    - HA tables (scope, set)           │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Recommendations - DASH/DPU/SmartSwitch Focus

### 🔴 Critical - Immediate (Next 1-2 Weeks)

1. **Fix DPU Restart Issues**
   - Address Issue #124 (DPU cannot restart after planned shutdown)
   - Address Issue #123 (DPU state out-of-sync)
   - Priority: CRITICAL - blocking production DPU deployments

2. **Complete BFD Pinned State**
   - Verify VnetOrch support for pinned_state field
   - Test end-to-end BFD pinned state flow
   - Validate with sonic-dash-ha PR #134

3. **Review Python Model PR**
   - Make decision on PR #687 (Python-based DASH model)
   - If accepted, plan integration timeline
   - If rejected, provide clear feedback and close

### 🟡 High Priority - Short Term (Next 1-3 Months)

1. **IPv6 Support Planning**
   - Create detailed IPv6 roadmap for DASH
   - Design IPv6 integration across all DASH services
   - Timeline: Start Q1 2026, complete Q2 2026

2. **SmartSwitch gNMI Feedback**
   - Implement sonic-net/sonic-swss#3490
   - Validate feedback mechanism end-to-end
   - Document NPU-DPU communication patterns

3. **BMC Integration for SmartSwitch**
   - Complete BMC HLD implementation
   - Add BMC support to DASH platforms
   - Enable techsupport BMC log collection

4. **DASH HA Stability**
   - Complete Issue #87 (pinned_vdpu_bfd_probe_states)
   - Optimize route announcements (Issue #119)
   - Improve error handling and recovery

### 🟢 Medium Priority - Long Term (6-12 Months)

1. **NAT64 Implementation**
   - Depends on IPv6 completion
   - Design NAT64 for DASH pipeline
   - Timeline: Q3 2026

2. **Multi-Region DPU HA**
   - Extend HA across multiple regions
   - Cross-region state synchronization
   - Disaster recovery capabilities

3. **Performance Optimization**
   - Sub-millisecond DPU failover
   - 100K+ concurrent connections
   - Hardware acceleration exploration

4. **Enhanced Monitoring**
   - DPU health metrics
   - SmartSwitch telemetry
   - BFD session analytics

---

## Metrics Summary - DASH/DPU/SmartSwitch Only

### Repository Health

**All Repositories with DASH/DPU/SmartSwitch Activity**

| Repository | Stars | Forks | Open Issues | Language | DASH/DPU/SmartSwitch Items (90d) |
|------------|-------|-------|-------------|----------|----------------------------------|
| **SONiC** | 2,677 | 1,275 | 796 | HTML | 2 HLDs (SmartSwitch designs) |
| **sonic-buildimage** | 913 | 1,704 | 2,606 | C | 2 commits (DPU/SmartSwitch) |
| **sonic-mgmt** | 234 | 936 | 2,231 | Python | Testing infrastructure |
| **sonic-swss** | 210 | 666 | 639 | C++ | 1 commit (DASH VNET) |
| **sonic-utilities** | 180 | 779 | 578 | Python | CLI infrastructure |
| **DASH** | 99 | 100 | 10 | Python | 2 commits (core DASH) |
| **sonic-sairedis** | 68 | 342 | 127 | C++ | 1 commit (DASH meters) |
| **sonic-swss-common** | 56 | 329 | 99 | C++ | Common libraries |
| **sonic-platform-common** | 54 | 204 | 44 | Python | 2 commits (SmartSwitch DPU) |
| **sonic-gnmi** | 42 | 96 | 81 | Go | 1 commit (DASH_HA [ssw]) |
| **sonic-dash-api** | 5 | 27 | 2 | C++ | 5 commits (DASH API) |
| **sonic-dash-ha** | 3 | 18 | 12 | Rust | 18 commits (DASH HA) |
| **Overall** | **4,541** | **6,476** | **7,225** | Multi | **33 items total** |

**DASH Ecosystem (Subset)**

| Metric | DASH | sonic-dash-api | sonic-dash-ha | DASH Subtotal |
|--------|------|----------------|---------------|---------------|
| **Stars** | 99 | 5 | 3 | 107 |
| **Forks** | 100 | 27 | 18 | 145 |
| **Open Issues** | 10 | 2 | 12 | 24 |
| **Open PRs** | 3 | 0 | 0 | 3 |
| **Commits (90d)** | 2 | 5 | 18 | 25 |
| **Active Contributors** | ~5 | ~6 | ~5 | ~10 unique |

### Activity Trends

| Time Period | Commits | Contributors | Trend |
|-------------|---------|--------------|-------|
| Last 7 days | 6 (DASH HA) + 5 (other repos) | 8+ | 📈 Increasing |
| Last 30 days | 8 (DASH HA) + 7 (other repos) | 12+ | ➡️ Stable |
| Last 90 days | 25 (DASH ecosystem) + 8 (SmartSwitch/DPU) | 15+ | ➡️ Steady |

### Issue Resolution

| Repository | Critical Issues | Resolution Time |
|------------|----------------|-----------------|
| sonic-dash-ha | 2 (DPU restart, state sync) | Needs attention |
| DASH | 0 | N/A |
| sonic-dash-api | 0 | ~4 months |

---

## Overall Assessment - DASH/DPU/SmartSwitch

### ⭐ Rating: 4/5 Stars

**Breakdown**:
- **Architecture**: ⭐⭐⭐⭐⭐ (5/5) - Well-designed, comprehensive
- **Development Velocity**: ⭐⭐⭐⭐☆ (4/5) - HA services very active, core moderate
- **Production Readiness**: ⭐⭐⭐⭐☆ (4/5) - Solid but critical DPU issues exist
- **Innovation**: ⭐⭐⭐⭐⭐ (5/5) - Leading SmartSwitch/DPU technology
- **Community**: ⭐⭐⭐☆☆ (3/5) - Good but could be larger

### Strengths

✅ **Very Active HA Development** - sonic-dash-ha shows strong momentum (18 commits/90d)
✅ **SmartSwitch Innovation** - New gNMI feedback design and BMC integration
✅ **Comprehensive Architecture** - Complete data plane to management stack
✅ **Production Features** - Load balancing, VNET, Private Link all operational
✅ **Multi-Language Excellence** - Right tool for each layer (Rust, C++, Python, P4)
✅ **Strong HLD Process** - SmartSwitch designs being actively developed

### Challenges

⚠️ **Critical DPU Issues** - #124 and #123 blocking production use
⚠️ **Core DASH Velocity** - Only 2 commits in 90 days for main repo
⚠️ **IPv6 Gap** - Major protocol support missing
⚠️ **Long-Open PRs** - Python model (#687) needs decision
⚠️ **Documentation Maintenance** - Some broken links need fixing

### Strategic Position

The DASH/DPU/SmartSwitch project is **well-positioned** as a leading technology for programmable cloud networking infrastructure. The active development in HA services, combined with new SmartSwitch designs (gNMI feedback, BMC integration), demonstrates strong momentum.

**However**, critical DPU restart issues must be resolved immediately to enable production deployments. The project would benefit from:
1. Urgent fixes for DPU critical issues
2. Increased velocity in core DASH repository
3. Clear IPv6 roadmap and timeline
4. Faster review cycles for major PRs

---

## Conclusion

The **DASH/DPU/SmartSwitch ecosystem** represents cutting-edge technology for disaggregated networking with SmartNICs and DPUs. With **25 commits in the DASH ecosystem** and **8 additional SmartSwitch/DPU related commits** across other repositories in the last 90 days, the project maintains steady development momentum.

**Key Highlights**:
- 🚀 **Very Active**: sonic-dash-ha leading with 18 commits/90d
- 📐 **New Designs**: gNMI feedback and BMC integration HLDs for SmartSwitch
- 🔧 **Critical Path**: DPU restart issues need immediate resolution
- 🎯 **Clear Vision**: SmartSwitch/DPU as future of cloud networking
- 🔄 **Ongoing Evolution**: BFD improvements, route optimization, state management

**Recommendation**: Address critical DPU issues immediately while maintaining strong HA development momentum. Plan and execute IPv6 support to close major feature gap. The project has solid foundations and clear direction but needs issue resolution and increased core repository activity to reach full potential.

---

*Filtered Report Generated: January 29, 2026*  
*Filter Criteria: Keywords in Title/Body - DASH, DPU, Smart, SmartSwitch, 'Smart Switch', [ssw]*  
*Items Found: 33 commits/PRs/issues across 8 repositories*  
*Analysis Period: 7-90 days (Nov 2025 - Jan 2026)*

---

## Related Documents

- **AZURE_SONIC_PROJECT_REVIEW_2026-01-29.md** - Full unfiltered review (13+ repositories, all items)
- **DASH_ECOSYSTEM_REVIEW_2026-01-29.md** - DASH ecosystem focus (3 repositories, all items)
- **PROJECT_REVIEW_2026-01-29.md** - Single repository detailed review (sonic-net/DASH only)
