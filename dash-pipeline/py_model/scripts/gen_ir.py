#!/usr/bin/env python3

import json
import itertools
from typing import Optional
from collections import OrderedDict

from py_model.libs.__id_map import *
from py_model.libs.__jsonize import *
from py_model.libs.__counters import *
from py_model.dash_py_v1model import *

node_id = itertools.count(1000000)
type_id = itertools.count(2000)

def make_source_fragment(counter_obj, var_name="VarName") -> str:
    # Case 1: SaiCounter-based Counter
    if hasattr(counter_obj, "config") and isinstance(counter_obj.config, SaiCounter):
        cfg = counter_obj.config

        # Build annotation part
        attrs = []
        if cfg.name:
            attrs.append(f'name="{cfg.name}"')
        if cfg.no_suffix:
            attrs.append('no_suffix="true"')
        if cfg.attr_type:
            attrs.append(f'attr_type="{cfg.attr_type}"')
        if cfg.action_names:
            if isinstance(cfg.action_names, str):
                names = cfg.action_names
            else:
                names = ",".join(cfg.action_names)
            attrs.append(f'action_names="{names}"')

        annotation = "@SaiCounter[" + ", ".join(attrs) + "]"

        # Counter type string (default to "packets" if not set)
        ctype = getattr(cfg.counter_type, "name", "packets").lower()

        fragment = f'{annotation} counter({cfg.size}, CounterType.{ctype}) {cfg.ctr_name};, Type = counter'
        return fragment.replace('"', '\\"')  # escape quotes

    # Case 2: DirectCounter
    elif isinstance(counter_obj, DirectCounter):
        ctype = getattr(counter_obj.counter_type, "name", "packets_and_bytes").lower()
        annotation = '@SaiCounter[attr_type="stats"]'
        fragment = f'{annotation} counter(64, CounterType.{ctype}) {counter_obj.name};, Type = counter'
        return fragment.replace('"', '\\"')

    else:
        raise TypeError(f"Unsupported counter type: {type(counter_obj)}")


def make_vec_node(ctr_name: str) -> Optional[OrderedDict]:
    filename, lineno = None, None

    ctr = DashCounters._counters.get(ctr_name)
    if ctr is None:
        print(f"Counter '{ctr_name}' not found in DashCounters._counters")
        return None

    node = OrderedDict(
        Node_ID=next(node_id),
        Node_Type="Declaration_Instance",
        name=ctr_name,
        annotations={},
        type=OrderedDict(
            Node_ID=next(type_id),
            Node_Type="Type_Name",
            path=OrderedDict(Node_ID=next(type_id), Node_Type="Path", name="counter")
        ),
        arguments={},
        properties={},
        Source_Info=OrderedDict(filename=filename, line=lineno, source_fragment=make_source_fragment(ctr))
    )

    return node


def gen_ir() -> OrderedDict:
    ir = OrderedDict(Node_ID=next(node_id), Node_Type="PyProgram")

    objects = OrderedDict(Node_ID=next(node_id), Node_Type="Vector<Node>")

    if not counter_ids:
        # print("counter_ids is empty, using DashCounters._counters instead")
        for key in DashCounters._counters.keys():
            counter_ids[key] = key

    obj_vecs = []
    for key in counter_ids:
        node = make_vec_node(key)
        if node:
            obj_vecs.append(node)

    objects["vec"] = obj_vecs
    ir["objects"] = objects
    return ir


if __name__ == "__main__":
    ir = gen_ir()
    with open("py_ir.json", "w") as f:
        json.dump(ir, f, indent=2, sort_keys=False)
    print("py_ir.json written.")
