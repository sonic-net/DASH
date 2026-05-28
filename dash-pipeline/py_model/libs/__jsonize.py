
def _write_str(file, str_value):
    file.write('"')
    file.write(str_value)
    file.write('"')

def _write_int(file, int_value):
    file.write(str(int_value))

def _write_bool(file, bool_value):
    file.write(str(bool_value))

def _write_dict(file, dict_value, level):
    file.write("{\n")
    i = 0
    for k in dict_value:
        file.write(" " * level)
        file.write('"')
        file.write(k)
        file.write('": ')
        _write_value(file, dict_value[k], level + 1)
        if i < len(dict_value) - 1:
            file.write(',')
        file.write("\n")
        i += 1
    file.write(" " * (level - 1))
    file.write("}")

def _write_list(file, list_value, level):
    file.write("[\n")
    i = 0
    for item in list_value:
        file.write(" " * level)
        _write_value(file, item, level + 1)
        if i < len(list_value) - 1:
            file.write(',')
        file.write("\n")
        i += 1
    file.write(" " * (level - 1))
    file.write("]")

def _write_value(file, value, level):
    value_type = type(value)
    if value_type == str:
        _write_str(file, value)
    elif value_type == dict:
        _write_dict(file, value, level)
    elif value_type == list:
        _write_list(file, value, level)
    elif value_type == int:
        _write_int(file, value)
    elif value_type == bool:
        _write_bool(file, value)
    else:
        raise ValueError("Type not supported")

def jsonize(file_name, value):
    file = open(file_name, "w")
    _write_value(file, value, 1)
    file.close()
