#!/usr/bin/env python3
"""
Build a cross-file call chain using Python AST.

Features:
- Recursively scans .py files under 'data_plane'.
- Collects only calls inside 'apply' functions.
- Filters out unwanted names (apply, *_apply, *_t, uppercase, .apply, builtins).
- Returns a unique list of function calls (last part only).
"""

import os, ast, json, builtins

def get_python_files(project_dir="."):
    """Return all .py files under project_dir containing 'data_plane'."""
    return [
        os.path.join(r, f)
        for r, _, files in os.walk(project_dir)
        for f in files if f.endswith(".py") and "data_plane" in r
    ]

class ImportTracker(ast.NodeVisitor):
    """Tracks import statements in a file."""
    def __init__(self):
        self.imports = {}
    def visit_Import(self, node):
        for a in node.names:
            self.imports[a.asname or a.name] = a.name
    def visit_ImportFrom(self, node):
        for a in node.names:
            self.imports[a.asname or a.name] = f"{node.module}.{a.name}" if node.module else a.name

class CallGraphVisitor(ast.NodeVisitor):
    """Collects calls inside 'apply' functions."""
    def __init__(self, imports):
        self.imports, self.calls, self.current = imports, set(), None
        self.skip = set(dir(builtins)) | {
            "get","keys","values","items","update","append","extend",
            "insert","pop","remove","clear","copy"
        }

    def visit_FunctionDef(self, node):
        if node.name == "apply":
            self.current = node.name
            self.generic_visit(node)
            self.current = None

    def visit_Call(self, node):
        if not self.current:
            return
        name = None
        is_class_method = False

        if isinstance(node.func, ast.Name):
            name = self.imports.get(node.func.id, node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ("self", "cls"):
                is_class_method = True
            name = node.func.attr

        if name:
            name = name.rsplit(".", 1)[-1]
            if not (
                name == "apply" or name == "py_log" or 
                name.endswith("_apply") or name.endswith("_t") or 
                name.isupper() or name in self.skip
            ):
                self.calls.add((name, is_class_method))

def generate_global_actions_chain(project_dir="."):
    """Return unique list of function calls inside 'apply' functions."""
    all_calls = set()
    for pyfile in get_python_files(project_dir):
        try:
            with open(pyfile, "r", encoding="utf-8") as f:
                source = f.read()
            if not source.strip():
                continue
            tree = ast.parse(source, filename=pyfile)
            tracker = ImportTracker(); tracker.visit(tree)
            visitor = CallGraphVisitor(tracker.imports); visitor.visit(tree)
            all_calls.update(visitor.calls)
        except Exception as e:
            print(f"Failed to parse {pyfile}: {e}")
    return sorted(all_calls)

if __name__ == "__main__":
    project_dir = "py_model/data_plane"

    graph = generate_global_actions_chain(project_dir)

    tagged_calls = [
        f"[class] {name}" if is_class_method else f"[func] {name}"
        for name, is_class_method in graph
    ]

    print("\nCombined call chain:")
    for item in tagged_calls:
        print(item)
