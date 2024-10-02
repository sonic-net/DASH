import json
import time
from pathlib import Path
from pprint import pprint

import pytest

# Constants
SWITCH_ID = 5


class TestSaiVnetInboundRoutingEntry:

    @pytest.mark.dependency()
    def test_vnet_inbound_routing_entry_create_setup(self, dpu):

        # Create VNET
        commands = [
            {
                "name": "vnet",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_VNET",
                "attributes": [
                    "SAI_VNET_ATTR_VNI",
                    "5000"
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
                    "False"
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
                    "10.10.2.10",
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

    @pytest.mark.skip(reason="https://github.com/sonic-net/DASH/issues/345 [P4Runtime] Invalid match type")
    def test_vnet_inbound_routing_entry_create(self, dpu):

        commands = [
            {
                "name": "inbound_routing_entry",
                "op": "create",
                "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "$eni_id",
                    "vni": "2000",
                    "sip": "10.10.2.0",
                    "sip_mask": "255.255.255.0",
                    "priority": 0
                },
                "attributes": [
                    "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION",
                    "SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP_PA_VALIDATE",
                    "SAI_INBOUND_ROUTING_ENTRY_ATTR_SRC_VNET_ID",
                    "$vnet",
                    "SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR",
                    "0",
                    "SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND",
                    "-1"
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values create =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_inbound_routing_entry_get1(self, dpu):

        commands = [
            {
                "name": "inbound_routing_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
                "attribute": "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_inbound_routing_entry_set(self, dpu):

        commands = [
            {
                "name": "inbound_routing_entry",
                "op": "set",
                "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
                "key": {
                    "switch_id": "$SWITCH_ID",
                    "eni_id": "$eni_id",
                    "vni": "2000",
                    "sip": "10.10.10.0",
                    "sip_mask": "255.255.255.0",
                    "priority": 0
                },
                "attribute": [
                    "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION",
                    "SAI_INBOUND_ROUTING_ENTRY_ACTION_TUNNEL_DECAP_CA_VALIDATE",
                ]
            },
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values set =======")
        pprint(results)

    @pytest.mark.skip(reason="get and set not implemented, yet")
    def test_vnet_inbound_routing_entry_get2(self, dpu):

        commands = [
            {
                "name": "inbound_routing_entry",
                "op": "get",
                "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
                "attribute": "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION"
            }
        ]
        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values get =======")
        pprint(results)

    @pytest.mark.skip(reason="https://github.com/sonic-net/DASH/issues/345 [P4Runtime] Invalid match type")
    def test_vnet_inbound_routing_entry_remove(self, dpu):
        
        commands = [
            {
                "name": "inbound_routing_entry",
                "op": "remove",
                "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
            },
        ]

        results = [*dpu.process_commands(commands)]
        print("\n======= SAI commands RETURN values remove =======")
        pprint(results)

    @pytest.mark.dependency(depends=['TestSaiVnetInboundRoutingEntry::test_vnet_inbound_routing_entry_create_setup'])
    def test_vnet_inbound_routing_entry_remove_cleanup(self, dpu):
        
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
