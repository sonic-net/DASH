# DASH Flow API HLD

DASH flow abstracts the flow state within DASH. In the quest for achieving cloud services, the control plane can generate a flow state table, performing operations such as adding, deleting, modifying, and obtaining. This design guarantees alignment between the flow entry and flow table across different cloud providers and vendors. We propose APIs to provide a vendor-neutral method for managing flow states, including uniform control of Programmable switches, SmartNICs, and Smart Switches.

DASH flow SAI APIs accommodate multiple flow tables and diverse flow entry operations. Primarily, it negates differences between vendors' implementations, offering universal interfaces. However, it acknowledges performance variations between DASH and SAI deployed on smart devices. For example, it supplies APIs to handle single and batch flows, with the entry count as a limiting factor.

With DASH flow SAI APIs it's possible to achieve varied cloud services requiring flow states. For instance, a cloud load balancer can add a flow decision entry and retrieve the flow entry via DASH flow API. It also lays the groundwork for DASH to provide basic services, such as high availability.

## Terminology

- **Flow**: It represents a single direction of the match-action entry for a transport layer (e.g., TCP, UDP) connection.
- **Flow entry**: Same as flow.
- **Flow Key**: The key that is used to match the packet for finding its flow.
- **Flow State**: The state of the flow, including the packet transformations and all other tracked states, such as TCP, HA, etc.
- **Flow Table**: The table to store a set of flows.

## Model

In the DASH flow abstraction, we model flows as being stored within a flow table and managed through DASH flow SAI APIs.

Upon the arrival of new flows, whether individually or in batches, corresponding flow entries are added to the table. These entries may represent either bidirectional or unidirectional flows. For bidirectional flows, the implementation adds entries for both the original flow and its reverse, linking their reverse flow keys to each other. For unidirectional flows, the current direction is specified. If a reverse flow for a unidirectional flow is created later, the implementation must add reverse keys for both and link them accordingly.

Flows can be modified and removed through the DASH flow SAI API and can also be aged by the hardware.

