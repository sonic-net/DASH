from .common import *
from .dash_p4_table_attribute import *
from .sai_type_solver import *


@dash_p4rt_parser
class DashP4TableActionParam(DashP4TableAttribute):
    def __init__(self):
        super().__init__()
        self.bitwidth: int = 0
        self.ip_is_v6_field_id: int = 0
        self.param_actions: List[Any] = []
        # TODO: Fix circular type references
        # self.param_actions: List[SAIAPITableAction] = []

    def parse_p4rt(self, p4rt_table_action_param: Dict[str, Any]) -> None:
        """
        This method parses the P4Runtime table action object and populates the SAI API table action object.

        Example P4Runtime table action object:

            { "id": 1, "name": "dst_vnet_id", "bitwidth": 16 }
        """
        self.bitwidth = int(p4rt_table_action_param[BITWIDTH_TAG])
        # print("Parsing table action param: " + self.name)

        self._parse_sai_table_attribute_annotation(p4rt_table_action_param)

        # If type is specified, use it. Otherwise, try to find the proper type using default heuristics.
        if self.type != None:
            sai_type_info = SAITypeSolver.get_sai_type(self.type)
        else:
            sai_type_info = SAITypeSolver.get_object_sai_type(self.bitwidth)

        self.set_sai_type(sai_type_info)

        return
