from typing import Dict, List


class SaiApiP4MetaAction:
    def __init__(self, name: str, id: int):
        self.name: str = name
        self.id: int = id
        self.attr_param_id: Dict[str, int] = {}


class SaiApiP4MetaTable:
    def __init__(self, id: int):
        self.id: int = id
        self.actions: Dict[str, SaiApiP4MetaAction] = {}


class SaiApiP4Meta:
    def __init__(self):
        self.tables: List[SaiApiP4MetaTable] = []
