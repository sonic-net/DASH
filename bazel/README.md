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

The foreign-Make launcher keeps complete ordered flags out of recursive
Make's environment. `CPPFLAGS` uses a GCC driver response file at its original
position. `LDFLAGS` uses the shared `configure_linker_flags.sh` and
`configure_environment.sh`: the shared compiler launcher expands the private
vector and shortens absolute library searches relative to each compiler's
working directory, retaining their original driver order and precedence.

For example, the SAI metadata `CXX="$(CXX) $(LDFLAGS)"` override turns a
130,698-byte linker vector into a 131,872-byte `MAKEFLAGS` value. Make then
cannot launch `which`, reporting a misleading missing `doxygen` error. A plain
GCC linker response file gets past Make but still overflows GCC's exported
`COLLECT_GCC_OPTIONS` when it starts `collect2`. Reusing both shared adapters
handles these boundaries without dropping paths or forwarding them behind
GCC's default library searches. Metadata/library compile commands keep their
`CPPFLAGS` response; their separate link commands consume the private linker vector.
Compiler choices, feature options and invalid-option rejection are unchanged.

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
| `//:runtime_packages.json` | `libsai` identity from the existing Debian control, dependencies derived from the runtime, and the runtime TAR hash |
| `//bazel:runtime_test` | Standalone runtime loading, installed SDK switch/generated DASH VIP API queries, pipeline validation, dependency closure, debug IDs/checksums, and GDB source-line lookup |
| `//bazel:make_flags_test` | Original recursive Make adapter with native GCC/G++, long Make-export negative control, ordered and quoted preprocessor flags, exact link flags and identical short/long-flag binaries |

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

Local builds and CI resolve PI, build-infra, P4C and `rules_distroless` from the
SONiC registry’s maintained `main` branch. Each module uses its published source
archive, patches and overlays.

The Infra `.28` minimum supplies `configure_linker_flags.sh` and the current shared
compiler adapters. PI `.4` and P4C `.3` supply their source SDKs; `rules_distroless`
`.18` supplies compact lock transport for that graph. Native CI installs `file`
before repository evaluation so APT can distinguish real ELF libraries from
linker scripts. Both native architectures retain the same build and runtime tests.

| Module | Selected support |
| --- | --- |
| `rules_distroless@0.9.4.sonic.18` | [Compact APT lock transport, registry #237](https://github.com/securely1g/sonic-bazel-registry/pull/237) |
| `p4lang-pi@0.1.3.sonic.4` | [PI source SDK and linker transport, registry #289](https://github.com/securely1g/sonic-bazel-registry/pull/289) |
| `p4c@1.2.4.2.sonic.3` | [P4C source and native execution support, registry #276](https://github.com/securely1g/sonic-bazel-registry/pull/276) |
| `sonic-build-infra@0.0.28-9965823498ab54816de5addb6084638470dd04d7` | [Shared flag adapters, native linking and complete APT lock, registry #287](https://github.com/securely1g/sonic-bazel-registry/pull/287) |
| `rules_foreign_cc@0.16.0.sonic.1` | [Published header search classifications, registry #119](https://github.com/securely1g/sonic-bazel-registry/pull/119) |

Workflow artifacts contain both TARs, generated package metadata, checksums, the
source revision, test results, the generated lock and the resolved module graph.
The archived `.bazelrc` identifies the registry endpoint. CI records the
registry’s `main` commit before and after each build.

The two `Native source and TARs` checks validate source builds, generated package
metadata and installed runtime/debug behavior on AMD64 and ARM64. A completed
analysis or a queued workflow does not establish that validation passed.
