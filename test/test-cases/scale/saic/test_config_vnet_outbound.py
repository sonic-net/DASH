"""
Test module with an example of parametrized test case
"""
import json
from pathlib import Path

import pytest


# The following test function will be executed twice - against each cfg_type: simple and scale
@pytest.mark.parametrize('cfg_type', ['simple', 'scale'])
def test_config_vnet_outbound_parametrized(dpu, cfg_type):

    # Loading unified SAI commands from file based on cfg_type
    current_file_dir = Path(__file__).parent
    with (current_file_dir / f'vnet_outbound_setup_commands_{cfg_type}.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)

    try:
        # Execute all commands in one shot
        result = [*dpu.process_commands(setup_commands)]

    finally:
        # The idea of finally here to try remove something if apply failed in the middle...
        # In other test suites remove is a part of the separate test case and is always executed.
        # This specific function executes a different configuration on each iteration and it's important
        # to keep remove commands next to the create ones.

        # Replace op="create" to op="remove"
        # Note that the order is reversed.
        cleanup_commands = []
        for command in reversed(setup_commands):
            command['op'] = 'remove'
            cleanup_commands.append(command)

        # Execute all remove commands
        result = [*dpu.process_commands(cleanup_commands)]
