# DASH flow API HLD

DASH flow abstracts the flow state within DASH. In the quest for achieving cloud services, the control plane can generate a flow state table, performing operations such as adding, deleting, modifying, and obtaining. This design guarantees alignment between the flow entry and flow table across different cloud providers and vendors. We propose APIs to provide a vendor-neutral method for managing flow states, including uniform control of Programmable switches, SmartNICs, and Smart Switches.

DASH flow SAI APIs accommodate multiple flow tables and diverse flow entry operations. Primarily, it negates differences between vendors' implementations, offering universal interfaces. However, it acknowledges performance variations between DASH and SAI deployed on smart devices. For example, it supplies APIs to handle single and batch flows, with the entry count as a limiting factor.

With DASH flow SAI APIs it's possible to achieve varied cloud services requiring flow states. For instance, a cloud load balancer can add a flow decision entry and retrieve the flow entry via the data plane. It also lays the groundwork for DASH to provide basic services, such as high availability.

## Terminology

- **Flow**: It represents a single direction of the match-action entry for a transport layer (e.g., TCP, UDP) connection.
- **Flow entry**: Same as flow.
- **Flow Key**: The key that is used to match the packet for finding its flow.
- **Flow State**: The state of the flow, including the packet transformations and all other tracked states, such as TCP, HA, etc.
- **Flow Table**: The table to store a set of flows.

## Model

In the DASH flow abstraction, we model flows as being stored within a flow table and managed through DASH flow SAI APIs.

Each table should be associated with an ENI. [TO-DO] Discussion needed.

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
| get_flow_entries                 | Get multiple entries from a certain flow table in bulk       |

```c
typedef struct _sai_dash_flow_api_t
{
    sai_create_flow_entry_fn           create_flow_entry;
    sai_remove_flow_entry_fn           remove_flow_entry;
    sai_set_flow_entry_attribute_fn    set_flow_entry_attribute;
    sai_get_flow_entry_attribute_fn    get_flow_entry_attribute;
    sai_bulk_create_flow_entry_fn      create_flow_entries;
    sai_bulk_remove_flow_entry_fn      remove_flow_entries;
    sai_bulk_get_flow_entry_fn         get_flow_entries;

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
/**
 * @brief Attribute ID for dash_flow_flow_table
 */
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
```

## Flow APIs

### Basic flow APIs

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
     * @brief Exact matched key dip
     */
    sai_ip_address_t dip;

    /**
     * @brief Exact matched key sip
     */
    sai_ip_address_t sip;

    /**
     * @brief Exact matched key protocol
     */
    sai_uint16_t protocol;

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
    sai_uint32_t direction;

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
     * @brief Action flow_entry_action parameter FLOW_VERSION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_VERSION = SAI_FLOW_ENTRY_ATTR_START,

    /**
     * @brief Action flow_entry_action parameter FLOW_PROTOBUF
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_PROTOBUF,

    /**
     * @brief Action flow_entry_action parameter FLOW_BIDIRECTIONAL
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_BIDIRECTIONAL,

    /**
     * @brief Action flow_entry_action parameter FLOW_DIRECTION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_DIRECTION,

    /**
     * @brief Action flow_entry_action parameter FLOW_REVERSE_KEY
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_REVERSE_KEY,

    /**
     * @brief Action flow_entry_action parameter FLOW_POLICY_RESULT
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_POLICY_RESULT,

    /**
     * @brief Action flow_entry_action parameter FLOW_DEST_PA
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_DEST_PA,

    /**
     * @brief Action flow_entry_action parameter FLOW_METERING_CLASS
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_METERING_CLASS,

    /**
     * @brief Action flow_entry_action parameter FLOW_REWRITE_INFO
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_REWRITE_INFO,

    /**
     * @brief Action flow_entry_action parameter FLOW_VENDOR_METADATA
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_ATTR_FLOW_VENDOR_METADATA,

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


```

### Bulk operation

```c
/**
 * @brief Attribute ID (attributes to filter) for get_flow_entries
 */