For more use cases, please refer to [Smart Switch HA HLD](https://github.com/sonic-net/SONiC/blob/master/doc/smart-switch/high-availability/smart-switch-ha-hld.md).

Here are the full DASH flow SAI APIs, and we will introduce their detailed definitions in the following sections.

| API                              | Description                                                  |
| -------------------------------- | :----------------------------------------------------------- |
| create_flow_table                | Create a new flow table                                      |
| remove_flow_table                | Remove a flow table                                          |
| set_flow_table_attribute         | Set the attributes of a flow table                           |
| get_flow_table_attribute         | Obtain the attributes of a flow table                        |
| create_flow_tables               | Create multiple flow tables in bulk                          |
| remove_flow_tables               | Remove multiple flow tables in bulk                          |
| create_flow_entry                | Add a single new entry to a certain flow table               |
| remove_flow_entry                | Remove a single entry in a certain flow table                |
| set_flow_entry_attribute         | Set attributes for a single entry in a certain flow table    |
| get_flow_entry_attribute         | Get attributes of a single entry in a certain flow table     |
| create_flow_entries              | Add multiple entries to a certain flow table in bulk         |
| remove_flow_entries              | Remove multiple entries in a certain flow table in bulk      |
| get_flow_entries_attribute       | Get multiple entries from a certain flow table in bulk       |

```c
typedef struct _sai_dash_flow_api_t
{
    sai_create_flow_entry_fn           create_flow_entry;
    sai_remove_flow_entry_fn           remove_flow_entry;
    sai_set_flow_entry_attribute_fn    set_flow_entry_attribute;
    sai_get_flow_entry_attribute_fn    get_flow_entry_attribute;
    sai_bulk_create_flow_entry_fn      create_flow_entries;
    sai_bulk_remove_flow_entry_fn      remove_flow_entries;
    sai_bulk_get_flow_entry_fn         get_flow_entries_attribute;

    sai_create_flow_table_fn           create_flow_table;
    sai_remove_flow_table_fn           remove_flow_table;
    sai_set_flow_table_attribute_fn    set_flow_table_attribute;
    sai_get_flow_table_attribute_fn    get_flow_table_attribute;
    sai_bulk_object_create_fn          create_flow_tables;
    sai_bulk_object_remove_fn          remove_flow_tables;

} sai_dash_flow_api_t;
```

## Flow Table APIs

```c
typedef enum _sai_flow_table_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_FLOW_TABLE_ATTR_START,

    /**
     * @brief Action flow_table_action parameter TABLE_SIZE
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_TABLE_ATTR_TABLE_SIZE = SAI_FLOW_TABLE_ATTR_START,

    /**
     * @brief Action flow_table_action parameter TABLE_EXPIRE_TIME
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_TABLE_ATTR_TABLE_EXPIRE_TIME,

    /**
     * @brief Action flow_table_action parameter TABLE_VERSION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_TABLE_ATTR_TABLE_VERSION,

    /**
     * @brief Action flow_table_action parameter TABLE_KEY_FLAG
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_TABLE_ATTR_TABLE_KEY_FLAG,

    /**
     * @brief Action flow_table_action parameter TABLE_TCP_TRACK_STATE
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_FLOW_TABLE_ATTR_TABLE_TCP_TRACK_STATE,

    /**
     * @brief Action flow_table_action parameter TABLE_TCP_RESET_ILLEGAL
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_FLOW_TABLE_ATTR_TABLE_TCP_RESET_ILLEGAL,

    /**
     * @brief End of attributes
     */
    SAI_FLOW_TABLE_ATTR_END,

    /** Custom range base value */
    SAI_FLOW_TABLE_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_FLOW_TABLE_ATTR_CUSTOM_RANGE_END,

} sai_flow_table_attr_t;

/**
 * @brief Create dash_flow_flow_table
 *
 * @param[out] flow_table_id Entry id
 * @param[in] switch_id Switch id
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_flow_table_fn)(
        _Out_ sai_object_id_t *flow_table_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove dash_flow_flow_table
 *
 * @param[in] flow_table_id Entry id
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_flow_table_fn)(
        _In_ sai_object_id_t flow_table_id);

/**
 * @brief Set attribute for dash_flow_flow_table
 *
 * @param[in] flow_table_id Entry id
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_flow_table_attribute_fn)(
        _In_ sai_object_id_t flow_table_id,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for dash_flow_flow_table
 *
 * @param[in] flow_table_id Entry id
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_flow_table_attribute_fn)(
        _In_ sai_object_id_t flow_table_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

```

## Flow APIs

### Basic flow APIs

```c

/**
 * @brief Entry for flow_entry
 */
typedef struct _sai_flow_entry_t
{
    /**
     * @brief Switch ID
     *
     * @objects SAI_OBJECT_TYPE_SWITCH
     */
    sai_object_id_t switch_id;

    /**
     * @brief Exact matched key dst_ip
     */
    sai_ip_address_t dst_ip;

    /**
     * @brief Exact matched key src_ip
     */
    sai_ip_address_t src_ip;

    /**
     * @brief Exact matched key protocol
     */
    sai_uint8_t protocol;

    /**
     * @brief Exact matched key src_port
     */
    sai_uint16_t src_port;

    /**
     * @brief Exact matched key dst_port
     */
    sai_uint16_t dst_port;

    /**
     * @brief Exact matched key direction
     */
    sai_uint16_t direction;

    /**
     * @brief Exact matched key eni_addr
     */
    sai_mac_t eni_addr;

} sai_flow_entry_t;

/**
 * @brief Attribute ID for dash_flow_flow_entry
 */
typedef enum _sai_flow_entry_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_FLOW_ENTRY_ATTR_START,

    /**
     * @brief Action flow_entry_action parameter FLOW_TABLE_ID
     *
     * @type sai_object_id_t
     * @flags CREATE_AND_SET
     * @objects SAI_OBJECT_TYPE_FLOW_TABLE
     * @allownull true
     * @default SAI_NULL_OBJECT_ID
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_TABLE_ID = SAI_FLOW_ENTRY_ATTR_START,

    /**
     * @brief Action flow_entry_action parameter FLOW_VERSION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_VERSION,

    /**
     * @brief Action flow_entry_action parameter FLOW_PROTOBUF
     *
     * @type sai_u8_list_t
     * @flags CREATE_AND_SET
     * @default empty
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_PROTOBUF,

    /**
     * @brief Action flow_entry_action parameter FLOW_BIDIRECTIONAL
     *
     * @type bool
     * @flags CREATE_AND_SET
     * @default false
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_BIDIRECTIONAL,

    /**
     * @brief Action flow_entry_action parameter FLOW_DIRECTION
     *
     * @type sai_uint8_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_DIRECTION,

    /**
     * @brief Action flow_entry_action parameter FLOW_REVERSE_KEY
     *
     * @type sai_uint64_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_REVERSE_KEY,

    /**
     * @brief Action flow_entry_action parameter FLOW_VENDOR_METADATA
     *
     * @type sai_u8_list_t
     * @flags CREATE_AND_SET
     * @default empty
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_VENDOR_METADATA,

    /**
     * @brief Action flow_entry_action parameter FLOW_TARGET_SERVER
     *
     * @type sai_flow_entry_target_server_data_t 
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_TARGET_SERVER,

    /**
     * @brief Action flow_entry_action parameter FLOW_ENTRY_FILTER
     *
     * @type sai_flow_entry_filter_data_t 
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_ENTRY_FILTER,

    /**
     * @brief Action flow_entry_action parameter VNI
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_VNI,

    /**
     * @brief Action flow_entry_action parameter DEST_VNET_VNI
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_DEST_VNET_VNI,

    /**
     * @brief Action flow_entry_action parameter UNDERLAY_SIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_UNDERLAY_SIP,

    /**
     * @brief Action flow_entry_action parameter UNDERLAY_DIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_UNDERLAY_DIP,

    /**
     * @brief Action flow_entry_action parameter UNDERLAY_SMAC
     *
     * @type sai_mac_t
     * @flags CREATE_AND_SET
     * @default 0:0:0:0:0:0
     */
    SAI_FLOW_ENTRY_ATTR_UNDERLAY_SMAC,

    /**
     * @brief Action flow_entry_action parameter UNDERLAY_DMAC
     *
     * @type sai_mac_t
     * @flags CREATE_AND_SET
     * @default 0:0:0:0:0:0
     */
    SAI_FLOW_ENTRY_ATTR_UNDERLAY_DMAC,

    /**
     * @brief Action flow_entry_action parameter DASH_ENCAPSULATION
     *
     * @type sai_dash_encapsulation_t
     * @flags CREATE_AND_SET
     * @default SAI_DASH_ENCAPSULATION_INVALID
     */
    SAI_FLOW_ENTRY_ATTR_DASH_ENCAPSULATION,

    /**
     * @brief Action flow_entry_action parameter ORIGINAL_OVERLAY_SIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_SIP,

    /**
     * @brief Action flow_entry_action parameter ORIGINAL_OVERLAY_DIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_DIP,

    /**
     * @brief Action flow_entry_action parameter DEST_MAC
     *
     * @type sai_mac_t
     * @flags CREATE_AND_SET
     * @default 0:0:0:0:0:0
     */
    SAI_FLOW_ENTRY_ATTR_DEST_MAC,

    /**
     * @brief Action flow_entry_action parameter SIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_SIP,

    /**
     * @brief Action flow_entry_action parameter DIP
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_DIP,

    /**
     * @brief Action flow_entry_action parameter SIP_MASK
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_SIP_MASK,

    /**
     * @brief Action flow_entry_action parameter DIP_MASK
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_ATTR_DIP_MASK,

    /**
     * @brief Action flow_entry_action parameter METER_CLASS
     *
     * @type sai_uint16_t
     * @flags CREATE_AND_SET
     * @isvlan false
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_METER_CLASS,

    /**
     * @brief IP address family for resource accounting
     *
     * @type sai_ip_addr_family_t
     * @flags READ_ONLY
     * @isresourcetype true
     */
    SAI_FLOW_ENTRY_ATTR_IP_ADDR_FAMILY,

    /**
     * @brief End of attributes
     */
    SAI_FLOW_ENTRY_ATTR_END,

    /** Custom range base value */
    SAI_FLOW_ENTRY_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_FLOW_ENTRY_ATTR_CUSTOM_RANGE_END,

} sai_flow_entry_attr_t;

/**
 * @brief Create dash_flow_flow_entry
 *
 * @param[in] flow_entry Entry
 * @param[in] attr_count Number of attributes
 * @param[in] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_create_flow_entry_fn)(
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

/**
 * @brief Remove dash_flow_flow_entry
 *
 * @param[in] flow_entry Entry
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_remove_flow_entry_fn)(
        _In_ const sai_flow_entry_t *flow_entry);

/**
 * @brief Set attribute for dash_flow_flow_entry
 *
 * @param[in] flow_entry Entry
 * @param[in] attr Attribute
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_set_flow_entry_attribute_fn)(
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ const sai_attribute_t *attr);

/**
 * @brief Get attribute for dash_flow_flow_entry
 *
 * @param[in] flow_entry Entry
 * @param[in] attr_count Number of attributes
 * @param[inout] attr_list Array of attributes
 *
 * @return #SAI_STATUS_SUCCESS on success Failure status code on error
 */
typedef sai_status_t (*sai_get_flow_entry_attribute_fn)(
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list);

/**
 * @brief Bulk create dash_flow_flow_entry
 *
 * @param[in] object_count Number of objects to create
 * @param[in] flow_entry List of object to create
 * @param[in] attr_count List of attr_count. Caller passes the number
 *    of attribute for each object to create.
 * @param[in] attr_list List of attributes for every object.
 * @param[in] mode Bulk operation error handling mode.
 * @param[out] object_statuses List of status for every object. Caller needs to
 * allocate the buffer
 *
 * @return #SAI_STATUS_SUCCESS on success when all objects are created or
 * #SAI_STATUS_FAILURE when any of the objects fails to create. When there is
 * failure, Caller is expected to go through the list of returned statuses to
 * find out which fails and which succeeds.
 */
typedef sai_status_t (*sai_bulk_create_flow_entry_fn)(
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ const uint32_t *attr_count,
        _In_ const sai_attribute_t **attr_list,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);

/**
 * @brief Bulk remove dash_flow_flow_entry
 *
 * @param[in] object_count Number of objects to remove
 * @param[in] flow_entry List of objects to remove
 * @param[in] mode Bulk operation error handling mode.
 * @param[out] object_statuses List of status for every object. Caller needs to
 * allocate the buffer
 *
 * @return #SAI_STATUS_SUCCESS on success when all objects are removed or
 * #SAI_STATUS_FAILURE when any of the objects fails to remove. When there is
 * failure, Caller is expected to go through the list of returned statuses to
 * find out which fails and which succeeds.
 */
typedef sai_status_t (*sai_bulk_remove_flow_entry_fn)(
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);

```

### Bulk operation

```c
/**
 * @brief Bulk Get Op filter keywords for flow_entry in get_flow_entries_attribute call
 */
typedef enum _sai_flow_entry_bulk_get_filter_t
{
    /** Bulk get filter key word for sai_ip_address_t dst_ip */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DST_IP,

    /** Bulk get filter key word for sai_ip_address_t src_ip */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_SRC_IP,

    /** Bulk get filter key word for sai_uint8_t protocol */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_PROTOCOL,

    /** Bulk get filter key word for sai_uint16_t src_port */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_SRC_PORT,

    /** Bulk get filter key word for sai_uint16_t dst_port */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DST_PORT,

    /** Bulk get filter key word for sai_uint16_t direction */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DIRECTION,

    /** Bulk get filter key word for sai_mac_t eni_addr */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_ENI_ADDR,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_TABLE_ID */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_TABLE_ID,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_VERSION */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_VERSION,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_PROTOBUF */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_PROTOBUF,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_BIDIRECTIONAL */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_BIDIRECTIONAL,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_DIRECTION */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_DIRECTION,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_REVERSE_KEY */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_REVERSE_KEY,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_VENDOR_METADATA */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_VENDOR_METADATA,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_TARGET_SERVER */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_TARGET_SERVER,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_FLOW_ENTRY_FILTER */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_FLOW_ENTRY_FILTER,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_VNI */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_VNI,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_DEST_VNET_VNI */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DEST_VNET_VNI,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_UNDERLAY_SIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_UNDERLAY_SIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_UNDERLAY_DIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_UNDERLAY_DIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_UNDERLAY_SMAC */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_UNDERLAY_SMAC,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_UNDERLAY_DMAC */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_UNDERLAY_DMAC,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_DASH_ENCAPSULATION */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DASH_ENCAPSULATION,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_SIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_ORIGINAL_OVERLAY_SIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_DIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_ORIGINAL_OVERLAY_DIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_DEST_MAC */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DEST_MAC,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_SIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_SIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_DIP */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DIP,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_SIP_MASK */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_SIP_MASK,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_DIP_MASK */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_DIP_MASK,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_METER_CLASS */
    SAI_FLOW_ENTRY_BULK_GET_FILTER_T_METER_CLASS,

} sai_flow_entry_bulk_get_filter_t;

/**
 * @brief Bulk Get Op for flow_entry in get_flow_entries_attribute call
 */
typedef enum _sai_flow_entry_bulk_get_op_t
{
    /** Indicate the last operation of the bulk get */
    SAI_FLOW_ENTRY_BULK_GET_OP_LAST_ITEM,

    /** Operation to compare the value is equal */
    SAI_FLOW_ENTRY_BULK_GET_OP_EQUAL_TO,

    /** Operation to compare the value is greater than */
    SAI_FLOW_ENTRY_BULK_GET_OP_GREATER_THAN,

    /** Operation to compare the value is greater than or equal to */
    SAI_FLOW_ENTRY_BULK_GET_OP_GREATER_THAN_OR_EQUAL_TO,

    /** Operation to compare the value is less than */
    SAI_FLOW_ENTRY_BULK_GET_OP_LESS_THAN,

    /** Operation to compare the value is less than or equal to */
    SAI_FLOW_ENTRY_BULK_GET_OP_LESS_THAN_OR_EQUAL_TO,

} sai_flow_entry_bulk_get_op_t;

typedef struct _sai_flow_entry_target_server_data_t
{
    sai_ip_address_t server_ip;
    sai_uint16_t server_port;
} sai_flow_entry_target_server_data_t;

typedef struct _sai_flow_entry_filter_data_t
{
    sai_flow_entry_bulk_get_filter_t filter;
    sai_flow_entry_bulk_get_op_t op;
    sai_uint64_t value;
} sai_flow_entry_filter_data_t;

/**
 * @brief Bulk create dash_flow_flow_entry
 *
 * @param[in] object_count Number of objects to create
 * @param[in] flow_entry List of object to create
 * @param[in] attr_count List of attr_count. Caller passes the number
 *    of attribute for each object to create.
 * @param[in] attr_list List of attributes for every object.
 * @param[in] mode Bulk operation error handling mode.
 * @param[out] object_statuses List of status for every object. Caller needs to
 * allocate the buffer
 *
 * @return #SAI_STATUS_SUCCESS on success when all objects are created or
 * #SAI_STATUS_FAILURE when any of the objects fails to create. When there is
 * failure, Caller is expected to go through the list of returned statuses to
 * find out which fails and which succeeds.
 */
typedef sai_status_t (*sai_bulk_create_flow_entry_fn)(
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ const uint32_t *attr_count,
        _In_ const sai_attribute_t **attr_list,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);

/**
 * @brief Bulk remove dash_flow_flow_entry
 *
 * @param[in] object_count Number of objects to remove
 * @param[in] flow_entry List of objects to remove
 * @param[in] mode Bulk operation error handling mode.
 * @param[out] object_statuses List of status for every object. Caller needs to
 * allocate the buffer
 *
 * @return #SAI_STATUS_SUCCESS on success when all objects are removed or
 * #SAI_STATUS_FAILURE when any of the objects fails to remove. When there is
 * failure, Caller is expected to go through the list of returned statuses to
 * find out which fails and which succeeds.
 */
typedef sai_status_t (*sai_bulk_remove_flow_entry_fn)(
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);

/**
 * @brief Bulk get dash_flow_flow_entry
 *
 * @param[in] object_count Max number of objects to get
 * @param[in] flow_entry List of object to get
 * @param[in] attr_count List of attr_count. Caller passes the number
 *    of attribute for each object to create.
 * @param[inout] attr_list List of attributes for every object.
 * @param[in] mode Bulk operation error handling mode.
 * @param[out] object_statuses Status for each object.
 *    If the allocated attribute count is not large enough,
 *    set the status to #SAI_STATUS_BUFFER_OVERFLOW.
 *
 * @return #SAI_STATUS_SUCCESS on success when all objects are created or
 * #SAI_STATUS_FAILURE when any of the objects fails to create. When there is
 * failure, Caller is expected to go through the list of returned statuses to
 * find out which fails and which succeeds.
 */
typedef sai_status_t (*sai_bulk_get_flow_entry_fn)(
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ const uint32_t *attr_count,
        _Inout_ sai_attribute_t **attr_list,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);


```

### Protobuf-based flow programming

In addition to the flow state attributes, the flow state can be represented using protobuf. Although the content of both attributes and protobuf may be identical, their applications differ. Attributes enable incremental updates to individual properties, whereas protobuf necessitates a complete update.

```protobuf
syntax = "proto3";

message SaiFlowEntry {
  uint64 flow_table_id = 1;
  uint32 flow_version = 2;
  bytes flow_protobuf = 3;
  bool flow_bidirectional = 4;
  uint32 flow_direction = 5;
  uint64 flow_reverse_key = 6;
  bytes flow_vendor_metadata = 7;
  uint64 flow_target_server = 8;
  uint64 flow_entry_filter = 9;
  uint32 vni = 10;
  uint32 dest_vnet_vni = 11;
  string underlay_sip = 12;
  string underlay_dip = 13;
  string underlay_smac = 14;
  string underlay_dmac = 15;
  DashEncapsulation dash_encapsulation = 16;
  string original_overlay_sip = 17;
  string original_overlay_dip = 18;
  string dest_mac = 19;
  string sip = 20;
  string dip = 21;
  string sip_mask = 22;
  string dip_mask = 23;
  uint32 meter_class = 24;
  IpAddrFamily ip_addr_family = 25;
}
```

## Example

When a service intends to use DASH Flow SAI APIs, it should first establish a flow table via the `create_flow_table()` function. After the table creation, the programmer can add, delete, modify, or retrieve flow entries to/from the table. For instance, when DASH HA needs to perform bulk sync from the active DPU to the standby DPU, it should initially fetch the entry from the active DPU using `get_flow_entries`, then transmit the flow entries to the standby DPU via the control plane. The standby DPU subsequently calls `create_flow_entries()`to add entries to the corresponding flow table. The DPU should have a built-in flow table aging capability, eliminating the need to scan all entries.

This example describes how to create a flow state table, and how to operate flow entries.

### Create Flow Table

```c
duint32_t attr_count = ...; 
sai_attribute_t *attr_list = ...;
sai_object_id_t flow_table_id;

sai_status_t status = create_flow_table(&flow_table_id, switch_id, attr_count, attr_list);
```

### Create Key of a Flow

```c
sai_flow_entry_t flow_entry;
flow_entry.switch_id = 12345;
flow_entry.sip = "10.10.10.10";
flow_entry.dip = "10.10.10.11";
flow_entry.protocol = 6;
flow_entry.src_port = 1234;
flow_entry.dst_port = 80;
flow_entry.direction = 1;
```

#### Create attribute and create the flow entry

```c
SaiDashFlowMetadata flow_metadata = SAI_DASH_FLOW_METADATA__INIT;
flow_metadata.version = 1;
flow_metadata.metering_class = 1001;
...

/* Serialize the protobuf message to bytes */
unsigned len = sai_dash_flow_metadata__get_packed_size(&flow_metadata);
uint8_t *buf = malloc(len);
sai_dash_flow_metadata__pack(&flow_metadata, buf);

uint32_t attr_count = 1;
sai_attribute_t sai_attrs_list[1];
sai_attrs_list[0].id = SAI_FLOW_ENTRY_ATTR_FLOW_PROTOBUF;
sai_attr_list[0].value = buf;

sai_status_t status = create_flow_entry(&flow_entry_example, attr_count, attr_list);

free(buf);
```

#### Add Flow Entries

```c
/* Add multiple flow entries to the table in bulk */
uint32_t flow_count = num_flow_states;
const sai_dash_flow_key_t flow_key[] = ...; 
uint32_t attr_count[] = ...; 
sai_attribute_t *attr_list[] = ...; 
sai_status_t object_statuses[] = ...; 

status = sai_dash_flow_bulk_create_entry(flow_table_id, flow_count, flow_key, attr_count, attr_list, SAI_BULK_OP_ERROR_MODE_IGNORE_ERROR, object_statuses);

```

#### Retrieve Flow Entry

```c
uint32_t attr_count = ...; 
sai_attribute_t attr_list[] = ...;

sai_flow_entry_t flow_entry;
flow_entry.switch_id = 12345;
flow_entry.sip = "10.10.10.10";
flow_entry.dip = "10.10.10.11";
flow_entry.protocol = 6;
flow_entry.src_port = 1234;
flow_entry.dst_port = 80;
flow_entry.direction = 1;

status = get_flow_entry_attribute(flow_entry, attr_count, attr_list);

```

#### Retrieve Flow Entries
Example: Get flow entries via filter all version < 5 and return via GRPC

```c
/* Object_count is set to UINT32_MAX as the exact number of entries in the flow table is unknown in advance when querying and filtering. */
uint32_t object_count = UINT32_MAX

/* Indicates the response should be sent to the GRPC server, with the specified IP and port as 10.10.10.10 and 1234, respectively. */
sai_flow_entry_target_server_data_t target_server;
target_server_data.server_ip = "10.10.10.10";
target_server_data.server_port = 1234;

/* Specifies that the filter operation should select versions less than 5. */
sai_flow_entry_filter_data_t version_filter_op;
version_filter.filter = SAI_FLOW_ENTRY_BULK_GET_FILTER_VERSION; 
version_filter.op = SAI_FLOW_ENTRY_BULK_GET_OP_LESS_THAN;
version_filter.value = 5;

/* Indicates the previous filter was the last one, with no additional attributes following. */
sai_flow_entry_filter_data_t last_filter_op;
last_filter_op.op = SAI_FLOW_ENTRY_BULK_GET_OP_LAST_ITEM;

sai_attribute_t sai_attrs_list[3][2];
sai_attrs_list[0][0].id = SAI_FLOW_ENTRY_ATTR_FLOW_TARGET_SERVER,;
sai_attrs_list[0][0].value = target_server;

sai_attrs_list[0][1].id = SAI_FLOW_ENTRY_ATTR_FLOW_ENTRY_FILTER;
sai_attrs_list[0][1].value = version_filter_op;

sai_attrs_list[0][2].id = SAI_FLOW_ENTRY_ATTR_FLOW_ENTRY_FILTER;
sai_attrs_list[0][2].value = last_filter_op;

status = sai_bulk_get_flow_entry_fn(object_count, flow_entry, attr_count, attr_list, mode, object_statuses);

```

#### Remove flow entry

```c
status = remove_flow_entry(flow_entry);
```

#### Remove flow table

```c
status = remove_flow_table(flow_table_id);
```
