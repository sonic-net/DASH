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
 * @file    saiswitch.h
 *
 * @brief   This module defines SAI Switch interface
 */

#if !defined (__SAISWITCH_H_)
#define __SAISWITCH_H_

#include <saitypes.h>

/**
 * @defgroup SAISWITCH SAI - Switch specific API definitions
 *
 * @{
 */

/**
 * @brief Attribute data for #SAI_SWITCH_ATTR_OPER_STATUS
 */
typedef enum _sai_switch_oper_status_t
{
    /** Unknown */
    SAI_SWITCH_OPER_STATUS_UNKNOWN,

    /** Up */
    SAI_SWITCH_OPER_STATUS_UP,

    /** Down */
    SAI_SWITCH_OPER_STATUS_DOWN,

    /** Switch encountered a fatal error */
    SAI_SWITCH_OPER_STATUS_FAILED,

} sai_switch_oper_status_t;

/**
 * @brief Attribute data for packet action
 */
typedef enum _sai_packet_action_t
{
    /* Basic Packet Actions */

    /*
     * These could be further classified based on the nature of action
     * - Data Plane Packet Actions
     * - CPU Path Packet Actions
     */

    /*
     * Data Plane Packet Actions.
     *
     * Following two packet actions only affect the packet action on the data plane.
     * Packet action on the CPU path remains unchanged.
     */

    /** Drop Packet in data plane */
    SAI_PACKET_ACTION_DROP,

    /** Forward Packet in data plane. */
    SAI_PACKET_ACTION_FORWARD,

    /*
     * CPU Path Packet Actions.
     *
     * Following two packet actions only affect the packet action on the CPU path.
     * Packet action on the data plane remains unchanged.
     */

    /**
     * @brief Packet action copy
     *
     * Copy Packet to CPU without interfering the original packet action in the
     * pipeline.
     */
    SAI_PACKET_ACTION_COPY,

    /** Cancel copy the packet to CPU. */
    SAI_PACKET_ACTION_COPY_CANCEL,

    /** Combination of Packet Actions */

    /**
     * @brief Packet action trap
     *
     * This is a combination of SAI packet action COPY and DROP:
     * A copy of the original packet is sent to CPU port, the original
     * packet is forcefully dropped from the pipeline.
     */
    SAI_PACKET_ACTION_TRAP,

    /**
     * @brief Packet action log
     *
     * This is a combination of SAI packet action COPY and FORWARD:
     * A copy of the original packet is sent to CPU port, the original
     * packet, if it was to be dropped in the original pipeline,
     * change the pipeline action to forward (cancel drop).
     */
    SAI_PACKET_ACTION_LOG,

    /** This is a combination of SAI packet action COPY_CANCEL and DROP */
    SAI_PACKET_ACTION_DENY,

    /** This is a combination of SAI packet action COPY_CANCEL and FORWARD */
    SAI_PACKET_ACTION_TRANSIT

} sai_packet_action_t;

/**
 * @brief Attribute Id in sai_set_switch_attribute() and
 * sai_get_switch_attribute() calls.
 */
typedef enum _sai_switch_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_SWITCH_ATTR_START,

    /**
     * @brief Number of active(created) ports on the switch
     *
     * @type sai_uint32_t
     * @flags READ_ONLY
     */
    SAI_SWITCH_ATTR_NUMBER_OF_ACTIVE_PORTS = SAI_SWITCH_ATTR_START,

    /**
     * @brief Get the port list
     *
     * @type sai_object_list_t
     * @flags READ_ONLY
     * @objects SAI_OBJECT_TYPE_PORT
     * @default internal
     */
    SAI_SWITCH_ATTR_PORT_LIST,

    /**
     * @brief Default switch MAC Address
     *
     * @type sai_mac_t
     * @flags CREATE_AND_SET
     * @default vendor
     */
    SAI_SWITCH_ATTR_SRC_MAC_ADDRESS,

    /**
     * @brief Default VXLAN destination UDP port
     *
     * @type sai_uint16_t
     * @flags CREATE_AND_SET
     * @isvlan false
     * @default 4789
     */
    SAI_SWITCH_ATTR_VXLAN_DEFAULT_PORT,

    /**
     * @brief Set to switch initialization or connect to NPU/SDK.
     *
     * TRUE - Initialize switch/SDK.
     * FALSE - Connect to SDK. This will connect library to the initialized SDK.
     * After this call the capability attributes should be ready for retrieval
     * via sai_get_switch_attribute()
     *
     * @type bool
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_SWITCH_ATTR_INIT_SWITCH,

    /**
     * @brief Port state change notification callback function passed to the adapter.
     *
     * In case driver does not support this attribute, The Host adapter should poll
     * port status by SAI_PORT_ATTR_OPER_STATUS.
     *
     * Use sai_port_state_change_notification_fn as notification function.
     *
     * @type sai_pointer_t sai_port_state_change_notification_fn
     * @flags CREATE_AND_SET
     * @default NULL
     */
    SAI_SWITCH_ATTR_PORT_STATE_CHANGE_NOTIFY,

     /**
     * @brief Get the CPU Port
     *
     * @type sai_object_id_t
     * @flags READ_ONLY
     * @objects SAI_OBJECT_TYPE_PORT
     * @default internal
     */
    SAI_SWITCH_ATTR_CPU_PORT,

    /**
     * @brief Default SAI Virtual Router ID
     *
     * Must return #SAI_STATUS_OBJECT_IN_USE when try to delete this VR ID.
     *
     * @type sai_object_id_t
     * @flags READ_ONLY
     * @objects SAI_OBJECT_TYPE_VIRTUAL_ROUTER
     * @default internal
     */
    SAI_SWITCH_ATTR_DEFAULT_VIRTUAL_ROUTER_ID,

    /**
     * @brief End of attributes
     */
    SAI_SWITCH_ATTR_END,

    /** Custom range base value */
    SAI_SWITCH_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_SWITCH_ATTR_CUSTOM_RANGE_END

} sai_switch_attr_t;

/**
 * @brief Create switch
 *
 * SDK initialization/connect to SDK. After the call the capability attributes should be
 * ready for retrieval via sai_get_switch_attribute(). Same Switch Object id should be
 * given for create/connect for each NPU.
 *
 * @param[out] switch_id The Switch Object ID
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_create_switch_fn)(
        _Out_ sai_object_id_t *switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove/disconnect Switch
 *
 * Release all resources associated with currently opened switch
 *
 * @param[in] switch_id The Switch id
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_remove_switch_fn)(
        _In_ sai_object_id_t switch_id);

/**
 * @brief Set switch attribute value
 *
 * @param[in] switch_id Switch id
 * @param[in] attr Switch attribute
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_set_switch_attribute_fn)(
        _In_ sai_object_id_t switch_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get switch attribute value
 *
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of switch attributes
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_get_switch_attribute_fn)(
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Switch method table retrieved with sai_api_query()
 */
typedef struct _sai_switch_api_t
{
    sai_create_switch_fn                   create_switch;
    sai_remove_switch_fn                   remove_switch;
    sai_set_switch_attribute_fn            set_switch_attribute;
    sai_get_switch_attribute_fn            get_switch_attribute;

} sai_switch_api_t;

/**
 * @}
 */
#endif /** __SAISWITCH_H_ */
