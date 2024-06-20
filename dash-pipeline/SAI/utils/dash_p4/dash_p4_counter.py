import copy
from typing import Iterator
from .common import *
from .dash_p4_table_attribute import *
from .sai_type_solver import *
from utils.p4ir import P4VarRefGraph


@dash_p4rt_parser
class DashP4Counter(DashP4TableAttribute):
    """
    This class represents a single counter in SAI and provides parser from the P4Runtime counter object
    """

    def __init__(self):
        super().__init__()
        self.bitwidth: int = 64
        self.isreadonly: str = "true"
        self.counter_type: str = "bytes"
        self.attr_type: str = "stats"
        self.no_suffix: bool = ""
        self.param_actions: List[str] = []

    def parse_p4rt(
        self, p4rt_counter: Dict[str, Any], var_ref_graph: P4VarRefGraph
    ) -> None:
        """
        This method parses the P4Runtime counter object and populates the SAI counter object.

        Example P4Runtime counter object:

            {
                "preamble": {
                    "id": 318423147,
                    "name": "dash_ingress.meter_bucket_inbound",
                    "alias": "meter_bucket_inbound"
                },
                "spec": {
                    "unit": "BYTES"
                },
                "size": "262144"
            }
        """
        print("Parsing counter: " + self.name)
        self.__parse_sai_counter_annotation(p4rt_counter)

        # If this counter needs to be generated as SAI attributes, we need to figure out the data type for the counter value.
        if self.attr_type != "counter_id":
            counter_storage_type = SAITypeSolver.get_object_sai_type(self.bitwidth)

        # Otherwise, this counter should be linked to a SAI counter using an object ID.
        # In this case, the type needs to be sai_object_id_t.
        else:
            counter_storage_type = SAITypeSolver.get_sai_type("sai_object_id_t")
            self.name = f"{self.name}_counter_id"
            self.isreadonly = "false"
            self.object_name = "counter"

        self.set_sai_type(counter_storage_type)

        counter_unit = str(p4rt_counter["spec"]["unit"]).lower()
        if counter_unit in ["bytes", "packets", "both"]:
            self.counter_type = counter_unit.lower()
        else:
            raise ValueError(f"Unknown counter unit: {counter_unit}")

        # If actions are specified by annotation, then we skip finding the referenced actions from the IR.
        if len(self.param_actions) == 0 and self.raw_name in var_ref_graph.var_refs:
            for ref in var_ref_graph.var_refs[self.raw_name]:
                if ref.caller_type == "P4Action":
                    self.param_actions.append(ref.caller)

            print(f"Counter {self.name} is referenced by {self.param_actions}")

        return

    def __parse_sai_counter_annotation(self, p4rt_counter: Dict[str, Any]) -> None:
        """
        This method parses the SAI annotations and populates the SAI counter object.

        Example SAI annotations:

            {
                "name": "SaiCounter",
                "kvPairList": {
                    "kvPairs": [
                        { "key": "name", "value": { "stringValue": "counter_name" } }
                    ]
                }
            }

        Whenever a new attribute is introduced, please update the doc here to get it captured: dash-pipeline/bmv2/README.md.
        """
        for anno in p4rt_counter[PREAMBLE_TAG][STRUCTURED_ANNOTATIONS_TAG]:
            if anno[NAME_TAG] == SAI_COUNTER_TAG:
                for kv in anno[KV_PAIR_LIST_TAG][KV_PAIRS_TAG]:
                    if self._parse_sai_common_annotation(kv):
                        continue
                    elif kv["key"] == "action_names":
                        self.param_actions = str(kv["value"]["stringValue"]).split(",")
                    elif kv["key"] == "attr_type":
                        self.attr_type = str(kv["value"]["stringValue"])
                        if self.attr_type not in [
                            "counter_attr",
                            "counter_id",
                            "stats",
                        ]:
                            raise ValueError(
                                f"Unknown counter attribute type: attr_type={self.attr_type}"
                            )
                    elif kv["key"] == "no_suffix":
                        self.no_suffix = str(kv["value"]["stringValue"]) == "true"
                    else:
                        raise ValueError("Unknown attr annotation " + kv["key"])

    def generate_counter_sai_attributes(self) -> "Iterator[DashP4Counter]":
        # If the SAI attribute type is counter id, we generate as standard SAI counter ID attributes, hence return as it is.
        if self.attr_type == "counter_id":
            yield self

        counter_types = (
            ["bytes", "packets"] if self.counter_type == "both" else [self.counter_type]
        )

        for index, counter_type in enumerate(counter_types):
            counter = self
            if index != len(counter_types) - 1:
                counter = copy.deepcopy(self)

            counter.counter_type = counter_type

            if counter.attr_type == "counter_attr":
                counter.name = (
                    f"{counter.name}_{counter.counter_type}_counter"
                    if not self.no_suffix
                    else f"{counter.name}_counter"
                )
            else:
                counter.name = (
                    f"{counter.name}_{counter.counter_type}"
                    if not self.no_suffix
                    else counter.name
                )

            yield counter

    #
    # Functions for generating SAI specs.
    #
    def get_sai_name(self, table_name: str) -> str:
        if self.attr_type == "stats":
            return f"SAI_{table_name.upper()}_STAT_{self.name.upper()}"

        return f"SAI_{table_name.upper()}_{self.name.upper()}"
    
    def get_sai_description(self, table_name: str):
        if self.attr_type == "stats":
            return f"DASH {table_name.upper()} {self.name.upper()} stat count"

        return f"Counter attribute {self.name.upper()}"