import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiVnetEniAddr:

    def test_vnet_eni_ether_address_create(self, dpu):

        commands = [
            {
                "name": "eni_ether_address_map_entry",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "address": "00:AA:AA:AA:AB:00"
                },
                "attributes": [
                    "SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID",
                    "1"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_ether_address_get1(self, dpu):

        commands = [
            {
                "name": "eni_ether_address_map_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_ether_address_set(self, dpu):

        commands = [
            {
                "name": "eni_ether_address_map_entry",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "address": "00:AA:AA:AA:BB:00"
                },
                "attributes": [
                    "SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID",
                    "$eni_id"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_ether_address_get2(self, dpu):

        commands = [
            {
                "name": "eni_ether_address_map_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    def test_vnet_eni_ether_address_remove(self, dpu):

        commands = [
            {
                "name": "eni_ether_address_map_entry",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY",
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)
