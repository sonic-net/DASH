#!/usr/bin/env python3
"""
Shared AST / filesystem utilities used by the graph extractors.

Provides:
- parse_files(directory)
- collect_class_methods(parsed_files) -> class_defs, file_class_map, global_funcs
- get_entry_class_nodes(entry_file) -> list of class names
- get_full_name(node) -> dotted name for Name/Attribute/Call
- extract_called_class_from_node(func_node, class_defs) -> class name or None
- called_classes(func_node, class_defs, cache=None) -> set of class names
"""

import ast
import os
from collections import defaultdict
from typing import Generator, Tuple, Dict, Any, Set, List


def parse_files(directory: str, skip_dirs: set | None = None) -> Generator[Tuple[str, ast.AST], None, None]:
    """Yield (path, ast.parse(tree)) for all .py files under directory.

    Skips common virtualenv / cache dirs by default.
    """
    if skip_dirs is None:
        skip_dirs = {"__pycache__", "venv", "site-packages", "tests"}
    directory = os.path.abspath(directory)
    for root, _, files in os.walk(directory):
        if any(skip in root for skip in skip_dirs):
            continue
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    yield path, ast.parse(f.read(), filename=path)
            except SyntaxError as e:
                print(f"Skipping {path}: {e}")

def collect_class_methods(parsed_files: List[Tuple[str, ast.AST]]
                          ) -> Tuple[Dict[str, Dict[str, ast.FunctionDef]], Dict[str, str], Dict[str, ast.FunctionDef]]:
    """From parsed_files produce:
    - class_defs: {class_name: {method_name: ast.FunctionDef}}
    - file_class_map: {class_name: file_path}
    - global_funcs: {func_name: ast.FunctionDef} stored under key '__global__' inside class_defs in some callers.
    """
    class_defs: Dict[str, Dict[str, ast.FunctionDef]] = defaultdict(dict)
    file_class_map: Dict[str, str] = {}
    global_funcs: Dict[str, ast.FunctionDef] = {}

    for path, tree in parsed_files:
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = {fn.name: fn for fn in node.body if isinstance(fn, ast.FunctionDef)}
                if methods:
                    class_defs[node.name].update(methods)
                else:
                    # ensure class exists even without methods
                    class_defs.setdefault(node.name, {})
                file_class_map[node.name] = path
            elif isinstance(node, ast.FunctionDef):
                global_funcs[node.name] = node

    return class_defs, file_class_map, global_funcs

def get_entry_class_names(entry_file: str) -> List[str]:
    """Return list of class names defined at top-level in entry_file."""
    if not os.path.exists(entry_file):
        raise RuntimeError(f"Entry file not found: {entry_file!r}")
    with open(entry_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=entry_file)
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]

def get_full_name(node: ast.AST) -> str | None:
    """Return dotted full name for Name/Attribute/Call nodes or None."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = get_full_name(node.value)
        return (parent + "." + node.attr) if parent else node.attr
    if isinstance(node, ast.Call):
        return get_full_name(node.func)
    return None

def extract_called_class_from_node(func_node: ast.AST, class_defs: Dict[str, Any]) -> str | None:
    """Return the class name if call target refers to a known class."""
    # Mirrors previous logic in the three scripts: check Attribute chain and Name nodes
    if isinstance(func_node, ast.Attribute):
        target = func_node
        while isinstance(target, ast.Attribute):
            if target.attr in class_defs:
                return target.attr
            target = target.value
        if isinstance(target, ast.Name) and target.id in class_defs:
            return target.id
    elif isinstance(func_node, ast.Name) and func_node.id in class_defs:
        return func_node.id
    return None

def called_classes(func_node: ast.AST, class_defs: Dict[str, Any], cache: Dict[ast.AST, Set[str]] | None = None) -> Set[str]:
    """Return set of class names called inside a function. Uses optional cache keyed by function node."""
    if func_node is None:
        return set()
    if cache is not None and func_node in cache:
        return cache[func_node]

    called = {
        callee for stmt in ast.walk(func_node)
        if isinstance(stmt, ast.Call)
        and (callee := extract_called_class_from_node(stmt.func, class_defs))
    }
    if cache is not None:
        cache[func_node] = called
    return called
