# DASH BMv2 source build with Bazel

The Bazel path compiles the existing BMv2 P4 pipeline with the declared p4c
execution tool, runs the existing SAI generator in a private source tree, and
invokes the original SAI metadata and DASH library Make targets through
`rules_foreign_cc`. It does not invoke Debian packaging. Existing Docker/Make
builds remain available with their original source files.

The adapter copies the generated source directory into a private writable build
directory. It first selects the upstream `libsaimetadata.so` target, which
generates the metadata headers and library, then builds the DASH library. It
does not run the upstream metadata developer `all` target or its header-check
scripts; the native CI gates below validate the installed producer artifacts.
The private SAI archive reuses the landed registry `configurable_aspell.patch`
(pinned URL and integrity), and metadata generation selects the declared `aspell`
executable and dictionaries through `SAI_ASPELL`. The patch is an immutable
source input, not a module-registry endpoint. The legacy source tree keeps its
original system executable.

Both legacy compile recipes retain their warning policies, except that
`-Wmissing-include-dirs` stays a warning for the paired source/generated
search candidates provided by Bazel. Missing headers and other warnings promoted by `-Werror`
still fail the build.

The adapter links the declared PI, gRPC, protobuf and Abseil libraries into
`libsai.so`'s dependency list and rejects unresolved symbols at link time. The
runtime test also loads the extracted library with `RTLD_NOW` from a separate
program that does not link the SDK, then queries generated APIs with an SDK
consumer. This catches dependencies that a consumer's own linkage could hide.

Public targets:

| Target | Output |
| --- | --- |
| `//:runtime` | Stripped `libsai.so`, `libdashsaimetadata.so`, and four generated `/etc/dash` pipeline files |
| `//:runtime.debug_symbols` | Matching detached symbols under `/usr/lib/debug/.build-id` |
| `//:sdk` | Installed public headers and a DASH SAI library for C++ consumers to link |
| `//bazel:runtime_test` | Standalone runtime loading, installed SDK switch/generated DASH VIP API queries, pipeline validation, dependency closure, debug IDs/checksums, and GDB source-line lookup |

Native Trixie AMD64 and ARM64 are the validation configurations. Cross-compiling
the source generator/metadata executables is not supported. Set both platforms
for ARM64:

```sh
bazel test //bazel:runtime_test \
  --platforms=@sonic_build_infra//platforms:aarch64_trixie \
  --host_platform=@sonic_build_infra//platforms:aarch64_trixie
```

AMD64 is the default. Bazel 8.5.1, compiler/tool dependencies and generator wheels
are declared. The tests run `readelf`, `objcopy` and GDB from the CI environment to
inspect outputs. Compilation uses the declared shared toolchain and target
dependencies; target dependency imports do not count as source builds of those
external libraries.

`requirements_lock.txt` is checked-in Python dependency input.
`MODULE.bazel.lock` is ignored generated resolution state retained in CI evidence.
`-g` and `--strip=never` preserve build-time symbols; shared `sonic_deploy_tar`
rules split the deployed runtime and debug TARs from the same linked ELF.

Local builds and CI use the maintained registry `main` endpoint from `.bazelrc`.
PI, p4c, shared tools and foreign-build support are published there. CI does not
replace that endpoint with a temporary snapshot. Workflow artifacts contain both
TARs, checksums, the source revision, test results, the generated lock and the
resolved module graph. The recorded registry tips before and after the build
are observations of `main`, not a frozen registry selection.

The selected published modules are:

| Module | Published support |
| --- | --- |
| `rules_distroless@0.9.4.sonic.10` | [Declared C++ header roots, registry #96](https://github.com/securely1g/sonic-bazel-registry/pull/96) |
| `p4lang-pi@0.1.3.sonic.2` | [PI source and runtime metadata, registry #107](https://github.com/securely1g/sonic-bazel-registry/pull/107) |
| `p4c@1.2.4.2.sonic.2` | [P4C source and runtime metadata, registry #109](https://github.com/securely1g/sonic-bazel-registry/pull/109) |
| `sonic-build-infra@0.0.22-a12bc826d6f811a157db5c7c02a2fe033896cc14` | [Shared build tools and metadata, registry #120](https://github.com/securely1g/sonic-bazel-registry/pull/120) |
| `rules_foreign_cc@0.16.0.sonic.1` | [Header search classifications, registry #119](https://github.com/securely1g/sonic-bazel-registry/pull/119) |

The two `Native source and TARs` checks are required on `main`. Their successful source builds and installed runtime/debug tests are merge gates; a completed analysis or a queued workflow does not satisfy them.
