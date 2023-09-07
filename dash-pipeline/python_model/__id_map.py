
id_map = {}

def _search_obj(search_obj):
    global id_map
    for id, obj in id_map.items():
        if obj is search_obj:
            return id
    return None

_id = 0
def generate_id(obj):
    global _id, id_map
    res = _search_obj(obj)
    if res is None:
        res = _id
        id_map[res] = obj
        _id += 1
    return res
