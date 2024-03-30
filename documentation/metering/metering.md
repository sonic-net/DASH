# DASH Metering HLD

| Rev | Date | Author | Change Description |
| --- | ---- | ------ | ------------------ |
| 0.1 | 03/30/2024 | Riff Jiang | Initial version |

1. [1. Background](#1-background)
2. [Resource modeling, requirement, and SLA](#resource-modeling-requirement-and-sla)
   1. [Resource modeling](#resource-modeling)
   2. [Scaling requirement](#scaling-requirement)
   3. [Reliability requirements](#reliability-requirements)
3. [SAI API design](#sai-api-design)
   1. [Meter bucket](#meter-bucket)
   2. [Policy-based meter attributes](#policy-based-meter-attributes)
      1. [Route attributes](#route-attributes)
      2. [Mapping attributes](#mapping-attributes)
      3. [Tunnel attributes](#tunnel-attributes)
      4. [Inbound route rule attributes](#inbound-route-rule-attributes)
   3. [Global meter policy](#global-meter-policy)
      1. [ENI](#eni)
      2. [Meter policy](#meter-policy)
      3. [Meter rule](#meter-rule)
4. [Metering bucket selection in DASH pipeline](#metering-bucket-selection-in-dash-pipeline)

## 1. Background

To support billing, DASH introduced metering related objects as traffic counters. These counters are only used for billing purposes and not related to traffic policer or shaping.

## Resource modeling, requirement, and SLA

### Resource modeling

- Each ENI will allocates a set of metering bucket for billing purposes.
- Metering bucket is indexed by a UINT16 number called metering class, which starts from 1. Meter class 0 will be reversed and considered as not set.
- Each metering bucket will contain 1 inbound counter and 1 outbound counter for at least counting bytes.
- Metering bucket shall reflect the traffic volume of the customer. This means:
  - It shall only count the size of the overlay packet.
  - On the outbound direction, it shall count the packets before the SDN transformation.
  - On the inbound direction, it shall count the packets after the SDN transformation.

### Scaling requirement

The scaling requirement for metering are listed as below:

| Metric | Requirement |
| --- | --- |
| # of meter buckets per ENI | 4095 (2^12 – 1, 0 is considered as not set) |
| # of meter rules per meter policy | (TBD)  |

### Reliability requirements

In HA setup, the metering info should be stored as part of flow and replicated to the standby side. Whenever the primary failover, the metering class id should be still the same for each flow.

The high level flow replication follows the same approach as the SmartSwitch HA design, hence omitted here.

## SAI API design

The following attributes will be involved in determining the final metering buckets in DASH.

### Meter bucket

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_METER_BUCKET_ATTR_ENI_ID | sai_object_id_t | SAI_NULL_OBJECT_ID | ENI ID of this metering class. |
| SAI_METER_BUCKET_ATTR_METER_CLASS | sai_uint16_t | 0 | Meter class of this meter bucket. |

To fetch the metering data from each meter bucket, we are going to leverage the SAI stats APIs, which provides get, get and clear and other frequently used semantics. It will also reduce the work in SONiC stack, as SONiC already have good support over the stats APIs.

| Attribute | Description |
| --- | --- |
| SAI_METER_BUCKET_STAT_OUTBOUND_BYTES | Total outbound traffic in bytes. |
| SAI_METER_BUCKET_STAT_INBOUND_BYTES | Total inbound traffic in bytes. |

### Policy-based meter attributes

#### Route attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR | sai_uint16_t | 0 | Meter class OR bits. |
| SAI_OUTBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND | sai_uint16_t | UINT16_MAX | Meter class AND bits. |

#### Mapping attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_OUTBOUND_CA_TO_PA_ENTRY_ATTR_METER_CLASS_OR | sai_uint16_t | 0 | Meter class OR bits. |

#### Tunnel attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_DASH_TUNNEL_ATTR_METER_CLASS_OR | sai_uint16_t | 0 | Meter class OR bits. |

#### Inbound route rule attributes

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_OR | sai_uint16_t | 0 | Meter class OR bits. |
| SAI_INBOUND_ROUTING_ENTRY_ATTR_METER_CLASS_AND | sai_uint16_t | UINT16_MAX | Meter class AND bits. |

### Global meter policy

#### ENI

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_ENI_ATTR_V4_METER_POLICY_ID | sai_object_id_t | SAI_NULL_OBJECT_ID | Global IPv4 meter policy ID for this ENI. |
| SAI_ENI_ATTR_V6_METER_POLICY_ID | sai_object_id_t | SAI_NULL_OBJECT_ID | Global IPv6 meter policy ID for this ENI. |

#### Meter policy

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_METER_POLICY_ATTR_IP_ADDR_FAMILY | sai_ip_addr_family_t | SAI_IP_ADDR_FAMILY_IPV4 | IP address family of the metering policy |

#### Meter rule

| Attribute | Type | Default Value | Description |
| --- | --- | --- | --- |
| SAI_METER_RULE_ATTR_METER_POLICY_ID | sai_object_id_t | SAI_NULL_OBJECT_ID | Meter policy ID of this meter rule. |
| SAI_METER_RULE_ATTR_METER_CLASS | sai_uint16_t | UINT16_MAX | Meter class when this meter rule is hit. |
| SAI_METER_RULE_ATTR_DIP | sai_ip_address_t | NA | Destination IP for ternary match. |
| SAI_METER_RULE_ATTR_DIP_MASK | sai_ip_address_t | NA | Destination IP mask for ternary match. |
| SAI_METER_RULE_ATTR_PRIORITY | sai_uint32_t | NA | Priority required for ternary match. |

## Metering bucket selection in DASH pipeline

In DASH, the packet shall be metered following the approach below.

When a packet arrives at an ENI, it will go through the steps below to find its metering bucket:

1. Init: AggregatedMeterClassOR = 0, AggregatedMeterClassAND = UINT16_MAX.
2. Conntrack Lookup: In Conntrack Lookup stage, if a valid flow is hit, the meter class stored in that flow shall be used for locating the metering bucket.
3. Policy match stages (Routing/Mapping): When flow is missing, the packet will go to slow path and walk through all the policy match stages. Depends on the stage it goes through, it will pick up the meter class OR bits and AND bits, and these 2 bits shall be aggregated separately:
   1. AggregatedMeterClassOR = AggregatedMeterClassOR | MeterClassOR 
   2. AggregatedMeterClassAND = AggregatedMeterClassAND & MeterClassAND 
4. After policy match stages: Now we calculates the meter class as below:
   1. MeterClass = AggregatedMeterClassOR & AggregatedMeterClassAND
5. Metering: If MeterClass is 0 at this moment, meter policy will be used for determining which meter class shall be used:
   1. Meter policy v4 or v6 will be selected based on the IP family of the original overlay packet.
   2. The overlay destination (outbound pipeline) / source (inbound pipeline) IP will be used for ternary match against the meter rules in the meter policy to find the meter class.
6. The final meter class will be used for update the counters in meter bucket. If final meter class is 0, no meter bucket will be updated.
