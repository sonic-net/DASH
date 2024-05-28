from .common import *


@sai_parser_from_p4rt
class SAIEnumMember(SAIObject):
    """
    This class represents a single SAI enum member and provides parser from the P4Runtime enum member object
    """

    def __init__(self):
        super().__init__()
        self.p4rt_value: str = ""

    def parse_p4rt(self, p4rt_member: Dict[str, Any]) -> None:
        """
        This method parses the P4Runtime enum member object and populates the SAI enum member object.

        Example P4Runtime enum member object:

            { "name": "INVALID", "value": "AAA=" }
        """
        self.p4rt_value = str(p4rt_member["value"])
