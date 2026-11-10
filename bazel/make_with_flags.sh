# Sourced by rules_foreign_cc's public tool_prefix before starting Make.
# Keep ordered flags out of recursive Make's MAKEFLAGS export. The CPP response
# stays at its driver position. Shared linker transport and compiler adaptation
# also avoid GCC's COLLECT_GCC_OPTIONS limit without changing -L precedence.
(
    set -eu
    linker_adapter=${1:?the declared linker transport is required}
    compiler_adapter=${2:?the declared compiler adapter is required}
    python=${3:?the declared Python interpreter is required}
    shift 3
    cppflags_file="$PWD/.bazel-dash-cppflags.rsp"
    printf '%s\n' "${CPPFLAGS:-}" > "$cppflags_file"
    export CPPFLAGS="@$cppflags_file"
    . "$linker_adapter" "$python" /bin/sh "$compiler_adapter" "$@"
)
