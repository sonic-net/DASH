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
 * @file    saiport.h
 *
 * @brief   This module defines SAI Port interface
 */

#if !defined (__SAIPORT_H_)
#define __SAIPORT_H_

#include <saitypes.h>

/**
 * @defgroup SAIPORT SAI - Port specific API definitions
 *
 * @{
 */

/**
 * @brief Attribute data for #SAI_PORT_ATTR_OPER_STATUS
 */
typedef enum _sai_port_oper_status_t
{
    /** Unknown */
    SAI_PORT_OPER_STATUS_UNKNOWN,

    /** Up */
    SAI_PORT_OPER_STATUS_UP,

    /** Down */
    SAI_PORT_OPER_STATUS_DOWN,

    /** Test Running */
    SAI_PORT_OPER_STATUS_TESTING,

    /** Not Present */
    SAI_PORT_OPER_STATUS_NOT_PRESENT

} sai_port_oper_status_t;

/**
 * @brief Defines the operational status of the port
 */
typedef struct _sai_port_oper_status_notification_t
{
    /**
     * @brief Port id.
     *
     * @objects SAI_OBJECT_TYPE_PORT, SAI_OBJECT_TYPE_BRIDGE_PORT, SAI_OBJECT_TYPE_LAG
     */
    sai_object_id_t port_id;

    /** Port operational status */
    sai_port_oper_status_t port_state;

} sai_port_oper_status_notification_t;

/**
 * @brief Attribute data for #SAI_PORT_ATTR_FEC_MODE
 */
typedef enum _sai_port_fec_mode_t
{
    /** No FEC */
    SAI_PORT_FEC_MODE_NONE,

    /** Enable RS-FEC - 25G, 50G, 100G ports. The specific RS-FEC mode will be automatically determined. */
    SAI_PORT_FEC_MODE_RS,

    /** Enable FC-FEC - 10G, 25G, 40G, 50G ports */
    SAI_PORT_FEC_MODE_FC,
} sai_port_fec_mode_t;

/**
 * @brief Attribute data for #SAI_PORT_ATTR_FEC_MODE_EXTENDED
 */
typedef enum _sai_port_fec_mode_extended_t
{
    /** No FEC */
    SAI_PORT_FEC_MODE_EXTENDED_NONE,

    /** Enable RS-528 FEC (CL91) - 25G, 50G, 100G ports */
    SAI_PORT_FEC_MODE_EXTENDED_RS528,

    /** Enable RS544-FEC - 100G PAM4, 200G ports */
    SAI_PORT_FEC_MODE_EXTENDED_RS544,

    /** Enable RS544-FEC (interleaved) - 100G, 200G, 400G ports */
    SAI_PORT_FEC_MODE_EXTENDED_RS544_INTERLEAVED,

    /** Enable FC-FEC (CL74) - 10G, 25G, 40G, 50G ports */
    SAI_PORT_FEC_MODE_EXTENDED_FC,
} sai_port_fec_mode_extended_t;

/**
 * @brief Attribute data for #SAI_PORT_ATTR_INTERFACE_TYPE
 * Used for selecting electrical interface with specific electrical pin and signal quality
 */
typedef enum _sai_port_interface_type_t
{
    /** Interface type none */
    SAI_PORT_INTERFACE_TYPE_NONE,

    /** Interface type CR */
    SAI_PORT_INTERFACE_TYPE_CR,

    /** Interface type CR2 */
    SAI_PORT_INTERFACE_TYPE_CR2,

    /** Interface type CR4 */
    SAI_PORT_INTERFACE_TYPE_CR4,

    /** Interface type SR */
    SAI_PORT_INTERFACE_TYPE_SR,

    /** Interface type SR2 */
    SAI_PORT_INTERFACE_TYPE_SR2,

    /** Interface type SR4 */
    SAI_PORT_INTERFACE_TYPE_SR4,

    /** Interface type LR */
    SAI_PORT_INTERFACE_TYPE_LR,

    /** Interface type LR4 */
    SAI_PORT_INTERFACE_TYPE_LR4,

    /** Interface type KR */
    SAI_PORT_INTERFACE_TYPE_KR,

    /** Interface type KR4 */
    SAI_PORT_INTERFACE_TYPE_KR4,

    /** Interface type CAUI */
    SAI_PORT_INTERFACE_TYPE_CAUI,

    /** Interface type GMII */
    SAI_PORT_INTERFACE_TYPE_GMII,

    /** Interface type SFI */
    SAI_PORT_INTERFACE_TYPE_SFI,

    /** Interface type XLAUI */
    SAI_PORT_INTERFACE_TYPE_XLAUI,

    /** Interface type KR2 */
    SAI_PORT_INTERFACE_TYPE_KR2,

    /** Interface type CAUI */
    SAI_PORT_INTERFACE_TYPE_CAUI4,

    /** Interface type XAUI */
    SAI_PORT_INTERFACE_TYPE_XAUI,

    /** Interface type XFI */
    SAI_PORT_INTERFACE_TYPE_XFI,

    /** Interface type XGMII */
    SAI_PORT_INTERFACE_TYPE_XGMII,

    /** Interface type MAX */
    SAI_PORT_INTERFACE_TYPE_MAX,

} sai_port_interface_type_t;

