/**
 * Copyright (c) 2014 Microsoft Open Technologies, Inc.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License"); you may
 *    not use this file except in compliance with the License. You may obtain
 *    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 *    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
 *    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
 *    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
 *    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
 *
 *    See the Apache Version 2.0 License for specific language governing
 *    permissions and limitations under the License.
 *
 *    Microsoft would like to thank the following companies for their review and
 *    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
 *    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
 *
 * @file    saiexperimental.h
 *
 * @brief   This module defines SAI P4 extension  interface
 */

#if !defined (__SAIEXPERIMENTAL_H_)
#define __SAIEXPERIMENTAL_H_

#include <saitypes.h>

/**
 * @defgroup SAIEXPERIMENTAL SAI - Extension specific API definitions
 *
 * @{
 */


/**
 * @brief Attribute data for #SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_ACTION
 */
typedef enum _sai_outbound_acl_stage1_entry_action_t
{
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ACTION_PERMIT,

    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ACTION_DENY,

    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_outbound_acl_stage1_entry_action_t;


/**
 * @brief Attribute data for #SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_ACTION
 */
typedef enum _sai_outbound_acl_stage2_entry_action_t
{
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ACTION_PERMIT,

    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ACTION_DENY,

    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_outbound_acl_stage2_entry_action_t;


/**
 * @brief Attribute data for #SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_ACTION
 */
typedef enum _sai_outbound_acl_stage3_entry_action_t
{
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ACTION_PERMIT,

    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ACTION_DENY,

    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_outbound_acl_stage3_entry_action_t;


/**
 * @brief Attribute data for #SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_ACTION
 */
typedef enum _sai_inbound_acl_stage1_entry_action_t
{
    SAI_INBOUND_ACL_STAGE1_ENTRY_ACTION_PERMIT,

    SAI_INBOUND_ACL_STAGE1_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_INBOUND_ACL_STAGE1_ENTRY_ACTION_DENY,

    SAI_INBOUND_ACL_STAGE1_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_inbound_acl_stage1_entry_action_t;


/**
 * @brief Attribute data for #SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_ACTION
 */
typedef enum _sai_inbound_acl_stage2_entry_action_t
{
    SAI_INBOUND_ACL_STAGE2_ENTRY_ACTION_PERMIT,

    SAI_INBOUND_ACL_STAGE2_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_INBOUND_ACL_STAGE2_ENTRY_ACTION_DENY,

    SAI_INBOUND_ACL_STAGE2_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_inbound_acl_stage2_entry_action_t;


/**
 * @brief Attribute data for #SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_ACTION
 */
typedef enum _sai_inbound_acl_stage3_entry_action_t
{
    SAI_INBOUND_ACL_STAGE3_ENTRY_ACTION_PERMIT,

    SAI_INBOUND_ACL_STAGE3_ENTRY_ACTION_PERMIT_AND_CONTINUE,

    SAI_INBOUND_ACL_STAGE3_ENTRY_ACTION_DENY,

    SAI_INBOUND_ACL_STAGE3_ENTRY_ACTION_DENY_AND_CONTINUE,

} sai_inbound_acl_stage3_entry_action_t;


/**
 * @brief direction_lookup_entry
 */
typedef struct _sai_direction_lookup_entry_t
{
    /**
     * @brief Exact matched key vni
     */
     sai_uint32_t vni;
} sai_direction_lookup_entry_t;
/**
 * @brief Attribute ID for direction_lookup_entry
 */
typedef enum _sai_direction_lookup_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_START,


    /**
     * @brief Action set_direction parameter direction
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION == SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_DIRECTION
     */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_DIRECTION,

    /**
     * @brief End of attributes
     */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_DIRECTION_LOOKUP_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_direction_lookup_entry_attr_t;


/**
 * @brief Attribute ID for appliance
 */
typedef enum _sai_appliance_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_APPLIANCE_ATTR_START,


    /**
     * @brief Action set_appliance parameter neighbor_mac
     *
     * @type sai_mac_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_APPLIANCE_ATTR_ACTION == SAI_APPLIANCE_ACTION_SET_APPLIANCE
     */
    SAI_APPLIANCE_ATTR_NEIGHBOR_MAC,

    /**
     * @brief Action set_appliance parameter mac
     *
     * @type sai_mac_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_APPLIANCE_ATTR_ACTION == SAI_APPLIANCE_ACTION_SET_APPLIANCE
     */
    SAI_APPLIANCE_ATTR_MAC,

    /**
     * @brief Action set_appliance parameter ip
     *
     * @type sai_ip_address_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_APPLIANCE_ATTR_ACTION == SAI_APPLIANCE_ACTION_SET_APPLIANCE
     */
    SAI_APPLIANCE_ATTR_IP,

    /**
     * @brief End of attributes
     */
    SAI_APPLIANCE_ATTR_END,

    /** Custom range base value */
    SAI_APPLIANCE_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_APPLIANCE_ATTR_CUSTOM_RANGE_END,

} sai_appliance_attr_t;


/**
 * @brief outbound_eni_lookup_from_vm_entry
 */
typedef struct _sai_outbound_eni_lookup_from_vm_entry_t
{
    /**
     * @brief Exact matched key smac
     */
     sai_mac_t smac;
} sai_outbound_eni_lookup_from_vm_entry_t;
/**
 * @brief Attribute ID for outbound_eni_lookup_from_vm_entry
 */
typedef enum _sai_outbound_eni_lookup_from_vm_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_START,


    /**
     * @brief Action set_eni parameter eni
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_ACTION == SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ACTION_SET_ENI
     */
    SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_ENI,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ENI_LOOKUP_FROM_VM_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_eni_lookup_from_vm_entry_attr_t;


/**
 * @brief outbound_eni_to_vni_entry
 */
typedef struct _sai_outbound_eni_to_vni_entry_t
{
    /**
     * @brief Exact matched key eni
     */
     sai_uint16_t eni;
} sai_outbound_eni_to_vni_entry_t;
/**
 * @brief Attribute ID for outbound_eni_to_vni_entry
 */
typedef enum _sai_outbound_eni_to_vni_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_START,


    /**
     * @brief Action set_vni parameter vni
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_ACTION == SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ACTION_SET_VNI
     */
    SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_VNI,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ENI_TO_VNI_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_eni_to_vni_entry_attr_t;


/**
 * @brief outbound_acl_stage1_entry
 */
typedef struct _sai_outbound_acl_stage1_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_outbound_acl_stage1_entry_t;
/**
 * @brief Attribute ID for outbound_acl_stage1_entry
 */
typedef enum _sai_outbound_acl_stage1_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_outbound_acl_stage1_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_ACTION = SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ACL_STAGE1_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_acl_stage1_entry_attr_t;


/**
 * @brief outbound_acl_stage2_entry
 */
typedef struct _sai_outbound_acl_stage2_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_outbound_acl_stage2_entry_t;
/**
 * @brief Attribute ID for outbound_acl_stage2_entry
 */
typedef enum _sai_outbound_acl_stage2_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_outbound_acl_stage2_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_ACTION = SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ACL_STAGE2_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_acl_stage2_entry_attr_t;


/**
 * @brief outbound_acl_stage3_entry
 */
typedef struct _sai_outbound_acl_stage3_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_outbound_acl_stage3_entry_t;
/**
 * @brief Attribute ID for outbound_acl_stage3_entry
 */
typedef enum _sai_outbound_acl_stage3_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_outbound_acl_stage3_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_ACTION = SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ACL_STAGE3_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_acl_stage3_entry_attr_t;


/**
 * @brief outbound_routing_entry
 */
typedef struct _sai_outbound_routing_entry_t
{
    /**
     * @brief Exact matched key eni
     */
     sai_uint16_t eni;

    /**
     * @brief LPM matched key destination
     */
      destination;
} sai_outbound_routing_entry_t;
/**
 * @brief Attribute ID for outbound_routing_entry
 */
typedef enum _sai_outbound_routing_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_ROUTING_ENTRY_ATTR_START,


    /**
     * @brief Action route_vnet parameter dest_vnet_vni
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_ROUTING_ENTRY_ATTR_ACTION == SAI_OUTBOUND_ROUTING_ENTRY_ACTION_ROUTE_VNET
     */
    SAI_OUTBOUND_ROUTING_ENTRY_ATTR_DEST_VNET_VNI,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_ROUTING_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_ROUTING_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_ROUTING_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_routing_entry_attr_t;


/**
 * @brief outbound_ca_to_pa_entry
 */
typedef struct _sai_outbound_ca_to_pa_entry_t
{
    /**
     * @brief Exact matched key dest_vni
     */
     sai_uint16_t dest_vni;

    /**
     * @brief Exact matched key dip
     */
     sai_ip_address_t dip;
} sai_outbound_ca_to_pa_entry_t;
/**
 * @brief Attribute ID for outbound_ca_to_pa_entry
 */
typedef enum _sai_outbound_ca_to_pa_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_START,


    /**
     * @brief Action set_tunnel_mapping parameter underlay_dip
     *
     * @type sai_ip_address_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_ACTION == SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_TUNNEL_MAPPING
     */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_UNDERLAY_DIP,

    /**
     * @brief Action set_tunnel_mapping parameter overlay_dmac
     *
     * @type sai_mac_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_ACTION == SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_TUNNEL_MAPPING
     */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_OVERLAY_DMAC,

    /**
     * @brief Action set_tunnel_mapping parameter use_dst_vni
     *
     * @type bool
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_ACTION == SAI_OUTBOUND_CA_TO_PA_ENTRY_ACTION_SET_TUNNEL_MAPPING
     */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_USE_DST_VNI,

    /**
     * @brief End of attributes
     */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_outbound_ca_to_pa_entry_attr_t;


/**
 * @brief inbound_eni_lookup_to_vm_entry
 */
typedef struct _sai_inbound_eni_lookup_to_vm_entry_t
{
    /**
     * @brief Exact matched key dmac
     */
     sai_mac_t dmac;
} sai_inbound_eni_lookup_to_vm_entry_t;
/**
 * @brief Attribute ID for inbound_eni_lookup_to_vm_entry
 */
typedef enum _sai_inbound_eni_lookup_to_vm_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_START,


    /**
     * @brief Action set_eni parameter eni
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_ACTION == SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ACTION_SET_ENI
     */
    SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_ENI,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_ENI_LOOKUP_TO_VM_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_inbound_eni_lookup_to_vm_entry_attr_t;


/**
 * @brief inbound_eni_to_vm_entry
 */
typedef struct _sai_inbound_eni_to_vm_entry_t
{
    /**
     * @brief Exact matched key eni
     */
     sai_uint16_t eni;
} sai_inbound_eni_to_vm_entry_t;
/**
 * @brief Attribute ID for inbound_eni_to_vm_entry
 */
typedef enum _sai_inbound_eni_to_vm_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_START,


    /**
     * @brief Action set_vm_id parameter vm_id
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_ACTION == SAI_INBOUND_ENI_TO_VM_ENTRY_ACTION_SET_VM_ID
     */
    SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_VM_ID,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_ENI_TO_VM_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_inbound_eni_to_vm_entry_attr_t;


/**
 * @brief Attribute ID for inbound_vm
 */
typedef enum _sai_inbound_vm_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_VM_ATTR_START,


    /**
     * @brief Action set_vm_attributes parameter underlay_dmac
     *
     * @type sai_mac_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_INBOUND_VM_ATTR_ACTION == SAI_INBOUND_VM_ACTION_SET_VM_ATTRIBUTES
     */
    SAI_INBOUND_VM_ATTR_UNDERLAY_DMAC,

    /**
     * @brief Action set_vm_attributes parameter underlay_dip
     *
     * @type sai_ip_address_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_INBOUND_VM_ATTR_ACTION == SAI_INBOUND_VM_ACTION_SET_VM_ATTRIBUTES
     */
    SAI_INBOUND_VM_ATTR_UNDERLAY_DIP,

    /**
     * @brief Action set_vm_attributes parameter vni
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @condition SAI_INBOUND_VM_ATTR_ACTION == SAI_INBOUND_VM_ACTION_SET_VM_ATTRIBUTES
     */
    SAI_INBOUND_VM_ATTR_VNI,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_VM_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_VM_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_VM_ATTR_CUSTOM_RANGE_END,

} sai_inbound_vm_attr_t;


/**
 * @brief inbound_acl_stage1_entry
 */
typedef struct _sai_inbound_acl_stage1_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_inbound_acl_stage1_entry_t;
/**
 * @brief Attribute ID for inbound_acl_stage1_entry
 */
typedef enum _sai_inbound_acl_stage1_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_inbound_acl_stage1_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_ACTION = SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_ACL_STAGE1_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_inbound_acl_stage1_entry_attr_t;


/**
 * @brief inbound_acl_stage2_entry
 */
typedef struct _sai_inbound_acl_stage2_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_inbound_acl_stage2_entry_t;
/**
 * @brief Attribute ID for inbound_acl_stage2_entry
 */
typedef enum _sai_inbound_acl_stage2_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_inbound_acl_stage2_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_ACTION = SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_ACL_STAGE2_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_inbound_acl_stage2_entry_attr_t;


/**
 * @brief inbound_acl_stage3_entry
 */
typedef struct _sai_inbound_acl_stage3_entry_t
{
    /**
     * @brief List matched key dip
     */
     sai_ip_address_t dip;

    /**
     * @brief List matched key sip
     */
     sai_ip_address_t sip;

    /**
     * @brief List matched key protocol
     */
     sai_ip_address_t protocol;

    /**
     * @brief Range_list matched key sport
     */
     sai_uint16_t sport;

    /**
     * @brief Range_list matched key dport
     */
     sai_uint16_t dport;
} sai_inbound_acl_stage3_entry_t;
/**
 * @brief Attribute ID for inbound_acl_stage3_entry
 */
typedef enum _sai_inbound_acl_stage3_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_START,

/**
     * @brief Action
     *
     * @type sai_inbound_acl_stage3_entry_action_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_ACTION = SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_START,

    /**
     * @brief End of attributes
     */
    SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_INBOUND_ACL_STAGE3_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_inbound_acl_stage3_entry_attr_t;


/**
 * @brief eni_meter_entry
 */
typedef struct _sai_eni_meter_entry_t
{
    /**
     * @brief Exact matched key eni
     */
     sai_uint16_t eni;

    /**
     * @brief Exact matched key direction
     */
     sai_uint16_t direction;

    /**
     * @brief Exact matched key dropped
     */
     sai_uint16_t dropped;
} sai_eni_meter_entry_t;
/**
 * @brief Attribute ID for eni_meter_entry
 */
typedef enum _sai_eni_meter_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_ENI_METER_ENTRY_ATTR_START,


    /**
     * @brief End of attributes
     */
    SAI_ENI_METER_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_ENI_METER_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_ENI_METER_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_eni_meter_entry_attr_t;

/**
 * @brief Create direction_lookup_entry
 *
 * @param[out] direction_lookup_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_direction_lookup_entry_fn)(
        _Out_ sai_object_id_t *direction_lookup_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove direction_lookup_entry
 *
 * @param[in] direction_lookup_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_direction_lookup_entry_fn)(
        _In_ sai_object_id_t direction_lookup_entry_id);

/**
 * @brief Set attribute for direction_lookup_entry
 *
 * @param[in] direction_lookup_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_direction_lookup_entry_attribute_fn)(
        _In_ sai_object_id_t direction_lookup_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for direction_lookup_entry
 *
 * @param[in] direction_lookup_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_direction_lookup_entry_attribute_fn)(
        _In_ sai_object_id_t direction_lookup_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create appliance
 *
 * @param[out] appliance_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_appliance_fn)(
        _Out_ sai_object_id_t *appliance_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove appliance
 *
 * @param[in] appliance_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_appliance_fn)(
        _In_ sai_object_id_t appliance_id);

/**
 * @brief Set attribute for appliance
 *
 * @param[in] appliance_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_appliance_attribute_fn)(
        _In_ sai_object_id_t appliance_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for appliance
 *
 * @param[in] appliance_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_appliance_attribute_fn)(
        _In_ sai_object_id_t appliance_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_eni_lookup_from_vm_entry
 *
 * @param[out] outbound_eni_lookup_from_vm_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_eni_lookup_from_vm_entry_fn)(
        _Out_ sai_object_id_t *outbound_eni_lookup_from_vm_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_eni_lookup_from_vm_entry
 *
 * @param[in] outbound_eni_lookup_from_vm_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_eni_lookup_from_vm_entry_fn)(
        _In_ sai_object_id_t outbound_eni_lookup_from_vm_entry_id);

/**
 * @brief Set attribute for outbound_eni_lookup_from_vm_entry
 *
 * @param[in] outbound_eni_lookup_from_vm_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_eni_lookup_from_vm_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_eni_lookup_from_vm_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_eni_lookup_from_vm_entry
 *
 * @param[in] outbound_eni_lookup_from_vm_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_eni_lookup_from_vm_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_eni_lookup_from_vm_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_eni_to_vni_entry
 *
 * @param[out] outbound_eni_to_vni_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_eni_to_vni_entry_fn)(
        _Out_ sai_object_id_t *outbound_eni_to_vni_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_eni_to_vni_entry
 *
 * @param[in] outbound_eni_to_vni_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_eni_to_vni_entry_fn)(
        _In_ sai_object_id_t outbound_eni_to_vni_entry_id);

/**
 * @brief Set attribute for outbound_eni_to_vni_entry
 *
 * @param[in] outbound_eni_to_vni_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_eni_to_vni_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_eni_to_vni_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_eni_to_vni_entry
 *
 * @param[in] outbound_eni_to_vni_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_eni_to_vni_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_eni_to_vni_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_acl_stage1_entry
 *
 * @param[out] outbound_acl_stage1_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_acl_stage1_entry_fn)(
        _Out_ sai_object_id_t *outbound_acl_stage1_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_acl_stage1_entry
 *
 * @param[in] outbound_acl_stage1_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_acl_stage1_entry_fn)(
        _In_ sai_object_id_t outbound_acl_stage1_entry_id);

/**
 * @brief Set attribute for outbound_acl_stage1_entry
 *
 * @param[in] outbound_acl_stage1_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_acl_stage1_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage1_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_acl_stage1_entry
 *
 * @param[in] outbound_acl_stage1_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_acl_stage1_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage1_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_acl_stage2_entry
 *
 * @param[out] outbound_acl_stage2_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_acl_stage2_entry_fn)(
        _Out_ sai_object_id_t *outbound_acl_stage2_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_acl_stage2_entry
 *
 * @param[in] outbound_acl_stage2_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_acl_stage2_entry_fn)(
        _In_ sai_object_id_t outbound_acl_stage2_entry_id);

/**
 * @brief Set attribute for outbound_acl_stage2_entry
 *
 * @param[in] outbound_acl_stage2_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_acl_stage2_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage2_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_acl_stage2_entry
 *
 * @param[in] outbound_acl_stage2_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_acl_stage2_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage2_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_acl_stage3_entry
 *
 * @param[out] outbound_acl_stage3_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_acl_stage3_entry_fn)(
        _Out_ sai_object_id_t *outbound_acl_stage3_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_acl_stage3_entry
 *
 * @param[in] outbound_acl_stage3_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_acl_stage3_entry_fn)(
        _In_ sai_object_id_t outbound_acl_stage3_entry_id);

/**
 * @brief Set attribute for outbound_acl_stage3_entry
 *
 * @param[in] outbound_acl_stage3_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_acl_stage3_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage3_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_acl_stage3_entry
 *
 * @param[in] outbound_acl_stage3_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_acl_stage3_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_acl_stage3_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_routing_entry
 *
 * @param[out] outbound_routing_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_routing_entry_fn)(
        _Out_ sai_object_id_t *outbound_routing_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_routing_entry
 *
 * @param[in] outbound_routing_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_routing_entry_fn)(
        _In_ sai_object_id_t outbound_routing_entry_id);

/**
 * @brief Set attribute for outbound_routing_entry
 *
 * @param[in] outbound_routing_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_routing_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_routing_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_routing_entry
 *
 * @param[in] outbound_routing_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_routing_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_routing_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create outbound_ca_to_pa_entry
 *
 * @param[out] outbound_ca_to_pa_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_outbound_ca_to_pa_entry_fn)(
        _Out_ sai_object_id_t *outbound_ca_to_pa_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove outbound_ca_to_pa_entry
 *
 * @param[in] outbound_ca_to_pa_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_outbound_ca_to_pa_entry_fn)(
        _In_ sai_object_id_t outbound_ca_to_pa_entry_id);

/**
 * @brief Set attribute for outbound_ca_to_pa_entry
 *
 * @param[in] outbound_ca_to_pa_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_outbound_ca_to_pa_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_ca_to_pa_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for outbound_ca_to_pa_entry
 *
 * @param[in] outbound_ca_to_pa_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_outbound_ca_to_pa_entry_attribute_fn)(
        _In_ sai_object_id_t outbound_ca_to_pa_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_eni_lookup_to_vm_entry
 *
 * @param[out] inbound_eni_lookup_to_vm_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_eni_lookup_to_vm_entry_fn)(
        _Out_ sai_object_id_t *inbound_eni_lookup_to_vm_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_eni_lookup_to_vm_entry
 *
 * @param[in] inbound_eni_lookup_to_vm_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_eni_lookup_to_vm_entry_fn)(
        _In_ sai_object_id_t inbound_eni_lookup_to_vm_entry_id);

/**
 * @brief Set attribute for inbound_eni_lookup_to_vm_entry
 *
 * @param[in] inbound_eni_lookup_to_vm_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_eni_lookup_to_vm_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_eni_lookup_to_vm_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_eni_lookup_to_vm_entry
 *
 * @param[in] inbound_eni_lookup_to_vm_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_eni_lookup_to_vm_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_eni_lookup_to_vm_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_eni_to_vm_entry
 *
 * @param[out] inbound_eni_to_vm_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_eni_to_vm_entry_fn)(
        _Out_ sai_object_id_t *inbound_eni_to_vm_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_eni_to_vm_entry
 *
 * @param[in] inbound_eni_to_vm_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_eni_to_vm_entry_fn)(
        _In_ sai_object_id_t inbound_eni_to_vm_entry_id);

/**
 * @brief Set attribute for inbound_eni_to_vm_entry
 *
 * @param[in] inbound_eni_to_vm_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_eni_to_vm_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_eni_to_vm_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_eni_to_vm_entry
 *
 * @param[in] inbound_eni_to_vm_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_eni_to_vm_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_eni_to_vm_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_vm
 *
 * @param[out] inbound_vm_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_vm_fn)(
        _Out_ sai_object_id_t *inbound_vm_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_vm
 *
 * @param[in] inbound_vm_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_vm_fn)(
        _In_ sai_object_id_t inbound_vm_id);

/**
 * @brief Set attribute for inbound_vm
 *
 * @param[in] inbound_vm_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_vm_attribute_fn)(
        _In_ sai_object_id_t inbound_vm_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_vm
 *
 * @param[in] inbound_vm_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_vm_attribute_fn)(
        _In_ sai_object_id_t inbound_vm_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_acl_stage1_entry
 *
 * @param[out] inbound_acl_stage1_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_acl_stage1_entry_fn)(
        _Out_ sai_object_id_t *inbound_acl_stage1_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_acl_stage1_entry
 *
 * @param[in] inbound_acl_stage1_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_acl_stage1_entry_fn)(
        _In_ sai_object_id_t inbound_acl_stage1_entry_id);

/**
 * @brief Set attribute for inbound_acl_stage1_entry
 *
 * @param[in] inbound_acl_stage1_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_acl_stage1_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage1_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_acl_stage1_entry
 *
 * @param[in] inbound_acl_stage1_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_acl_stage1_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage1_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_acl_stage2_entry
 *
 * @param[out] inbound_acl_stage2_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_acl_stage2_entry_fn)(
        _Out_ sai_object_id_t *inbound_acl_stage2_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_acl_stage2_entry
 *
 * @param[in] inbound_acl_stage2_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_acl_stage2_entry_fn)(
        _In_ sai_object_id_t inbound_acl_stage2_entry_id);

/**
 * @brief Set attribute for inbound_acl_stage2_entry
 *
 * @param[in] inbound_acl_stage2_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_acl_stage2_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage2_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_acl_stage2_entry
 *
 * @param[in] inbound_acl_stage2_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_acl_stage2_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage2_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create inbound_acl_stage3_entry
 *
 * @param[out] inbound_acl_stage3_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_inbound_acl_stage3_entry_fn)(
        _Out_ sai_object_id_t *inbound_acl_stage3_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove inbound_acl_stage3_entry
 *
 * @param[in] inbound_acl_stage3_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_inbound_acl_stage3_entry_fn)(
        _In_ sai_object_id_t inbound_acl_stage3_entry_id);

/**
 * @brief Set attribute for inbound_acl_stage3_entry
 *
 * @param[in] inbound_acl_stage3_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_inbound_acl_stage3_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage3_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for inbound_acl_stage3_entry
 *
 * @param[in] inbound_acl_stage3_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_inbound_acl_stage3_entry_attribute_fn)(
        _In_ sai_object_id_t inbound_acl_stage3_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Create eni_meter_entry
 *
 * @param[out] eni_meter_entry_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_eni_meter_entry_fn)(
        _Out_ sai_object_id_t *eni_meter_entry_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove eni_meter_entry
 *
 * @param[in] eni_meter_entry_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_eni_meter_entry_fn)(
        _In_ sai_object_id_t eni_meter_entry_id);

/**
 * @brief Set attribute for eni_meter_entry
 *
 * @param[in] eni_meter_entry_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_eni_meter_entry_attribute_fn)(
        _In_ sai_object_id_t eni_meter_entry_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for eni_meter_entry
 *
 * @param[in] eni_meter_entry_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_eni_meter_entry_attribute_fn)(
        _In_ sai_object_id_t eni_meter_entry_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

typedef struct _sai__api_t
{
    sai_create_direction_lookup_entry_fn                      create_direction_lookup_entry;
    sai_remove_direction_lookup_entry_fn                      remove_direction_lookup_entry;
    sai_set_direction_lookup_entry_attribute_fn               set_direction_lookup_entry_attribute;
    sai_get_direction_lookup_entry_attribute_fn               get_direction_lookup_entry_attribute;
    sai_create_appliance_fn                                   create_appliance;
    sai_remove_appliance_fn                                   remove_appliance;
    sai_set_appliance_attribute_fn                            set_appliance_attribute;
    sai_get_appliance_attribute_fn                            get_appliance_attribute;
    sai_create_outbound_eni_lookup_from_vm_entry_fn           create_outbound_eni_lookup_from_vm_entry;
    sai_remove_outbound_eni_lookup_from_vm_entry_fn           remove_outbound_eni_lookup_from_vm_entry;
    sai_set_outbound_eni_lookup_from_vm_entry_attribute_fn    set_outbound_eni_lookup_from_vm_entry_attribute;
    sai_get_outbound_eni_lookup_from_vm_entry_attribute_fn    get_outbound_eni_lookup_from_vm_entry_attribute;
    sai_create_outbound_eni_to_vni_entry_fn                   create_outbound_eni_to_vni_entry;
    sai_remove_outbound_eni_to_vni_entry_fn                   remove_outbound_eni_to_vni_entry;
    sai_set_outbound_eni_to_vni_entry_attribute_fn            set_outbound_eni_to_vni_entry_attribute;
    sai_get_outbound_eni_to_vni_entry_attribute_fn            get_outbound_eni_to_vni_entry_attribute;
    sai_create_outbound_acl_stage1_entry_fn                   create_outbound_acl_stage1_entry;
    sai_remove_outbound_acl_stage1_entry_fn                   remove_outbound_acl_stage1_entry;
    sai_set_outbound_acl_stage1_entry_attribute_fn            set_outbound_acl_stage1_entry_attribute;
    sai_get_outbound_acl_stage1_entry_attribute_fn            get_outbound_acl_stage1_entry_attribute;
    sai_create_outbound_acl_stage2_entry_fn                   create_outbound_acl_stage2_entry;
    sai_remove_outbound_acl_stage2_entry_fn                   remove_outbound_acl_stage2_entry;
    sai_set_outbound_acl_stage2_entry_attribute_fn            set_outbound_acl_stage2_entry_attribute;
    sai_get_outbound_acl_stage2_entry_attribute_fn            get_outbound_acl_stage2_entry_attribute;
    sai_create_outbound_acl_stage3_entry_fn                   create_outbound_acl_stage3_entry;
    sai_remove_outbound_acl_stage3_entry_fn                   remove_outbound_acl_stage3_entry;
    sai_set_outbound_acl_stage3_entry_attribute_fn            set_outbound_acl_stage3_entry_attribute;
    sai_get_outbound_acl_stage3_entry_attribute_fn            get_outbound_acl_stage3_entry_attribute;
    sai_create_outbound_routing_entry_fn                      create_outbound_routing_entry;
    sai_remove_outbound_routing_entry_fn                      remove_outbound_routing_entry;
    sai_set_outbound_routing_entry_attribute_fn               set_outbound_routing_entry_attribute;
    sai_get_outbound_routing_entry_attribute_fn               get_outbound_routing_entry_attribute;
    sai_create_outbound_ca_to_pa_entry_fn                     create_outbound_ca_to_pa_entry;
    sai_remove_outbound_ca_to_pa_entry_fn                     remove_outbound_ca_to_pa_entry;
    sai_set_outbound_ca_to_pa_entry_attribute_fn              set_outbound_ca_to_pa_entry_attribute;
    sai_get_outbound_ca_to_pa_entry_attribute_fn              get_outbound_ca_to_pa_entry_attribute;
    sai_create_inbound_eni_lookup_to_vm_entry_fn              create_inbound_eni_lookup_to_vm_entry;
    sai_remove_inbound_eni_lookup_to_vm_entry_fn              remove_inbound_eni_lookup_to_vm_entry;
    sai_set_inbound_eni_lookup_to_vm_entry_attribute_fn       set_inbound_eni_lookup_to_vm_entry_attribute;
    sai_get_inbound_eni_lookup_to_vm_entry_attribute_fn       get_inbound_eni_lookup_to_vm_entry_attribute;
    sai_create_inbound_eni_to_vm_entry_fn                     create_inbound_eni_to_vm_entry;
    sai_remove_inbound_eni_to_vm_entry_fn                     remove_inbound_eni_to_vm_entry;
    sai_set_inbound_eni_to_vm_entry_attribute_fn              set_inbound_eni_to_vm_entry_attribute;
    sai_get_inbound_eni_to_vm_entry_attribute_fn              get_inbound_eni_to_vm_entry_attribute;
    sai_create_inbound_vm_fn                                  create_inbound_vm;
    sai_remove_inbound_vm_fn                                  remove_inbound_vm;
    sai_set_inbound_vm_attribute_fn                           set_inbound_vm_attribute;
    sai_get_inbound_vm_attribute_fn                           get_inbound_vm_attribute;
    sai_create_inbound_acl_stage1_entry_fn                    create_inbound_acl_stage1_entry;
    sai_remove_inbound_acl_stage1_entry_fn                    remove_inbound_acl_stage1_entry;
    sai_set_inbound_acl_stage1_entry_attribute_fn             set_inbound_acl_stage1_entry_attribute;
    sai_get_inbound_acl_stage1_entry_attribute_fn             get_inbound_acl_stage1_entry_attribute;
    sai_create_inbound_acl_stage2_entry_fn                    create_inbound_acl_stage2_entry;
    sai_remove_inbound_acl_stage2_entry_fn                    remove_inbound_acl_stage2_entry;
    sai_set_inbound_acl_stage2_entry_attribute_fn             set_inbound_acl_stage2_entry_attribute;
    sai_get_inbound_acl_stage2_entry_attribute_fn             get_inbound_acl_stage2_entry_attribute;
    sai_create_inbound_acl_stage3_entry_fn                    create_inbound_acl_stage3_entry;
    sai_remove_inbound_acl_stage3_entry_fn                    remove_inbound_acl_stage3_entry;
    sai_set_inbound_acl_stage3_entry_attribute_fn             set_inbound_acl_stage3_entry_attribute;
    sai_get_inbound_acl_stage3_entry_attribute_fn             get_inbound_acl_stage3_entry_attribute;
    sai_create_eni_meter_entry_fn                             create_eni_meter_entry;
    sai_remove_eni_meter_entry_fn                             remove_eni_meter_entry;
    sai_set_eni_meter_entry_attribute_fn                      set_eni_meter_entry_attribute;
    sai_get_eni_meter_entry_attribute_fn                      get_eni_meter_entry_attribute;
} sai__api_t;

/**
 * @}
 */
#endif /** __SAIEXPERIMENTAL_H_ */
