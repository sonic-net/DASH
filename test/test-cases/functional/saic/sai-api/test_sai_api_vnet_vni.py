import json
import time
from pathlib import Path
from pprint import pprint

import pytest


class TestSaiVnetVni:

    @pytest.mark.dependency(scope='session')
    def test_vnet_vni_create(self, dpu):

        commands = [
            {
                "name": "vnet",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "2000"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_vni_get1(self, dpu):

        commands = [
            {
                "name": "vnet",
                "vnet_oid": "$vnet",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": ["SAI_VNET_ATTR_VNI", 0]
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_vni_set(self, dpu):

        commands = [
            {
                "name": "vnet",
                "vnet_oid": "$vnet",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "4000"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_vni_get2(self, dpu):

        commands = [
            {
                "name": "vnet",
                "vnet_oid": "$vnet",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": ["SAI_VNET_ATTR_VNI", 0]
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_vni_remove(self, dpu):

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