/**
 * @brief Attribute Id in sai_set_port_attribute() and
 * sai_get_port_attribute() calls
 */
typedef enum _sai_port_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_PORT_ATTR_START,

    /* READ-ONLY */

    /**
     * @brief Query list of supported port speed(full-duplex) in Mbps
     *
     * @type sai_u32_list_t
     * @flags READ_ONLY
     */
    SAI_PORT_ATTR_SUPPORTED_SPEED,

    /* READ-WRITE */

    /**
     * @brief Hardware Lane list
     *
     * @type sai_u32_list_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY | KEY
     */
    SAI_PORT_ATTR_HW_LANE_LIST,

    /**
     * @brief Speed in Mbps
     *
     * On get, returns the configured port speed.
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_AND_SET
     */
    SAI_PORT_ATTR_SPEED,

    /**
     * @brief Auto Negotiation configuration
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_PORT_ATTR_AUTO_NEG_MODE,

    /**
     * @brief Admin Mode
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_PORT_ATTR_ADMIN_STATE,

    /**
     * @brief Query/Configure list of Advertised port speed (Full-Duplex) in Mbps
     *
     * Used when auto negotiation is on. Empty list means all supported values are enabled.
     *
     * @type sai_u32_list_t
     * @flags CREATE_AND_SET
     * @default empty
     */
    SAI_PORT_ATTR_ADVERTISED_SPEED,

    /**
     * @brief Forward Error Correction (FEC) control
     *
     * @type sai_port_fec_mode_t
     * @flags CREATE_AND_SET
     * @default SAI_PORT_FEC_MODE_NONE
     * @validonly SAI_PORT_ATTR_USE_EXTENDED_FEC == false
     */
    SAI_PORT_ATTR_FEC_MODE,

    /**
     * @brief MTU
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 1514
     */
    SAI_PORT_ATTR_MTU,

    /**
     * @brief Configure Interface type
     *
     * @type sai_port_interface_type_t
     * @flags CREATE_AND_SET
     * @default SAI_PORT_INTERFACE_TYPE_NONE
     */
    SAI_PORT_ATTR_INTERFACE_TYPE,

    /**
     * @brief End of attributes
     */
    SAI_PORT_ATTR_END,

    /** Custom range base value */
    SAI_PORT_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_PORT_ATTR_CUSTOM_RANGE_END

} sai_port_attr_t;

/**
 * @brief Port counter IDs in sai_get_port_stats() call
 *
 * @flags Contains flags
 */
