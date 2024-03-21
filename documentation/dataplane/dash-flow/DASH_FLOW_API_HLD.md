# DASH Flow API HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/20/2024 | Zhixiong Niu | Initial version |

[TOC]

## Introduction

DASH supports the storage and processing of millions of flow states. To further enhance the DASH flow processing capabilities, we offer a DASH flow abstraction layer to facilitate vendor-neutral flow management. This layer ensures uniform control over flows across programmable switches, DPUs, and smart switches. The DASH flow abstraction provides concepts of flow tables and flow entries, as well as APIs to manage the flows. Cloud providers can build their services on top of the DASH flow abstraction layer. For example, a cloud load balancer can add a flow decision entry and retrieve it via the DASH flow API. This also lays the foundation for DASH to offer basic services, such as high availability.

[To-do] What flow api can do? E.g. Redirect, re-simluate, dataplane app;  update target Senairos Different Senarios: 

## Terminology

- **Flow**: It represents a single direction of the match-action entry for a connection.
- **Flow entry**: Same as flow.
- **Flow Key**: The key that is used to match the packet for finding its flow.
- **Flow State**: The state of the flow, including the packet transformations and all other tracked states, such as TCP, HA, etc.
- **Flow Table**: The table to store a set of flows.

## Model

In the DASH flow abstraction, we model flows as being stored within a flow table and managed through DASH flow SAI APIs.

[To-Do] How to store? Figure ? Not bind with ENI, draw.io, Flow-entry, Flow-key, Flow state, Flow Table Relationship

Upon the arrival of new flows, whether individually or in batches, corresponding flow entries are added to the table. These entries may represent either bidirectional or unidirectional flows. For bidirectional flows, the implementation adds entries for both the original flow and its reverse, linking their reverse flow keys to each other. For unidirectional flows, the current direction is specified. If a reverse flow for a unidirectional flow is created later, the implementation must add reverse keys for both and link them accordingly.

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

    SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL = 1 << 0,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_IP = 1 << 1,

    SAI_DASH_FLOW_ENABLED_KEY_DST_IP = 1 << 2,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT = 1 << 3,

    SAI_DASH_FLOW_ENABLED_KEY_DST_PORT = 1 << 4,

} sai_dash_flow_enabled_key_t;
```

## Flow APIs

### Basic flow APIs

The flow_entry APIs are defined as follows:

| API                        | Description                                               |
| -------------------------- | :-------------------------------------------------------- |
| create_flow_entry          | Add a single new entry to a certain flow table            |
| remove_flow_entry          | Remove a single entry in a certain flow table             |
| set_flow_entry_attribute   | Set attributes for a single entry in a certain flow table |
| get_flow_entry_attribute   | Get attributes of a single entry in a certain flow table  |
| create_flow_entries        | Add multiple entries to a certain flow table in bulk      |
| remove_flow_entries        | Remove multiple entries in a certain flow table in bulk   |
| get_flow_entries_attribute | Get multiple entries from a certain flow table in bulk    |

### Keys of flow entry

The keys for a flow entry are defined as follows:

Please note that there is an attribute in the *flow_table* that can specify which of the following keys are enabled. If a key is not enabled, it will not be used in match and action.

The *flow_table_id* is used to designate the flow table for the flow only, which is not used in match and action.

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
     * @brief Exact matched key flow_table_id
     *
     * @objects SAI_OBJECT_TYPE_FLOW_TABLE
     */
    sai_object_id_t flow_table_id;

    /**
     * @brief Exact matched key ip_protocol
     */
    sai_uint8_t ip_protocol;

    /**
     * @brief Exact matched key src_ip_addr
     */
    sai_ip_address_t src_ip_addr;

    /**
     * @brief Exact matched key dst_ip_addr
     */
    sai_ip_address_t dst_ip_addr;

    /**
     * @brief Exact matched key src_l4_port
     */
    sai_uint16_t src_l4_port;

    /**
     * @brief Exact matched key dst_l4_port
     */
    sai_uint16_t dst_l4_port;

} sai_flow_entry_t;
```

