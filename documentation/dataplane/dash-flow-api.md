# DASH Flow API HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/20/2024 | Zhixiong Niu | Initial version |

## Table of Contents

- [DASH Flow API HLD](#dash-flow-api-hld)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Overview](#overview)
  - [Flow Table APIs](#flow-table-apis)
  - [Flow APIs](#flow-apis)
    - [Basic flow APIs](#basic-flow-apis)
    - [Keys of flow entry](#keys-of-flow-entry)
    - [Attributes of flow entry](#attributes-of-flow-entry)
      - [Flow basic metadata](#flow-basic-metadata)
      - [Reverse flow key](#reverse-flow-key)
      - [Flow encap related attributes](#flow-encap-related-attributes)
      - [Flow overlay rewrite related attributes](#flow-overlay-rewrite-related-attributes)
    - [Extra flow metadata](#extra-flow-metadata)
    - [Flow Bulk Get Session](#flow-bulk-get-session)
      - [Flow Bulk Get Session filter](#flow-bulk-get-session-filter)
      - [Flow Bulk Get Session API](#flow-bulk-get-session-api)
      - [Bulk Get Session Event Notification](#bulk-get-session-event-notification)
    - [Protobuf-based flow programming](#protobuf-based-flow-programming)
    - [Capability](#capability)
  - [Examples](#examples)
    - [Create flow table](#create-flow-table)
    - [Create flow entry key](#create-flow-entry-key)
    - [Create flow entry](#create-flow-entry)
    - [Add flow entries](#add-flow-entries)
    - [Retrieve flow entry](#retrieve-flow-entry)
    - [Retrieve flow entries via flow entry bulk get session](#retrieve-flow-entries-via-flow-entry-bulk-get-session)
    - [Remove flow entry](#remove-flow-entry)
    - [Remove flow table](#remove-flow-table)

## Introduction

DASH supports the storage and processing of millions of flow states. To further enhance the DASH flow processing capabilities, we offer a DASH flow abstraction layer to facilitate vendor-neutral flow management. This layer ensures uniform control over flows across programmable switches, DPUs, and smart switches. The DASH flow abstraction provides concepts of flow tables and flow entries, as well as APIs to manage the flows.

The DASH flow APIs enable the creation, removal, retrieval, and configuration of flow tables, entries, and bulk sync sessions with flow filters.

Cloud providers can leverage DASH flow to develop services tailored to a diverse array of scenarios. Examples of achievable functionalities include:

- **Dataplane Applications**: Such as cloud gateways, load balancers, etc.
- **Flow Management**: Including flow offloading and updating, with tasks like flow redirection and resimulation, etc.
- **Dataplane Debugging**: Diagnosing the behaviors of different flows.
- **Foundational Flow Services**: Flow state high availability, etc.

## Overview

- **Flow/flow entry**: It represents a single direction of the match-action entry for a connection.

- **Flow Key**: The key that is used to match the packet for finding its flow.

- **Flow State**: The state of the flow, including the packet transformations and all other tracked states, such as TCP, HA, etc.

- **Flow Table**: The table to store a set of flows.

![dash_flow_model](images/dash-flow-api-model.svg)

The figure above illustrates the flow abstraction model. We represent flows as being stored within a flow table and managed through DASH flow SAI APIs. Flow entries, which contain the state information of flows, are organized within these flow tables. The key of a flow entry is utilized to retrieve its associated flow state. It's important to note that the ENI and flow table are not directly linked; for example, a single table can contain flow entries associated with various ENIs, and flows with the same ENI may span multiple flow tables. The choice of arrangement depends on specific scenarios.

Upon the arrival of new flows, whether individually or in batches, corresponding flow entries are added to the table. These entries may represent either bidirectional or unidirectional flows. For bidirectional flows, the implementation adds entries for both the original flow and its reverse, linking their reverse flow keys to each other. For unidirectional flows, the current direction is specified. If a reverse flow for a unidirectional flow is created later, the user can add reverse keys for both and link them accordingly.

Flows can be modified and removed through the DASH flow SAI API and can also be aged by the hardware.

For more use cases, please refer to [Smart Switch HA HLD](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md).

## Flow Table APIs

The flow_table APIs are define as follows:

| API                      | Description                           |
| ------------------------ | :------------------------------------ |
| create_flow_table        | Create a new flow table               |
| remove_flow_table        | Remove a flow table                   |
| set_flow_table_attribute | Set the attributes of a flow table    |
| get_flow_table_attribute | Obtain the attributes of a flow table |
| create_flow_tables       | Create multiple flow tables in bulk   |
| remove_flow_tables       | Remove multiple flow tables in bulk   |

The attributes of the flow_table are defined as follows:

| Attribute name                         | Type                       | Description                                     |
|----------------------------------------|----------------------------|-------------------------------------------------|
| SAI_FLOW_TABLE_ATTR_MAX_FLOW_COUNT     | `sai_uint32_t`             | Maximum number of flows allowed in the table.   |
| SAI_FLOW_TABLE_ATTR_DASH_FLOW_ENABLED_KEY | `sai_dash_flow_enabled_key_t` | Key enable mask |
| SAI_FLOW_TABLE_ATTR_FLOW_TTL_IN_MILLISECONDS | `sai_uint32_t`     | Time-to-live (TTL) for flows in milliseconds.  |

The sai_dash_flow_enabled_key_t is defined as follows:

```c
typedef enum _sai_dash_flow_enabled_key_t
{
    SAI_DASH_FLOW_ENABLED_KEY_NONE = 0,

    SAI_DASH_FLOW_ENABLED_KEY_ENI_MAC = 1 << 1,
  
    SAI_DASH_FLOW_ENABLED_KEY_VNI = 1 << 2,

    SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL = 1 << 3,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_IP = 1 << 4,

    SAI_DASH_FLOW_ENABLED_KEY_DST_IP = 1 << 5,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT = 1 << 6,

    SAI_DASH_FLOW_ENABLED_KEY_DST_PORT = 1 << 7,

} sai_dash_flow_enabled_key_t;
```

## Flow APIs

### Basic flow APIs

The flow_entry APIs are defined as follows:

| API                      | Description                                                  |
| ------------------------ | :----------------------------------------------------------- |
| create_flow_entry        | Add a single new entry to a certain flow table               |
| remove_flow_entry        | Remove a single entry in a certain flow table. Note that the flow removal process deletes two flows if it is a bi-directional flow. If you wish to remove a flow in only one direction, you should set the flow to be uni-directional in advance. |
| set_flow_entry_attribute | Set attributes for a single entry in a certain flow table    |
| get_flow_entry_attribute | Get attributes of a single entry in a certain flow table     |
| create_flow_entries      | Add multiple entries to a certain flow table in bulk         |
| remove_flow_entries      | Remove multiple entries from a specific flow table in bulk. Note that the flow removal process deletes two flows if it is a bi-directional flow. If you wish to remove a flow in only one direction, you should set the flow to be uni-directional in advance. |

### Keys of flow entry

The keys for a flow entry are defined as follows:

Please note that there is an attribute in the *flow_table* that can specify which of the following keys are enabled. If a key is not enabled, it will not be used in match and action.

The *flow_table_id* is used to designate the flow table for the flow only, which is not used in match and action.

```c
typedef struct _sai_flow_entry_t
{
    /**
     * @brief Switch ID
     *
     * @objects SAI_OBJECT_TYPE_SWITCH
     */
    sai_object_id_t switch_id;

    /**
     * @brief Exact matched key flow_table_id
     *
     * @objects SAI_OBJECT_TYPE_FLOW_TABLE
     */
    sai_object_id_t flow_table_id;

    /**
     * @brief Exact matched key eni_mac
     */
    sai_mac_t eni_mac;
  
    /**
     * @brief Exact matched key vni
     */
    sai_uint32_t vni;

    /**
     * @brief Exact matched key ip_protocol
     */
    sai_uint8_t ip_proto;

    /**
     * @brief Exact matched key src_ip
     */
    sai_ip_address_t src_ip;

    /**
     * @brief Exact matched key dst_ip
     */
    sai_ip_address_t dst_ip;

    /**
     * @brief Exact matched key src_port
     */
    sai_uint16_t src_port;

    /**
     * @brief Exact matched key dst_port
     */
    sai_uint16_t dst_port;

} sai_flow_entry_t;
```

### Attributes of flow entry

The attributes of the flow entry can be divided into different categories. Please see below for further details.

#### Flow basic metadata

These are the basic attributes of flow entry.

| Attribute name                             | Type                     | Description                                                  |
| ------------------------------------------ | ------------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_VERSION                | `sai_uint32_t`           | Version of the flow entry                                    |
| SAI_FLOW_ENTRY_ATTR_DASH_DIRECTION         | `sai_dash_direction_t`   | Direction of the DASH flow                                   |
| SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION       | `sai_dash_flow_action_t` | Action to be applied on the flow                             |
| SAI_FLOW_ENTRY_ATTR_METER_CLASS            | `sai_uint32_t`           | Meter class for flow entry, used for traffic metering and policing. |
| SAI_FLOW_ENTRY_ATTR_IS_UNIDIRECTIONAL_FLOW | `bool`                   | Indicates if the flow is unidirectional                      |

#### Reverse flow key

When configuring a flow_entry, it can be specified whether it is unidirectional or bidirectional. If it is bidirectional, it can be designated as a reverse flow key, allowing for the rapid identification of the corresponding reverse flow. Of course, if a flow entry is initially established as unidirectional, its reverse flow can also be set up later, utilizing these attributes to link them together.

| Attribute name                            | Type               | Description                                 |
| ----------------------------------------- | ------------------ | ------------------------------------------- |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_ENI_MAC  | `sai_mac_t`        | Eni mac addr for the reverse flow           |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_VNI      | `sai_uint32_t`     | VNI for reverse flow                        |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_IP_PROTO | `sai_uint8_t`      | IP protocol number for the reverse flow     |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_SRC_IP   | `sai_ip_address_t` | Source IP address for the reverse flow      |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_DST_IP   | `sai_ip_address_t` | Destination IP address for the reverse flow |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_SRC_PORT | `sai_uint16_t`     | L4 source port for the reverse flow         |
| SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_DST_PORT | `sai_uint16_t`     | L4 destination port for the reverse flow    |

#### Flow encap related attributes

These are the related attributes of flow encapsulation.

| Attribute name                                   | Type                       | Description                                                  |
| ------------------------------------------------ | -------------------------- | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY0_VNI                | `sai_uint32_t`             | Destination VNI in the underlay network                      |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY0_SIP                | `sai_uint32_t`             | Source IP address in the underlay network                    |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DIP                | `sai_uint32_t`             | Destination IP address in the underlay network               |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DASH_ENCAPSULATION | `sai_dash_encapsulation_t` | Encapsulation method for DASH traffic in the underlay network |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_VNI                | `sai_uint32_t`             | Destination VNI in the 2nd underlay network                  |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SIP                | `sai_uint32_t`             | Source IP address in the 2nd underlay network                |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DIP                | `sai_uint32_t`             | Destination IP address in the 2nd underlay network           |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SMAC               | `sai_mac_t`                | Source MAC address in the 2nd underlay network               |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DMAC               | `sai_mac_t`                | Destination MAC address in the 2nd underlay network          |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DASH_ENCAPSULATION | `sai_dash_encapsulation_t` | Encapsulation method for DASH traffic in the 2nd underlay network |

#### Flow overlay rewrite related attributes

These are the related attributes of flow rewrite.

| Attribute name               | Type               | Description                                                  |
| ---------------------------- | ------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_DST_MAC  | `sai_mac_t`        | Destination MAC address for the flow entry.                  |
| SAI_FLOW_ENTRY_ATTR_SIP      | `sai_ip_address_t` | Source IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_DIP      | `sai_ip_address_t` | Destination IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_SIP_MASK | `sai_ip_address_t` | Subnet mask for the source IP address.                       |
| SAI_FLOW_ENTRY_ATTR_DIP_MASK | `sai_ip_address_t` | Subnet mask for the destination IP address.                  |

### Extra flow metadata

Here are some extra metadata for different purposes.

| Attribute name                      | Type            | Description                                                  |
| ----------------------------------- | --------------- | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_VENDOR_METADATA | `sai_u8_list_t` | Vendor-specific metadata that can be attached to the flow entry for custom processing. |
| SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB    | `sai_u8_list_t` | The flow data protocol buffer enables high-efficiency creation, retrieval, and communication for a flow entry. |

### Flow Bulk Get Session

#### Flow Bulk Get Session filter

To manage data transfer to a server via gRPC or event notification, we introduce a flow entry bulk session that incorporates filtering capabilities to precisely define the data range for transfer. The procedure for setting up these filters is straightforward:

1. Initially, create up to five flow bulk get session filters based on the specific needs for filtering the flows.
2. Subsequently, establish a flow bulk get session filter and integrate these filters as attributes.

For example, consider the scenario where it's necessary to select all flow entries with a version less than 5 and greater than version 3. In this case, two distinct filters should be defined to meet the criteria and then create the flow entry bulk session.

The filter, defined as an object, is specified as follows:

| Function                                         | Description                                                  |
| ------------------------------------------------ | ------------------------------------------------------------ |
| create_flow_entry_bulk_get_session_filter        | Add a single new filter for flow entry bulk get session feature. |
| remove_flow_entry_bulk_get_session_filter        | Remove a single filter for flow entry bulk get session feature. |
| set_flow_entry_bulk_get_session_filter_attribute | Set attributes for a single filter in flow entry bulk get session. |
| get_flow_entry_bulk_get_session_filter_attribute | Get attributes of a single filter in flow entry bulk get session. |
| create_flow_entry_bulk_get_session_filters       | Add multiple new filters for flow entry bulk get session feature. |
| remove_flow_entry_bulk_get_session_filters       | Remove multiple filters for flow entry bulk get session feature. |

| Attribute Name                                               | Type                                                | Description                                                  |
| ------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY | `sai_dash_flow_entry_bulk_get_session_filter_key_t` | Key of the filter                                            |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY | `sai_dash_flow_entry_bulk_get_session_op_key_t`     | Operation of the filter                                      |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_INT_VALUE        | `sai_uint64_t`                                      | INT Value of the filter , ``@validonly SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_IP_PROTO || SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_PORT || SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_PORT ||  SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_FLOW_VERSION` |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_IP_VALUE         | `sai_ip_address_t`                                  | IP Value of the filter, `@validonly SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_IP || SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_IP` |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_MAC_VALUE        | `sai_mac_t`                                         | Mac Value of the filter, `@validonly SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY == SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_ENI_MAC` |

```c
typedef enum _sai_dash_flow_entry_bulk_get_session_filter_key_t
{
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_NONE,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_ENI_MAC,
  
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_VNI,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_IP_PROTO,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_IP,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_IP,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_PORT,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_PORT,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_FLOW_VERSION,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_AGED,

} sai_dash_flow_entry_bulk_get_session_filter_key_t;
```

```c
typedef enum _sai_dash_flow_entry_bulk_get_session_op_key_t
{
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_INVALID,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_EQUAL_TO,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_GREATER_THAN,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_GREATER_THAN_OR_EQUAL_TO,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_LESS_THAN,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_LESS_THAN_OR_EQUAL_TO,

} sai_dash_flow_entry_bulk_get_session_op_key_t;
```

#### Flow Bulk Get Session API

Upon establishing the bulk get session filters, we can initiate a flow bulk get session, which is defined as follows:

| Function                                  | Description                                                 |
| ----------------------------------------- | ----------------------------------------------------------- |
| create_flow_entry_bulk_get_session        | Add a single new session for flow entry bulk get feature    |
| remove_flow_entry_bulk_get_session        | Remove a single new session for flow entry bulk get feature |
| set_flow_entry_bulk_get_session_attribute | Set attributes for a single session                         |
| get_flow_entry_bulk_get_session_attribute | Get attributes of a single session                          |
| create_flow_entry_bulk_get_sessions       | Add multiple new sessions for flow entry bulk get feature   |
| remove_flow_entry_bulk_get_sessions       | Remove multiple sessions for flow entry bulk get feature    |

In the attributes, we allow specifying the gRPC server and port when the mode is gRPC. For filtering flow entries, we support up to five filters. Each filter is a bulk get session filter object, and different filters are combined using an *AND* operation. If no filters are specified, the bulk get session returns all flow entries.

| Attribute Name                                               | Type                                                         | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_FLOW_TABLE | `sai_object_id_t`                                            | Flow table to bulk get                                       |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_MODE   | `sai_dash_flow_entry_bulk_get_session_mode_t`                | Specify bulk get mode                                        |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_ENTRY_LIMITATION   | `sai_uint32_t`                                               | Specify a maximum limit for the bulk get session             |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_SERVER_IP | `sai_ip_address_t`                                           | The IP address to use for the bulk get session.              |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_SERVER_PORT | `sai_uint16_t`                                               | The port to use for the bulk get session.                    |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FIRST_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter BULK_GET_SESSION_IP |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_SECOND_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter BULK_GET_SESSION_PORT |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_THIRD_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter FIRST_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FOURTH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter SECOND_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FIFTH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter THIRD_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |

```c
typedef enum _sai_dash_flow_entry_bulk_get_session_mode_t

{
  SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_GRPC,

  SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT,
  
  SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_MODE_EVENT_WITHOUT_FLOW_STATE,

} sai_dash_flow_entry_bulk_get_session_mode_t;
```

#### Bulk Get Session Event Notification

| Attribute name                                     | Type                                              | Description                                                  |
| -------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ |
| SAI_SWITCH_ATTR_FLOW_BULK_GET_SESSION_EVENT_NOTIFY | `sai_flow_bulk_get_session_event_notification_fn` | The callback function for receiving events on flow bulk get session event notification. |

```c
/**
 * @brief bulk flow get event type
 */
typedef enum _sai_flow_bulk_get_session_event_t
{
    SAI_FLOW_BULK_GET_SESSION_FINISHED,

    SAI_FLOW_BULK_GET_SESSION_FLOW_ENTRY,

} sai_flow_bulk_get_session_event_t;

/**
 * @brief Notification data format received from SAI HA set callback
 *
 * @count attr[attr_count]
 */
typedef struct _sai_flow_bulk_get_session_event_data_t
{
    sai_flow_bulk_get_session_event_t event_type;

    sai_object_id_t flow_bulk_session_id;
  
    sai_flow_entry_t *flow_entry;
  
    uint32_t attr_count; 
  
    sai_attribute_t *attr_list; 

} sai_flow_bulk_get_session_event_data_t;

/**
 * @brief dash flow get bulk session notification
 *
 * Passed as a parameter into sai_initialize_switch()
 *
 * @count data[count]
 *
 * @param[in] count Number of notifications
 * @param[in] data Array of flow bulk get session events
 */
typedef void (*sai_flow_bulk_get_session_event_notification_fn)(
        _In_ uint32_t count,
        _In_ const sai_flow_bulk_get_session_event_data_t *flow_bulk_get_session_event_data);
```

### Protobuf-based flow programming

In addition to the flow state attributes, the flow state can be represented using protobuf for high-efficiency. The attribute of the flow entry is SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB.

Although the content of both attributes and protobuf may be identical, their applications differ. Attributes enable incremental updates to individual properties, whereas protobuf necessitates a complete update.

```protobuf
syntax = "proto3";

message MacAddress {
  bytes address = 1 [(validate.rules).bytes.len = 6];  // MAC address bytes
}

message IpAddress {
  uint16 type = 1;  // IP address type (IPv4 = 2 or IPv6 = 10)
  bytes address = 2 [(validate.rules).bytes.len = {const: 4 | const: 16}];  // IP address bytes, 4 bytes for IPv4, 16 bytes for IPv6
}

message SaiDashFlowKey {
  bytes eni_mac = 1;  // ENI MAC address, using bytes to match MacAddress structure
  uint32 vni = 2; // VNI
  IpAddress src_ip = 3;  // Source IP address
  IpAddress dst_ip = 4;  // Destination IP address
  uint8 ip_proto = 5; // IP Protocol
  uint32 src_port = 6;  // Source port
  uint32 dst_port = 7;  // Destination port
}

message SaiDashFlowState {
  uint32 version = 1;  // SAI_FLOW_ENTRY_ATTR_VERSION
  uint16 dash_direction = 2; // SAI_FLOW_ENTRY_ATTR_DASH_DIRECTION
  uint32 dash_flow_action = 3;  // SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION
  uint32 meter_class = 4;  // SAI_FLOW_ENTRY_ATTR_METER_CLASS
  bool is_unidirectional_flow = 5;  // SAI_FLOW_ENTRY_ATTR_IS_UNIDIRECTIONAL_FLOW
  uint32 underlay0_vni = 6;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY0_VNI
  IpAddress underlay0_sip = 7;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY0_SIP
  IpAddress underlay0_dip = 8;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DIP
  uint16 underlay0_dash_encapsulation = 9; // SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DASH_ENCAPSULATION
  uint32 underlay1_vni = 10;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_VNI
  IpAddress underlay1_sip = 11;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SIP
  IpAddress underlay1_dip = 12;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DIP
  MacAddress underlay1_smac = 13;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SMAC
  MacAddress underlay1_dmac = 14;  // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DMAC
  uint16 underlay1_dash_encapsulation = 15; // SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DASH_ENCAPSULATION
  MacAddress dst_mac = 16;  // SAI_FLOW_ENTRY_ATTR_DST_MAC
  IpAddress sip = 17;  // SAI_FLOW_ENTRY_ATTR_SIP
  IpAddress dip = 18;  // SAI_FLOW_ENTRY_ATTR_DIP
  bytes sip_mask = 19;  // SAI_FLOW_ENTRY_ATTR_SIP_MASK
  bytes dip_mask = 20;  // SAI_FLOW_ENTRY_ATTR_DIP_MASK
}

message SaiDashFlowEntry {
  SaiDashFlowKey flow_key = 1;
  SaiDashFlowKey reverse_flow_key = 2;
  SaiDashFlowState flow_state = 3;
}

```

### Capability

| Attribute Name                                      | Type                          | Description                                        |
| --------------------------------------------------- | ----------------------------- | -------------------------------------------------- |
| SAI_SWITCH_ATTR_DASH_CAPS_MAX_FLOW_TABLE_COUNT      | `sai_uint32_t`                | The max number of flow tables that can be created  |
| SAI_SWITCH_ATTR_DASH_CAPS_MAX_FLOW_ENTRY_COUNT      | `sai_uint32_t`                | The max number of flow entries for all tables      |
| SAI_SWITCH_ATTR_DASH_CAPS_SUPPORTED_ENABLED_KEY     | `sai_dash_flow_enabled_key_t` | Indicates what flow key mask can be used           |
| SAI_SWITCH_ATTR_DASH_CAPS_BULK_GET_SESSION          | `bool`                        | Indicates if it supports bulk get sessions         |
| SAI_SWITCH_ATTR_DASH_CAPS_UNIDIRECTIONAL_FLOW_ENTRY | `bool`                        | Indicates if it supports unidirectional flow entry |
| SAI_SWITCH_ATTR_DASH_CAPS_FLOW_CREATE               | `bool`                        | Indicates if it supports flow create               |
| SAI_SWITCH_ATTR_DASH_CAPS_FLOW_REMOVE               | `bool`                        | Indicates if it supports flow remove               |
| SAI_SWITCH_ATTR_DASH_CAPS_FLOW_SET                  | `bool`                        | Indicates if it supports flow set                  |
| SAI_SWITCH_ATTR_DASH_CAPS_FLOW_GET                  | `bool`                        | Indicates if it supports flow get                  |

## Examples

When a service intends to use the DASH Flow SAI APIs, it should first establish a flow table via the `create_flow_table()` function. After the table creation, the programmer can add, delete, modify, or retrieve flow entries from the table using the DASH flow API. It can also use `flow_entry_bulk_get_session` to retrieve flows with filters, allowing it to handle flows in batches under specific conditions.

![dash_flow_example](images/dash-flow-api-example.svg)

For instance, the figure above shows an example of a DASH flow HA between two DPUs. First, both DPUs should create flow tables for initialization via `create_flow_table`. When performing Inline Sync, DPU1 and DPU2 use `create_flow_entry` to create new flows as new flows arrive. When DASH flow HA needs to perform bulk sync from the active DPU to the standby DPU, it should initially fetch the entry from the active DPU using `create_flow_entry_bulk_get_session` to create a bulk get session to transfer the flows to DPU2 via gRPC. Then, the standby DPU subsequently calls `create_flow_entries()` to add entries to the corresponding flow table.

Below are detailed examples to use the DASH flow API.

### Create flow table

```c
uint32_t attr_count = 3; 
sai_attribute_t attr_list[3];
attr_list[0].id = SAI_FLOW_TABLE_ATTR_DASH_FLOW_ENABLED_KEY;
attr_list[0].value = SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL |
                         SAI_DASH_FLOW_ENABLED_KEY_ENI_MAC |
                         SAI_DASH_FLOW_ENABLED_KEY_VNI |
                         SAI_DASH_FLOW_ENABLED_KEY_SRC_IP | 
                         SAI_DASH_FLOW_ENABLED_KEY_DST_IP | 
                         SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT | 
                         SAI_DASH_FLOW_ENABLED_KEY_DST_PORT;
...  

sai_object_id_t flow_table_id;
sai_status_t status = create_flow_table(&flow_table_id, switch_id, attr_count, attr_list);
```

### Create flow entry key

```c
sai_flow_entry_t flow_entry;

flow_entry.flow_table_id = 0x112233;
flow_entry.ip_proto = 6;
flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip.addr.ip4);
flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip.addr.ip4);
flow_entry.src_port = 12345;
flow_entry.dst_port = 80;
```

### Create flow entry

```c
SaiDashFlowEntry flow_entry_pb = SAI_DASH_FLOW_ENTRY__INIT;
...

unsigned len = sai_dash_flow_entry__get_packed_size(&flow_entry_pb);
uint8_t *buf = malloc(len);
sai_dash_flow_entry__pack(&flow_entry_pb, buf);

sai_attribute_t sai_attrs_list[1];
sai_attrs_list[0].id = SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB;
sai_attr_list[0].value = buf;

sai_status_t status = create_flow_entry(&flow_entry, 1, attr_list);

free(buf);
```

### Add flow entries

```c
uint32_t flow_count = num_flow_states;
const sai_dash_flow_key_t flow_key[] = ...; 
uint32_t attr_count[] = ...; 
sai_attribute_t *attr_list[] = ...; 
sai_status_t object_statuses[] = ...; 

status = create_flow_entries(flow_table_id, flow_count, flow_key, attr_count, attr_list, SAI_BULK_OP_ERROR_MODE_IGNORE_ERROR, object_statuses);
```

### Retrieve flow entry

```c
sai_flow_entry_t flow_entry;
flow_entry.flow_table_id = 0x112233;
flow_entry.ip_proto = 6;
flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip_addr.addr.ip4);
flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip_addr.addr.ip4);
flow_entry.src_port = 12345;
flow_entry.dst_port = 80;

status = get_flow_entry_attribute(flow_entry, attr_count, attr_list);
```

### Retrieve flow entries via flow entry bulk get session

Example: Retrieve flow entries by filtering for all versions greater than 3 and less than 5, and return the results via GRPC.

```c
/* Filter: Flow Entry Version > 3 */
sai_attribute_t filter1_attr_list[3];
filter1_attr_list[0].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY;
filter1_attr_list[0].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_KEY_VERSION;
filter1_attr_list[1].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY;
filter1_attr_list[1].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_GREATER_THAN,;
filter1_attr_list[2].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_INT_VALUE;
filter1_attr_list[2].value = 3;

sai_object_id_t filter1_id;
status = create_flow_entry_bulk_get_session_filter(&filter1_id, switch_id, 3, filter1_attr_list);

/* Filter: Flow Entry Version < 5 */
sai_attribute_t filter2_attr_list[3];
filter2_attr_list[0].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY;
filter2_attr_list[0].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_KEY_VERSION;
filter2_attr_list[1].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY;
filter2_attr_list[1].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_LESS_THAN;
filter2_attr_list[2].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_INT_VALUE;
filter2_attr_list[2].value = 5;

sai_object_id_t filter2_id;
status = create_flow_entry_bulk_get_session_filter(&filter2_id, switch_id, 3, filter2_attr_list);

/* Session */
sai_attribute_t session_attr_list[4];
session_attr_list[0].value.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "10.0.0.1", &(session_attr_list[0].value.addr.ip4));
session_attr_list[1].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_PORT;
session_attr_list[1].value = 1000;
session_attr_list[2].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FIRST_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID;
session_attr_list[2].value = filter1_id;
session_attr_list[3].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_SECOND_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID;
session_attr_list[3].value = filter2_id;

sai_object_id_t flow_entry_bulk_get_session_id;
status = create_flow_entry_bulk_get_session(&flow_entry_bulk_get_session_id, switch_id, 4, session_attr_list);
```

### Remove flow entry

```c
/* Note that the flow removal process deletes two flows if it is a bi-directional flow. If you wish to remove a flow in only one direction, you should set the flow to be uni-directional in advance */

sai_flow_entry_t flow_entry;
flow_entry.flow_table_id = 0x112233;
flow_entry.ip_proto = 6;
flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip.addr.ip4);
flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip.addr.ip4);
flow_entry.src_port = 12345;
flow_entry.dst_port = 80;

status = remove_flow_entry(flow_entry);
```

### Remove flow table

```c
sai_object_id_t flow_table_id = 0x112233;
status = remove_flow_table(flow_table_id);
```