typedef enum _sai_port_stat_t
{
    /** SAI port stat if in octets */
    SAI_PORT_STAT_IF_IN_OCTETS,

    /** SAI port stat if in ucast pkts */
    SAI_PORT_STAT_IF_IN_UCAST_PKTS,

    /** SAI port stat if in non ucast pkts */
    SAI_PORT_STAT_IF_IN_NON_UCAST_PKTS,

    /** SAI port stat if in discards */
    SAI_PORT_STAT_IF_IN_DISCARDS,

    /** SAI port stat if in errors */
    SAI_PORT_STAT_IF_IN_ERRORS,

    /** SAI port stat if in unknown protocols */
    SAI_PORT_STAT_IF_IN_UNKNOWN_PROTOS,

    /** SAI port stat if in broadcast pkts */
    SAI_PORT_STAT_IF_IN_BROADCAST_PKTS,

    /** SAI port stat if in multicast pkts */
    SAI_PORT_STAT_IF_IN_MULTICAST_PKTS,

    /** SAI port stat if in vlan discards */
    SAI_PORT_STAT_IF_IN_VLAN_DISCARDS,

    /** SAI port stat if out octets */
    SAI_PORT_STAT_IF_OUT_OCTETS,

    /** SAI port stat if out ucast pkts */
    SAI_PORT_STAT_IF_OUT_UCAST_PKTS,

    /** SAI port stat if out non ucast pkts */
    SAI_PORT_STAT_IF_OUT_NON_UCAST_PKTS,

    /** SAI port stat if out discards */
    SAI_PORT_STAT_IF_OUT_DISCARDS,

    /** SAI port stat if out errors */
    SAI_PORT_STAT_IF_OUT_ERRORS,

    /** SAI port stat if out queue length */
    SAI_PORT_STAT_IF_OUT_QLEN,

    /** SAI port stat if out broadcast pkts */
    SAI_PORT_STAT_IF_OUT_BROADCAST_PKTS,

    /** SAI port stat if out multicast pkts */
    SAI_PORT_STAT_IF_OUT_MULTICAST_PKTS,

    /** SAI port stat ether stats drop events */
    SAI_PORT_STAT_ETHER_STATS_DROP_EVENTS,

    /** SAI port stat ether stats multicast pkts */
    SAI_PORT_STAT_ETHER_STATS_MULTICAST_PKTS,

    /** SAI port stat ether stats broadcast pkts */
    SAI_PORT_STAT_ETHER_STATS_BROADCAST_PKTS,

    /** SAI port stat ether stats undersized pkts */
    SAI_PORT_STAT_ETHER_STATS_UNDERSIZE_PKTS,

    /** SAI port stat ether stats fragments */
    SAI_PORT_STAT_ETHER_STATS_FRAGMENTS,

    /** SAI port stat ether stats pkts 64 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_64_OCTETS,

    /** SAI port stat ether stats pkts 65 to 127 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_65_TO_127_OCTETS,

    /** SAI port stat ether stats pkts 128 to 255 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_128_TO_255_OCTETS,

    /** SAI port stat ether stats pkts 256 to 511 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_256_TO_511_OCTETS,

    /** SAI port stat ether stats pkts 512 to 1023 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_512_TO_1023_OCTETS,

    /** SAI port stat ether stats pkts 1024 to 1518 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_1024_TO_1518_OCTETS,

    /** SAI port stat ether stats pkts 1519 to 2047 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_1519_TO_2047_OCTETS,

    /** SAI port stat ether stats pkts 2048 to 4095 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_2048_TO_4095_OCTETS,

    /** SAI port stat ether stats pkts 4096 to 9216 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_4096_TO_9216_OCTETS,

    /** SAI port stat ether stats pkts 9217 to 16383 octets */
    SAI_PORT_STAT_ETHER_STATS_PKTS_9217_TO_16383_OCTETS,

    /** SAI port stat ether stats oversize pkts */
    SAI_PORT_STAT_ETHER_STATS_OVERSIZE_PKTS,

    /** SAI port stat ether rx oversize pkts */
    SAI_PORT_STAT_ETHER_RX_OVERSIZE_PKTS,

    /** SAI port stat ether tx oversize pkts */
    SAI_PORT_STAT_ETHER_TX_OVERSIZE_PKTS,

    /** SAI port stat ether stats jabbers */
    SAI_PORT_STAT_ETHER_STATS_JABBERS,

    /** SAI port stat ether stats octets */
    SAI_PORT_STAT_ETHER_STATS_OCTETS,

    /** SAI port stat ether stats pkts */
    SAI_PORT_STAT_ETHER_STATS_PKTS,

    /** SAI port stat ether stats collisions */
    SAI_PORT_STAT_ETHER_STATS_COLLISIONS,

    /** SAI port stat ether stats CRC align errors */
    SAI_PORT_STAT_ETHER_STATS_CRC_ALIGN_ERRORS,

    /** SAI port stat ether stats tx no errors */
    SAI_PORT_STAT_ETHER_STATS_TX_NO_ERRORS,

    /** SAI port stat ether stats rx no errors */
    SAI_PORT_STAT_ETHER_STATS_RX_NO_ERRORS,

    /** SAI port stat IP in receives */
    SAI_PORT_STAT_IP_IN_RECEIVES,

    /** SAI port stat IP in octets */
    SAI_PORT_STAT_IP_IN_OCTETS,

    /** SAI port stat IP in ucast pkts */
    SAI_PORT_STAT_IP_IN_UCAST_PKTS,

    /** SAI port stat IP in non ucast pkts */
    SAI_PORT_STAT_IP_IN_NON_UCAST_PKTS,

    /** SAI port stat IP in discards */
    SAI_PORT_STAT_IP_IN_DISCARDS,

    /** SAI port stat IP out octets */
    SAI_PORT_STAT_IP_OUT_OCTETS,

    /** SAI port stat IP out ucast pkts */
    SAI_PORT_STAT_IP_OUT_UCAST_PKTS,

    /** SAI port stat IP out non ucast pkts */
    SAI_PORT_STAT_IP_OUT_NON_UCAST_PKTS,

    /** SAI port stat IP out discards */
    SAI_PORT_STAT_IP_OUT_DISCARDS,

    /** SAI port stat IPv6 in receives */
    SAI_PORT_STAT_IPV6_IN_RECEIVES,

    /** SAI port stat IPv6 in octets */
    SAI_PORT_STAT_IPV6_IN_OCTETS,

    /** SAI port stat IPv6 in ucast pkts */
    SAI_PORT_STAT_IPV6_IN_UCAST_PKTS,

    /** SAI port stat IPv6 in non ucast pkts */
    SAI_PORT_STAT_IPV6_IN_NON_UCAST_PKTS,

    /** SAI port stat IPv6 in mcast pkts */
    SAI_PORT_STAT_IPV6_IN_MCAST_PKTS,

    /** SAI port stat IPv6 in discards */
    SAI_PORT_STAT_IPV6_IN_DISCARDS,

    /** SAI port stat IPv6 out octets */
    SAI_PORT_STAT_IPV6_OUT_OCTETS,

    /** SAI port stat IPv6 out ucast pkts */
    SAI_PORT_STAT_IPV6_OUT_UCAST_PKTS,

    /** SAI port stat IPv6 out non ucast pkts */
    SAI_PORT_STAT_IPV6_OUT_NON_UCAST_PKTS,

    /** SAI port stat IPv6 out mcast pkts */
    SAI_PORT_STAT_IPV6_OUT_MCAST_PKTS,

    /** SAI port stat IPv6 out discards */
    SAI_PORT_STAT_IPV6_OUT_DISCARDS,

    /** Get/set WRED green packet count [uint64_t] */
    SAI_PORT_STAT_GREEN_WRED_DROPPED_PACKETS,

    /** Get/set WRED green byte count [uint64_t] */
    SAI_PORT_STAT_GREEN_WRED_DROPPED_BYTES,

    /** Get/set WRED yellow packet count [uint64_t] */
    SAI_PORT_STAT_YELLOW_WRED_DROPPED_PACKETS,

    /** Get/set WRED yellow byte count [uint64_t] */
    SAI_PORT_STAT_YELLOW_WRED_DROPPED_BYTES,

    /** Get/set WRED red packet count [uint64_t] */
    SAI_PORT_STAT_RED_WRED_DROPPED_PACKETS,

    /** Get/set WRED red byte count [uint64_t] */
    SAI_PORT_STAT_RED_WRED_DROPPED_BYTES,

    /** Get/set WRED dropped packets count [uint64_t] */
    SAI_PORT_STAT_WRED_DROPPED_PACKETS,

    /** Get/set WRED dropped bytes count [uint64_t] */
    SAI_PORT_STAT_WRED_DROPPED_BYTES,

    /** Get/set packets marked by ECN count [uint64_t] */
    SAI_PORT_STAT_ECN_MARKED_PACKETS,

    /** Packet size based packets count rt stat ether in pkts 64 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_64_OCTETS,

    /** SAI port stat ether in pkts 65 to 127 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_65_TO_127_OCTETS,

    /** SAI port stat ether in pkts 128 to 255 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_128_TO_255_OCTETS,

    /** SAI port stat ether in pkts 256 to 511 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_256_TO_511_OCTETS,

    /** SAI port stat ether in pkts 512 to 1023 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_512_TO_1023_OCTETS,

    /** SAI port stat ether in pkts 1024 to 1518 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_1024_TO_1518_OCTETS,

    /** SAI port stat ether in pkts 1519 to 2047 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_1519_TO_2047_OCTETS,

    /** SAI port stat ether in pkts 2048 to 4095 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_2048_TO_4095_OCTETS,

    /** SAI port stat ether in pkts 4096 to 9216 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_4096_TO_9216_OCTETS,

    /** SAI port stat ether in pkts 9217 to 16383 octets */
    SAI_PORT_STAT_ETHER_IN_PKTS_9217_TO_16383_OCTETS,

    /** SAI port stat ether out pkts 64 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_64_OCTETS,

    /** SAI port stat ether out pkts 65 to 127 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_65_TO_127_OCTETS,

    /** SAI port stat ether out pkts 128 to 255 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_128_TO_255_OCTETS,

    /** SAI port stat ether out pkts 256 to 511 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_256_TO_511_OCTETS,

    /** SAI port stat ether out pkts 512 to 1023 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_512_TO_1023_OCTETS,

    /** SAI port stat ether out pkts 1024 to 1518 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_1024_TO_1518_OCTETS,

    /** SAI port stat ether out pkts 1519 to 2047 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_1519_TO_2047_OCTETS,

    /** SAI port stat ether out pkts 2048 to 4095 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_2048_TO_4095_OCTETS,

    /** SAI port stat ether out pkts 4096 to 9216 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_4096_TO_9216_OCTETS,

    /** SAI port stat ether out pkts 9217 to 16383 octets */
    SAI_PORT_STAT_ETHER_OUT_PKTS_9217_TO_16383_OCTETS,

    /** Get in port current occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_IN_CURR_OCCUPANCY_BYTES,

    /** Get in port watermark occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_IN_WATERMARK_BYTES,

    /** Get in port current shared occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_IN_SHARED_CURR_OCCUPANCY_BYTES,

    /** Get in port watermark shared occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_IN_SHARED_WATERMARK_BYTES,

    /** Get out port current occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_OUT_CURR_OCCUPANCY_BYTES,

    /** Get out port watermark occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_OUT_WATERMARK_BYTES,

    /** Get out port current shared occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_OUT_SHARED_CURR_OCCUPANCY_BYTES,

    /** Get out port watermark shared occupancy in bytes [uint64_t] */
    SAI_PORT_STAT_OUT_SHARED_WATERMARK_BYTES,

    /** Get in port packet drops due to buffers [uint64_t] */
    SAI_PORT_STAT_IN_DROPPED_PKTS,

    /** Get out port packet drops due to buffers [uint64_t] */
    SAI_PORT_STAT_OUT_DROPPED_PKTS,

    /** Get the number of pause frames received on the port [uint64_t] */
    SAI_PORT_STAT_PAUSE_RX_PKTS,

    /** Get the number of pause frames transmitted on the port [uint64_t] */
    SAI_PORT_STAT_PAUSE_TX_PKTS,

    /** PFC Packet Counters for RX and TX per PFC priority [uint64_t] */
    SAI_PORT_STAT_PFC_0_RX_PKTS,

    /** SAI port stat PFC 0 tx pkts */
    SAI_PORT_STAT_PFC_0_TX_PKTS,

    /** SAI port stat PFC 1 rx pkts */
    SAI_PORT_STAT_PFC_1_RX_PKTS,

    /** SAI port stat PFC 1 tx pkts */
    SAI_PORT_STAT_PFC_1_TX_PKTS,

    /** SAI port stat PFC 2 rx pkts */
    SAI_PORT_STAT_PFC_2_RX_PKTS,

    /** SAI port stat PFC 2 tx pkts */
    SAI_PORT_STAT_PFC_2_TX_PKTS,

    /** SAI port stat PFC 3 rx pkts */
    SAI_PORT_STAT_PFC_3_RX_PKTS,

    /** SAI port stat PFC 3 tx pkts */
    SAI_PORT_STAT_PFC_3_TX_PKTS,

    /** SAI port stat PFC 4 rx pkts */
    SAI_PORT_STAT_PFC_4_RX_PKTS,

    /** SAI port stat PFC 4 tx pkts */
    SAI_PORT_STAT_PFC_4_TX_PKTS,

    /** SAI port stat PFC 5 rx pkts */
    SAI_PORT_STAT_PFC_5_RX_PKTS,

    /** SAI port stat PFC 5 tx pkts */
    SAI_PORT_STAT_PFC_5_TX_PKTS,

    /** SAI port stat PFC 6 rx pkts */
    SAI_PORT_STAT_PFC_6_RX_PKTS,

    /** SAI port stat PFC 6 tx pkts */
    SAI_PORT_STAT_PFC_6_TX_PKTS,

    /** SAI port stat PFC 7 rx pkts */
    SAI_PORT_STAT_PFC_7_RX_PKTS,

    /** SAI port stat PFC 7 tx pkts */
    SAI_PORT_STAT_PFC_7_TX_PKTS,

    /**
     * @brief PFC pause duration for RX and TX per PFC priority [uint64_t]
     *
     * RX pause duration for certain priority is a the duration quanta in ingress pause
     * frame for that priority (a pause frame received by the switch).
     * While TX pause duration for certain priority is the duration quanta in egress pause
     * frame for that priority (a pause frame sent by the switch).
     */
    SAI_PORT_STAT_PFC_0_RX_PAUSE_DURATION,

    /** SAI port stat PFC 0 tx duration */
    SAI_PORT_STAT_PFC_0_TX_PAUSE_DURATION,

    /** SAI port stat PFC 1 rx duration */
    SAI_PORT_STAT_PFC_1_RX_PAUSE_DURATION,

    /** SAI port stat PFC 1 tx duration */
    SAI_PORT_STAT_PFC_1_TX_PAUSE_DURATION,

    /** SAI port stat PFC 2 rx duration */
    SAI_PORT_STAT_PFC_2_RX_PAUSE_DURATION,

    /** SAI port stat PFC 2 tx duration */
    SAI_PORT_STAT_PFC_2_TX_PAUSE_DURATION,

    /** SAI port stat PFC 3 rx duration */
    SAI_PORT_STAT_PFC_3_RX_PAUSE_DURATION,

    /** SAI port stat PFC 3 tx duration */
    SAI_PORT_STAT_PFC_3_TX_PAUSE_DURATION,

    /** SAI port stat PFC 4 rx duration */
    SAI_PORT_STAT_PFC_4_RX_PAUSE_DURATION,

    /** SAI port stat PFC 4 tx duration */
    SAI_PORT_STAT_PFC_4_TX_PAUSE_DURATION,

    /** SAI port stat PFC 5 rx duration */
    SAI_PORT_STAT_PFC_5_RX_PAUSE_DURATION,

    /** SAI port stat PFC 5 tx duration */
    SAI_PORT_STAT_PFC_5_TX_PAUSE_DURATION,

    /** SAI port stat PFC 6 rx duration */
    SAI_PORT_STAT_PFC_6_RX_PAUSE_DURATION,

    /** SAI port stat PFC 6 tx duration */
    SAI_PORT_STAT_PFC_6_TX_PAUSE_DURATION,

    /** SAI port stat PFC 7 rx duration */
    SAI_PORT_STAT_PFC_7_RX_PAUSE_DURATION,

    /** SAI port stat PFC 7 tx duration */
    SAI_PORT_STAT_PFC_7_TX_PAUSE_DURATION,

    /**
     * @brief PFC pause duration for RX and TX per PFC priority in micro seconds [uint64_t]
     *
     * RX pause duration for certain priority is a the duration in micro seconds converted
     * from quanta in ingress pause frame for that priority (a pause frame received by the
     * switch).
     * While TX pause duration for certain priority is the duration in micro seconds converted
     * from quanta in egress pause frame for that priority (a pause frame sent by the switch).
     */
    SAI_PORT_STAT_PFC_0_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 0 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_0_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 1 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_1_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 1 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_1_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 2 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_2_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 2 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_2_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 3 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_3_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 3 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_3_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 4 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_4_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 4 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_4_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 5 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_5_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 5 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_5_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 6 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_6_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 6 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_6_TX_PAUSE_DURATION_US,

    /** SAI port stat PFC 7 rx duration in micro seconds */
    SAI_PORT_STAT_PFC_7_RX_PAUSE_DURATION_US,

    /** SAI port stat PFC 7 tx duration in micro seconds */
    SAI_PORT_STAT_PFC_7_TX_PAUSE_DURATION_US,

    /** PFC based ON to OFF pause transitions counter per PFC priority [uint64_t] */
    SAI_PORT_STAT_PFC_0_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 1 on to off rx pkts */
    SAI_PORT_STAT_PFC_1_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 2 on to off rx pkts */
    SAI_PORT_STAT_PFC_2_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 3 on to off rx pkts */
    SAI_PORT_STAT_PFC_3_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 4 on to off rx pkts */
    SAI_PORT_STAT_PFC_4_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 5 on to off rx pkts */
    SAI_PORT_STAT_PFC_5_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 6 on to off rx pkts */
    SAI_PORT_STAT_PFC_6_ON2OFF_RX_PKTS,

    /** SAI port stat PFC 7 on to off rx pkts */
    SAI_PORT_STAT_PFC_7_ON2OFF_RX_PKTS,

    /** Frames received that are not an integral number of octets in length and do not pass the FCS check */
    SAI_PORT_STAT_DOT3_STATS_ALIGNMENT_ERRORS,

    /** Frames received that are an integral number of octets in length but do not pass the FCS check */
    SAI_PORT_STAT_DOT3_STATS_FCS_ERRORS,

    /** Frames that are involved in a single collision, and are subsequently transmitted successfully */
    SAI_PORT_STAT_DOT3_STATS_SINGLE_COLLISION_FRAMES,

    /** Frames that are involved in a more than one collision collision, and are subsequently transmitted successfully */
    SAI_PORT_STAT_DOT3_STATS_MULTIPLE_COLLISION_FRAMES,

    /** Number of times that the SQE TEST ERROR is received */
    SAI_PORT_STAT_DOT3_STATS_SQE_TEST_ERRORS,

    /** Frames for which the first transmission attempt is delayed because the medium is busy */
    SAI_PORT_STAT_DOT3_STATS_DEFERRED_TRANSMISSIONS,

    /** Number of times that a collision is detected later than one slot time into the transmission of a packet */
    SAI_PORT_STAT_DOT3_STATS_LATE_COLLISIONS,

    /** Frames for which transmission fails due to excessive collisions */
    SAI_PORT_STAT_DOT3_STATS_EXCESSIVE_COLLISIONS,

    /** Frames for which transmission fails due to an internal MAC sublayer transmit error */
    SAI_PORT_STAT_DOT3_STATS_INTERNAL_MAC_TRANSMIT_ERRORS,

    /** Number of times that the carrier sense condition was lost or never asserted when attempting to transmit a frame */
    SAI_PORT_STAT_DOT3_STATS_CARRIER_SENSE_ERRORS,

    /** Frames received that exceed the maximum permitted frame size */
    SAI_PORT_STAT_DOT3_STATS_FRAME_TOO_LONGS,

    /** Frames for which reception fails due to an internal MAC sublayer receive error */
    SAI_PORT_STAT_DOT3_STATS_INTERNAL_MAC_RECEIVE_ERRORS,

    /** Number of times there was an invalid data symbol, incremented at most once per carrier event */
    SAI_PORT_STAT_DOT3_STATS_SYMBOL_ERRORS,

    /** MAC Control frames received that contain an opcode that is not supported by this device */
    SAI_PORT_STAT_DOT3_CONTROL_IN_UNKNOWN_OPCODES,

    /**
     * @brief Number of times port state changed from
     * high power mode to low power mode in TX direction [uint64_t]
     */
    SAI_PORT_STAT_EEE_TX_EVENT_COUNT,

    /**
     * @brief Number of times port state changed from
     * high power mode to low power mode in RX direction [uint64_t]
     */
    SAI_PORT_STAT_EEE_RX_EVENT_COUNT,

    /**
     * @brief Port Low power mode duration(micro secs) in TX direction [uint64_t].
     *
     * This Duration is accumulative since EEE enable on port/from last clear stats.
     */
    SAI_PORT_STAT_EEE_TX_DURATION,

    /**
     * @brief Port Low power mode duration(micro secs) in RX direction [uint64_t]
     *
     * This Duration is accumulative since EEE enable on port/from last clear stats.
     */
    SAI_PORT_STAT_EEE_RX_DURATION,

    /** PRBS Error Count */
    SAI_PORT_STAT_PRBS_ERROR_COUNT,

    /** SAI port stat if in FEC correctable pkts */
    SAI_PORT_STAT_IF_IN_FEC_CORRECTABLE_FRAMES,

    /** SAI port stat if in FEC not correctable pkts */
    SAI_PORT_STAT_IF_IN_FEC_NOT_CORRECTABLE_FRAMES,

    /** SAI port stat if in FEC symbol errors */
    SAI_PORT_STAT_IF_IN_FEC_SYMBOL_ERRORS,

    /** Fabric port stat in data units */
    SAI_PORT_STAT_IF_IN_FABRIC_DATA_UNITS,

    /** Fabric port stat out data units */
    SAI_PORT_STAT_IF_OUT_FABRIC_DATA_UNITS,

    /** Port stat in drop reasons range start */
    SAI_PORT_STAT_IN_DROP_REASON_RANGE_BASE = 0x00001000,

    /** Get in port packet drops configured by debug counter API at index 0 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_0_DROPPED_PKTS = SAI_PORT_STAT_IN_DROP_REASON_RANGE_BASE,

    /** Get in port packet drops configured by debug counter API at index 1 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_1_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 2 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_2_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 3 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_3_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 4 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_4_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 5 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_5_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 6 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_6_DROPPED_PKTS,

    /** Get in port packet drops configured by debug counter API at index 7 */
    SAI_PORT_STAT_IN_CONFIGURED_DROP_REASONS_7_DROPPED_PKTS,

    /** Port stat in drop reasons range end */
    SAI_PORT_STAT_IN_DROP_REASON_RANGE_END = 0x00001fff,

    /** Port stat out drop reasons range start */
    SAI_PORT_STAT_OUT_DROP_REASON_RANGE_BASE = 0x00002000,

    /** Get out port packet drops configured by debug counter API at index 0 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_0_DROPPED_PKTS = SAI_PORT_STAT_OUT_DROP_REASON_RANGE_BASE,

    /** Get out port packet drops configured by debug counter API at index 1 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_1_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 2 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_2_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 3 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_3_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 4 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_4_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 5 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_5_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 6 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_6_DROPPED_PKTS,

    /** Get out port packet drops configured by debug counter API at index 7 */
    SAI_PORT_STAT_OUT_CONFIGURED_DROP_REASONS_7_DROPPED_PKTS,

    /** Port stat out drop reasons range end */
    SAI_PORT_STAT_OUT_DROP_REASON_RANGE_END = 0x00002fff,

} sai_port_stat_t;