typedef enum _sai_flow_entry_bulk_get_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_START,

    /**
     * @brief Exact matched key dip
     *
     * @type sai_ip_address_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_DIP = SAI_FLOW_ENTRY_BULK_GET_ATTR_START,

    /**
     * @brief Exact matched key sip
     *
     * @type sai_ip_address_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_SIP,

    /**
     * @brief Exact matched key protocol
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @isvlan false
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_PROTOCOL,

    /**
     * @brief Exact matched key src_port
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @isvlan false
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_SRC_PORT,

    /**
     * @brief Exact matched key dst_port
     *
     * @type sai_uint16_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     * @isvlan false
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_DST_PORT,

    /**
     * @brief Exact matched key direction
     *
     * @type sai_uint32_t
     * @flags MANDATORY_ON_CREATE | CREATE_ONLY
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_DIRECTION,

    /**
     * @brief Action flow_entry_action parameter FLOW_VERSION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_VERSION,

    /**
     * @brief Action flow_entry_action parameter FLOW_PROTOBUF
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_PROTOBUF,

    /**
     * @brief Action flow_entry_action parameter FLOW_BIDIRECTIONAL
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_BIDIRECTIONAL,

    /**
     * @brief Action flow_entry_action parameter FLOW_DIRECTION
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_DIRECTION,

    /**
     * @brief Action flow_entry_action parameter FLOW_REVERSE_KEY
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_REVERSE_KEY,

    /**
     * @brief Action flow_entry_action parameter FLOW_POLICY_RESULT
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_POLICY_RESULT,

    /**
     * @brief Action flow_entry_action parameter FLOW_DEST_PA
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_DEST_PA,

    /**
     * @brief Action flow_entry_action parameter FLOW_METERING_CLASS
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_METERING_CLASS,

    /**
     * @brief Action flow_entry_action parameter FLOW_REWRITE_INFO
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_REWRITE_INFO,

    /**
     * @brief Action flow_entry_action parameter FLOW_VENDOR_METADATA
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_VENDOR_METADATA,

    /**
     * @brief IP address family for resource accounting
     *
     * @type sai_ip_addr_family_t
     * @flags READ_ONLY
     * @isresourcetype true
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_IP_ADDR_FAMILY,

    /**
     * @brief End of attributes
     */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_END,

    /** Custom range base value */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_FLOW_ENTRY_BULK_GET_ATTR_CUSTOM_RANGE_END,

} sai_flow_entry_bulk_get_attr_t;

/**
 * @brief Attribute ID (operation) for get_flow_entries;
 */
typedef enum _sai_flow_entry_bulk_get_op_attr_t
{
    /**
     * @brief Start of attributes
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_START,

    /**
     * @brief Action operation parameter for normal return
     *
     * @type sai_uint32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_NORMAL_RETURN,

    /**
     * @brief Action operation parameter for GRPC return (server IP address)
     *
     * @type sai_ip_address_t
     * @flags CREATE_AND_SET
     * @default 0.0.0.0
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_GRPC_SERVER_IP,

    /**
     * @brief Action operation parameter for GRPC return (server port)
     *
     * @type sai_uint16_t
     * @flags CREATE_AND_SET
     * @isvlan false
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_GRPC_SERVER_PORT,

    /**
     * @brief Action operation parameter for get filter operator
     *
     * @type sai_uint16_t
     * @flags CREATE_AND_SET
     * @isvlan false
     * @default 0
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_FILTER_OP,

    /**
     * @brief End of attributes
     */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_END,

    /** Custom range base value */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_CUSTOM_RANGE_START = 0x10000000,

    /** End of custom range base */
    SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_CUSTOM_RANGE_END,

} sai_flow_entry_bulk_get_op_attr_t;

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
 * @param[inout] attr_count List of attr_count. Caller passes the number
 *    of attribute for each object to create.
 * @param[inout] attr_list List of attributes for every object.
 * @param[inout] object_statuses Status for each object.
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
        _Inout_ uint32_t *attr_count,
        _Inout_ sai_attribute_t **attr_list,
        _Inout_ sai_status_t *object_statuses);

```

### Protobuf-based flow programming

In addition to the flow state attributes, the flow state can be represented using protobuf. Although the content of both attributes and protobuf may be identical, their applications differ. Attributes enable incremental updates to individual properties, whereas protobuf necessitates a complete update.

```protobuf
syntax = "proto3";

message SaiDashFlowMetadata {
    uint32 version = 1;
    SaiDashPolicyResult policy_result = 2;
    /* Destination PA IP address */
    string dest_pa = 3; 
    uint64 metering_class = 4;
    uint64 metering_class2 = 5;
    SaiDashHaRewriteInfo rewrite_info = 6;
    /* Vendor specific metadata */
    bytes vendor_metadata = 7; 
}

