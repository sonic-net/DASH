from typing import Dict, List, Optional


class SaiApiP4MetaActionParam:
    def __init__(self, id: int, field: str, bitwidth: int,
                 ip_is_v6_field_id: int, skipattr: str):
        self.id: int = id
        self.field: str =  field
        self.bitwidth: int =  bitwidth
        self.ip_is_v6_field_id: int = ip_is_v6_field_id
        self.skipattr: str = skipattr

class SaiApiP4MetaAction:
    def __init__(self, name: str, id: int):
        self.name: str = name
        self.id: int = id
        self.attr_params: Dict[str, SaiApiP4MetaActionParam] = {}

class SaiApiP4MetaKey:
    def __init__(self, name: str, id: int, match_type: str,
                 field: str, bitwidth: int, ip_is_v6_field_id: int,
                 is_object_key: bool):
        self.name: str = name
        self.id: int = id
        self.match_type: int = match_type
        self.field: str =  field
        self.bitwidth: int =  bitwidth
        self.ip_is_v6_field_id: int = ip_is_v6_field_id
        self.is_object_key: bool = is_object_key

class SaiApiP4MetaTable:
    def __init__(self, id: int, stage: Optional[str] = None):
        self.id: int = id
        self.stage: Optional[str] = stage
        self.keys: List[SaiApiP4MetaKey] = []
        self.actions: Dict[str, SaiApiP4MetaAction] = {}


class SaiApiP4Meta:
    def __init__(self):
        self.tables: List[SaiApiP4MetaTable] = []
