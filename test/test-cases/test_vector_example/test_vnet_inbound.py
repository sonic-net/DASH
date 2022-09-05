import json
from pathlib import Path

current_file_dir = Path(__file__).parent


def test_vnet_inbound(dpu, dataplane):
    with (current_file_dir / 'test_vnet_inbound_setup_commands.json').open(mode='r') as config_file:
        vnet_inbound_setup_commands = json.load(config_file)

    result = [*dpu.process_commands(vnet_inbound_setup_commands)]

    with (current_file_dir / 'test_vnet_inbound_cleanup_commands.json').open(mode='r') as config_file:
        vnet_inbound_cleanup_commands = json.load(config_file)

    result = [*dpu.process_commands(vnet_inbound_cleanup_commands)]
