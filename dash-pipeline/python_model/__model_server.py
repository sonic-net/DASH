from scapy.all import *
from __main import *
from __id_map import *
import socketserver
import json

class InsertRequest:
    class Value:
        class Ternary:
            value : str
            mask  : str
        
        class LPM:
            value : str
            prefix_len : int
        
        class Range:
            first : str
            last  : str

        exact   : str
        ternary : Ternary
        prefix  : LPM
        range   : Range
        ternary_list : list[Ternary]
        range_list : list[Range]

    table    : int
    values   : list[Value]
    action   : int
    params   : list[str]
    priority : int


def insert_request_to_table_entry(insertRequest: InsertRequest, key_format: list):
    entry = Entry()

    entry.values = []
    for idx, val in enumerate(insertRequest.values):
        if key_format[idx] is EXACT:
            entry.values.append(int(val.exact, 0))
        elif key_format[idx] is TERNARY:
            ternary = Entry.Ternary()
            ternary.value = int(val.ternary.value , 0)
            ternary.mask = int(val.ternary.mask , 0)
            entry.values.append(ternary)
        elif key_format[idx] is LIST:
            ternary_list = []
            for t in val.ternary_list:
                ternary = Entry.Ternary()
                ternary.value = int(t.value , 0)
                ternary.mask = int(t.mask , 0)
                ternary_list.append(ternary)
            entry.values.append(ternary_list)
        elif key_format[idx] is RANGE:
            range = Entry.Range()
            range.first = int(val.range.first , 0)
            range.last = int(val.range.last , 0)
            entry.values.append(range)
        elif key_format[idx] is RANGE_LIST:
            range_list = []
            for r in val.range_list:
                range = Entry.Range()
                range.first = int(r.first , 0)
                range.last = int(r.last , 0)
                range_list.append(range)
            entry.values.append(range_list)
        elif key_format[idx] is LPM:
            lpm = Entry.LPM()
            lpm.value = int(val.prefix.value , 0)
            lpm.prefix_len = val.prefix.prefix_len
            entry.values.append(lpm)

    entry.action = id_map[insertRequest.action]

    entry.params = []
    for param_str in insertRequest.params:
        entry.params.append(int(param_str , 0))

    entry.priority = insertRequest.priority
    return entry

def table_insert_api(insertRequest: InsertRequest):
    table = id_map[insertRequest.table]
    table.insert(insert_request_to_table_entry(insertRequest, list(table.key.values())))

def json_obj_to_insert_request(json_obj):
    insertRequest = InsertRequest()
    insertRequest.table = json_obj["table"]

    insertRequest.values = []
    for value_in_json in json_obj["values"]:
        value = InsertRequest.Value()
        value.exact = value_in_json["exact"]

        value.ternary = InsertRequest.Value.Ternary()
        value.ternary.value = value_in_json["ternary"]["value"]
        value.ternary.mask = value_in_json["ternary"]["mask"]

        value.prefix = InsertRequest.Value.LPM()
        value.prefix.value = value_in_json["prefix"]["value"]
        value.prefix.prefix_len = value_in_json["prefix"]["prefix_len"]

        value.range = InsertRequest.Value.Range()
        value.range.first = value_in_json["range"]["first"]
        value.range.last = value_in_json["range"]["last"]

        value.ternary_list = []
        for ternary_in_json in value_in_json["ternary_list"]:
            ternary = InsertRequest.Value.Ternary()
            ternary.value = ternary_in_json["value"]
            ternary.mask = ternary_in_json["mask"]
            value.ternary_list.append(ternary)

        value.range_list = []
        for range_in_json in value_in_json["range_list"]:
            range = InsertRequest.Value.Range()
            range.first = range_in_json["first"]
            range.last = range_in_json["last"]
            value.range_list.append(range)

        insertRequest.values.append(value)
    
    insertRequest.action = json_obj["action"]

    insertRequest.params = []
    for param_str in json_obj["params"]:
        insertRequest.params.append(param_str)

    insertRequest.priority = json_obj["priority"]
    return insertRequest

class ModelTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        api_id = self.request.recv(1)[0]
        if api_id == 0:
            json_buf_size = int(self.request.recv(8).decode("ascii"), 16)
            json_obj = json.loads(self.request.recv(json_buf_size))
            insertRequest = json_obj_to_insert_request(json_obj)
            table_insert_api(insertRequest)
            self.request.sendall(b'\x00')

HOST, PORT = "localhost", 46500

with socketserver.TCPServer((HOST, PORT), ModelTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
