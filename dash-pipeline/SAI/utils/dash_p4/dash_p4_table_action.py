from typing import List
from .common import *
from .dash_p4_table_action_param import *
from .dash_p4_counter import *
from .dash_p4_enum import *


@dash_p4rt_parser
class DashP4TableAction(DashP4Object):
    def __init__(self):
        super().__init__()
        self.params: List[DashP4TableActionParam] = []
        self.counters: List[DashP4Counter] = []

    def parse_p4rt(
        self,
        p4rt_table_action: Dict[str, Any],
        sai_enums: List[DashP4Enum],
        counters_by_action_name: Dict[str, List[DashP4Counter]],
    ) -> None:
        """
        This method parses the P4Runtime table action object and populates the SAI API table action object.

        Example P4Runtime table action object:

            {
                "preamble": {
                    "id": 25364446,
                    "name": "dash_ingress.outbound.route_vnet",
                    "alias": "route_vnet"
                },
                "params": [
                    { "id": 1, "name": "dst_vnet_id", "bitwidth": 16 },
                    { "id": 2, "name": "meter_class_or", "bitwidth": 32 },
                    { "id": 3, "name": "meter_class_and", "bitwidth": 32 }
                ]
            }
        """
        # print("Parsing table action: " + self.name)
        self.parse_action_params(p4rt_table_action, sai_enums)
        self.counters = (
            counters_by_action_name[self.name]
            if self.name in counters_by_action_name
            else []
        )

    def parse_action_params(
        self, p4rt_table_action: Dict[str, Any], sai_enums: List[DashP4Enum]
    ) -> None:
        if PARAMS_TAG not in p4rt_table_action:
            return

        # Parse all params.
        for p in p4rt_table_action[PARAMS_TAG]:
            param = DashP4TableActionParam.from_p4rt(p)
            self.params.append(param)

        self.params = DashP4TableAttribute.link_ip_is_v6_vars(self.params)

        return
