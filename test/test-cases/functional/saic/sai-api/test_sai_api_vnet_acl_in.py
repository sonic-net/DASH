import json
import time
from pathlib import Path
from pprint import pprint

import pytest


class TestSaiVnetAclIn:

    def test_vnet_acl_in_create(self, dpu):

        commands = [
            {
                "name": "acl_in",
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

        assert all(results), "SAI_IP_ADDR_FAMILY_IPV4 Create error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_in_get1(self, dpu):

        commands = [
            {
                "name": "acl_in",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

        assert all( [result == 0 for result in results]), "SAI_IP_ADDR_FAMILY_IPV4 GET error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_in_set(self, dpu):

        commands = [
            {
                "name": "acl_in",
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

        assert all( [result == 0 for result in results]), "SAI_IP_ADDR_FAMILY_IPV4 Set error"

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_acl_in_get2(self, dpu):

        commands = [
            {
                "name": "acl_in",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

        assert all( [result == 0 for result in results]), "SAI_IP_ADDR_FAMILY_IPV4 GET error"

    def test_vnet_acl_in_remove(self, dpu):

        commands = [
            {
                "name": "acl_in",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP"
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)

        assert all( [result == 0 for result in results]), "SAI_IP_ADDR_FAMILY_IPV4 Remove error"
