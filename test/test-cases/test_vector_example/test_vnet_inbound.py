import json
from pathlib import Path

current_file_dir = Path(__file__).parent


def test_vnet_inbound(dpu, dataplane):
    with (current_file_dir / 'vnet_inbound_setup_commands.json').open(mode='r') as config_file:
        vnet_inbound_setup_commands = json.load(config_file)

    result = [*dpu.process_commands(vnet_inbound_setup_commands)]

    vnet_inbound_cleanup_commands = []
    for command in reversed(vnet_inbound_setup_commands):
        command['op'] = 'remove'
        vnet_inbound_cleanup_commands.append(command)

    result = [*dpu.process_commands(vnet_inbound_cleanup_commands)]
