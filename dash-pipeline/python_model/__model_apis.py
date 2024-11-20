
class Ternary:
    value: str
    mask: str

class LPM:
    value: str
    prefix_len: int

class Range:
    first: str
    last: str

class Value:
    exact: str
    ternary: Ternary
    prefix: LPM
    range: Range
    ternary_list: list[Ternary]
    range_list: list[Range]

class InsertRequest:
    table : int
    values: list[Value]
    action: int
    params: list[str]
    priority: int

def insert_entry(insertRequest: InsertRequest):
    pass
