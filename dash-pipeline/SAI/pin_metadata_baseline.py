#!/usr/bin/env python3
"""Compare generated SAI metadata with pristine headers at the selected gitlink."""

from pathlib import Path
import subprocess


def git(directory, *arguments):
    return subprocess.check_output(
        ["git", "-C", str(directory), *arguments], text=True
    ).strip()


def main():
    repository = Path(__file__).resolve().parents[2]
    relative = "dash-pipeline/SAI/SAI"
    sai = repository / relative
    entry = git(repository, "ls-tree", "HEAD", "--", relative).split()
    if len(entry) != 4 or entry[:2] != ["160000", "commit"]:
        raise RuntimeError("DASH HEAD must record the SAI submodule gitlink")
    selected = entry[2]
    if Path(git(sai, "rev-parse", "--show-toplevel")).resolve() != sai.resolve():
        raise RuntimeError("Initialize the SAI submodule before generating metadata")
    if git(sai, "rev-parse", "HEAD") != selected:
        raise RuntimeError("SAI checkout does not match the gitlink recorded in DASH HEAD")

    script = sai / "meta/size.sh"
    original = subprocess.check_output(
        ["git", "-C", str(sai), "show", selected + ":meta/size.sh"]
    )
    assignment = b"\nCOMMIT=origin/master # should be corresponding branch HEAD\n"
    if original.count(assignment) != 1:
        raise RuntimeError("Unrecognized SAI size.sh baseline assignment")
    pinned = original.replace(
        assignment, ("\nCOMMIT=" + selected + " # selected SAI gitlink\n").encode()
    )
    current = script.read_bytes()
    if current not in (original, pinned):
        raise RuntimeError("SAI size.sh has unrelated local edits; refusing to overwrite them")
    if current != pinned:
        script.write_bytes(pinned)
    print("SAI source and pristine metadata baseline: " + selected)


if __name__ == "__main__":
    main()
