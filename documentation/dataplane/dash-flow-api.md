# DASH Flow API HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/20/2024 | Zhixiong Niu | Initial version |

## Table of Contents

- [DASH Flow API HLD](#dash-flow-api-hld)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Terminology](#terminology)
  - [Model](#model)
  - [Flow Table APIs](#flow-table-apis)
  - [Flow APIs](#flow-apis)
    - [Basic flow APIs](#basic-flow-apis)
    - [Keys of flow entry](#keys-of-flow-entry)
    - [Attributes of flow entry](#attributes-of-flow-entry)
      - [Flow basic metadata](#flow-basic-metadata)
      - [Reverse flow key](#reverse-flow-key)
      - [Flow encap](#flow-encap)
      - [Flow rewrite](#flow-rewrite)
    - [Flow Bulk Get Session](#flow-bulk-get-session)
    - [Protobuf-based flow programming](#protobuf-based-flow-programming)
    - [Capability](#capability)
  - [Examples](#examples)
    - [Create flow table](#create-flow-table)
    - [Create flow key](#create-flow-key)
    - [Create attribute and flow entry](#create-attribute-and-flow-entry)
    - [Add flow entries](#add-flow-entries)
    - [Retrieve flow entry](#retrieve-flow-entry)
    - [Retrieve flow entries via flow entry bulk get session](#retrieve-flow-entries-via-flow-entry-bulk-get-session)
    - [Remove flow entry](#remove-flow-entry)
    - [Remove flow table](#remove-flow-table)

## Introduction

DASH supports the storage and processing of millions of flow states. To further enhance the DASH flow processing capabilities, we offer a DASH flow abstraction layer to facilitate vendor-neutral flow management. This layer ensures uniform control over flows across programmable switches, DPUs, and smart switches. The DASH flow abstraction provides concepts of flow tables and flow entries, as well as APIs to manage the flows.

Cloud providers can build their services on top of the DASH flow to cater to various scenarios. They use the DASH flow to achieve SDN, re-simulation, dataplane applications, cloud gateways, and load balancing for their flow operations. This also lays the foundation for DASH to offer foundational services, such as flow-level high availability and debuggability.

## Terminology

- **Flow**: It represents a single direction of the match-action entry for a connection.
- **Flow entry**: Same as flow.
- **Flow Key**: The key that is used to match the packet for finding its flow.
- **Flow State**: The state of the flow, including the packet transformations and all other tracked states, such as TCP, HA, etc.
- **Flow Table**: The table to store a set of flows.

## Model

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

    SAI_DASH_FLOW_ENABLED_KEY_ENI_ADDR = 1 << 1,

    SAI_DASH_FLOW_ENABLED_KEY_PROTOCOL = 1 << 2,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_IP = 1 << 3,

    SAI_DASH_FLOW_ENABLED_KEY_DST_IP = 1 << 4,

    SAI_DASH_FLOW_ENABLED_KEY_SRC_PORT = 1 << 5,

    SAI_DASH_FLOW_ENABLED_KEY_DST_PORT = 1 << 6,

} sai_dash_flow_enabled_key_t;
```

## Flow APIs

### Basic flow APIs

The flow_entry APIs are defined as follows:

| API                        | Description                                                  |
| -------------------------- | :----------------------------------------------------------- |
| create_flow_entry          | Add a single new entry to a certain flow table               |
| remove_flow_entry          | Remove a single entry in a certain flow table. Note that the flow removal process deletes two flows if it is a bi-directional flow. If you wish to remove a flow in only one direction, you should set the flow to be uni-directional in advance. |
| set_flow_entry_attribute   | Set attributes for a single entry in a certain flow table    |
| get_flow_entry_attribute   | Get attributes of a single entry in a certain flow table     |
| create_flow_entries        | Add multiple entries to a certain flow table in bulk         |
| remove_flow_entries        | Remove multiple entries from a specific flow table in bulk. Note that the flow removal process deletes two flows if it is a bi-directional flow. If you wish to remove a flow in only one direction, you should set the flow to be uni-directional in advance. |
| get_flow_entries_attribute | Get multiple entries from a certain flow table in bulk       |

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
     * @brief Exact matched key eni_addr
     */
    sai_mac_t eni_addr;

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

| Attribute name                       | Type                                                         | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_VERSION          | `sai_uint32_t`                                               | Version of the flow entry                                    |
| SAI_FLOW_ENTRY_ATTR_DASH_DIRECTION   | `sai_dash_direction_t`                                       | Direction of the DASH flow                                   |
| SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION | `sai_dash_flow_action_t`                                     | Action to be applied on the flow                             |
| SAI_FLOW_ENTRY_ATTR_METER_CLASS      | `sai_uint16_t`                                               | Meter class for flow entry, used for traffic metering and policing. |
| SAI_FLOW_SYNC_SESSION_STATE          | @type `sai_object_id_t` @objects: `DASH_FLOW_SYNC_SESSION_STATE` | Indicates the flow sync session state                        |

#### Reverse flow key

When configuring a flow_entry, it can be specified whether it is unidirectional or bidirectional. If it is bidirectional, it can be designated as a reverse flow key, allowing for the rapid identification of the corresponding reverse flow. Of course, if a flow entry is initially established as unidirectional, its reverse flow can also be set up later, utilizing these attributes to link them together.

| Attribute name                            | Type               | Description                                 |
| ----------------------------------------- | ------------------ | ------------------------------------------- |
| SAI_FLOW_ENTRY_ATTR_IS_BIDIRECTIONAL_FLOW | `bool`             | Indicates if the flow is bidirectional      |
| SAI_FLOW_ENTRY_ATTR_REVERSE_ENI_ADDR      | `sai_mac_t`        | Eni mac addr for the recerse flow           |
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

#### Flow rewrite

These are the related attributes of flow rewrite.

| Attribute name               | Type               | Description                                                  |
| ---------------------------- | ------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_ATTR_IS_IPV6  | `bool`             | Indicates whether the flow is IPv6 (true) or IPv4 (false).   |
| SAI_FLOW_ENTRY_ATTR_DST_MAC  | `sai_mac_t`        | Destination MAC address for the flow entry.                  |
| SAI_FLOW_ENTRY_ATTR_SIP      | `sai_ip_address_t` | Source IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_DIP      | `sai_ip_address_t` | Destination IP address for the flow entry, supporting both IPv4 and IPv6. |
| SAI_FLOW_ENTRY_ATTR_SIP_MASK | `sai_ip_address_t` | Subnet mask for the source IP address.                       |
| SAI_FLOW_ENTRY_ATTR_DIP_MASK | `sai_ip_address_t` | Subnet mask for the destination IP address.                  |

### Flow Bulk Get Session

To manage data transfer to a server via gRPC, we introduce a flow entry bulk session that incorporates filtering capabilities to precisely define the data range for transfer. The procedure for setting up these filters is straightforward:

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

| Attribute Name                                               | Type                                                | Description                                                 |
| ------------------------------------------------------------ | --------------------------------------------------- | ----------------------------------------------------------- |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY | `sai_dash_flow_entry_bulk_get_session_filter_key_t` | Key of the filter                                           |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY | `sai_dash_flow_entry_bulk_get_session_op_key_t`     | Operation of the filter                                     |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_INT_VALUE        | `sai_uint64_t`                                      | INT Value of the filter (Mutually exclusive with IP Value.) |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_IP_VALUE         | `sai_ip_address_t`                                  | IP Value of the filter (Mutually exclusive with INT Value.) |

```c
typedef enum _sai_dash_flow_entry_bulk_get_session_filter_key_t
{
    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_INVAILD,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_FLOW_TABLE_ID,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_ENI_ADDR,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_IP_PROTOCOL,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_IP_ADDR,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_IP_ADDR,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_SRC_L4_PORT,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_DST_L4_PORT,

    SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_KEY_VERSION,

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

Upon establishing the bulk get session filters, we can initiate a flow bulk get session, which is defined as follows:

| Function                                  | Description                                                 |
| ----------------------------------------- | ----------------------------------------------------------- |
| create_flow_entry_bulk_get_session        | Add a single new session for flow entry bulk get feature    |
| remove_flow_entry_bulk_get_session        | Remove a single new session for flow entry bulk get feature |
| set_flow_entry_bulk_get_session_attribute | Set attributes for a single session                         |
| get_flow_entry_bulk_get_session_attribute | Get attributes of a single session                          |
| create_flow_entry_bulk_get_sessions       | Add multiple new sessions for flow entry bulk get feature   |
| remove_flow_entry_bulk_get_sessions       | Remove multiple sessions for flow entry bulk get feature    |

In the attributes, we allow specifying the gRPC server and port. For filtering flow entries, we support up to five filters. Each filter is a bulk get session filter object, and different filters are combined using an *AND* operation. If no filters are specified, the bulk get session returns all flow entries.

| Attribute Name                                               | Type                                                         | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_IP     | `sai_ip_address_t`                                           | The IP address to use for the bulk get session.              |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_BULK_GET_SESSION_PORT   | `sai_uint16_t`                                               | The port to use for the bulk get session.                    |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FIRST_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter BULK_GET_SESSION_IP |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_SECOND_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter BULK_GET_SESSION_PORT |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_THIRD_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter FIRST_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FOURTH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter SECOND_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |
| SAI_FLOW_ENTRY_BULK_GET_SESSION_ATTR_FIFTH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID | @type: `sai_object_id_t` @objects `SAI_OBJECT_TYPE_FLOW_ENTRY_BULK_GET_SESSION_FILTER` | Action set_flow_entry_bulk_get_session_attr parameter THIRD_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ID |

### Protobuf-based flow programming

In addition to the flow state attributes, the flow state can be represented using protobuf for high-efficiency. The attribute of the flow entry is SAI_FLOW_ENTRY_ATTR_FLOW_DATA_PB.

Although the content of both attributes and protobuf may be identical, their applications differ. Attributes enable incremental updates to individual properties, whereas protobuf necessitates a complete update.

```protobuf
syntax = "proto3";

message SaiFlowEntry {
  uint32 version = 1; // SAI_FLOW_ENTRY_ATTR_VERSION
  uint32 dash_flow_action = 2; // SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION
  uint32 meter_class = 3; // SAI_FLOW_ENTRY_ATTR_METER_CLASS
  bool is_bidirectional_flow = 4; // SAI_FLOW_ENTRY_ATTR_IS_BIDIRECTIONAL_FLOW
  uint8 reverse_ip_protocol = 5; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_PROTOCOL
  string reverse_src_ip_addr = 6; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR for source
  string reverse_dst_ip_addr = 7; // SAI_FLOW_ENTRY_ATTR_REVERSE_IP_ADDR for destination
  uint32 reverse_src_l4_port = 8; // SAI_FLOW_ENTRY_ATTR_REVERSE_SRC_L4_PORT
  uint32 reverse_dst_l4_port = 9; // SAI_FLOW_ENTRY_ATTR_REVERSE_DST_L4_PORT
  uint32 dest_vnet_vni = 10; // SAI_FLOW_ENTRY_ATTR_DEST_VNET_VNI
  string underlay_sip = 11; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_SIP
  string underlay_dip = 12; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_DIP
  string underlay_smac = 13; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_SMAC
  string underlay_dmac = 14; // SAI_FLOW_ENTRY_ATTR_UNDERLAY_DMAC
  bool is_ipv6 = 15; // SAI_FLOW_ENTRY_ATTR_IS_IPV6
  string dst_mac = 16; // SAI_FLOW_ENTRY_ATTR_DEST_MAC
  string sip = 17; // SAI_FLOW_ENTRY_ATTR_SIP
  string dip = 18; // SAI_FLOW_ENTRY_ATTR_DIP
  string sip_mask = 19; // SAI_FLOW_ENTRY_ATTR_SIP_MASK
  string dip_mask = 20; // SAI_FLOW_ENTRY_ATTR_DIP_MASK
}
```

### Capability

Ffffffff

## Examples

When a service intends to use DASH Flow SAI APIs, it should first establish a flow table via the `create_flow_table()` function. After the table creation, the programmer can add, delete, modify, or retrieve flow entries to/from the table. For instance, when DASH HA needs to perform bulk sync from the active DPU to the standby DPU, it should initially fetch the entry from the active DPU using `get_flow_entries`, then transmit the flow entries to the standby DPU via the control plane. The standby DPU subsequently calls `create_flow_entries()`to add entries to the corresponding flow table.

These examples describe how to create a flow state table, and how to operate flow entries.

### Create flow table

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

### Create flow key

```c

sai_flow_entry_t flow_entry;

flow_entry.flow_table_id = 0x112233;
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
uint32_t attr_count = ...; 
sai_attribute_t attr_list[] = ...;

sai_flow_entry_t flow_entry;
flow_entry.flow_table_id = 0x112233;
flow_entry.ip_protocol = 6;
flow_entry.src_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.1", &flow_entry.src_ip_addr.addr.ip4);
flow_entry.dst_ip_addr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
inet_pton(AF_INET, "192.168.1.2", &flow_entry.dst_ip_addr.addr.ip4);
flow_entry.src_l4_port = 12345;
flow_entry.dst_l4_port = 80;

status = get_flow_entry_attribute(flow_entry, attr_count, attr_list);

```

### Retrieve flow entries via flow entry bulk get session

Example: Retrieve flow entries by filtering for all versions greater than 3 and less than 5, and return the results via GRPC.

```c
/* Filter Version > 3 */
sai_attribute_t filter1_attr_list[3];
filter1_attr_list[0].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY;
filter1_attr_list[0].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_FILTER_KEY_KEY_VERSION;
filter1_attr_list[1].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY;
filter1_attr_list[1].value = SAI_DASH_FLOW_ENTRY_BULK_GET_SESSION_OP_KEY_FILTER_OP_GREATER_THAN,;
filter1_attr_list[2].id = SAI_FLOW_ENTRY_BULK_GET_SESSION_FILTER_ATTR_INT_VALUE;
filter1_attr_list[2].value = 3;

sai_object_id_t filter1_id;
status = create_flow_entry_bulk_get_session_filter(&filter1_id, switch_id, 3, filter1_attr_list);

/* Filter Version < 5 */
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