### Attributes of flow entry

The attributes of the flow entry can be divided into different categories. Please see below for further details.

#### Flow basic metadata

These are the basic attributes of flow entry.

| Attribute name                       | Type                     | Description                                                  |
| ------------------------------------ | ------------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_VERSION          | `sai_uint32_t`           | Version of the flow entry                                    |
| SAI_FLOW_ENTRY_ATTR_DASH_DIRECTION   | `sai_dash_direction_t`   | Direction of the DASH flow                                   |
| SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION | `sai_dash_flow_action_t` | Action to be applied on the flow                             |
| SAI_FLOW_ENTRY_ATTR_METER_CLASS      | `sai_uint16_t`           | Meter class for flow entry, used for traffic metering and policing. |

#### Reverse flow key

When configuring a flow_entry, it can be specified whether it is unidirectional or bidirectional. If it is bidirectional, it can be designated as a reverse flow key, allowing for the rapid identification of the corresponding reverse flow. Of course, if a flow entry is initially established as unidirectional, its reverse flow can also be set up later, utilizing these attributes to link them together.

| Attribute name                            | Type               | Description                                 |
| ----------------------------------------- | ------------------ | ------------------------------------------- |
| SAI_FLOW_ENTRY_ATTR_IS_BIDIRECTIONAL_FLOW | `bool`             | Indicates if the flow is bidirectional      |
| SAI_FLOW_ENTRY_ATTR_REVERSE_IP_PROTOCOL   | `sai_uint8_t`      | IP protocol number for the reverse flow     |
| SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR       | `sai_ip_address_t` | Source IP address for the reverse flow      |
| SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR       | `sai_ip_address_t` | Destination IP address for the reverse flow |
| SAI_FLOW_ENTRY_ATTR_REVERSE_SRC_L4_PORT   | `sai_uint16_t`     | L4 source port for the reverse flow         |
| SAI_FLOW_ENTRY_ATTR_REVERSE_DST_L4_PORT   | `sai_uint16_t`     | L4 destination port for the reverse flow    |

#### Flow encap

These are the related attributes of flow encapsulation.

| Attribute name                         | Type                       | Description                                     |
| -------------------------------------- | -------------------------- | ----------------------------------------------- |
| SAI_FLOW_ENTRY_ATTR_DEST_VNET_VNI      | `sai_uint32_t`             | Destination VNI                                 |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY_SIP       | `sai_uint32_t`             | Source IP address in the underlay network       |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY_DIP       | `sai_uint32_t`             | Destination IP address in the underlay network  |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY_SMAC      | `sai_mac_t`                | Source MAC address in the underlay network      |
| SAI_FLOW_ENTRY_ATTR_UNDERLAY_DMAC      | `sai_mac_t`                | Destination MAC address in the underlay network |
| SAI_FLOW_ENTRY_ATTR_DASH_ENCAPSULATION | `sai_dash_encapsulation_t` | Encapsulation method for DASH traffic           |
|                                        |                            |                                                 |
|                                        |                            |                                                 |

#### Flow rewrite

These are the related attributes of flow rewrite.

| Attribute name               | Type               | Description                                                  |
| ---------------------------- | ------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_IS_IPV6  | `bool`             | Indicates whether the flow is IPv6 (true) or IPv4 (false).   |
| SAI_FLOW_ENTRY_ATTR_D_MAC    | `sai_mac_t`        | Destination MAC address for the flow entry.                  |
| SAI_FLOW_ENTRY_ATTR_SIP      | `sai_ip_address_t` | Source IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_DIP      | `sai_ip_address_t` | Destination IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_SIP_MASK | `sai_ip_address_t` | Subnet mask for the source IP address.                       |
| SAI_FLOW_ENTRY_ATTR_DIP_MASK | `sai_ip_address_t` | Subnet mask for the destination IP address.                  |

#### Flow bulk filter and get

