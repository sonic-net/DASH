import json
import time
from pathlib import Path
from pprint import pprint

import pytest


class TestSaiVnetAclOut:

    def test_vnet_acl_out_create(self, dpu):

        commands = [
            {
                "name": "acl_out",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP",
                "attributes": [
                    "SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY",
                    "SAI_IP_ADDR_FAMILY_IPV4"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_out_get1(self, dpu):

        commands = [
            {
                "name": "acl_out",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_out_set(self, dpu):

        commands = [
            {
                "name": "acl_out",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP",
                "attributes": [
                    "SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY",
                    "SAI_IP_ADDR_FAMILY_IPV4"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_out_get2(self, dpu):

        commands = [
            {
                "name": "acl_out",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    def test_vnet_acl_out_remove(self, dpu):

        commands = [
            {
                "name": "acl_out",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)
