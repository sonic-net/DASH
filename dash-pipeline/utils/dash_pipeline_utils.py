import grpc
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
import socket


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


class P4Table():
    def __init__(self, target=None):
        if not target:
            target='localhost:9559'
        channel = grpc.insecure_channel(target)
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)
        self.p4info = P4info(self.stub)

    def read(self, table_id, match_list = None, priority = None):
        entry = p4runtime_pb2.TableEntry()
        entry.table_id = table_id
        if match_list:
            entry.match.extend(match_list)
        if priority != None:
            entry.priority = priority

        req = p4runtime_pb2.ReadRequest()
        req.device_id = 0
        entity = req.entities.add()
        entity.table_entry.CopyFrom(entry)
        for response in self.stub.Read(req):
            for entity in response.entities:
                yield entity.table_entry

    def write(self, entry, update_type):
        req = p4runtime_pb2.WriteRequest()
        req.device_id = 0
        update = req.updates.add()
        update.type = update_type
        update.entity.table_entry.CopyFrom(entry)
        self.stub.Write(req)

    def find(self, table_id, user_match_list, priority = None):
        for entry in self.read(table_id, user_match_list, priority):
            return entry
        return None

    def update(self, table_id, user_match_list, action_id, user_params, priority = None):
        entry = self.find(table_id, user_match_list, priority)
        if entry:
            changed = 0

            for param in entry.action.action.params:
                if param.param_id in user_params:
                    byte_data, _ = user_params[param.param_id]
                    if byte_data is not None and byte_data != param.value:
                        param.value = byte_data
                        changed += 1

            if changed:
                self.write(entry, p4runtime_pb2.Update.MODIFY)
            return

        # Add one entry
        entry = p4runtime_pb2.TableEntry()
        entry.table_id = table_id
        if priority is not None:
            entry.priority = priority
        entry.match.extend(user_match_list)

        entry.action.action.action_id = action_id
        action = entry.action.action

        for param_id,param_value in user_params.items():
            param = action.params.add()
            param.param_id = param_id
            if param_value[0] is not None:
                param.value = param_value[0]
            else:
                param.value = param_value[1]

        self.write(entry, p4runtime_pb2.Update.INSERT)


class P4InternalConfigTable(P4Table):
    def __init__(self, target=None):
        super(P4InternalConfigTable, self).__init__(target)
        self.p4info_table = self.p4info.get_table("dash_ingress.dash_lookup_stage.pre_pipeline_stage.internal_config")
        self.match_id_map = { mf.name: mf.id for mf in self.p4info_table.match_fields}
        self.set_internal_config = self.p4info.get_action("dash_ingress.dash_lookup_stage.pre_pipeline_stage.set_internal_config")
        self.set_internal_config_id_map = { param.name: param.id for param in self.set_internal_config.params }

    def to_match_list(self, appliance_id :int = 0):
        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['meta.appliance_id']
        match.ternary.value = appliance_id.to_bytes(1, byteorder='big')
        match.ternary.mask = b'\xff'

        return [match]

    def get(self, appliance_id :int = 0):
        '''
        Get dash pipeline internal config

        '''

        user_match_list = self.to_match_list(appliance_id)
        return self.find(self.p4info_table.preamble.id, user_match_list, priority = 1)

    def set(self,
            appliance_id :int = 0,
            neighbor_mac :bytes = None,
            mac :bytes = None,
            cpu_mac :bytes = None,
            flow_enabled :bytes = None):
        '''
        Set dash pipeline internal config by updating table entry of internal_config.

        if one argument is not specifed, the action param is not changed in the
        existing table entry, otherwise set default value in new table entry.

        '''

        user_match_list = self.to_match_list(appliance_id)

        # param_id -> (value, default value)
        user_params = {
            self.set_internal_config_id_map['neighbor_mac']: (
                neighbor_mac, b'\x00\x00\x00\x00\x00\x00'
            ),
            self.set_internal_config_id_map['mac']: (
                mac, b'\x00\x00\x00\x00\x00\x00'
            ),
            self.set_internal_config_id_map['cpu_mac']: (
                cpu_mac, b'\x00\x00\x00\x00\x00\x00'
            ),
            self.set_internal_config_id_map['flow_enabled']: (
                flow_enabled, b'\x00'
            )
        }

        self.update(self.p4info_table.preamble.id,
                    user_match_list,
                    self.set_internal_config.preamble.id,
                    user_params,
                    priority = 1)

    def unset(self, appliance_id :int = 0):
        '''
        Unset dash pipeline internal config
        '''

        entry = self.get(appliance_id)
        if entry:
            self.write(entry, p4runtime_pb2.Update.DELETE)
        else:
            print(f'Internal config for appliance {appliance_id} not found.')


class P4UnderlayRoutingTable(P4Table):
    def __init__(self, target=None):
        super(P4UnderlayRoutingTable, self).__init__(target)
        self.p4info_table = self.p4info.get_table("dash_ingress.underlay.underlay_routing")
        self.match_id_map = { mf.name: mf.id for mf in self.p4info_table.match_fields}
        self.pkt_act = self.p4info.get_action("dash_ingress.underlay.pkt_act")
        self.pkt_act_id_map = { param.name: param.id for param in self.pkt_act.params }

    def to_match_list(self,
            ip_prefix :str = '::', # ipv6 string, ::x.x.x.x for ipv4
            ip_prefix_len :int = 128): # in bits
        match = p4runtime_pb2.FieldMatch()
        match.field_id = self.match_id_map['meta.dst_ip_addr']
        match.lpm.value = socket.inet_pton(socket.AF_INET6, ip_prefix)
        match.lpm.prefix_len = ip_prefix_len

        return [match]

    def get(self,
            ip_prefix :str = '::', # ipv6 string, ::x.x.x.x for ipv4
            ip_prefix_len :int = 128): # in bits
        '''
        Get underlay route entry with ip prefix

        '''

        user_match_list = self.to_match_list(ip_prefix, ip_prefix_len)
        return self.find(self.p4info_table.preamble.id, user_match_list)

    def set(self,
            ip_prefix :str = '::', # ipv6 string, ::x.x.x.x for ipv4
            ip_prefix_len :int = 128, # in bits
            packet_action :int = None,
            next_hop_id :int = None):
        '''
        Set underlay route entry with ip prefix

        if one argument is not specifed, the action param is not changed in the
        existing table entry, otherwise set default value in new table entry.

        '''

        if packet_action is not None:
            packet_action = packet_action.to_bytes(2, byteorder='big')
        if next_hop_id is not None:
            next_hop_id = next_hop_id.to_bytes(2, byteorder='big')

        user_match_list = self.to_match_list(ip_prefix, ip_prefix_len)

        # param_id -> (value, default value)
        user_params = {
            self.pkt_act_id_map['packet_action']: (
                packet_action, b'\x00\x01' # ACTION_FORWARD
            ),
            self.pkt_act_id_map['next_hop_id']: (
                next_hop_id, b'\x00\x00' # port 0
            )
        }

        self.update(self.p4info_table.preamble.id,
                    user_match_list,
                    self.pkt_act.preamble.id,
                    user_params)

    def unset(self,
              ip_prefix :str = '::', # ipv6 string, ::x.x.x.x for ipv4
              ip_prefix_len :int = 128): # in bits
        '''
        Unset underlay route entry with ip prefix
        '''

        entry = self.get(ip_prefix, ip_prefix_len)
        if entry:
            self.write(entry, p4runtime_pb2.Update.DELETE)
        else:
            print(f'Route entry for {ip_prefix}/{ip_prefix_len} not found.')