Compared to the generic bulk_get function, in the flow API, when using bulk get, filters can be added to obtain the desired flow entries. This is primarily because DASH supports millions of flows, and in most cases, it is not feasible to retrieve all flows with a single bulk get. Filters must be used to obtain only the necessary flows. Additionally, the flow entry bulk get supports returning results to a specified server and port using GRPC. Compared to direct returns, using GRPC for the return can enhance the efficiency of bulk get responses.

Please note, the flow bulk get function is named `get_flow_entries_attribute`.

```c
typedef sai_status_t get_flow_entries_attribute (
        _In_ uint32_t object_count,
        _In_ const sai_flow_entry_t *flow_entry,
        _In_ const uint32_t *attr_count,
        _Inout_ sai_attribute_t **attr_list,
        _In_ sai_bulk_op_error_mode_t mode,
        _Out_ sai_status_t *object_statuses);
```

Here are the attributes for flow entry bulk get.

| Attribute name                                     | Type                                   | Description                                                  |
| -------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP             | `sai_bulk_get_filter_op_t`             | Specifies the filter operation for bulk get operations       |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY | `sai_bulk_get_flow_entry_filter_key_t` | Defines the filter key for bulk get operations               |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_INT      | `sai_uint64_t`                         | Integer filter value for bulk get operations, facilitating specific attribute filtering. |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_IP       | `sai_ip_address_t`                     | IP address filter value for bulk get operations, used for filtering based on IP criteria. |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_IP      | `sai_ip_address_t`                     | Target GRPC server IP address for bulk get operations, specifying the server for data retrieval. |
| SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_PORT    | `sai_uint16_t`                         | Target GRPC server port for bulk get operations, indicating the server port for data retrieval. |

```c
typedef enum _sai_bulk_get_filter_op_t
{
    /** Indicate the last operation of the bulk get */
    SAI_BULK_GET_FILTER_OP_END_OF_LIST,

    /** Operation to compare the value is equal */
    SAI_BULK_GET_FILTER_OP_EQUAL_TO,

    /** Operation to compare the value is greater than */
    SAI_BULK_GET_FILTER_OP_GREATER_THAN,

    /** Operation to compare the value is greater than or equal to */
    SAI_BULK_GET_FILTER_OP_GREATER_THAN_OR_EQUAL_TO,

    /** Operation to compare the value is less than */
    SAI_BULK_GET_FILTER_OP_LESS_THAN,

    /** Operation to compare the value is less than or equal to */
    SAI_BULK_GET_FILTER_OP_LESS_THAN_OR_EQUAL_TO,

} sai_bulk_get_filter_op_t;
```

```c
typedef enum _sai_bulk_get_flow_entry_filter_key_t
{
    /** Bulk get filter key word for sai_object_id_t flow_table_id */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_FLOW_TABLE_ID,

    /** Bulk get filter key word for sai_uint8_t ip_protocol */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_IP_PROTOCOL,

    /** Bulk get filter key word for sai_ip_address_t src_ip_addr */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_SRC_IP_ADDR,

    /** Bulk get filter key word for sai_ip_address_t dst_ip_addr */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_DST_IP_ADDR,

    /** Bulk get filter key word for sai_uint16_t src_l4_port */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_SRC_L4_PORT,

    /** Bulk get filter key word for sai_uint16_t dst_l4_port */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_DST_L4_PORT,

    /** Bulk get filter key word for SAI_FLOW_ENTRY_ATTR_VERSION */
    SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_VERSION,

} sai_bulk_get_flow_entry_filter_key_t;

```

Its declaration is similar to that of the generic bulk get and it can support using filters or returning data via GRPC must adhere to the following requirements in different senarios.

- **Without both filter and GRPC**

  Consistent with the standard bulk get, it is necessary to pre-provide the `flow_entry` count and `flow entry`, with memory allocation for the corresponding `attr_count` and `attr_list` allocated in advance. Additionally, it is necessary to explicitly indicate that there are no query conditions by setting SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP to SAI_BULK_GET_FILTER_OP_END_OF_LIST in the first ATTR_LIST.

  Below is an example of an input attr_list to claim there is no filter:

