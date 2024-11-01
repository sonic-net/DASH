import grpc
import json
from google.protobuf import json_format
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from p4.config.v1 import p4info_pb2  # Import the P4Info protobuf definition

# Define the P4Runtime server address and port
P4RUNTIME_SERVER = 'localhost:9559'

# Define the P4Info and device configuration files
P4INFO_FILE = '../../dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline_p4rt.json'
DEVICE_CONFIG_FILE = '../../dash-pipeline/bmv2/dash_pipeline.bmv2/dash_pipeline.json'

# Define the table name and entry details
TABLE_NAME = 'dash_ingress.dash_lookup_stage.pre_pipeline_stage.internal_config'
ACTION_NAME = 'dash_ingress.dash_lookup_stage.pre_pipeline_stage.set_internal_config'
FLOW_ENABLED_FIELD = 'meta.appliance_id'
FLOW_ENABLED_VALUE = True
NEIGHBOR_MAC_VALUE = '00:11:22:33:44:55'  # Example MAC address for neighbor_mac
MAC_VALUE = '66:77:88:99:AA:BB'  # Example MAC address for mac

def read_p4info(p4info_file_path):
    with open(p4info_file_path, 'r') as f:
        p4info = json.load(f)
    return p4info

def get_table_id(p4info, table_name):
    for table in p4info['tables']:
        if table['preamble']['name'] == table_name:
            return table['preamble']['id']
    raise Exception(f"Table {table_name} not found in P4Info")

def get_field_id(p4info, table_name, field_name):
    for table in p4info['tables']:
        if table['preamble']['name'] == table_name:
            for match_field in table['matchFields']:
                if match_field['name'] == field_name:
                    return match_field['id']
    raise Exception(f"Field {field_name} not found in table {table_name}")

def get_action_id(p4info, action_name):
    for action in p4info['actions']:
        if action['preamble']['name'] == action_name:
            return action['preamble']['id']
    raise Exception(f"Action {action_name} not found in P4Info")

def get_param_id(p4info, action_name, param_name):
    for action in p4info['actions']:
        if action['preamble']['name'] == action_name:
            for param in action['params']:
                if param['name'] == param_name:
                    return param['id']
    raise Exception(f"Param {param_name} not found in action {action_name}")

def mac_to_bytes(mac):
    return bytes(int(b, 16) for b in mac.split(':'))

def set_forwarding_pipeline_config(stub, p4info, device_config, election_id):
    request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    request.device_id = 1
    request.election_id.high = election_id.high
    request.election_id.low = election_id.low
    config = request.config
    config.p4info.CopyFrom(p4info)
    with open(device_config, 'rb') as f:
        config.p4_device_config = f.read()
    config.cookie.cookie = 1
    response = stub.SetForwardingPipelineConfig(request)
    print("Forwarding pipeline config set successfully")

def send_master_arbitration_update(stub, election_id):
    request = p4runtime_pb2.StreamMessageRequest()
    arbitration = request.arbitration
    arbitration.device_id = 1
    arbitration.election_id.high = election_id.high
    arbitration.election_id.low = election_id.low
    stream = stub.StreamChannel(iter([request]))
    response = next(stream)
    if response.arbitration.status.code != grpc.StatusCode.OK:
        print(response.arbitration.status.code)
        raise Exception("Failed to become the primary client")
    print("Became the primary client successfully")

def main():
    # Read the P4Info file
    p4info = read_p4info(P4INFO_FILE)

    # Get the table ID and field ID
    table_id = get_table_id(p4info, TABLE_NAME)
    field_id = get_field_id(p4info, TABLE_NAME, FLOW_ENABLED_FIELD)

    # Get the action ID and parameter IDs
    action_id = get_action_id(p4info, ACTION_NAME)
    neighbor_mac_param_id = get_param_id(p4info, ACTION_NAME, 'neighbor_mac')
    mac_param_id = get_param_id(p4info, ACTION_NAME, 'mac')
    flow_enabled_param_id = get_param_id(p4info, ACTION_NAME, 'flow_enabled')

    # Create a P4Runtime client
    channel = grpc.insecure_channel(P4RUNTIME_SERVER)
    stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

    # Send MasterArbitrationUpdate to become the primary controller
    election_id = p4runtime_pb2.Uint128(high=0, low=2)  # Use a higher election ID
    send_master_arbitration_update(stub, election_id)

    # Create a WriteRequest message
    request = p4runtime_pb2.WriteRequest()
    request.device_id = 1
    request.election_id.high = election_id.high
    request.election_id.low = election_id.low

    # Create a table entry
    table_entry = p4runtime_pb2.TableEntry()
    table_entry.table_id = table_id
    table_entry.match.add(field_id=field_id, ternary=p4runtime_pb2.FieldMatch.Ternary(value=b'\x01', mask=b'\x01'))

    # Create an action entry
    action = p4runtime_pb2.Action()
    action.action_id = action_id
    action.params.add(param_id=neighbor_mac_param_id, value=mac_to_bytes(NEIGHBOR_MAC_VALUE))
    action.params.add(param_id=mac_param_id, value=mac_to_bytes(MAC_VALUE))
    action.params.add(param_id=flow_enabled_param_id, value=b'\x01' if FLOW_ENABLED_VALUE else b'\x00')

    # Assign the action to the table entry
    table_entry.action.action.CopyFrom(action)

    # Add the table entry to the request
    request.updates.add(type=p4runtime_pb2.Update.INSERT, entity=p4runtime_pb2.Entity(table_entry=table_entry))

    # Send the WriteRequest to the P4Runtime server
    response = stub.Write(request)
    print("Entry inserted successfully")

if __name__ == '__main__':
    main()