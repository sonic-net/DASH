"""
Test module with an example of loading unified SAI config format from the file
"""

import json
from pathlib import Path

import pytest


@pytest.mark.skip(reason="https://github.com/sonic-net/DASH/issues/345 [P4Runtime] Invalid match type")
class TestConfigVnetInboundRouting:

    @pytest.fixture(scope="class")
    def vnet_in_config(self):
        """
        Fixture returns the content of the file with SAI configuration commands.
        scope=class - The file is loaded once for the whole test class
        """
        current_file_dir = Path(__file__).parent
        with (current_file_dir / 'vnet_inbound_setup_commands.json').open(mode='r') as config_file:
            vnet_inbound_setup_commands = json.load(config_file)
        return vnet_inbound_setup_commands

    def test_config_vnet_inbound_create(self, dpu, vnet_in_config):
        """
        Apply configuration that is loaded from the file.
        """

        result = [*dpu.process_commands(vnet_in_config)]
        # User may want to verify result.

    def test_config_vnet_inbound_remove(self, dpu, vnet_in_config):
        """
        Remove configuration that is loaded from the file.
        """
        # NOTE: vnet_in_config contains op="create".
        # In the following loop "create" is replaced with "remove"
        # Note that the order is reversed.
        vnet_inbound_cleanup_commands = []
        for command in reversed(vnet_in_config):
            command['op'] = 'remove'
            vnet_inbound_cleanup_commands.append(command)

        # Another example of applying commands one by one.
        # Extremely useful when you have a generator instead of the list
        result = []
        for command in vnet_inbound_cleanup_commands:
            result.append(dpu.command_processor.process_command(command))