| attr_list [x, y] sai_attr_id_t: sai_attribute_value_t | y = 0                                                        |
|-----------------------------------------------------------|--------------------------------------------------------------|
| x = 0                                                     | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: SAI_BULK_GET_FILTER_OP_END_OF_LIST |

- **With filter**

  The `flow_entry` count represents the maximum number of flow entries desired, and space for the flow entries, attr_count, and attr_list should be allocated in advance.

  For the filter conditions, they should be passed in using `attr_count` and `attr_lis`t. Since `attr_list` is two-dimensional, each row represents a query condition, consisting of SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY, SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP, SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]. Different rows will undergo AND operations. The last row must end with a standalone SAI_BULK_GET_FILTER_OP_END_OF_LIST.

  Below is an example of an input attr_list for a filter:

| attr_list [x, y] sai_attr_id_t: sai_attribute_value_t | y = 0 | y = 1 | y = 2 |
|-------------------------------------------------------|--------|--------|--------|
| x = 0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY: key_attribute_value0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: op_attribute_value0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]: filter_value_attribute_value0 |
| x = 1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY: key_attribute_value1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: op_attribute_value1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]: filter_value_attribute_value1 |
| x = 2 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: SAI_BULK_GET_FILTER_OP_END_OF_LIST | | |

- **With GRPC**

  If you wish to use GRPC, the GRPC IP address and port should be specified in the attr_list (SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_IP, SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_PORT).

  Below is an example of an input attr_list for a GRPC return:

| attr_list [x, y] sai_attr_id_t: sai_attribute_value_t | y = 0                                                        | y = 1                                                        |
|------------------------------------------------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| x = 0                                                      | SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_IP: server_ip_value | SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_PORT: server_port_value |
| x = 1                                                      | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: SAI_BULK_GET_FILTER_OP_END_OF_LIST |                                                              |

- **With both filter and GRPC**

  There is no need to allocate the memory in advance.

  For the filter conditions, they should be passed in using `attr_count` and `attr_list`. Since `attr_list` is two-dimensional, each row represents a query condition, consisting of SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY, SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP, SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]. Different rows will undergo AND operations. The last row must end with a standalone SAI_BULK_GET_FILTER_OP_END_OF_LIST.

  If you wish to use GRPC, the GRPC IP address and port should be specified in the attr_list (SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_IP, SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_PORT).

  Below is an example of an input attr_list for a GRPC return with filter:

| attr_list [x, y] sai_attr_id_t: sai_attribute_value_t | y = 0 | y = 1 | y = 2 |
|------------------------------------------------------------|-------|-------|-------|
| x = 0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY: key_attribute_value0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: op_attribute_value0 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]: filter_value_attribute_value0 |
| x = 1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY: key_attribute_value1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: op_attribute_value1 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_[INT, IP]: filter_value_attribute_value1 |
| x = 2 | SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_IP: server_ip_value | SAI_FLOW_ENTRY_ATTR_BULK_GET_TARGET_SERVER_PORT: server_port_value |       |
| x = 3 | SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP: SAI_BULK_GET_FILTER_OP_END_OF_LIST |       |       |

#### Extra flow metadata

Here are some extra metadata for different purposes.

| Attribute name                      | Type            | Description                                                  |
| ----------------------------------- | --------------- | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_VENDOR_METADATA | `sai_u8_list_t` | Vendor-specific metadata that can be attached to the flow entry for custom processing. |
| SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB    | `sai_u8_list_t` | The flow data protocol buffer enables high-efficiency creation, retrieval, and communication for a flow entry. |

### Protobuf-based flow programming

In addition to the flow state attributes, the flow state can be represented using protobuf for high-efficiency. The attribute of the flow entry is SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB.

Although the content of both attributes and protobuf may be identical, their applications differ. Attributes enable incremental updates to individual properties, whereas protobuf necessitates a complete update.

