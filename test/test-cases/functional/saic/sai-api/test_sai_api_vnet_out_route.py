import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiVnetOutboundRoutingEntry:

    def test_vnet_outbound_routing_entry_create(self, dpu):

        # Create VNET
        commands = [
            {
                "name": "vnet",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "9000"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)
        
        # Create Routing Group
        commands = [
            {
                "name": "routing_group",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_GROUP",
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_GROUP_ATTR_DISABLED",
                    "True"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)
        
        # Create ENI
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
                    "SAI_ENI_ATTR_HA_SCOPE_ID",
                    "0",
                    "SAI_ENI_ATTR_VM_UNDERLAY_DIP",
                    "10.10.9.10",
                    "SAI_ENI_ATTR_VM_VNI",
                    "9",
                    "SAI_ENI_ATTR_VNET_ID",
                    "$vnet",
                    "SAI_ENI_ATTR_OUTBOUND_ROUTING_GROUP_ID",
                    "$routing_group",
                    "SAI_ENI_ATTR_PL_SIP",
                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                    "SAI_ENI_ATTR_PL_SIP_MASK",
                    "2001:0db8:85a3:0000:0000:0000:0000:0000",
                    "SAI_ENI_ATTR_PL_UNDERLAY_SIP",
                    "10.0.0.18",
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
                    "0",
                    "SAI_ENI_ATTR_DASH_TUNNEL_DSCP_MODE",
                    "SAI_DASH_TUNNEL_DSCP_MODE_PRESERVE_MODEL",
                    "SAI_ENI_ATTR_DSCP",
                    "0",
                    "SAI_ENI_ATTR_DISABLE_FAST_PATH_ICMP_FLOW_REDIRECTION",
                    "False",
                    "SAI_ENI_ATTR_FULL_FLOW_RESIMULATION_REQUESTED",
                    "False",
                    "SAI_ENI_ATTR_MAX_RESIMULATED_FLOW_PER_SECOND",
                    "0"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)
        
        commands = [
            {
                "name": "ore",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "routing_group_id": "$routing_group",
                    "destination": "10.1.0.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DASH_TUNNEL_ID", "SAI_NULL_OBJECT_ID",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR", "0",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND", "-1",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ROUTING_ACTIONS_DISABLED_IN_FLOW_RESIMULATION", "0"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_get1(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @ pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_set(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "routing_group_id": "$routing_group",
                    "destination": "10.1.1.0/16"
                },
                "attributes": [
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION", "SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DST_VNET_ID", "$vnet",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DASH_TUNNEL_ID", "SAI_NULL_OBJECT_ID",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR", "0",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND", "-1",
                    "SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ROUTING_ACTIONS_DISABLED_IN_FLOW_RESIMULATION", "0"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_outbound_routing_entry_get2(self, dpu):

        commands = [
            {
                "name": "ore",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    def test_vnet_outbound_routing_entry_remove(self, dpu):
        commands = [
            {
                "name": "ore",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_ENTRY",
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

        # Remove ENI
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

        # Remove VNET
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

        # Remove routing group
        commands = [
            {
                "name": "routing_group",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_OUTBOUND_ROUTING_GROUP"
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)
