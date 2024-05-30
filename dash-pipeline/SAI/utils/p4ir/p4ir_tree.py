import json
import jsonpath_ng.ext as jsonpath_ext
from typing import Any, Dict, Callable


class P4IRTree:
    @staticmethod
    def from_file(path: str) -> "P4IRTree":
        with open(path, "r") as f:
            return P4IRTree(json.load(f))

    def __init__(self, program: Dict[str, Any]) -> None:
        self.program = program

    def walk(self, path: str, on_match: Callable[[Any, Any], None]) -> None:
        jsonpath_exp = jsonpath_ext.parse(path)
        for match in jsonpath_exp.find(self.program):
            on_match(match)
