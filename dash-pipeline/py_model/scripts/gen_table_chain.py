#!/usr/bin/env python3
"""
Multi-file Table() chain extractor.

Start from classes in dash_pipeline.py, follow Class.method chains like in MultiFileCallGraph,
but instead of methods, stop at Table() objects defined inside classes.
Outputs dotted chains ending at Table object names.

This file keeps the original behavior while using the shared helper.
"""

import ast
import os
from collections import defaultdict
from typing import List

from py_model.scripts.gen_helper import parse_files, collect_class_methods, get_entry_class_names, get_full_name


class MultiFileTableGraph:
    def __init__(self, directory: str, entry_file: str = "dash_pipeline.py"):
        self.directory = os.path.abspath(directory)
        self.entry_file = os.path.join(self.directory, entry_file)
        self.class_defs = defaultdict(dict)   # {class_name: {method_name: ast.FunctionDef}}
        self.tables = defaultdict(set)        # {class_name: {table_var_names}}

        # parse & collect
        self.parsed_files = list(parse_files(self.directory))
        self._collect_defs_and_tables()

    # ---------------------------
    # Collect defs + Table() objects (class-level)
    # ---------------------------
    def _collect_defs_and_tables(self):
        # Build class methods map first
        class_defs, _, _ = collect_class_methods(self.parsed_files)
        self.class_defs.update(class_defs)

        # Now collect Table() assignments inside classes (scan ASTs for Assign nodes inside class bodies)
        for path, tree in self.parsed_files:
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue

                # collect Table() assignments inside class
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                        call = stmt.value
                        if isinstance(call.func, ast.Name) and call.func.id == "Table":
                            for target in stmt.targets:
                                if isinstance(target, ast.Name):
                                    self.tables[node.name].add(target.id)

    # ---------------------------
    # Helpers: get_full_name already imported
    # ---------------------------
    def _extract_called_class(self, dotted_target: str | None) -> str | None:
        """Given dotted_target like 'foo.bar.Baz' return the longest part matching a known class."""
        if not dotted_target:
            return None
        parts = dotted_target.split(".")
        for i in reversed(range(len(parts))):
            if parts[i] in self.class_defs:
                return parts[i]
        return None

    def _called_classes(self, func_node):
        called_classes = set()
        if func_node is None:
            return called_classes
        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Call):
                target = get_full_name(stmt.func)
                callee_class = self._extract_called_class(target)
                if callee_class:
                    called_classes.add(callee_class)
        return called_classes

    def build_table_chains(self, cls_name, prefix="", visited=None):
        visited = set(visited or [])
        if cls_name in visited:
            return []
        visited.add(cls_name)

        chains = []
        methods = self.class_defs.get(cls_name, {})

        for mname, mnode in methods.items():
            for callee in sorted(self._called_classes(mnode)):
                subprefix = f"{prefix}.{cls_name}" if prefix else cls_name
                chains.extend(self.build_table_chains(callee, subprefix, visited.copy()))

        # at this class, append all tables
        if cls_name in self.tables:
            subprefix = f"{prefix}.{cls_name}" if prefix else cls_name
            for tname in sorted(self.tables[cls_name]):
                chain = f"{subprefix}.{tname}"
                chains.append(chain)

        return chains

    # ---------------------------
    # Entry point
    # ---------------------------
    def resolve_from_entry(self) -> List[str]:
        if not os.path.exists(self.entry_file):
            raise RuntimeError(f"Entry file not found: {self.entry_file!r}")

        roots = get_entry_class_names(self.entry_file)
        if not roots:
            print(f"No classes found in entry file: {self.entry_file}")
            return []

        all_chains = []
        for root in roots:
            all_chains.extend(self.build_table_chains(root))

        # Filter only dash_ingress.* chains (same as original)
        filtered = [c for c in all_chains if c.startswith("dash_ingress.")]

        return sorted(set(filtered))


def generate_table_chain(project_dir: str, entry_file: str = "dash_pipeline.py") -> List[str]:
    tg = MultiFileTableGraph(project_dir, entry_file=entry_file)
    return tg.resolve_from_entry()


if __name__ == "__main__":
    project_dir = "py_model/data_plane"

    chains = generate_table_chain(project_dir, entry_file="dash_pipeline.py")

    print("\nFinal Table Object Call Chains:")
    for i, c in enumerate(chains, 1):
        print(f"{i:2d}. {c}")
