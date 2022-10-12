import json
from pathlib import Path

import pytest

current_file_dir = Path(__file__).parent


@pytest.mark.parametrize('cfg_type', ['simple', 'scale'])
def test_vnet_outbound_simple(dpu, cfg_type):
    with (current_file_dir / f'vnet_outbound_setup_commands_{cfg_type}.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)

    result = [*dpu.process_commands(setup_commands)]

    cleanup_commands = []
    for command in reversed(setup_commands):
        command['op'] = 'remove'
        cleanup_commands.append(command)

    result = [*dpu.process_commands(cleanup_commands)]
