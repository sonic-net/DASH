import json
from typing import Any


class P4IRVarInfo:
    @staticmethod
    def from_ir(ir_def_node: Any) -> "P4IRVarInfo":
        return P4IRVarInfo(
            ir_def_node["Node_ID"],
            ir_def_node["name"],
            ir_def_node["Source_Info"]["source_fragment"],
            ir_def_node["type"]["path"]["name"],
        )

    def __init__(
        self, ir_id: int, ir_name: str, code_name: str, type_name: str
    ) -> None:
        self.ir_id = ir_id
        self.ir_name = ir_name
        self.code_name = code_name
        self.type_name = type_name

    def __str__(self) -> str:
        return f"ID = {self.ir_id}, Name = {self.ir_name}, VarName = {self.code_name}, Type = {self.type_name}"
