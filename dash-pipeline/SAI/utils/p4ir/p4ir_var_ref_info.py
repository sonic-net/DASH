from typing import Any
from .p4ir_var_info import P4IRVarInfo


class P4IRVarRefInfo:
    @staticmethod
    def from_ir(ir_ref_node: Any, ir_var_info: P4IRVarInfo) -> "P4IRVarRefInfo":
        return P4IRVarRefInfo(
            ir_var_info,
            ir_ref_node["Node_ID"],
            ir_ref_node["Node_Type"],
            ir_ref_node["name"],
        )

    def __init__(
        self, var: P4IRVarInfo, caller_id: int, caller_type: str, caller: str
    ) -> None:
        self.var = var
        self.caller_id = caller_id
        self.caller_type = caller_type
        self.caller = caller

    def __str__(self) -> str:
        return f"VarName = {self.var.code_name}, CallerID = {self.caller_id}, CallerType = {self.caller_type}, Caller = {self.caller}"
