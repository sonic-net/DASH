# DASH routing actions

As [DASH packet flow HLD](../general/dash-sai-pipeline-packet-flow.md) describes, routing actions are the fundamental building blocks that describe the packet transformations and form the high level scenarios in DASH. And this doc is used to describe the routing action definitions in details.

1. [Overview](#overview)
2. [Stage transition actions](#stage-transition-actions)
   1. [Basic stage transition actions](#basic-stage-transition-actions)
      1. [`drop` action](#drop-action)
      2. [`trap` action](#trap-action)
   2. [Matching stage transition actions](#matching-stage-transition-actions)
      1. [IP-based stage transition actions](#ip-based-stage-transition-actions)
         1. [`lpmrouting` action](#lpmrouting-action)
         2. [`maprouting` action](#maprouting-action)
      2. [Port-based stage transition actions](#port-based-stage-transition-actions)
         1. [`portmaprouting` action](#portmaprouting-action)
3. [Packet transformation actions](#packet-transformation-actions)
   1. [`staticencap` action](#staticencap-action)
   2. [`tunnel` action](#tunnel-action)
   3. [`reverse_tunnel` action](#reverse_tunnel-action)
   4. [`4to6` action](#4to6-action)
   5. [`6to4` action](#6to4-action)
   6. [`nat` action](#nat-action)

## Overview

On high level, there are 2 types of routing actions:

- Packet transformation actions:
  - These actions are used to transform the packet header fields, such as modify the packet fields, adding encaps, etc.
  - These actions can only be used in the routing types that specified in the `routing_type` field in each match stage entry.
- Stage transition actions:
  - These actions are used to describe the stage transitions in the DASH pipeline, such as transit to maprouting stage.
  - This actions can only be used in the routing types that specified in the `transition` field in each match stage entry.

For how routing action works, please refer to the ["Routing action and routing types" section in DASH packet flow HLD](../general/dash-sai-pipeline-packet-flow.md#57-routing-actions-and-routing-types).

## Stage transition actions

### Basic stage transition actions

#### `drop` action

- Actions:
  - Drop the packet after the entry is matched.

#### `trap` action

- Actions:
  - Trap the packet to CPU after the entry is matched.

### Matching stage transition actions

All matching stage transition actions will support the following parameters:

- `default_routing_type`: If no entry is found, use this routing type to route the packet. If `default_routing_type` is not set, the packet will be dropped by default.
- `stage_index`: If there are multiple stage of the same stage type, use this field to specify which stage to transit to. The index is starting from 0 and by default 0.

#### IP-based stage transition actions

All IP-based stage transition actions will support the following parameters:

- `use_src_ip`: Use source IP in routing and mapping stages.
- `ip_mask`: IP mask to apply before matching the entries.

##### `lpmrouting` action

- Actions:
  - The packet will be routed to the next LPM routing stage specified by the `stage_index` field.

The port mapping entries can be described as below:

```json
// Key Format: DASH_SAI_ROUTE_TABLE|<ENI ID>|<Stage Index>|<IP Cidr>
"DASH_SAI_ROUTE_TABLE|123456789012|0|10.0.1.0/24": {
    "transition": "some_transition",
    "routing_type": "do_somethng",

    // Metadata properties ...
}
```

##### `maprouting` action

- Actions:
  - The packet will be routed to the next map routing stage specified by the `stage_index` field.

A map routing entry can be described as below:

```json
// Key Format: DASH_VNET_MAPPING_TABLE|<VNET ID>|<Stage Index>|<IP>
"DASH_VNET_MAPPING_TABLE|Vnet1|0|10.0.1.1": {
    "transition": "some_transition",
    "routing_type": "do_somethng",

    // Metadata properties ...
}
```

#### Port-based stage transition actions

##### `portmaprouting` action

- Actions:
  - The packet will be routed to the next stage with TCP or UDP port mapping.

The port mapping entries can be described as below:

```json
// Key Format: DASH_SAI_PORT_MAPPING_TABLE|<Port Mapping Id>
"DASH_SAI_PORT_MAPPING_TABLE|portmapping-0": [
    // ...
    {
        "transition": "some_transition",
        "routing_type": "do_something",

        // Port range to match
        "src_port_min": 0,
        "src_port_max": 65535,
        "dst_port_min": 2000,
        "dst_port_max": 2099,

        // Metadata properties ...
    }
    // ...
]
```

## Packet transformation actions

### `staticencap` action

- Metadata parameters:
  - `underlay_dip`: Destination IP used in encap.
  - `underlay_sip`: Source IP used in encap.
  - `encap_type`: Encap type: "nvgre|vxlan"
  - `encap_key`: GRE key in NvGRE or VNI in VxLAN.
  - `dscp_mode`: DSCP handling mode: "preserve|pipe"
  - `dscp`: DSCP value to set in the encap header.
- Actions:
  - Enable the underlay encap header based on the encap type.
  - Update the underlay encap header with `encap_key`, `underlay_dip`, `underlay_sip`.
    - If `underlay_dip` / `underlay_sip` is not set, use the original IP.

### `tunnel` action

- Action parameters:
  - `target` = "underlay|tunnel1|tunnel2|..."
- Metadata Parameters:
  - `(underlay|tunnel1|tunnel2|...)_tunnel_id`: The ID of the tunnel we are going to use. 
    - The definition of the tunnel can be found below.
    - The ECMP hash is calculated based on the 5 tuple of the inner-most (overlay) packet.
  - `dscp_mode`: DSCP handling mode: "preserve|pipe"
  - `dscp`: DSCP value to set in the encap header.
- Actions:
  - Enable the encap header based on the target tunnel and encap_type.
  - Update the encap information with the `encap_key`, `dip` and `sip`.

A tunnel entry can be described as below:

```json
"DASH_SAI_TUNNEL_TABLE|<TUNNEL_ID>":{
    "name": "tunnel-123",
    "dips": "100.0.1.1",
    "sip": "2.2.2.1",
    "encap_type": "vxlan",
    "encap_key": 101
}
```

### `reverse_tunnel` action

- Action parameters:
  - `target` = "underlay|tunnel1|tunnel2|..."
- Metadata Parameters:
  - `(underlay|tunnel1|tunnel2|...)_tunnel_id`: The ID of the tunnel we are going to use. 
    - The definition of the tunnel can be found below.
    - The ECMP hash is calculated based on the 5 tuple of the inner-most (overlay) packet.
- Actions:
  - No packet transformation should be done on the packet.
  - When creating the flow, in the reverse flow,
    - Enable the encap header based on the target tunnel and encap_type.
    - Update the encap information with the `encap_key`, `dip` and `sip`.

The tunnel entry is the same as the one in `tunnel` action.

### `4to6` action

- Metadata parameters:
  - `4to6_sip_encoding`: "value_bits/mask_bits"
  - `4to6_dip_encoding`: "value_bits/mask_bits"
- Metadata merging in parameter evaluation:
  - When same metadata is found during route action parameter evaluation process, value_bits and mask_bits will be reduced into one with following operation:
    - new_value_bits = (old_value_bits & !mask_bits) | value_bits
    - new_mask_bits = old_mask_bits | mask_bits
- Actions:
  - New SIP/DIP v6 = (SIP/DIP v4 & !4to6_sip/dip_encoding.mask_bits) | 4to6_sip/dip_encoding.value_bits.

### `6to4` action

- Metadata parameters:
  - `6to4_sip_encoding`: "value_bits/mask_bits"
  - `6to4_dip_encoding`: "value_bits/mask_bits"
- Metadata merging in parameter evaluation:
  - When same metadata is found during route action parameter evaluation process, value_bits and mask_bits will be reduced into one with following operation:
    - new_value_bits = (old_value_bits & !mask_bits) | value_bits
    - new_mask_bits = old_mask_bits | mask_bits
- Actions:
  - New SIP/DIP = (SIP/DIP v6 with higher bits removed & !6to4_sip/dip_encoding.mask_bits) | 6to4_sip/dip_encoding.value_bits.

### `nat` action

- Metadata parameters:
  - `nat_dip` / `nat_sip`: The destination / source IP that we need to update to.
  - `nat_dport` / `nat_sport`: The destination / source port that we need to update to.
- Action:
  - "nat" action always works on the overlay (inner most) packet.
  - It updates the IP and Port based on the metadata parameters.
  - If IP version doesn’t match, this action will fail and acting as no-op. 