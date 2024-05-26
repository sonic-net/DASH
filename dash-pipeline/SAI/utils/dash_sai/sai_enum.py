from typing import List
from .common import *
from .sai_type_solver import SAITypeSolver
from .sai_enum_member import SAIEnumMember


@sai_parser_from_p4rt
class SAIEnum(SAIObject):
    """
    This class represents a single SAI enum and provides parser from the P4Runtime enum object
    """

    def __init__(self):
        super().__init__()
        self.bitwidth: int = 0
        self.members: List[SAIEnumMember] = []

    def parse_p4rt(self, p4rt_enum: Dict[str, Any]) -> None:
        """
        This method parses the P4Runtime enum object and populates the SAI enum object.

        Example P4Runtime enum object:

            "dash_encapsulation_t": {
                "underlyingType": { "bitwidth": 16 },
                "members": [
                    { "name": "INVALID", "value": "AAA=" },
                    { "name": "VXLAN", "value": "AAE=" },
                    { "name": "NVGRE", "value": "AAI=" }
                ]
            }
        """
        print("Parsing enum: " + self.name)

        self.name = self.name[:-2]
        self.bitwidth = int(p4rt_enum["underlyingType"][BITWIDTH_TAG])
        self.members = [
            SAIEnumMember.from_p4rt(enum_member)
            for enum_member in p4rt_enum[MEMBERS_TAG]
        ]

        # Register enum type info.
        SAITypeSolver.register_sai_type(
            "sai_" + self.name + "_t",
            "s32",
            default="SAI_" + self.name.upper() + "_" + self.members[0].name.upper(),
            is_enum=True,
        )
