# Generated DASH runtime package metadata

`//:runtime_packages.json` is a generated target. Its package identity comes
from the existing `dash-pipeline/SAI/debian/libsai_1.0.0_amd64/DEBIAN/control`
file, which already includes the package version. The BUILD definition only
maps `libsai` to its public runtime TAR and declares the source/APT libraries
needed to analyze the actual compiled files.

The dependency provider also carries the runtime libraries exported by the
public SDK. For example, the DASH-enabled `syncd_dash` in `sonic-sairedis` links against
`libprotobuf-lite.so.32` through `libprotobuf-dev`; declaring the matching
APT payload and control lets its metadata generator resolve that library.

The metadata generator calculates shared-library dependencies from the selected
TAR; it does not copy the old handwritten dependency list. Target architecture
comes from the Bazel configuration, including ARM64 despite the legacy control
file's AMD64 directory name. The image checks the owner target and actual TAR
hash and records the selected source module version.

This produces metadata without creating a Debian package, running installation
scripts, or changing the legacy Make recipe.
