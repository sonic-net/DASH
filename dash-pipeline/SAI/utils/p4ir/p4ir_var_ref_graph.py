import json
import jsonpath_ng as jsonpath
import jsonpath_ng.ext as jsonpath_ext
from typing import Any, Dict, Callable, List
from .p4ir_tree import P4IRTree
from .p4ir_var_info import P4IRVarInfo
from .p4ir_var_ref_info import P4IRVarRefInfo


class P4VarRefGraph:
    def __init__(self, ir: P4IRTree) -> None:
        self.ir = ir
        self.counters: Dict[str, P4IRVarInfo] = {}
        self.var_refs: Dict[str, List[P4IRVarRefInfo]] = {}
        self.__build_graph()

    def __build_graph(self) -> None:
        self.__build_counter_list()
        self.__build_counter_caller_mapping()
        pass

    def __build_counter_list(self) -> None:
        def on_counter_definition(match: jsonpath.DatumInContext) -> None:
            ir_value = P4IRVarInfo.from_ir(match.value)
            self.counters[ir_value.ir_name] = ir_value
            print(f"Counter definition found: {ir_value}")

        self.ir.walk(
            '$..*[?Node_Type = "Declaration_Instance" & type.Node_Type = "Type_Name" & type.path.name = "counter"]',
            on_counter_definition,
        )

    def __build_counter_caller_mapping(self) -> None:
        # Build the mapping from counter name to its caller.
        def on_counter_invocation(match: jsonpath.DatumInContext) -> None:
            var_ir_name: str = match.value["expr"]["path"]["name"]
            if var_ir_name not in self.counters:
                return

            # Walk through the parent nodes to find the closest action or control block.
            cur_node = match
            while cur_node.context is not None:
                cur_node = cur_node.context
                if "Node_Type" not in cur_node.value:
                    continue

                if cur_node.value["Node_Type"] in ["P4Action", "P4Control"]:
                    var = self.counters[var_ir_name]
                    var_ref = P4IRVarRefInfo.from_ir(cur_node.value, var)
                    self.var_refs.setdefault(var.code_name, []).append(var_ref)
                    print(f"Counter reference found: {var_ref}")
                    break

        # Get all nodes with Node_Type =  and name = "counter". This will be the nodes that represent the counter calls.
        self.ir.walk(
            '$..*[?Node_Type = "Member" & member = "count"]', on_counter_invocation
        )
