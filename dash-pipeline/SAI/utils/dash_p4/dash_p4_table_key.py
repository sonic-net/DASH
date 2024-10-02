from .common import *
from .dash_p4_table_attribute import *
from .sai_type_solver import *


@dash_p4rt_parser
class DashP4TableKey(DashP4TableAttribute):
    """
    This class represents a single SAI API table key and provides parser from the P4Runtime table key object.
    """

    def __init__(self):
        super().__init__()
        self.ip_is_v6_field_id: int = 0

    def parse_p4rt(self, p4rt_table_key: Dict[str, Any]) -> None:
        """
        This method parses the P4Runtime table key object and populates the SAI API table key object.

        Example P4Runtime table key object:

            {
                "id": 1,
                "name": "meta.vnet_id:vnet_id",
                "bitwidth": 16,
                "matchType": "EXACT"
            },
            {
                "id": 2,
                "name": "hdr.ipv4.src_addr:sip",
                "bitwidth": 32,
                "matchType": "EXACT"
            }
        """

        self.bitwidth = int(p4rt_table_key[BITWIDTH_TAG])
        # print("Parsing table key: " + self.name)

        if OTHER_MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type = str(p4rt_table_key[OTHER_MATCH_TYPE_TAG].lower())
        elif MATCH_TYPE_TAG in p4rt_table_key:
            self.match_type = str(p4rt_table_key[MATCH_TYPE_TAG].lower())
        else:
            raise ValueError(f"No valid match tag found")

        self._parse_sai_table_attribute_annotation(p4rt_table_key)

        # If type is specified, use it. Otherwise, try to find the proper type using default heuristics.
        if self.type != None:
            sai_type_info = SAITypeSolver.get_sai_type(self.type)
        else:
            sai_type_info = SAITypeSolver.get_match_key_sai_type(
                self.match_type, self.bitwidth
            )

        self.set_sai_type(sai_type_info)

        return

    #
    # Functions for generating SAI specs.
    #
    def get_sai_description(self, table_name: str):
        return f"{self.match_type.capitalize()} matched key {self.name}"