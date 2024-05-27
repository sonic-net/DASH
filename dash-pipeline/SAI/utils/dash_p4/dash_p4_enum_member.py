import base64
from .common import *
from ..sai_spec import SaiEnumMember


@dash_p4rt_parser
class DashP4EnumMember(DashP4Object):
    """
    This class represents a single SAI enum member and provides parser from the P4Runtime enum member object
    """

    def __init__(self):
        super().__init__()
        self.enum_value: int = ""

    def parse_p4rt(self, p4rt_member: Dict[str, Any]) -> None:
        """
        This method parses the P4Runtime enum member object and populates the SAI enum member object.

        Example P4Runtime enum member object:

            { "name": "INVALID", "value": "AAA=" }
        """
        decoded_bytes = base64.b64decode(str(p4rt_member["value"]))
        self.enum_value = int.from_bytes(decoded_bytes, byteorder="big")

    def to_sai(self) -> SaiEnumMember:
        return SaiEnumMember(self.name, "", str(self.enum_value))
