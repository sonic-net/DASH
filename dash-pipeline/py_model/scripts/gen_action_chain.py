#!/usr/bin/env python3
"""
Multi-file call-graph extractor

Start from classes defined in dash_pipeline.py and follow Class.method chains across files,
then expand leaf classes to list all their methods, including @staticmethod/@classmethod.
Prints flat list.

This is the refactor of your original MultiFileCallGraph using the shared helper.
"""

import ast
import os
from collections import defaultdict
from typing import List

from py_model.scripts.gen_helper import parse_files, collect_class_methods, get_entry_class_names, get_full_name, called_classes


class MultiFileCallGraph:
    def __init__(self, directory: str, entry_file: str = "dash_pipeline.py"):
        self.directory = os.path.abspath(directory)
        self.entry_file = os.path.join(self.directory, entry_file)
        self.class_defs = defaultdict(dict)  # {class_name: {method_name: ast.FunctionDef}}
        self.file_class_map = {}             # {class_name: file_path}
        self.parsed_files = list(parse_files(self.directory))
        self._collect_defs()

    # ---------------------------
    # Parse files & collect defs
    # ---------------------------
    def _collect_defs(self):
        class_defs, file_class_map, global_funcs = collect_class_methods(self.parsed_files)
        self.class_defs.update(class_defs)
        self.file_class_map.update(file_class_map)
        # ensure a slot for global functions
        self.class_defs.setdefault("__global__", {})
        self.class_defs["__global__"].update(global_funcs)

    # ---------------------------
    # Helpers: name resolution (get_full_name imported)
    # ---------------------------
    def _get_full_name(self, node, current_class=None):
        return get_full_name(node)

    def _extract_called_class(self, dotted_target):
        if not dotted_target:
            return None
        parts = dotted_target.split(".")
        for i in reversed(range(len(parts))):
            if parts[i] in self.class_defs:
                return parts[i]
        return None

    def _should_skip(self, name: str) -> bool:
        if not name:
            return True
        base = name.split(".")[-1]
        if base == "py_log" or base.isupper() or base == "get" or base == "hash" or base.endswith("_t"):
            return True
        return False

    def _called_targets(self, func_node, current_class):
        called_classes_set, called_funcs = set(), set()
        if func_node is None:
            return called_classes_set, called_funcs

        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.Call):
                target = self._get_full_name(stmt.func, current_class)
                if not target or self._should_skip(target):
                    continue
                callee_class = self._extract_called_class(target)
                if callee_class:
                    called_classes_set.add(callee_class)
                else:
                    called_funcs.add(target)
        return called_classes_set, called_funcs

    # ---------------------------
    # Build graph
    # ---------------------------
    def build_graph(self, cls_name, visited=None):
        visited = set(visited or [])
        if cls_name in visited:
            return {}
        visited.add(cls_name)

        if cls_name == "__global__":
            return {}

        methods = self.class_defs.get(cls_name, {})
        children = {}

        # expand all methods in this class
        for mname, mnode in methods.items():
            called_classes, called_funcs = self._called_targets(mnode, cls_name)
            subchildren = {}
            for callee in sorted(called_classes):
                subchildren.update(self.build_graph(callee, visited.copy()))
            for func in sorted(called_funcs):
                fn_node = None
                if "." in func:
                    base, meth = func.split(".", 1)
                    if base == cls_name:
                        fn_node = methods.get(meth)
                else:
                    fn_node = self.class_defs["__global__"].get(func)
                if fn_node:
                    subchildren[func] = self._expand_function(func, fn_node, cls_name, visited.copy())
                else:
                    subchildren[func] = {}
            children[mname] = subchildren

        return {cls_name: children}

    def _expand_function(self, name, fn_node, current_class, visited):
        called_classes_set, called_funcs = self._called_targets(fn_node, current_class)
        children = {}
        for callee in sorted(called_classes_set):
            children.update(self.build_graph(callee, visited.copy()))
        for func in sorted(called_funcs):
            fn_node2 = None
            if "." in func:
                base, meth = func.split(".", 1)
                if base == current_class:
                    fn_node2 = self.class_defs[current_class].get(meth)
            else:
                fn_node2 = self.class_defs["__global__"].get(func)
            if fn_node2:
                children[func] = self._expand_function(func, fn_node2, current_class, visited.copy())
            else:
                children[func] = {}
        return children

    # ---------------------------
    # Flatten graph -> dotted chains
    # ---------------------------
    def _flatten_graph(self, node, prefix=""):
        results = []
        for name, children in node.items():
            full = f"{prefix}.{name}" if prefix else name
            results.append(full)
            if children:
                results.extend(self._flatten_graph(children, full))
        return results

    # ---------------------------
    # Entry point
    # ---------------------------
    def resolve_from_entry(self):
        if not os.path.exists(self.entry_file):
            raise RuntimeError(f"Entry file not found: {self.entry_file!r}")

        roots = get_entry_class_names(self.entry_file)
        if not roots:
            print(f"No classes found in entry file: {self.entry_file}")
            return []

        raw_graphs = {}
        for root in roots:
            raw_graphs[root] = self.build_graph(root)

        # flatten graphs
        all_chains = []
        for graph in raw_graphs.values():
            all_chains.extend(self._flatten_graph(graph))

        # Include all static/class methods that might not be called
        for cls, methods in self.class_defs.items():
            if cls == "__global__":
                continue
            for mname, mnode in methods.items():
                full_name = f"{cls}.{mname}"
                if full_name not in all_chains:
                    all_chains.append(full_name)

        return sorted(set(all_chains))


from typing import List


def generate_action_chain(project_dir: str, entry_file: str = "dash_pipeline.py") -> List[str]:
    cg = MultiFileCallGraph(project_dir, entry_file=entry_file)
    chains = cg.resolve_from_entry()

    # Filter chains starting with 'dash_ingress.' and ignoring 'cls.'
    dash_ingress_chains = [c for c in chains if c.startswith("dash_ingress.") and "cls." not in c]

    # Remove all '.apply.' and '.cls.'
    cleaned_chains = [c.replace(".apply.", ".").replace(".cls.", ".") for c in dash_ingress_chains]

    # Ignore chains where the last function is 'apply'
    cleaned_chains = [c for c in cleaned_chains if not c.split(".")[-1] == "apply"]

    # Skip trivial/builtin functions
    skip_funcs = {"print", "bool", "get", "set"}
    cleaned_chains = [c for c in cleaned_chains if c.split(".")[-1] not in skip_funcs]

    # Deduplicate and sort
    final_chains = sorted(set(cleaned_chains))

    return final_chains


if __name__ == "__main__":
    project_dir = "py_model/data_plane"
    chains = generate_action_chain(project_dir, entry_file="dash_pipeline.py")

    print("Filtered, cleaned, deduplicated call chain:")
    for i, c in enumerate(chains, 1):
        print(i, " : ", c)
