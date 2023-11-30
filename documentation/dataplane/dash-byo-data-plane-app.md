# DASH BYO (Bring-Your-Own) data plane app

1. [1. Data plane app](#1-data-plane-app)
2. [2. BYO data plane app](#2-byo-data-plane-app)
   1. [2.1. DASH management role and system overview](#21-dash-management-role-and-system-overview)
   2. [2.2. Initialization work flow](#22-initialization-work-flow)
   3. [2.3. ASIC programming work flow](#23-asic-programming-work-flow)
   4. [2.4. Flow management](#24-flow-management)
   5. [2.5. RSS support](#25-rss-support)
3. [3. SAI API design](#3-sai-api-design)
   1. [3.1. SAI switch attribute updates](#31-sai-switch-attribute-updates)
   2. [3.2. DASH pipeline programming APIs](#32-dash-pipeline-programming-apis)
4. [4. Future work](#4-future-work)

## 1. Data plane app

Data plane app is one of the most important pieces in DASH pipeline. It is mainly responsible for:

- Flow management, such as flow creation, deletion, resimulation, etc.
- Work with ASIC to complete the table lookup and packet transformations. Depends on ASIC capability, if any operation could not be completed inside ASIC, it can be postponed to data plane app and completed in software.
- ASIC management, such as initializing and programming match stage, etc.
- and more.

![DASH data plane app](./images/dash-default-data-plane-app.svg)

By default, DASH technology providers will provide their own data plane app. This is usually closed source and can satisfy the DASH community requirement. However, in some cases, you might want to use your own data plane app due to some reasons, such as: private protocol support or support special logic in packet handling that is not supported by DASH technology providers. In this case, you can enable DASH BYO data plane app.

## 2. BYO data plane app

BYO data plane app is essentially a DPDK application that directly interacts with the data plane netdev.

When BYO data plane app is enabled, the data plane app provided by technology providers will be either disabled or running without tied to the data plane netdev and only act as part of SAI API implementation if needed. With this setup, DASH users can start to use that device to run their own data plane app and process the packets.

### 2.1. DASH management role and system overview

With BYO data plane app, from our customer's perspective, we will have 2 sources to program the ASIC, such as creating match stage entries or managing flow entries:

1. DASH users can explicitly program the ASIC via DASH SAI API proxy. A typical scenario is programming a new SDN policy.
2. BYO data plane app can also program the ASIC. A typical scenario is creating flow entries.

Even further, these 2 sources sometimes might need to work together in certain scenarios. For example, when a VNET mapping is updated, we need to update the VNET mapping entry as well as triggering flow resimulation to update all the flow entries that are related to this VNET mapping.

Hence we need a design to avoid the same set of SAI APIs being called in 2 different processes accidentally and causing problems, such as managing the stage entries, as the last caller will overwrite the ASIC state without any synchronization and knowledge from the other side.

To solve this problem, we are introducing 2 roles in DASH:

- Controller, which is responsible for initializing the ASIC and environments.
- Worker, which is responsible for processing the packets of new flows, programming the match stage entries, managing the flows and more.

At a high level, the system architecture will be look like below:

![DASH BYO data plane app](./images/dash-byo-data-plane-app.svg)

To explain how these 2 roles works together, we will dive into the initialization and ASIC programming work flow here.

### 2.2. Initialization work flow

The work flow of enabling the BYO data plane app will be like below:

```mermaid
sequenceDiagram

participant User
participant SP as SAI Proxy
participant SC as SAI (Controller)
participant IDPA as DASH Inbox data plane app
participant BYODPA as BYO data plane app
participant SH as SAI Handler
participant SW as SAI (Worker)
participant netdev

note over User,netdev: Controller initialization
User->>SP: SAI create switch<br>with controller role<br>and settings
SP->>SC: Forward request to SAI
SC->>SC: Initialize card<br>envirionment
SC->>IDPA: Configure inbox<br>data plane app
User->>SP: Get netdev name<br>as switch attribute
SP->>SC: Get netdev name<br>as switch attribute

note over User,netdev: BYO data plane app initialization
User->>BYODPA: Launch and configure BYO data plane app
BYODPA->>SH: Initialize
activate SH
SH->>SW: SAI create switch<br>with worker role
SH->>SP: Connect to proxy for handling stage entry and flow management request
SP->>User: Send BYO data plane app<br>ready notification
deactivate SH
BYODPA->>netdev: Initialize on top of netdev
```

After initialization, the BYO data plane app will be able to:

- Receive/Send packets from/to netdev
- Use SAI API to program the ASIC

> **NOTE**:
>
> Since BYO data plane app and DASH controller is essentially provided by our customer, so there are a few more things that BYO data plane app could do, but not listed in the diagram:
>
> 1. Controller can directly call into BYO data plane app for managing private features that is not provided by DASH.
> 2. BYO data plane app could call into the platform-dependent APIs (ASIC SDK) directly for managing the ASIC. However, by doing so, it also loses the portability of the BYO data plane app.
> 3. Since BYO data plane app is essentially a DPDK-based application, it can also use DPDK APIs to manage the netdev and the ASIC, e.g., setting up RSS options, etc.

### 2.3. ASIC programming work flow

With this setup, whenever we need to program the ASIC with new entries, we will forward the request to the data plane app.

Here is the example that shows how the users updates an existing mapping entry with flow resimulation, as well as how a BYO data plane app updates a flow entry:

```mermaid
sequenceDiagram

participant User
participant SP as SAI Proxy
participant BYODPA as BYO data plane app
participant SW as SAI (Worker)

note over User,SW: User updates a mapping entry
User->>SP: SAI create mapping entry
SP->>BYODPA: Forward request to worker
BYODPA->>SW: Update mapping entry
BYODPA->>SW: Trigger flow resimulation or other actions if needed.

note over User,SW: BYO data plane app updates a flow entry
BYODPA->>SW: SAI updates flow entry
```

### 2.4. Flow management

One of the most important responsibility of data plane app is flow management. Essentially, whenever a packet that cannot be handled by the hardware flow table, it will run through the DASH pipeline and sent to the data plane app. The data plane app will need to decide if a flow needs to be created, deleted or resimulated, and how.

In DASH-SAI APIs, we have provided a set of APIs to help manage the flows. Please refer to DASH Flow API design doc for more details.

### 2.5. RSS support

RSS is a frequently used feature in data plane app, which allows the packets to be distributed among different worker threads to increase throughput.

To enable and configure RSS, we don't have any extra APIs in SAI, and BYO data plane app can follow the standard way in DPDK to achieve this.

## 3. SAI API design

### 3.1. SAI switch attribute updates

```c
typedef enum _sai_dash_management_role_t {
    /**
     * @brief Controller role.
     */
    SAI_DASH_MANAGEMENT_ROLE_CONTROLLER,

    /**
     * @brief Worker role. Should only be used by BYO data plane app.
     */
    SAI_DASH_MANAGEMENT_ROLE_WORKER,
} sai_dash_management_role_t;

typedef void (*sai_switch_dash_byo_data_plane_app_ready_notification_fn)(
        _In_ sai_object_id_t switch_id);

typedef enum _sai_switch_attr_extensions_t {
    // ...


    /**
     * @brief DASH management role.
     *
     * @type sai_dash_management_role_t
     * @flags CREATE_ONLY
     */
    SAI_SWITCH_ATTR_DASH_MANAGEMENT_ROLE,

    /**
     * @brief Inbox data plane app worker count. (-1 = Disable, 0 = Auto, > 0 = Specified count)
     *
     * @type sai_int32_t
     * @flags CREATE_AND_SET
     * @default 0
     */
    SAI_SWITCH_ATTR_DASH_INBOX_DATA_PLANE_APP_WORKER_COUNT,

    /**
     * @brief BYO data plane app netdev name.
     *
     * @type sai_s8_list_t
     * @flags READ_ONLY
     */
    SAI_SWITCH_ATTR_DASH_BYO_DATA_PLANE_APP_NETDEV_NAME,

    /**
     * @brief Data plane app ready notification callback function.
     *
     * @type sai_switch_dash_byo_data_plane_app_ready_notification_fn
     * @flags CREATE_ONLY
     * @default NULL
     */
    SAI_SWITCH_ATTR_DASH_BYO_DATA_PLANE_APP_READY_NOTIFY,
} sai_switch_attr_extensions_t;
```

### 3.2. DASH pipeline programming APIs

Please refer to the DASH-SAI APIs for more details: <https://github.com/opencomputeproject/SAI/tree/master/experimental>.

## 4. Future work

- Hybrid data plane app, where both inbox and BYO data plane app are enabled at the same time.
