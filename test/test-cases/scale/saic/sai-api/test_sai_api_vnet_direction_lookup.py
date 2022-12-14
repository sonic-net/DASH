import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiDirectionLookup:

    def test_direction_lookup_create(self, dpu):

        commands = [
            {
                "name": "direction_lookup_entry",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "vni": "2000"
                },
                "attributes": [
                    "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
                    "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_direction_lookup_get1(self, dpu):

        commands = [
            {
                "name": "$vpe",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY"
            }
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(result)

        assert (result[0].value() == "2000")

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_direction_lookup_set(self, dpu):

        commands = [
            {
                "name": "$vpe",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "vni": "4000"
                },
                "attributes": [
                    "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
                    "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
                ]
            },
        ]

        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_direction_lookup_get2(self, dpu):

        commands = [
            {
                "name": "$vpe",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_VIP_ENTRY"
            }
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(result)

        assert (result[0].value() == "4000")

    def test_direction_lookup_remove(self, dpu):

        commands = [
            {
                "name": "direction_lookup_entry",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "vni": "2000"
                },
                "attributes": [
                    "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
                    "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
                ]
            },
        ]

        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(result)
