import json
from pathlib import Path

current_file_dir = Path(__file__).parent


def test_vnet_outbound(dpu, dataplane):
    with (current_file_dir / 'test_vnet_outbound_setup_commands.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)

    result = [*dpu.process_commands(setup_commands)]

    with (current_file_dir / 'test_vnet_outbound_cleanup_commands.json').open(mode='r') as config_file:
        cleanup_commands = json.load(config_file)

    result = [*dpu.process_commands(cleanup_commands)]
