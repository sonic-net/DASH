# DASH Metering HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/30/2024 | Riff Jiang | Initial version |
| 0.2 | 04/03/2024 | Riff Jiang | Updated meter class from 16 bits to 32 bits. Added capability for meter bucket. |

1. [1. Background](#1-background)
2. [2. Resource modeling, requirement, and SLA](#2-resource-modeling-requirement-and-sla)
   1. [2.1. Resource modeling](#21-resource-modeling)
   2. [2.2. Scaling requirement](#22-scaling-requirement)
   3. [2.3. Reliability requirements](#23-reliability-requirements)
3. [3. SAI API design](#3-sai-api-design)
   1. [3.1. Meter bucket](#31-meter-bucket)
   2. [3.2. Policy-based meter attributes](#32-policy-based-meter-attributes)
      1. [3.2.1. Route attributes](#321-route-attributes)
      2. [3.2.2. Mapping attributes](#322-mapping-attributes)
      3. [3.2.3. Tunnel attributes](#323-tunnel-attributes)
      4. [3.2.4. Inbound route rule attributes](#324-inbound-route-rule-attributes)
   3. [3.3. Global meter policy](#33-global-meter-policy)
      1. [3.3.1. ENI](#331-eni)
      2. [3.3.2. Meter policy](#332-meter-policy)
      3. [3.3.3. Meter rule](#333-meter-rule)
   4. [3.4. Capability](#34-capability)
4. [4. Metering bucket selection in DASH pipeline](#4-metering-bucket-selection-in-dash-pipeline)
5. [5. Metering bucket stats fetch process](#5-metering-bucket-stats-fetch-process)
   1. [5.1. Metering bucket creation](#51-metering-bucket-creation)
   2. [5.2. Fetching metering bucket stats](#52-fetching-metering-bucket-stats)

## 1. Background

To support billing, DASH introduced metering related objects as traffic counters. These counters are only used for billing purposes and not related to traffic policer or shaping.

## 2. Resource modeling, requirement, and SLA

### 2.1. Resource modeling

- Each ENI will allocates a set of metering bucket for billing purposes.
- Metering bucket is indexed by a UINT32 number called metering class, which starts from 1. Meter class 0 will be reversed and considered as not set.
- Each metering bucket will contain 1 inbound counter and 1 outbound counter for at least counting bytes.
- Metering bucket shall reflect the traffic volume of the customer. This means:
  - It shall only count the size of the overlay packet.
  - On the outbound direction, it shall count the packets before the SDN transformation.
  - On the inbound direction, it shall count the packets after the SDN transformation.

### 2.2. Scaling requirement

The scaling requirement for metering are listed as below:

| Metric | Requirement |
| --- | --- |
| # of meter buckets per ENI | 4095 (2^12 – 1, 0 is considered as not set) |
| # of meter rules per meter policy | (TBD)  |

### 2.3. Reliability requirements

In HA setup, the metering info should be stored as part of flow and replicated to the standby side. Whenever the primary failover, the metering class id should be still the same for each flow.

The high level flow replication follows the same approach as the SmartSwitch HA design, hence omitted here.

## 3. SAI API design

The following attributes will be involved in determining the final metering buckets in DASH.

### 3.1. Meter bucket

The meter bucket is defined as an entry table with each entry defined as below:

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| eni_id | `sai_object_id_t` | SAI_NULL_OBJECT_ID | ENI ID of this metering class. |
| meter_class | `sai_uint32_t` | 0 | Meter class of this meter bucket. |

To fetch the metering data from each meter bucket, we are going to leverage the SAI stats APIs, which provides get, get and clear and other frequently used semantics. It will also reduce the work in SONiC stack, as SONiC already have good support over the stats APIs.

| Attribute | Description |
| --- | --- |
| SAI_METER_BUCKET_STAT_OUTBOUND_BYTES | Total outbound traffic in bytes. |
| SAI_METER_BUCKET_STAT_INBOUND_BYTES | Total inbound traffic in bytes. |

### 3.2. Policy-based meter attributes

#### 3.2.1. Route attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR | `sai_uint32_t` | 0 | Meter class OR bits. |
| SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND | `sai_uint32_t` | UINT32_MAX | Meter class AND bits. |

#### 3.2.2. Mapping attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS_OR | `sai_uint32_t` | 0 | Meter class OR bits. |

#### 3.2.3. Tunnel attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_DASH_TUNNEL_ATTR_METER_CLASS_OR | `sai_uint32_t` | 0 | Meter class OR bits. |

#### 3.2.4. Inbound route rule attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR | `sai_uint32_t` | 0 | Meter class OR bits. |
| SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND | `sai_uint32_t` | UINT32_MAX | Meter class AND bits. |

### 3.3. Global meter policy

#### 3.3.1. ENI

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_ENI_ATTR_V4_METER_POLICY_ID | `sai_object_id_t` | SAI_NULL_OBJECT_ID | Global IPv4 meter policy ID for this ENI. |
| SAI_ENI_ATTR_V6_METER_POLICY_ID | `sai_object_id_t` | SAI_NULL_OBJECT_ID | Global IPv6 meter policy ID for this ENI. |

#### 3.3.2. Meter policy

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_METER_POLICY_ATTR_IP_ADDR_FAMILY | `sai_ip_addr_family_t` | SAI_IP_ADDR_FAMILY_IPV4 | IP address family of the metering policy |

#### 3.3.3. Meter rule

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_METER_RULE_ATTR_METER_POLICY_ID | `sai_object_id_t` | SAI_NULL_OBJECT_ID | Meter policy ID of this meter rule. |
| SAI_METER_RULE_ATTR_METER_CLASS | `sai_uint32_t` | UINT32_MAX | Meter class when this meter rule is hit. |
| SAI_METER_RULE_ATTR_DIP | `sai_ip_address_t` | NA | Destination IP for ternary match. |
| SAI_METER_RULE_ATTR_DIP_MASK | `sai_ip_address_t` | NA | Destination IP mask for ternary match. |
| SAI_METER_RULE_ATTR_PRIORITY | `sai_uint32_t` | NA | Priority required for ternary match. |

### 3.4. Capability

To enable the DASH providers be able to tell the host how much metering buckets are supported, we are going to introduce a new capability attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| SAI_SWITCH_ATTR_DASH_CAPS_MAX_METER_BUCKET_COUNT_PER_ENI | `sai_uint32_t` | Max number of meter buckets per ENI supported by the DASH implementation. |

## 4. Metering bucket selection in DASH pipeline

In DASH, the packet shall be metered following the approach below.

When a packet arrives at an ENI, it will go through the steps below to find its metering bucket:

1. **Init**: `AggregatedMeterClassOR` = 0, `AggregatedMeterClassAND` = UINT32_MAX.
2. **Conntrack Lookup**: In Conntrack Lookup stage, if a valid flow is hit, the meter class stored in that flow shall be used for locating the metering bucket.
3. **Policy match stages (Routing/Mapping)**: When flow is missing, the packet will go to slow path and walk through all the policy match stages. Depends on the stage it goes through, it will pick up the meter class OR bits and AND bits, and these 2 bits shall be aggregated separately:
   1. `AggregatedMeterClassOR` = `AggregatedMeterClassOR` | `MeterClassOR`
   2. `AggregatedMeterClassAND` = `AggregatedMeterClassAND` & `MeterClassAND`
4. **After policy match stages**: Now we calculates the meter class as below:
   1. `MeterClass` = `AggregatedMeterClassOR` & `AggregatedMeterClassAND`
   2. This allows us to use the info from routing entry to override the some meter class bits set in the mapping.
5. **Metering**: If `MeterClass` is 0 at this moment, meter policy will be used for determining which meter class shall be used:
   1. Meter policy v4 or v6 will be selected based on the IP family of the original overlay packet.
   2. The overlay destination (outbound pipeline) / source (inbound pipeline) IP will be used for ternary match against the meter rules in the meter policy to find the meter class.
6. **Meter Update**: The final meter class will be used for update the counters in meter bucket. If final meter class is 0, no meter bucket will be updated.

## 5. Metering bucket stats fetch process

### 5.1. Metering bucket creation

Whenever the ENI is created, we will assume the all metering buckets are created together with the ENI and initialized to 0, without the need of any additional SAI API calls, such as `create_meter_bucket`.

Each ENI will maintain the metering bucket from 1 to SAI_SWITCH_ATTR_DASH_CAPS_MAX_METER_BUCKET_COUNT_PER_ENI, inclusive.

### 5.2. Fetching metering bucket stats

Every once a while, the counters of each metering bucket will be pulled. 

To save the cost, it is preferred to use the buck get stats API defined in `saiobject.h` to get all stats back in one call, with all metering bucket entry specified:

```c
sai_status_t sai_bulk_object_get_stats(
        _In_ sai_object_id_t switch_id,
        _In_ sai_object_type_t object_type,
        _In_ uint32_t object_count,
        _In_ const sai_object_key_t *object_key,
        _In_ uint32_t number_of_counters,
        _In_ const sai_stat_id_t *counter_ids,
        _In_ sai_stats_mode_t mode,
        _Inout_ sai_status_t *object_statuses,
        _Out_ uint64_t *counters);
```
