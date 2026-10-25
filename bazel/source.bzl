"""Compile P4 and generate DASH's private SAI tree with declared tools."""

def _relative(file, owner):
    prefix = owner.workspace_root
    return file.path[len(prefix) + 1:] if prefix else file.path

def _prepare_impl(ctx):
    output = ctx.actions.declare_directory(ctx.label.name)
    manifest = ctx.actions.declare_file(ctx.label.name + ".inputs.json")
    entries = [[f.path, _relative(f, ctx.label)] for f in ctx.files.srcs]
    entries += [[f.path, "dash-pipeline/SAI/SAI/" + _relative(f, ctx.attr.sai_sources.label)] for f in ctx.files.sai_sources]
    entries.append([ctx.file.makefile.path, "Makefile"])
    ctx.actions.write(manifest, json.encode(entries))
    args = ctx.actions.args()
    args.add("prepare")
    args.add("--manifest", manifest)
    args.add("--output", output.path)
    args.add("--p4c", ctx.executable.p4c)
    args.add("--launcher", ctx.executable._prepare)
    args.add("--make", ctx.executable.make)
    args.add("--tool-runtime", ctx.file.tool_runtime.path)
    ctx.actions.run(
        executable = ctx.attr._prepare[DefaultInfo].files_to_run,
        arguments = [args],
        inputs = depset(ctx.files.srcs + ctx.files.sai_sources + [manifest, ctx.file.makefile, ctx.file.tool_runtime]),
        tools = [ctx.attr.p4c[DefaultInfo].files_to_run, ctx.attr.make[DefaultInfo].files_to_run],
        outputs = [output],
        mnemonic = "DashGenerate",
        progress_message = "Compile DASH P4 and generate SAI sources",
    )
    return [DefaultInfo(files = depset([output]))]

prepare_dash = rule(
    implementation = _prepare_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
        "sai_sources": attr.label(mandatory = True),
        "makefile": attr.label(allow_single_file = True, mandatory = True),
        "p4c": attr.label(executable = True, cfg = "exec", mandatory = True),
        "make": attr.label(executable = True, cfg = "exec", default = "@sonic_build_infra//tools/build_tools:make"),
        "tool_runtime": attr.label(allow_single_file = True, cfg = "exec", default = "@sonic_build_infra//tools/build_tools:foreign_runtime"),
        "_prepare": attr.label(executable = True, cfg = "exec", default = "//bazel:prepare"),
    },
)