enum SaiDashPolicyResult {
    SAI_DASH_POLICY_RESULT_NONE = 0;
    SAI_DASH_POLICY_RESULT_ALLOW = 1;
    SAI_DASH_POLICY_RESULT_DENY = 2;
}

enum SaiDashHaRewriteFlags {
    SAI_DASH_REWRITE_NONE = 0; /* Default, unused value */
    SAI_DASH_REWRITE_IFLOW_DMAC = 1;
    SAI_DASH_REWRITE_IFLOW_SIP = 2;
    SAI_DASH_REWRITE_IFLOW_SPORT = 4;
    SAI_DASH_REWRITE_IFLOW_VNI = 8;
    SAI_DASH_REWRITE_RFLOW_SIP = 16;
    SAI_DASH_REWRITE_RFLOW_DIP = 32;
    SAI_DASH_REWRITE_RFLOW_DPORT = 64;
    SAI_DASH_REWRITE_RFLOW_SPORT = 128;
    SAI_DASH_REWRITE_RFLOW_VNI = 256;
}

message SaiDashHaRewriteInfo {
    /* Bitmap of SaiDashHaRewriteFlags */
    uint64 rewrite_flags = 1; 
    /* Initiator Flow DMAC */
    string iflow_dmac = 2; 
    /* Initiator Flow Source IP address */
    string iflow_sip = 3; 
    /* Initiator Flow L4 Source Port */
    uint32 iflow_sport = 4; 
    /* Initiator Flow VNID */
    uint32 iflow_vni = 5; 
    /* Reverse Flow Source IP address */
    string rflow_sip = 6; 
    /* Reverse Flow Destination IP address */
    string rflow_dip = 7; 
    /* Reverse Flow Destination Port */
    uint32 rflow_dport = 8;
    /* Reverse Flow Source Port */
    uint32 rflow_sport = 9; 
    /* Reverse Flow VNID */
    uint32 rflow_vni = 10; 
}
```

## Example

When a service intends to use DASH Flow SAI APIs, it should first establish a flow table via the `create_flow_table()` function. After the table creation, the programmer can add, delete, modify, or retrieve flow entries to/from the table. For instance, when DASH HA needs to perform bulk sync from the active DPU to the standby DPU, it should initially fetch the entry from the active DPU using `get_flow_entries`, then transmit the flow entries to the standby DPU via the control plane. The standby DPU subsequently calls `create_flow_entries()`to add entries to the corresponding flow table. The DPU should have a built-in flow table aging capability, eliminating the need to scan all entries.

This example describes how to create a flow state table, and how to operate flow entries.

### Create Flow Table

```c
/* Attributes for the flow table */
uint32_t attr_count = ...; // Specify the number of attributes
sai_attribute_t *attr_list = ...; // Provide the specific array of attributes

/* Create a new flow table */
sai_status_t status = create_flow_table(&flow_table_id, switch_id, attr_count, attr_list);
if (status != SAI_STATUS_SUCCESS) {
    /* handle the error */
}
```

### Create Key

```c
sai_flow_entry_t flow_entry_example = {
    .switch_id = 12345, // Example switch ID
    .dip = {
        .addr_family = SAI_IP_ADDR_FAMILY_IPV4,
        .addr.ip4 = htonl(0xC0A80101) // Destination IP address 192.168.1.1
    },
    .sip = {
        .addr_family = SAI_IP_ADDR_FAMILY_IPV4,
        .addr.ip4 = htonl(0xC0A80102) // Source IP address 192.168.1.2
    },
    .protocol = 6,
    .src_port = htons(1234),
    .dst_port = htons(80),
    .direction = 1,
};
```

#### Create attribute and create the flow entry

```c
/* Initialize the SAI_FLOW_STATE_ATTR_METADATA_PROTOBUF attribute */
SaiDashFlowMetadata flow_metadata = SAI_DASH_FLOW_METADATA__INIT;

/* Set properties for the flow metadata */
flow_metadata.version = 1;
flow_metadata.policy_result = SAI_DASH_POLICY_RESULT__SAI_DASH_POLICY_RESULT_ALLOW;
flow_metadata.dest_pa = "192.168.1.1";
flow_metadata.metering_class = 1001;

/* Initialize and set properties for the rewrite info */
SaiDashHaRewriteInfo rewrite_info = SAI_DASH_REWRITE_INFO__INIT;
rewrite_info.rewrite_flags = SAI_DASH_REWRITE_FLAGS__SAI_DASH_REWRITE_IFLOW_DMAC |
                             SAI_DASH_REWRITE_FLAGS__SAI_DASH_REWRITE_IFLOW_SIP;
