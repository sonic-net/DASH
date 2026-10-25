"""Exercise baseline selection and ABI failures in disposable local Git repos."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).with_name("pin_metadata_baseline.py")
SIZE_SCRIPT = """#!/bin/sh
set -eu
COMMIT=origin/master # should be corresponding branch HEAD
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
git -C .. archive "$COMMIT" inc | tar -x -C "$temporary"
cc -I"$temporary/inc" baseline.c -o "$temporary/size"
"$temporary/size" > saimetadatasize.h
"""


class BaselineTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Metadata regression fixture",
            "GIT_COMMITTER_NAME": "Metadata regression fixture",
            "GIT_AUTHOR_EMAIL": "securely1g@gmail.com",
            "GIT_COMMITTER_EMAIL": "securely1g@gmail.com",
        }
        source = self.root / "source"
        source.mkdir()
        self.run_command(source, "git", "init", "-q")
        (source / "inc").mkdir()
        (source / "meta").mkdir()
        (source / "inc/saitypes.h").write_text("typedef union { char data[40]; } sai_value_t;\n")
        (source / "meta/size.sh").write_text(SIZE_SCRIPT)
        (source / "meta/baseline.c").write_text(
            '#include <stdio.h>\n#include <saitypes.h>\n'
            'int main(void) { printf("#define EXPECTED_SIZE %zu\\n", sizeof(sai_value_t)); }\n'
        )
        self.commit(source)
        self.selected = self.run_command(source, "git", "rev-parse", "HEAD").stdout.strip()
        (source / "inc/saitypes.h").write_text("typedef union { char data[56]; } sai_value_t;\n")
        self.commit(source)
        self.newer = self.run_command(source, "git", "rev-parse", "HEAD").stdout.strip()

        self.parent = self.root / "dash"
        self.parent.mkdir()
        self.run_command(self.parent, "git", "init", "-q")
        self.run_command(
            self.parent, "git", "-c", "protocol.file.allow=always", "submodule", "add",
            str(source), "dash-pipeline/SAI/SAI",
        )
        self.sai = self.parent / "dash-pipeline/SAI/SAI"
        self.run_command(self.sai, "git", "checkout", "--detach", self.selected)
        self.run_command(self.sai, "git", "update-ref", "refs/remotes/origin/master", self.newer)
        self.helper = self.sai.parent / HELPER.name
        shutil.copyfile(HELPER, self.helper)
        self.commit(self.parent)

    def run_command(self, directory, *arguments, check=True):
        return subprocess.run(
            arguments, cwd=directory, env=self.env, text=True, capture_output=True,
            check=check, timeout=30,
        )

    def commit(self, directory):
        self.run_command(directory, "git", "add", ".")
        self.run_command(directory, "git", "commit", "-qm", "Create regression fixture")

    def pin(self, check=True):
        return self.run_command(self.parent, sys.executable, str(self.helper), check=check)

    def check_size(self):
        meta = self.sai / "meta"
        self.run_command(meta, "sh", "size.sh")
        (meta / "actual.c").write_text(
            '#include <saitypes.h>\n#include "saimetadatasize.h"\n'
            'int main(void) { return sizeof(sai_value_t) != EXPECTED_SIZE; }\n'
        )
        self.run_command(meta, "cc", "-I../inc", "actual.c", "-o", "actual")
        return self.run_command(meta, "./actual", check=False).returncode

    def test_pinned_positive_moving_ref_and_enlarged_union(self):
        self.assertEqual(self.check_size(), 1, "moving master must reproduce the mismatch")
        self.pin()
        self.assertEqual(self.check_size(), 0)
        before = (self.sai / "meta/size.sh").read_bytes()
        self.pin()
        self.assertEqual((self.sai / "meta/size.sh").read_bytes(), before)
        for revision in (self.selected, self.newer):
            self.run_command(self.sai, "git", "update-ref", "refs/remotes/origin/master", revision)
            self.assertEqual(self.check_size(), 0)
        (self.sai / "inc/saitypes.h").write_text("typedef union { char data[80]; } sai_value_t;\n")
        self.assertEqual(self.check_size(), 1, "pinned baseline must still reject ABI growth")

    def test_wrong_checkout_is_rejected(self):
        self.run_command(self.sai, "git", "checkout", "--detach", self.newer)
        self.assertNotEqual(self.pin(check=False).returncode, 0)
        self.assertEqual((self.sai / "meta/size.sh").read_text(), SIZE_SCRIPT)

    def test_unexpected_local_script_is_preserved(self):
        script = self.sai / "meta/size.sh"
        edited = SIZE_SCRIPT + "echo keep local edits\n"
        script.write_text(edited)
        self.assertNotEqual(self.pin(check=False).returncode, 0)
        self.assertEqual(script.read_text(), edited)

    def test_unknown_upstream_assignment_is_rejected(self):
        script = self.sai / "meta/size.sh"
        edited = SIZE_SCRIPT.replace("COMMIT=origin/master", "# COMMIT=origin/master")
        script.write_text(edited)
        self.commit(self.sai)
        self.commit(self.parent)
        self.assertNotEqual(self.pin(check=False).returncode, 0)
        self.assertEqual(script.read_text(), edited)

    def test_uninitialized_submodule_is_rejected(self):
        self.run_command(self.parent, "git", "submodule", "deinit", "-f", "--", "dash-pipeline/SAI/SAI")
        self.assertNotEqual(self.pin(check=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
