
id_map = {}

_id = 0
def generate_id(obj):
    global _id, id_map
    res = _id
    id_map[res] = obj
    _id += 1
    return res