/**
 * @brief Create port
 *
 * @param[out] port_id Port id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_create_port_fn)(
        _Out_ sai_object_id_t *port_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove port
 *
 * @param[in] port_id Port id
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_remove_port_fn)(
        _In_ sai_object_id_t port_id);

/**
 * @brief Set port attribute value.
 *
 * @param[in] port_id Port id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_set_port_attribute_fn)(
        _In_ sai_object_id_t port_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get port attribute value.
 *
 * @param[in] port_id Port id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_get_port_attribute_fn)(
        _In_ sai_object_id_t port_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Get port statistics counters. Deprecated for backward compatibility.
 *
 * @param[in] port_id Port id
 * @param[in] number_of_counters Number of counters in the array
 * @param[in] counter_ids Specifies the array of counter ids
 * @param[out] counters Array of resulting counter values.
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_get_port_stats_fn)(
        _In_ sai_object_id_t port_id,
        _In_ uint32_t number_of_counters,
        _In_ const sai_stat_id_t *counter_ids,
        _Out_ uint64_t *counters);

/**
 * @brief Get port statistics counters extended.
 *
 * @param[in] port_id Port id
 * @param[in] number_of_counters Number of counters in the array
 * @param[in] counter_ids Specifies the array of counter ids
 * @param[in] mode Statistics mode
 * @param[out] counters Array of resulting counter values.
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_get_port_stats_ext_fn)(
        _In_ sai_object_id_t port_id,
        _In_ uint32_t number_of_counters,
        _In_ const sai_stat_id_t *counter_ids,
        _In_ sai_stats_mode_t mode,
        _Out_ uint64_t *counters);

/**
 * @brief Clear port statistics counters.
 *
 * @param[in] port_id Port id
 * @param[in] number_of_counters Number of counters in the array
 * @param[in] counter_ids Specifies the array of counter ids
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_clear_port_stats_fn)(
        _In_ sai_object_id_t port_id,
        _In_ uint32_t number_of_counters,
        _In_ const sai_stat_id_t *counter_ids);

/**
 * @brief Clear port's all statistics counters.
 *
 * @param[in] port_id Port id
 *
 * @return #SAI_STATUS_SUCCESS on success, failure status code on error
 */
typedef sai_status_t (*sai_clear_port_all_stats_fn)(
        _In_ sai_object_id_t port_id);

/**
 * @brief Port state change notification
 *
 * Passed as a parameter into sai_initialize_switch()
 *
 * @count data[count]
 *
 * @param[in] count Number of notifications
 * @param[in] data Array of port operational status
 */
typedef void (*sai_port_state_change_notification_fn)(
        _In_ uint32_t count,
        _In_ const sai_port_oper_status_notification_t *data);

/**
 * @brief Port methods table retrieved with sai_api_query()
 */
typedef struct _sai_port_api_t
{
    sai_create_port_fn                     create_port;
    sai_remove_port_fn                     remove_port;
    sai_set_port_attribute_fn              set_port_attribute;
    sai_get_port_attribute_fn              get_port_attribute;
    sai_get_port_stats_fn                  get_port_stats;
    sai_get_port_stats_ext_fn              get_port_stats_ext;
    sai_clear_port_stats_fn                clear_port_stats;
    sai_clear_port_all_stats_fn            clear_port_all_stats;
} sai_port_api_t;

/**
 * @}
 */
#endif /** __SAIPORT_H_ */
