import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiVnetOutboundRoutingEntry:

    @pytest.mark.dependency(depends=['test_sai_api_vnet_vni.py::test_vnet_vni_create'], scope='session')
    def test_vnet_outbound_routing_entry_create(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "1",
                    "destination": "10.1.0.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet"
                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_get(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

        assert (result[0].value() ==
                "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET")

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_set(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "1",
                    "destination": "10.1.1.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet"
                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_get(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

        assert (result[0].value() ==
                "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET")

    @pytest.mark.dependency(depends=['test_vnet_outbound_routing_entry_create'], scope='session')
    def test_vnet_outbound_routing_entry_remove(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "1",
                    "destination": "10.1.0.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet"
                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)