```protobuf
syntax = "proto3";

message SaiFlowEntry {
  uint64 flow_table_id = 1;
  uint32 version = 2; // SAI_FLOW_ENTRY_ATTR_VERSION
  DashEncapsulation dash_flow_action = 3; // SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION combined with dash_encapsulation for simplicity
  uint32 meter_class = 4; // SAI_FLOW_ENTRY_ATTR_METER_CLASS
  bool is_bidirectional_flow = 5; // SAI_FLOW_ENTRY_ATTR_IS_BIDIRECTIONAL_FLOW
  uint8 reverse_ip_protocol = 6; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_PROTOCOL
  string reverse_src_ip_addr = 7; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR for source
  string reverse_dst_ip_addr = 8; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR for destination
  uint32 reverse_src_l4_port = 9; // SAI_FLOW_ENTRY_ATTR_REVERSE_SRC_L4_PORT
  uint32 reverse_dst_l4_port = 10; // SAI_FLOW_ENTRY_ATTR_REVERSE_DST_L4_PORT
  uint32 dest_vnet_vni = 11; // SAI_FLOW_ENTRY_ATTR_DEST_VNET_VNI
  string underlay_sip = 12; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_SIP
  string underlay_dip = 13; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_DIP
  string underlay_smac = 14; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_SMAC
  string underlay_dmac = 15; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_DMAC
  string original_overlay_sip = 16; // SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_SIP
  string original_overlay_dip = 17; // SAI_FLOW_ENTRY_ATTR_ORIGINAL_OVERLAY_DIP
  bool is_ipv6 = 18; // SAI_FLOW_ENTRY_ATTR_IS_IPV6
  string d_mac = 19; // SAI_FLOW_ENTRY_ATTR_D_MAC
  string sip = 20; // SAI_FLOW_ENTRY_ATTR_SIP
  string dip = 21; // SAI_FLOW_ENTRY_ATTR_DIP
  string sip_mask = 22; // SAI_FLOW_ENTRY_ATTR_SIP_MASK
  string dip_mask = 23; // SAI_FLOW_ENTRY_ATTR_DIP_MASK
}
```

## Examples

When a service intends to use DASH Flow SAI APIs, it should first establish a flow table via the `create_flow_table()` function. After the table creation, the programmer can add, delete, modify, or retrieve flow entries to/from the table. For instance, when DASH HA needs to perform bulk sync from the active DPU to the standby DPU, it should initially fetch the entry from the active DPU using `get_flow_entries`, then transmit the flow entries to the standby DPU via the control plane. The standby DPU subsequently calls `create_flow_entries()`to add entries to the corresponding flow table.

These examples describe how to create a flow state table, and how to operate flow entries.

### Create Flow Table

```c
duint32_t attr_count = 3; 
sai_attribute_t attr_list[3];
attr_list[0].id = SAI_FLOW_TABLE_ATTR_DASH_FLOW_ENABLED_KEY;
attr_list[0].value = SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL | 
                         SAI_DASH_FLOW_ENABLED_KEY_SRC_IP | 
                         SAI_DASH_FLOW_ENABLED_KEY_DST_IP | 
                         SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT | 
                         SAI_DASH_FLOW_ENABLED_KEY_DST_PORT;
...  
sai_object_id_t flow_table_id;

sai_status_t status = create_flow_table(&flow_table_id, switch_id, attr_count, attr_list);
```

### Create Key of a Flow entry

```c

sai_flow_entry_t flow_entry;

flow_entry.flow_table_id = 0x123456789abc; /* Not a key, only indicate its table id */
flow_entry.ip_protocol = 6;
flow_entry.src_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip_addr.addr.ip4);
flow_entry.dst_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip_addr.addr.ip4);
flow_entry.src_l4_port = 12345;
flow_entry.dst_l4_port = 80;

```

### Create attribute and flow entry

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

### Add Flow Entries