rewrite_info.iflow_dmac = "AA:BB:CC:DD:EE:FF";
rewrite_info.iflow_sip = "10.0.0.1";
rewrite_info.iflow_sport = 12345;
rewrite_info.iflow_vni = 1002;

/* Assign the rewrite info to the flow metadata */
flow_metadata.rewrite_info = &rewrite_info;

/* Serialize the protobuf message to bytes */
unsigned len = sai_dash_flow_metadata__get_packed_size(&flow_metadata);
uint8_t *buf = malloc(len);
sai_dash_flow_metadata__pack(&flow_metadata, buf);

sai_attribute_t sai_attrs_list[1];
sai_attrs_list[0].id = SAI_FLOW_STATE_ATTR_METADATA_PROTOBUF;
sai_attr_list[0].value = buf;

sai_status_t status = create_flow_entry(&flow_entry_example, 1, attr_list);

if (status == SAI_STATUS_SUCCESS) {
    // Success processing
} else {
    // Error handling
}

/* Free the allocated buffer */
free(buf);
```

#### Add Flow Entries

```c
/* Add multiple flow entries to the table in bulk */
uint32_t flow_count = num_flow_states;
const sai_dash_flow_key_t flow_key[] = ...; // Provide the specific array of flow keys
uint32_t attr_count[] = ...; // Specify the number of attributes for each flow
sai_attribute_t *attr_list[] = ...; // Provide the specific arrays of attributes for each flow
sai_status_t object_statuses[] = ...; // Buffer to store statuses for each flow

status = sai_dash_flow_bulk_create_entry(flow_table_id, flow_count, flow_key, attr_count, attr_list, SAI_BULK_OP_ERROR_MODE_IGNORE_ERROR, object_statuses);
if (status != SAI_STATUS_SUCCESS) {
    /* handle error */
}

```

#### Retrieve Flow Entry

```c
sai_flow_entry_t flow_entry_example = {
    .switch_id = 12345, // Example switch ID
    .dip = {
        .addr_family = SAI_IP_ADDR_FAMILY_IPV4,
        .addr.ip4 = htonl(0xC0A80101) // Destination IP address 192.168.1.1
    },
    .sip = {
        .addr_family = SAI_IP_ADDR_FAMILY_IPV4,
        .addr.ip4 = htonl(0xC0A80102) // Source IP address 192.168.1.2
    },
    .protocol = 6,
    .src_port = htons(1234),
    .dst_port = htons(80),
    .direction = 1,
};
/* allocate the attributes here */

status = get_flow_entry_attribute(flow_entry, attr_count, attr_list);
if (status != SAI_STATUS_SUCCESS) {
    /* handle error */
}
```

#### Retrieve Flow Entries

Example: Get all version < 5 and return via GRPC

```c
uint32_t object_count = INT_MAX

/* Allocate object_statuses and attr_count */
sai_attribute_t sai_attrs_list[3][2];
sai_attrs_list[0][0].id = SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_FILTER_OP;
sai_attrs_list[0][0].value = SAI_DASH_BULK_GET_FILTER_OP_LESS_THAN;
sai_attrs_list[0][1].id = SAI_FLOW_ENTRY_BULK_GET_ATTR_FLOW_VERSION;
sai_attrs_list[0][1].value = 5;

sai_attrs_list[1][0].id = SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_GRPC_SERVER_IP;
sai_attrs_list[1][0].value = "10.10.10.10";
sai_attrs_list[1][1].id = SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_GRPC_SERVER_PORT;
sai_attrs_list[1][1].value = "1234";

sai_attrs_list[2][0].id = SAI_FLOW_ENTRY_BULK_GET_OP_ATTR_END;
sai_attrs_list[2][0].value = true;

status = sai_bulk_get_flow_entry_fn(object_count, attr_count, attr_list, object_statuses);

```

#### Remove flow entry

```c
/* Remove the flow entry from the table */
status = remove_flow_entry(flow_entry);
if (status != SAI_STATUS_SUCCESS) {
    /* handle error */
}

```

#### Remove flow table

```c
/* Finally, remove the flow table */
status = remove_flow_table(flow_table_id);
if (status != SAI_STATUS_SUCCESS) {
    /* handle error */
}
```
