import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiVnetVni:

    def test_vnet_pa_validation_entry_create(self, dpu):

        # Create VNET
        commands = [
            {
                "name": "vnet",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "7000"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

        assert all(results), "SAI_OBJECT_TYPE_VNET Create error"
        
        commands = [
            {
                "name": "pa_validation_entry",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "sip": "10.10.2.10",
                    "vnet_id": "$vnet"
                },
                "attributes": [
                    "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION",
                    "SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT"
                ]
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

        assert all(results), "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY Create error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_pa_validation_entry_get1(self, dpu):

        commands = [
            {
                "name": "pa_validation_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "attribute": "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

        assert all([result == 0 for result in results]), "SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT Get error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_pa_validation_entry_set(self, dpu):

        commands = [
            {
                "name": "pa_validation_entry",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "sip": "10.10.10.10",
                    "vnet_id": "$vnet"
                },
                "attribute": [
                    "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION",
                    "SAI_PA_VALIDATION_ENTRY_ACTION_DENY"
                ]
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

        assert all([result == 0 for result in results]), "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY Set error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_pa_validation_entry_get2(self, dpu):

        commands = [
            {
                "name": "pa_validation_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
                "attribute": "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

        assert all([result == 0 for result in results]), "SAI_PA_VALIDATION_ENTRY_ACTION_DENY Get error"

    def test_vnet_pa_validation_entry_remove(self, dpu):

        commands = [
            {
                "name": "pa_validation_entry",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
            }
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)

        assert all([result == 0 for result in results]), "SAI_PA_VALIDATION_ENTRY_ACTION_DENY Get error"
        
        commands = [
            {
                "name": "vnet",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_VNET"
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)

        assert all( [result == 0 for result in results]), "SAI_OBJECT_TYPE_VNET Remove error"

