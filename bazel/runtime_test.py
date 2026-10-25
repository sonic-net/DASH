"""Check the deployed DASH API, generated pipeline and matching debug symbols."""

import json
import os
from pathlib import Path
import platform
import re
import shlex
import struct
import subprocess
import sys
import tarfile
import tempfile
import zlib


def command(*args, **kwargs):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=60, **kwargs)


def build_id(path):
    found = re.findall(r"Build ID: ([0-9a-f]+)", command("readelf", "-n", str(path)))
    assert len(found) == 1, (path, found)
    return found[0]


def main():
    runtime, debug, pi_runtime, consumer, runtime_loader = [Path(x).resolve() for x in sys.argv[1:6]]
    dependencies = [Path(path).resolve() for group in sys.argv[6:] for path in shlex.split(group)]
    with tempfile.TemporaryDirectory(dir=os.environ["TEST_TMPDIR"]) as temporary:
        root = Path(temporary)
        for archive in [*dependencies, pi_runtime, runtime]:
            with tarfile.open(archive) as contents:
                contents.extractall(root, filter="data")
        elfs = []
        with tarfile.open(runtime) as contents:
            for member in contents:
                assert member.uid == member.gid == 0, member.name
                if member.isfile() and contents.extractfile(member).read(4) == b"\x7fELF":
                    elfs.append(root / member.name)
        assert {p.name for p in elfs} == {"libsai.so", "libdashsaimetadata.so"}
        expected_machine = {"x86_64": 62, "aarch64": 183}[platform.machine()]
        for binary in elfs:
            assert struct.unpack_from("<H", binary.read_bytes(), 18)[0] == expected_machine
            assert ".debug_info" not in command("readelf", "-SW", str(binary))
            assert not re.search(r"\((RPATH|RUNPATH)\)", command("readelf", "-d", str(binary)))

        pipeline = root / "etc/dash"
        assert {p.name for p in pipeline.iterdir()} == {
            "dash_pipeline.json", "dash_pipeline_p4rt.json", "dash_pipeline_p4rt.txt", "dash_pipeline_ir.json",
        }
        model = json.loads((pipeline / "dash_pipeline.json").read_text())
        assert model["pipelines"] and model["actions"] and model["headers"]
        info = json.loads((pipeline / "dash_pipeline_p4rt.json").read_text())
        assert info["tables"] and info["actions"]
        assert json.loads((pipeline / "dash_pipeline_ir.json").read_text())
        assert (pipeline / "dash_pipeline_p4rt.txt").stat().st_size > 0

        # Resolve every native dependency from the assembled payload, without
        # the runner's ld.so cache or Bazel's SDK library paths.
        loaders = {p.resolve() for p in root.rglob("ld-linux-*.so.*") if p.is_file()}
        assert len(loaders) == 1, loaders
        search = sorted({str(p.parent) for p in root.rglob("*.so*") if p.is_file()})
        loader = [str(loaders.pop()), "--inhibit-cache", "--library-path", os.pathsep.join(search)]
        environment = {k: v for k, v in os.environ.items() if k not in {"LD_PRELOAD", "LD_LIBRARY_PATH", "LD_AUDIT"}}
        for binary in [*elfs, consumer, runtime_loader]:
            resolved = command(*loader, "--list", str(binary), env=environment)
            assert "not found" not in resolved, resolved
            assert all(Path(p).resolve().is_relative_to(root) for p in re.findall(r"=> (/\S+)", resolved)), resolved
        assert "DASH installed SDK API query passed" in command(*loader, str(consumer), env=environment)

        library = next(p for p in elfs if p.name == "libsai.so")
        assert "Standalone DASH runtime load passed" in command(
            *loader, str(runtime_loader), str(library), env=environment,
        )

        def source_line():
            return command("gdb", "-nx", "-batch", "-ex", "set debuginfod enabled off",
                           "-ex", f"set debug-file-directory {root}/usr/lib/debug",
                           "-ex", f"file {library}", "-ex", "info line sai_api_query")

        assert not re.search(r"Line \d+ of", source_line())
        with tarfile.open(debug) as contents:
            contents.extractall(root, filter="data")
        for binary in elfs:
            identity = build_id(binary)
            symbols = root / "usr/lib/debug/.build-id" / identity[:2] / (identity[2:] + ".debug")
            assert build_id(symbols) == identity
            assert ".debug_info" in command("readelf", "-SW", str(symbols))
            section = root / "debug-link"
            command("objcopy", "--dump-section", f".gnu_debuglink={section}", str(binary), str(root / "elf-copy"))
            data = section.read_bytes()
            assert data.split(b"\0", 1)[0].decode() == symbols.name
            assert struct.unpack("<I", data[-4:])[0] == zlib.crc32(symbols.read_bytes())
        assert re.search(r"Line \d+ of .*saifixedapis\.cpp", source_line())
        print("DASH native installed SDK, pipeline and detached debug symbols passed")


if __name__ == "__main__":
    main()
