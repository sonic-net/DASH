import json
from pathlib import Path
from pprint import pprint

import pytest

class TestConfigVnetRouting:

    @pytest.fixture(scope="class")
    def vnet_in_config(self):
        """
        Fixture returns the content of the file with SAI configuration commands.
        scope=class - The file is loaded once for the whole test class
        """
        current_file_dir = Path(__file__).parent
        with (current_file_dir / 'vnet_route_setup_commands_unidirectional.json').open(mode='r') as config_file:
            vnet_route_setup_commands = json.load(config_file)
        return vnet_route_setup_commands

    def test_config_vnet_routing_unidirectional_create(self, dpu, vnet_in_config):
        """
        Apply configuration that is loaded from the file.
        """

        results = [*dpu.process_commands(vnet_in_config)]
        print('======= SAI commands RETURN values create =======')
        pprint(results)
        assert all(results), 'Create error'

    def test_config_vnet_routing_unidirectional_remove(self, dpu, vnet_in_config):
        """
        Remove configuration that is loaded from the file.
        """
        results = [*dpu.process_commands(vnet_in_config, cleanup=True)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)
        assert all(
            [result == 'SAI_STATUS_SUCCESS' for result in results]
        ), 'Remove error'
