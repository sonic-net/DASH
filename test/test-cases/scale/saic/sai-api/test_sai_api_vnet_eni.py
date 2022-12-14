import json
import time
from pathlib import Path
from pprint import pprint

import pytest


class TestSaiVnetEni:

    @pytest.mark.dependency(depends=['test_sai_api_vnet_vni.py::test_vnet_vni_create'], scope='session')
    def test_vnet_eni_create(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_ENI",
                "attributes": [
                    "SAI_ENI_ATTR_CPS",
                    "10000",
                    "SAI_ENI_ATTR_PPS",
                    "100000",
                    "SAI_ENI_ATTR_FLOWS",
                    "100000",
                    "SAI_ENI_ATTR_ADMIN_STATE",
                    "True",
                    "SAI_ENI_ATTR_VM_UNDERLAY_DIP",
                    "10.10.2.10",
                    "SAI_ENI_ATTR_VM_VNI",
                    "9",
                    "SAI_ENI_ATTR_VNET_ID",
                    "$vnet",
                    "SAI_ENI_ATTR_INBOUND_V4_STAGE1_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V4_STAGE2_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V4_STAGE3_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V4_STAGE4_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V4_STAGE5_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V6_STAGE1_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V6_STAGE2_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V6_STAGE3_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V6_STAGE4_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_INBOUND_V6_STAGE5_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V4_STAGE1_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V4_STAGE2_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V4_STAGE3_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V4_STAGE4_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V4_STAGE5_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V6_STAGE1_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V6_STAGE2_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V6_STAGE3_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V6_STAGE4_DASH_ACL_GROUP_ID",
                    "0",
                    "SAI_ENI_ATTR_OUTBOUND_V6_STAGE5_DASH_ACL_GROUP_ID",
                    "0"
                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_get1(self, dpu):

        commands = [
            {
                "name": "$eni_id",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI",
                "atrribute": "SAI_ENI_ATTR_VM_UNDERLAY_DIP"
            }
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(result)

        assert (result[0].value() == "10.10.2.10")

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_set(self, dpu):

        commands = [
            {
                "name": "$eni_id",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_ENI",
                "attribute": [
                    "SAI_ENI_ATTR_VM_UNDERLAY_DIP",
                    "20.10.2.10",

                ]
            },
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(result)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_get2(self, dpu):

        commands = [
            {
                "name": "$eni_id",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI",
                "atrribute": "SAI_ENI_ATTR_VM_UNDERLAY_DIP"

            }
        ]
        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(result)

        assert (result[0].value() == "20.10.2.10")

    @pytest.mark.dependency(depends=['test_sai_api_vnet_in_route.py::test_vnet_inbound_routing_entry_remove'], scope='session')
    def test_vnet_eni_remove(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_ENI",
            },
        ]

        result = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(result)
