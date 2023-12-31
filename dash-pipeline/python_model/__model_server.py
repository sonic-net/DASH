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


def table_insert_api(insertRequest: InsertRequest):
    table = id_map[insertRequest.table]
    


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


#        self.request.sendall(data)


HOST, PORT = "localhost", 46500

with socketserver.TCPServer((HOST, PORT), ModelTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
