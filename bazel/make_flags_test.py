"""Exercise the original recursive Make adapter with ordered GCC flags."""

import errno
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


def main():
    adapter, frontend, linker_adapter, compiler_adapter = [Path(value).resolve() for value in sys.argv[1:]]
    tools = {name: shutil.which(name) for name in ("bash", "make", "gcc", "g++", "ar", "as", "ld", "which")}
    assert all(tools.values()), tools
    with tempfile.TemporaryDirectory(dir=os.environ.get("TEST_TMPDIR")) as temporary:
        root = Path(temporary).resolve()
        # Give the shared adapter an explicit fixture linker/assembler root;
        # the selected host GCC still performs the actual compile and link.
        compiler_tools = root / "compiler-tools"
        compiler_tools.mkdir()
        for name in ("as", "ld"):
            (compiler_tools / name).symlink_to(tools[name])
        generated = root / "generated_sources"
        metadata = generated / "dash-pipeline/SAI/SAI/meta"
        library = generated / "dash-pipeline/SAI/lib"
        metadata.mkdir(parents=True)
        library.mkdir(parents=True)
        shutil.copyfile(frontend, generated / "Makefile")
        for name, value in (("first", 13), ("second", 29)):
            (root / name).mkdir()
            (root / name / "selected.h").write_text(f"#define SELECTED {value}\n")
        (root / "quoted include").mkdir()
        (root / "quoted include/quoted_path.h").write_text("#define SPACE_HEADER 31\n")
        (root / "compiler-system").mkdir()
        (root / "compiler-system/selected.h").write_text("#define SELECTED 47\n")
        # Competing archives make linker search order observable in the result;
        # spaced directories also exercise the driver's response-file quoting.
        for name, value in (("link first", 13), ("link second", 29)):
            directory = root / name
            directory.mkdir()
            (directory / "value.c").write_text(f"int linker_value(void) {{ return {value}; }}\n")
            subprocess.run([tools["gcc"], "-c", str(directory / "value.c"),
                            "-o", str(directory / "value.o")], check=True)
            subprocess.run([tools["ar"], "rcs", str(directory / "liborder.a"),
                            str(directory / "value.o")], check=True)
        program = (
            "#include <selected.h>\n#include <quoted_path.h>\n"
            '#ifdef __cplusplus\nextern "C"\n#endif\nint linker_value(void);\n'
            "static const char *text = STRING;\n"
            "int main(void) { return VALUE + SELECTED != 24 || SPACE_HEADER != 31 || "
            "text[0] != 'q' || text[6] != ' ' || text[7] != 'v' || linker_value() != 13; }\n"
        )
        (metadata / "unit.c").write_text(program)
        (library / "unit.cc").write_text(program)
        # Use the real frontend's two recursive calls. The metadata call carries
        # link flags in CXX (used only to link the C object); the library call
        # carries GXX_FLAGS and LDFLAGS as
        # command-line overrides, which GNU Make also exports in MAKEFLAGS.
        (metadata / "Makefile").write_text(
            # Match the upstream parse-time tool probe; gcc is known to exist.
            "BINS = gcc\n"
            '$(foreach bin,$(BINS),$(if $(shell which $(bin)),,$(error "Missing $(bin) in PATH")))\n'
            ".PHONY: libsaimetadata.so\nlibsaimetadata.so:\n"
            "\t$(file >makeflags.txt,$(MAKEFLAGS))\n"
            "\t$(CC) $(CFLAGS) -c unit.c -o unit.o\n"
            "\t$(CXX) unit.o -o program\n"
        )
        (library / "Makefile").write_text(
            ".PHONY: all\nall:\n"
            "\t$(file >makeflags.txt,$(MAKEFLAGS))\n"
            "\t$(file >linkflags.txt,$(LDFLAGS))\n"
            "\t$(file >libs.txt,$(LIBS))\n"
            "\t$(CXX) $(GXX_FLAGS) -c unit.cc -o unit.o\n"
            "\t$(CXX) unit.o $(LDFLAGS) -o program\n"
        )
        common = shlex.join([
            "-DVALUE=1", "-UVALUE", "-DVALUE=7", '-DSTRING="quoted value"',
            "-isystem", str(root / "first"), "-isystem", str(root / "second"),
            "-I" + str(root / "quoted include"), "-Wno-unused-parameter",
        ])
        large_cpp = " ".join(f"-I/nonexistent/{i}/" + "x" * 180 for i in range(430)) + " " + common
        link_flags = [
            "-L" + str(root / "link first"), "-L" + str(root / "link second"),
            "-Wl,--whole-archive", "-lorder", "-Wl,--no-whole-archive", "-Wl,--as-needed",
        ]
        common_link = shlex.join(link_flags)
        large_link = " ".join(f"-L/nonexistent/{i}/" + "y" * 180 for i in range(330)) + " " + common_link
        # Each original variable fits execve, but their recursive Make export
        # exceeds the per-string bound seen in the actual DASH failure.
        assert len(large_cpp) < 131072 and len(large_link) < 131072
        assert len(large_cpp) + len(large_link) > 131072

        # The observed 130,698-byte LDFLAGS fits execve on its own. Embedding
        # it in CXX and escaping that override into MAKEFLAGS overflows even
        # after CPPFLAGS is compact. Keep each synthetic directory bounded.
        remaining = 130698 - len(common_link.encode()) - 1
        near_paths = []
        near_prefix = "-L" + str(root / "nonexistent/near")
        tail = "-L" + str(root / "nonexistent/padding") + "/"
        while remaining > len(near_prefix) + len(tail) + 200:
            token = f"{near_prefix}/{len(near_paths)}/" + "z" * 180
            near_paths.append(token)
            remaining -= len(token) + 1
        assert remaining >= len(tail)
        near_paths.append(tail + "z" * (remaining - len(tail)))
        near_limit_link = " ".join(near_paths) + " " + common_link
        assert len(near_limit_link.encode()) == 130698

        def run(cppflags, ldflags, prefix):
            assignments = {
                "CC": tools["gcc"], "CXX": tools["g++"], "CPPFLAGS": cppflags,
                "CFLAGS": "-O2 -g -frandom-seed=fixture -UVALUE -DVALUE=11 -isystem " + shlex.quote(str(root / "compiler-system")),
                "CXXFLAGS": "-O2 -g -frandom-seed=fixture -UVALUE -DVALUE=11 -isystem " + shlex.quote(str(root / "compiler-system")),
                "LDFLAGS": ldflags, "LIBS": "",
            }
            command = " ".join(key + "=" + shlex.quote(value) for key, value in assignments.items())
            if prefix:
                command += " source " + shlex.join([str(adapter), str(linker_adapter), str(compiler_adapter), sys.executable])
            command += " " + shlex.join([tools["make"], "--no-print-directory", "-f", "generated_sources/Makefile", "all"])
            script = root / "invoke.sh"
            script.write_text(command + "\n")
            env = dict(os.environ, EXT_BUILD_ROOT=str(root), COMPILER_PATH=str(compiler_tools))
            return subprocess.run([tools["bash"], script], cwd=root, env=env, capture_output=True, text=True)

        # Prove the exact recursive override/export failure independently of
        # GCC: a trivial child cannot start when MAKEFLAGS exceeds the limit.
        probe = root / "probe"
        probe.mkdir()
        (probe / "Makefile").write_text(
            "all:\n\t$(file >makeflags.txt,$(MAKEFLAGS))\n\t@/bin/true\n"
        )
        small = subprocess.run(
            [tools["make"], "--no-print-directory", "-C", str(probe),
             "GXX_FLAGS=" + common, "LDFLAGS=" + common_link],
            capture_output=True, text=True,
        )
        assert small.returncode == 0, small.stderr
        old = subprocess.run(
            [tools["make"], "--no-print-directory", "-C", str(probe),
             "GXX_FLAGS=" + large_cpp, "LDFLAGS=" + large_link],
            capture_output=True, text=True,
        )
        assert len((probe / "makeflags.txt").read_bytes()) > 131072
        assert old.returncode != 0, old.stderr
        # Make under PRoot/QEMU can report only child status 127. Prove the
        # actual exec limit using its captured export, rather than accepting
        # an arbitrary failed child or relying on Make's diagnostic wording.
        exec_probe = subprocess.run(
            [sys.executable, "-c",
             "import os, sys\nfrom pathlib import Path\n"
             "env = dict(os.environ, MAKEFLAGS=Path(sys.argv[1]).read_text().removesuffix('\\n'))\n"
             "try:\n    os.execve('/bin/true', ['/bin/true'], env)\n"
             "except OSError as error:\n    print(error.errno)\n",
             str(probe / "makeflags.txt")],
            capture_output=True, text=True,
        )
        assert exec_probe.returncode == 0 and exec_probe.stdout.strip() == str(errno.E2BIG), (
            exec_probe.returncode, exec_probe.stdout, exec_probe.stderr
        )

        # A preprocessor-only response would reorder CPPFLAGS after native
        # compiler include options. Keep this concrete negative control: the
        # first header must win across the CPPFLAGS/CFLAGS boundary.
        (root / "order.c").write_text("#include <selected.h>\nSELECTED\n")
        (root / "order.rsp").write_text("-isystem " + str(root / "first") + "\n")
        def selected(flags):
            return subprocess.check_output([tools["gcc"], "-E", "-P", *flags,
                                            "-isystem", str(root / "compiler-system"),
                                            str(root / "order.c")], text=True).strip()
        assert selected(["-isystem", str(root / "first")]) == "13"
        assert selected(["-Wp,@" + str(root / "order.rsp")]) == "47"
        assert selected(["@" + str(root / "order.rsp")]) == "13"

        hashes = []
        for cppflags, ldflags in ((common, near_limit_link), (common, common_link), (large_cpp, large_link)):
            accepted = run(cppflags, ldflags, True)
            assert accepted.returncode == 0, accepted.stdout + accepted.stderr
            assert (root / ".bazel-dash-cppflags.rsp").read_text() == cppflags + "\n"
            linker_response = root / ".sonic-linker-arguments"
            assert linker_response.read_text().splitlines() == ["sonic-linker-arguments-v1", *shlex.split(ldflags)]
            installed = root / "dash-pipeline/SAI"
            assert (installed / "lib/linkflags.txt").read_text() == "@" + str(linker_response) + " -Wl,-z,defs\n"
            assert (installed / "lib/libs.txt").read_text().strip() == "-lpiprotogrpc -lpiprotobuf -lgrpc++ -lgrpc -lprotobuf -lgpr -labsl_synchronization"
            assert len((installed / "SAI/meta/makeflags.txt").read_bytes()) < 131072
            assert len((installed / "lib/makeflags.txt").read_bytes()) < 131072
            row = {}
            for name in ("SAI/meta/program", "lib/program"):
                binary = installed / name
                subprocess.run([binary], check=True)
                row[name] = hashlib.sha256(binary.read_bytes()).hexdigest()
            hashes.append(row)
        assert hashes[0] == hashes[1] == hashes[2], hashes
        # Reversing only the search directories must select the other archive,
        # proving that the successful binaries checked actual linker ordering.
        reversed_link = shlex.join(list(reversed(link_flags[:2])) + link_flags[2:])
        assert run(common, reversed_link, True).returncode == 0
        for name in ("SAI/meta/program", "lib/program"):
            assert subprocess.run([root / "dash-pipeline/SAI" / name]).returncode == 1
        # Isolate option rejection from the header/archive fixtures: both the
        # original command and the adapted command must reach the same error.
        for source in (metadata / "unit.c", library / "unit.cc"):
            source.write_text("int main(void) { return 0; }\n")
        for prefix in (False, True):
            rejected = run("-fdefinitely-invalid-dash-option", "", prefix)
            assert rejected.returncode != 0 and "unrecognized command-line option" in rejected.stderr, rejected.stderr
            rejected = run("", "-Wl,--definitely-invalid-dash-linker-option", prefix)
            assert rejected.returncode != 0 and "unrecognized option" in rejected.stderr, rejected.stderr
        print(json.dumps({"status": "passed", "cppflags_bytes": len(large_cpp), "ldflags_bytes": len(large_link),
                          "near_limit_ldflags_bytes": len(near_limit_link), "binaries": hashes[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
