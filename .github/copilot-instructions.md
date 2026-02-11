# Copilot Instructions for DASH

## Project Overview

DASH (Disaggregated APIs for SONiC Hosts) extends SONiC functionality to stateful workloads running on SmartNICs, DPUs (Data Processing Units), and smart switches. It defines APIs and behavioral models for high-performance network services like VNET-to-VNET communication, load balancing, NAT, and ACLs — targeting 10-100x performance improvements over traditional software implementations.

## Architecture

```
DASH/
├── documentation/              # Design docs, HLDs, requirements
│   ├── general/                # High-level design documents
│   │   ├── dash-high-level-design.md
│   │   ├── dash-sonic-hld.md   # SONiC integration HLD
│   │   └── sdn-features-packet-transforms.md
│   ├── dataplane/              # Data plane specifications
│   ├── load-bal-service/       # Load balancer service design
│   └── README.md               # Documentation table of contents
├── dash-pipeline/              # P4 behavioral model pipeline
│   ├── bmv2/                   # BMv2 behavioral model
│   ├── SAI/                    # SAI API auto-generation
│   └── tests/                  # Pipeline tests
├── test/                       # Test infrastructure
│   ├── test-cases/             # Test case definitions
│   └── docs-tests/             # Documentation tests
├── .github/
│   └── workflows/              # GitHub Actions CI (BMv2 CI, spellcheck)
├── Governance.md               # Project governance
└── README.md
```

### Key Concepts
- **DPU/SmartNIC**: Programmable network devices that offload network functions from the host CPU
- **Behavioral Model (BMv2)**: P4-based software model simulating DPU/SmartNIC behavior
- **SAI for DASH**: Extended SAI APIs for stateful packet processing (DASH SAI)
- **SDN transforms**: Packet encapsulation/decapsulation for VNET, load balancing, NAT
- **HERO test**: High-performance stress test for DPU hardware validation

## Language & Style

- **Documentation**: Markdown with standard SONiC HLD format
- **P4**: P4_16 language for behavioral model pipeline definitions
- **Python**: Test scripts and automation
- **Default branch**: `main` (not `master`)
- **Naming**: Follow SONiC conventions for SAI objects and tables
- **Diagrams**: Use Mermaid or embedded images in documentation

## Build Instructions

```bash
# Build BMv2 behavioral model (requires P4 toolchain)
cd dash-pipeline
make

# Run CI tests
# See .github/workflows/ for CI pipeline definitions
```

## Testing

- **BMv2 CI**: Automated tests run against the P4 behavioral model
- **Test cases**: Defined in `test/test-cases/`
- **Spellcheck**: Documentation spellcheck via GitHub Actions

## Documentation

- Start with `documentation/general/dash-high-level-design.md` for architecture overview
- `documentation/general/dash-sonic-hld.md` for SONiC integration design
- `documentation/general/sdn-features-packet-transforms.md` for networking scenarios

## PR Guidelines

- **Signed-off-by**: Required on all commits
- **CLA**: Sign Linux Foundation EasyCLA
- **Documentation PRs**: Follow the HLD template format; include diagrams
- **SAI changes**: API changes must be coordinated with SAI maintainers
- **P4 changes**: Must pass BMv2 CI tests
- **Spellcheck**: Documentation must pass the spellcheck workflow
- **Base branch**: PRs target `main` (not `master`)

## Gotchas

- **Default branch is `main`**: Not `master` — use the correct base branch for PRs
- **P4 toolchain**: Building the behavioral model requires P4 compiler and BMv2 runtime
- **SAI generation**: DASH SAI APIs are auto-generated from specifications — don't edit generated files
- **Stateful processing**: DASH handles connection tracking and stateful NAT — different from traditional SAI
- **Multi-vendor**: APIs must be vendor-neutral — avoid hardware-specific assumptions
- **Performance targets**: DASH aims for hardware-level performance — design with DPU offload in mind
- **Documentation-heavy**: Many PRs are documentation/design — follow the HLD process
