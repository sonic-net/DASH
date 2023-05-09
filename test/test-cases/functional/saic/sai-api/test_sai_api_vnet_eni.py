import json
import time
from pathlib import Path
from pprint import pprint

import pytest


class TestSaiVnetEni:
    def test_vnet_eni_create(self, dpu):

        commands = [
            {
                "name": "vnet",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "2001"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)
        
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
                    "10.10.1.10",
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
                    "0",
                    "SAI_ENI_ATTR_V4_METER_POLICY_ID",
                    "0",
                    "SAI_ENI_ATTR_V6_METER_POLICY_ID",
                    "0"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_get1(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI",
                "atrribute": "SAI_ENI_ATTR_VM_UNDERLAY_DIP"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_set(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_ENI",
                "attribute": [
                    "SAI_ENI_ATTR_VM_UNDERLAY_DIP",
                    "20.10.2.10",

                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_eni_get2(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_ENI",
                "atrribute": "SAI_ENI_ATTR_VM_UNDERLAY_DIP"

            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    def test_vnet_eni_remove(self, dpu):

        commands = [
            {
                "name": "eni_id",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_ENI",
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)
        
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
