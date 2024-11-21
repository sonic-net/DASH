import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from ipaddress import ip_address
from scapy.all import *


def get_mac(interface):
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline().strip()
    except:
        mac = "00:00:00:00:00:00"
    return mac


def mac_in_bytes(mac):
    return bytes(int(b, 16) for b in mac.split(":"))


class P4info():
    def __init__(self, stub):
        self.config = P4info.get_pipeline_config(stub)

    @staticmethod
    def get_pipeline_config(stub):
        try:
            req = p4runtime_pb2.GetForwardingPipelineConfigRequest()
            req.device_id = 0
            req.response_type = p4runtime_pb2.GetForwardingPipelineConfigRequest.ResponseType.P4INFO_AND_COOKIE
            return stub.GetForwardingPipelineConfig(req).config.p4info
        except Exception as e:
            print(f'gRPC error: str({e})')
            return None

    def get_table(self, name):
        for table in self.config.tables:
            if table.preamble.name == name:
                return table

        return None

    def get_action(self, name):
        for action in self.config.actions:
            if action.preamble.name == name:
                return action

        return None


def set_internal_config(neighbor_mac :bytes = None,
                        mac :bytes = None,
                        cpu_mac :bytes = None,
                        flow_enabled :bytes = None):
    '''
    Set dash pipeline internal config by updating table entry of internal_config.

    if one argument is not specifed, the action param is not changed in the
    existing table entry, otherwise set default value in new table entry.
    '''
    channel = grpc.insecure_channel('localhost:9559')
    stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

    p4info = P4info(stub)
    internal_config = p4info.get_table("dash_ingress.dash_lookup_stage.pre_pipeline_stage.internal_config")

    entry = p4runtime_pb2.TableEntry()
    entry.table_id = internal_config.preamble.id
    entry.priority = 1

    match = entry.match.add()
    match.field_id = 1
    match.ternary.value = b'\x00'
    match.ternary.mask = b'\xff'

    req = p4runtime_pb2.ReadRequest()
    req.device_id = 0
    entity = req.entities.add()
    entity.table_entry.CopyFrom(entry)
    for response in stub.Read(req):
        if not response.entities:
            continue
        entry = response.entities[0].table_entry
        changed = 0

        param = entry.action.action.params[0]
        if neighbor_mac and neighbor_mac != param.value:
            param.value = neighbor_mac
            changed += 1

        param = entry.action.action.params[1]
        if mac and mac != param.value:
            param.value = mac
            changed += 1

        param = entry.action.action.params[2]
        if cpu_mac and cpu_mac != param.value:
            param.value = cpu_mac
            changed += 1

        param = entry.action.action.params[3]
        if flow_enabled and flow_enabled != param.value:
            param.value = flow_enabled
            changed += 1

        if not changed:
            return # none of change

        req = p4runtime_pb2.WriteRequest()
        req.device_id = 0
        update = req.updates.add()
        update.type = p4runtime_pb2.Update.MODIFY
        update.entity.table_entry.CopyFrom(entry)
        stub.Write(req)
        return

    # Add one entry
    set_internal_config = p4info.get_action("dash_ingress.dash_lookup_stage.pre_pipeline_stage.set_internal_config")
    entry.action.action.action_id = set_internal_config.preamble.id
    action = entry.action.action

    param = action.params.add()
    param.param_id = 1
    if neighbor_mac:
        param.value = neighbor_mac
    else:   # default value
        param.value = b'\x00\x00\x00\x00\x00\x00'

    param = action.params.add()
    param.param_id = 2
    if mac:
        param.value = mac
    else:   # default value
        param.value = b'\x00\x00\x00\x00\x00\x00'

    param = action.params.add()
    param.param_id = 3
    if cpu_mac:
        param.value = cpu_mac
    else:   # default value
        param.value = b'\x00\x00\x00\x00\x00\x00'

    param = action.params.add()
    param.param_id = 4
    if flow_enabled:
        param.value = flow_enabled
    else:   # default value
        param.value = b'\x00'

    req = p4runtime_pb2.WriteRequest()
    req.device_id = 0
    update = req.updates.add()
    update.type = p4runtime_pb2.Update.INSERT
    update.entity.table_entry.CopyFrom(entry)
    stub.Write(req)


def use_flow(cls):
    _setUp = getattr(cls, "setUp", None)
    _tearDown = getattr(cls, "tearDown", None)

    def setUp(self, *args, **kwargs):
        if _setUp is not None:
            _setUp(self, *args, **kwargs)
        print(f'*** Enable Flow lookup')
        set_internal_config(cpu_mac = mac_in_bytes(get_mac("veth5")),
                            flow_enabled = b'\x01')
        return

    def tearDown(self, *args, **kwargs):
        print(f'*** Disable Flow lookup')
        set_internal_config(flow_enabled = b'\x00')
        if _tearDown is not None:
            _tearDown(self, *args, **kwargs)
        return

    setattr(cls, "setUp", setUp)
    setattr(cls, "tearDown", tearDown)
    return cls


class P4Table():
    def __init__(self):
        channel = grpc.insecure_channel('localhost:9559')
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)
        self.p4info = P4info(self.stub)

    def read(self, table_id, match_list = None):
        entry = p4runtime_pb2.TableEntry()
        entry.table_id = table_id
        if match_list:
            entry.match.extend(match_list)

        req = p4runtime_pb2.ReadRequest()
        req.device_id = 0
        entity = req.entities.add()
        entity.table_entry.CopyFrom(entry)
        for response in self.stub.Read(req):
            for entity in response.entities:
                yield entity.table_entry


class P4FlowTable(P4Table):
    def __init__(self):
        super(P4FlowTable, self).__init__()
        self.p4info_table_flow = self.p4info.get_table("dash_ingress.conntrack_lookup_stage.flow_entry")

    def print_flow_table(self):
        for entry in self.read(self.p4info_table_flow.preamble.id):
            print(entry)

    def get_flow_entry(self, eni_mac, vnet_id,
                       src_ip, dst_ip,
                       src_port, dst_port, ip_proto):
        match_list = []

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 1
        match.exact.value = mac_in_bytes(eni_mac)
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 2
        match.exact.value = vnet_id.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 3
        match.exact.value = ip_address(src_ip).packed
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 4
        match.exact.value = ip_address(dst_ip).packed
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 5
        match.exact.value = src_port.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 6
        match.exact.value = dst_port.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 7
        match.exact.value = ip_proto.to_bytes(1, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = 8
        match.exact.value = b'\x00' if ip_address(src_ip).version == 4 else b'\x01'
        match_list.append(match)

        for entry in self.read(self.p4info_table_flow.preamble.id, match_list):
            return entry

        return None


def verify_flow(eni_mac, vnet_id, packet, existed = True):
    if packet.haslayer(TCP):
        sport = packet['TCP'].sport
        dport = packet['TCP'].dport
    elif packet.haslayer(UDP):
        sport = packet['UDP'].sport
        dport = packet['UDP'].dport
    else:   # TODO: later for other ip proto
        assert False, "Not TCP/UDP packet"

    flow_table = P4FlowTable()
    flow = flow_table.get_flow_entry(eni_mac, vnet_id,
                                     packet['IP'].src,
                                     packet['IP'].dst,
                                     sport,
                                     dport,
                                     packet['IP'].proto)
    if existed:
        assert flow, "flow not found"
    else:
        assert not flow, "flow still found"


def verify_no_flow(eni_mac, vnet_id, packet):
    verify_flow(eni_mac, vnet_id, packet, existed = False)
