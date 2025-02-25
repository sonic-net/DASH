from p4.v1 import p4runtime_pb2
from ipaddress import ip_address
from scapy.all import *
from dash_pipeline_utils import P4Table, P4InternalConfigTable, mac_in_bytes

def get_mac(interface):
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline().strip()
    except:
        mac = "00:00:00:00:00:00"
    return mac


class P4FlowTable(P4Table):
    def __init__(self, target=None):
        super(P4FlowTable, self).__init__(target)
        self.p4info_table = self.p4info.get_table("dash_ingress.conntrack_lookup_stage.flow_entry")
        self.match_id_map = { mf.name: mf.id for mf in self.p4info_table.match_fields}

    def print_flow_table(self):
        for entry in self.read(self.p4info_table.preamble.id):
            print(entry)

    def get(self,
            eni_mac, vnet_id,
            src_ip, dst_ip, src_port, dst_port, ip_proto):
        match_list = []

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.eni_mac']
        match.exact.value = mac_in_bytes(eni_mac)
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.vnet_id']
        match.exact.value = vnet_id.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.src_ip']
        match.exact.value = ip_address(src_ip).packed
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.dst_ip']
        match.exact.value = ip_address(dst_ip).packed
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.src_port']
        match.exact.value = src_port.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.dst_port']
        match.exact.value = dst_port.to_bytes(2, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.ip_proto']
        match.exact.value = ip_proto.to_bytes(1, byteorder='big')
        match_list.append(match)

        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['hdr.flow_key.is_ip_v6']
        match.exact.value = b'\x00' if ip_address(src_ip).version == 4 else b'\x01'
        match_list.append(match)

        return self.find(self.p4info_table.preamble.id, match_list)


def use_flow(cls):
    _setUp = getattr(cls, "setUp", None)
    _tearDown = getattr(cls, "tearDown", None)
    table = P4InternalConfigTable()

    def setUp(self, *args, **kwargs):
        if _setUp is not None:
            _setUp(self, *args, **kwargs)
        print(f'*** Enable Flow lookup')
        table.set(cpu_mac = get_mac("veth5"), flow_enabled = 1)
        return

    def tearDown(self, *args, **kwargs):
        print(f'*** Disable Flow lookup')
        table.set(flow_enabled = 0)
        if _tearDown is not None:
            _tearDown(self, *args, **kwargs)
        return

    setattr(cls, "setUp", setUp)
    setattr(cls, "tearDown", tearDown)
    return cls


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
    flow = flow_table.get(eni_mac, vnet_id,
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