```c
/* Add multiple flow entries to the table in bulk */
uint32_t flow_count = num_flow_states;
const sai_dash_flow_key_t flow_key[] = ...; 
uint32_t attr_count[] = ...; 
sai_attribute_t *attr_list[] = ...; 
sai_status_t object_statuses[] = ...; 

status = create_flow_entries(flow_table_id, flow_count, flow_key, attr_count, attr_list, SAI_BULK_OP_ERROR_MODE_IGNORE_ERROR, object_statuses);

```

### Retrieve Flow Entry

```c
uint32_t attr_count = ...; 
sai_attribute_t attr_list[] = ...;

sai_flow_entry_t flow_entry;
flow_entry.flow_table_id = 0x123456789abc; /* Not a key, only indicate its table id */
flow_entry.ip_protocol = 6;
flow_entry.src_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip_addr.addr.ip4);
flow_entry.dst_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip_addr.addr.ip4);
flow_entry.src_l4_port = 12345;
flow_entry.dst_l4_port = 80;

status = get_flow_entry_attribute(flow_entry, attr_count, attr_list);

```

### Retrieve Flow Entries

Example: Retrieve flow entries by filtering for all versions greater than 3 and less than 5, and return the results via GRPC.

```c
/* Object_count is set to UINT32_MAX because the precise number of 
 * entries in the flow table is unknown before querying. This 
 * approach allows for querying and filtering without a predefined limit. */

uint32_t object_count = UINT32_MAX

/* Indicates the response should be sent to the GRPC server */
sai_ip_address_t server_ip_addr;
uint16_t server_port;
server_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &server_ip_addr.addr.ip4);
server_port = 12345;

/* Specifies that the filter operation should select versions greater than 3 and less than 5.
 * Row 0 - Specifies the first filter condition to select versions greater than 3:
 *   Column 0: Identifies the filter key (version) 
 *   Column 1: Specifies the filter operation (greater than)
 *   Column 2: Provides the filter value (3)
 * Row 1 - Specifies the second filter condition to select versions less than 5:
 *   Column 0: Identifies the filter key (version)
 *   Column 1: Specifies the filter operation (less than)
 *   Column 2: Provides the filter value (5)
 * Row 2 - Marks the end of the list:
 *   Column 0: Specifies the operation to end the list */

sai_attribute_t attr_list[3][3];

attr_list[0][0].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY,;
attr_list[0][0].value = SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_VERSION;
attr_list[0][1].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP;
attr_list[0][1].value = SAI_BULK_GET_FILTER_OP_GREATER_THAN;
attr_list[0][2].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_INT;
attr_list[0][2].value = 3;

attr_list[1][0].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FLOW_ENTRY_FILTER_KEY,;
attr_list[1][0].value = SAI_BULK_GET_FLOW_ENTRY_FILTER_KEY_VERSION;
attr_list[1][1].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP;
attr_list[1][1].value = SAI_BULK_GET_FILTER_OP_LESS_THAN;
attr_list[1][2].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_VALUE_INT;
attr_list[1][2].value = 5;

attr_list[2][0].id = SAI_FLOW_ENTRY_ATTR_BULK_GET_FILTER_OP;
attr_list[2][0].value = SAI_BULK_GET_FILTER_OP_END_OF_LIST;

/* Call the function */
status = get_flow_entries_attribute(object_count, flow_entry, attr_count, attr_list, mode, object_statuses);

```

### Remove flow entry

[TO-DO] Remove two direction flows

```c
sai_flow_entry_t flow_entry;
flow_entry.flow_table_id = 0x123456789abc; /* Not a key, only indicate its table id */
flow_entry.ip_protocol = 6;
flow_entry.src_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip_addr.addr.ip4);
flow_entry.dst_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip_addr.addr.ip4);
flow_entry.src_l4_port = 12345;
flow_entry.dst_l4_port = 80;

status = remove_flow_entry(flow_entry);
```

### Remove flow table

```c
sai_object_id_t flow_table_id = 0x112233;
status = remove_flow_table(flow_table_id);
```
