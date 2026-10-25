"""Install DASH's source-built library and its matching symbol files."""

load("@sonic_build_infra//tar:sonic_deploy_tar.bzl", "sonic_deploy_tar")

def dash_runtime(name, triplet):
    sonic_deploy_tar(
        name = name,
        binaries = {
            "usr/lib/" + triplet + "/libsai.so uid=0 gid=0 mode=0755 type=file": ":libsai",
            "usr/lib/" + triplet + "/libdashsaimetadata.so uid=0 gid=0 mode=0755 type=file": ":libdashsaimetadata",
        },
        force_debug_build = True,
        srcs = [":pipeline_" + name for name in ["json", "p4rt_json", "p4rt_txt", "ir_json"]] + ["//:LICENSE-CODE.md", "@dash_sai_source//:LICENSE.txt"],
        mtree = [
            "etc/dash/dash_pipeline.json uid=0 gid=0 mode=0644 type=file content=$(location :pipeline_json)",
            "etc/dash/dash_pipeline_p4rt.json uid=0 gid=0 mode=0644 type=file content=$(location :pipeline_p4rt_json)",
            "etc/dash/dash_pipeline_p4rt.txt uid=0 gid=0 mode=0644 type=file content=$(location :pipeline_p4rt_txt)",
            "etc/dash/dash_pipeline_ir.json uid=0 gid=0 mode=0644 type=file content=$(location :pipeline_ir_json)",
            "usr/share/doc/dash-sai/LICENSE uid=0 gid=0 mode=0644 type=file content=$(location //:LICENSE-CODE.md)",
            "usr/share/doc/dash-sai/SAI-LICENSE.txt uid=0 gid=0 mode=0644 type=file content=$(location @dash_sai_source//:LICENSE.txt)",
        ],
        visibility = ["//visibility:public"],
    )
