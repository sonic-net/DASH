###############################################################
#                  Declaring Global variables
###############################################################

TOTALPACKETS = 1000
PPS = 100
PACKET_LENGTH = 128
ENI_IP = "1.1.0.1"
NETWORK_IP1 = "1.128.0.1"
NETWORK_IP2 = "1.128.0.2"

DPU_VTEP_IP = "221.0.0.2"
ENI_VTEP_IP = "221.0.1.11"
NETWORK_VTEP_IP = "221.0.2.101"
OUTER_SRC_MAC = "80:09:02:01:00:01"
OUTER_DST_MAC = "c8:2c:2b:00:d1:30" #MAC from DUT
INNER_SRC_MAC = "00:1A:C5:00:00:01"
INNER_DST_MAC = "00:1b:6e:00:00:01"
OUTER_SRC_MAC_F2 = "80:09:02:02:00:01"
OUTER_DST_MAC_F2 = "c8:2c:2b:00:d1:34"  


###############################################################
#                  DPU Config
###############################################################
dpu_config = [
  {
    "name": "vip_entry",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_VIP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "vip": DPU_VTEP_IP
    },
    "attributes": [
      "SAI_VIP_ENTRY_ATTR_ACTION",
      "SAI_VIP_ENTRY_ACTION_ACCEPT"
    ]
  },
  {
    "name": "dle_#1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "vni": "11"
    },
    "attributes": [
      "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
      "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
    ]
  },
   {
    "name": "dle_#2",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_DIRECTION_LOOKUP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "vni": "101"
    },
    "attributes": [
      "SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION",
      "SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION"
    ]
  },
  {
    "name": "acl_in_1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP",
    "attributes": [
      "SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY",
      "SAI_IP_ADDR_FAMILY_IPV4"
    ]
  },
  {
    "name": "acl_out_1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_DASH_ACL_GROUP",
    "attributes": [
      "SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY",
      "SAI_IP_ADDR_FAMILY_IPV4"
    ]
  },
  {
    "name": "vnet_#1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_VNET",
    "attributes": [
      "SAI_VNET_ATTR_VNI",
      "1000"
    ]
  },
  {
    "name": "eni_#1",
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
      ENI_VTEP_IP,
      "SAI_ENI_ATTR_VM_VNI",
      "9",
      "SAI_ENI_ATTR_VNET_ID",
      "$vnet_#1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE1_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE2_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE3_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE4_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE5_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE1_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE2_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE3_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE4_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE5_DASH_ACL_GROUP_ID",
      "$acl_out_1",
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
    {
    "name": "eni_#2",
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
      NETWORK_VTEP_IP,
      "SAI_ENI_ATTR_VM_VNI",
      "9",
      "SAI_ENI_ATTR_VNET_ID",
      "$vnet_#1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE1_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE2_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE3_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE4_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V4_STAGE5_DASH_ACL_GROUP_ID",
      "$acl_in_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE1_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE2_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE3_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE4_DASH_ACL_GROUP_ID",
      "$acl_out_1",
      "SAI_ENI_ATTR_INBOUND_V6_STAGE5_DASH_ACL_GROUP_ID",
      "$acl_out_1",
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

  {
    "name": "eni_ether_address_map_entry",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "address": INNER_SRC_MAC
    },
    "attributes": [
      "SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID",
      "$eni_#1"
    ]
  },
    {
    "name": "eni_ether_address_map_entry2",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_ENI_ETHER_ADDRESS_MAP_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "address": INNER_DST_MAC
    },
    "attributes": [
      "SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID",
      "$eni_#2"
    ]
  },
    {
    "name": "inbound_routing_entry_#1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "eni_id": "$eni_#1",
      "vni": "11",
      "sip": "1.1.0.0",
      "sip_mask": "255.255.255.0",
      "priority": 0
    },
    "attributes": [
      "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION",
      "SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE",
      "SAI_INBOUND_ROUTING_ENTRY_ATTR_SRC_VNET_ID",
      "$vnet_#1"
    ]
  },
    {
    "name": "inbound_routing_entry_#2",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_INBOUND_ROUTING_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "eni_id": "$eni_#2",
      "vni": "101",
      "sip": "1.128.0.0",
      "sip_mask": "255.255.255.0",
      "priority": 0
    },
    "attributes": [
      "SAI_INBOUND_ROUTING_ENTRY_ATTR_ACTION",
      "SAI_INBOUND_ROUTING_ENTRY_ACTION_VXLAN_DECAP_PA_VALIDATE",
      "SAI_INBOUND_ROUTING_ENTRY_ATTR_SRC_VNET_ID",
      "$vnet_#1"
    ]
  },
  {
    "name": "pa_validation_entry_#1",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "sip": ENI_IP,
      "vnet_id": "$vnet_#1"
    },
    "attributes": [
      "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION",
      "SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT"
    ]
  },
    {
    "name": "pa_validation_entry_#2",
    "op": "create",
    "type": "SAI_OBJECT_TYPE_PA_VALIDATION_ENTRY",
    "key": {
      "switch_id": "$SWITCH_ID",
      "sip": NETWORK_IP1,
      "vnet_id": "$vnet_#1"
    },
    "attributes": [
      "SAI_PA_VALIDATION_ENTRY_ATTR_ACTION",
      "SAI_PA_VALIDATION_ENTRY_ACTION_PERMIT"
    ]
  }
]
