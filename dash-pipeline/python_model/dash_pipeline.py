from __table import *
from __byte_counter import *
from dash_vxlan import *
from dash_outbound import *
from dash_inbound import *
from dash_underlay import *
from __sai_keys import *

def drop_action():
    mark_to_drop(standard_metadata)

def deny():
    meta.dropped = True

def accept():
    pass

vip = Table(
    key = {
        "hdr.ipv4.dst_addr": (EXACT, {SAI_KEY_NAME: "VIP"})
    },
    actions = [
       accept,
       (deny, {DEFAULT_ONLY: True})
    ],
    default_action = deny
)

def set_outbound_direction():
    meta.direction = dash_direction_t.OUTBOUND

def set_inbound_direction():
    meta.direction = dash_direction_t.INBOUND

direction_lookup = Table(
    key = {
        "hdr.vxlan.vni": (EXACT, {SAI_KEY_NAME: "VNI"})
    },
    actions = [
       set_outbound_direction,
       (set_inbound_direction, {DEFAULT_ONLY : True})
    ],
    default_action = set_inbound_direction
)

def set_appliance(neighbor_mac: Annotated[int, 48], mac: Annotated[int, 48]):
    meta.encap_data.underlay_dmac = neighbor_mac
    meta.encap_data.underlay_smac = mac

appliance = Table(
    key = {
        "meta.appliance_id" : TERNARY
    },
    actions = [
       set_appliance
    ]
)

def set_eni_attrs(cps                : Annotated[int, 32],
                  pps                : Annotated[int, 32],
                  flows              : Annotated[int, 32],
                  admin_state        : Annotated[int, 1],
                  vm_underlay_dip    : Annotated[int, 32],
                  vm_vni             : Annotated[int, 24, {TYPE : "sai_uint32_t"}],
                  vnet_id            : Annotated[int, 16],
                  v4_meter_policy_id : Annotated[int, 16],
                  v6_meter_policy_id : Annotated[int, 16],
                  inbound_v4_stage1_dash_acl_group_id : Annotated[int, 16],
                  inbound_v4_stage2_dash_acl_group_id : Annotated[int, 16],
                  inbound_v4_stage3_dash_acl_group_id : Annotated[int, 16],
                  inbound_v4_stage4_dash_acl_group_id : Annotated[int, 16],
                  inbound_v4_stage5_dash_acl_group_id : Annotated[int, 16],                  

                  inbound_v6_stage1_dash_acl_group_id : Annotated[int, 16],
                  inbound_v6_stage2_dash_acl_group_id : Annotated[int, 16],
                  inbound_v6_stage3_dash_acl_group_id : Annotated[int, 16],
                  inbound_v6_stage4_dash_acl_group_id : Annotated[int, 16],
                  inbound_v6_stage5_dash_acl_group_id : Annotated[int, 16],

                  outbound_v4_stage1_dash_acl_group_id : Annotated[int, 16],
                  outbound_v4_stage2_dash_acl_group_id : Annotated[int, 16],
                  outbound_v4_stage3_dash_acl_group_id : Annotated[int, 16],
                  outbound_v4_stage4_dash_acl_group_id : Annotated[int, 16],
                  outbound_v4_stage5_dash_acl_group_id : Annotated[int, 16],

                  outbound_v6_stage1_dash_acl_group_id : Annotated[int, 16],
                  outbound_v6_stage2_dash_acl_group_id : Annotated[int, 16],
                  outbound_v6_stage3_dash_acl_group_id : Annotated[int, 16],
                  outbound_v6_stage4_dash_acl_group_id : Annotated[int, 16],
                  outbound_v6_stage5_dash_acl_group_id : Annotated[int, 16]
                  ):
    meta.eni_data.cps            = cps
    meta.eni_data.pps            = pps
    meta.eni_data.flows          = flows
    meta.eni_data.admin_state    = admin_state
    meta.encap_data.underlay_dip = vm_underlay_dip
    # vm_vni is the encap VNI used for tunnel between inbound DPU -> VM
    # and not a VNET identifier
    meta.encap_data.vni          = vm_vni
    meta.vnet_id                 = vnet_id

    if meta.is_overlay_ip_v6 == 1:
        if meta.direction == dash_direction_t.OUTBOUND:
            meta.stage1_dash_acl_group_id = outbound_v6_stage1_dash_acl_group_id
            meta.stage2_dash_acl_group_id = outbound_v6_stage2_dash_acl_group_id
            meta.stage3_dash_acl_group_id = outbound_v6_stage3_dash_acl_group_id
            meta.stage4_dash_acl_group_id = outbound_v6_stage4_dash_acl_group_id
            meta.stage5_dash_acl_group_id = outbound_v6_stage5_dash_acl_group_id
        else:
            meta.stage1_dash_acl_group_id = inbound_v6_stage1_dash_acl_group_id
            meta.stage2_dash_acl_group_id = inbound_v6_stage2_dash_acl_group_id
            meta.stage3_dash_acl_group_id = inbound_v6_stage3_dash_acl_group_id
            meta.stage4_dash_acl_group_id = inbound_v6_stage4_dash_acl_group_id
            meta.stage5_dash_acl_group_id = inbound_v6_stage5_dash_acl_group_id
        meta.meter_policy_id = v6_meter_policy_id
    else:
        if meta.direction == dash_direction_t.OUTBOUND:
            meta.stage1_dash_acl_group_id = outbound_v4_stage1_dash_acl_group_id
            meta.stage2_dash_acl_group_id = outbound_v4_stage2_dash_acl_group_id
            meta.stage3_dash_acl_group_id = outbound_v4_stage3_dash_acl_group_id
            meta.stage4_dash_acl_group_id = outbound_v4_stage4_dash_acl_group_id
            meta.stage5_dash_acl_group_id = outbound_v4_stage5_dash_acl_group_id
        else:
            meta.stage1_dash_acl_group_id = inbound_v4_stage1_dash_acl_group_id
            meta.stage2_dash_acl_group_id = inbound_v4_stage2_dash_acl_group_id
            meta.stage3_dash_acl_group_id = inbound_v4_stage3_dash_acl_group_id
            meta.stage4_dash_acl_group_id = inbound_v4_stage4_dash_acl_group_id
            meta.stage5_dash_acl_group_id = inbound_v4_stage5_dash_acl_group_id
        meta.meter_policy_id = v4_meter_policy_id

eni = Table(
    key = {
        "meta.eni_id" : EXACT
    },
    actions = [
       set_eni_attrs,
       (deny, {DEFAULT_ONLY : True})
    ],
    default_action = deny
)

def permit():
    pass

def vxlan_decap_pa_validate(src_vnet_id: Annotated[int, 16]):
    meta.vnet_id = src_vnet_id

pa_validation = Table(
    key = {
        "meta.vnet_id"     : EXACT,
        "hdr.ipv4.src_addr": (EXACT, {SAI_KEY_NAME : "sip"})
    },
    actions = [
       permit,
       (deny, {DEFAULT_ONLY: True})
    ],
    default_action = deny
)

inbound_routing = Table(
    key = {
        "meta.eni_id"       : EXACT,
        "hdr.vxlan.vni"     : (EXACT,   {SAI_KEY_NAME: "VNI"}),
        "hdr.ipv4.src_addr" : (TERNARY, {SAI_KEY_NAME : "sip"})
    },
    actions = [
       vxlan_decap,
       vxlan_decap_pa_validate,
       (deny, {DEFAULT_ONLY: True})
    ],
    default_action = deny
)

def check_ip_addr_family(ip_addr_family: Annotated[int, 32, {TYPE : "sai_ip_addr_family_t", ISRESOURCETYPE : "true"}]):
    if ip_addr_family == 0:
        if meta.is_overlay_ip_v6 == 1:
            meta.dropped = True
    else:
        if meta.is_overlay_ip_v6 == 0:
            meta.dropped = True

meter_policy = Table(
    key = {
        "meta.meter_policy_id" : EXACT
    },
    actions = [
       check_ip_addr_family
    ],
    api_name = "dash_meter",
    is_object = "true"
)

def set_policy_meter_class(meter_class: Annotated[int, 16]):
    meta.policy_meter_class = meter_class

meter_rule = Table(
    key = {
        "meta.meter_policy_id" : (EXACT,    {TYPE : "sai_object_id_t", ISRESOURCETYPE : "true", OBJECTS : "METER_POLICY"}),
        "hdr.ipv4.dst_addr"    : (TERNARY,  {SAI_KEY_NAME : "dip"})
    },
    actions = [
       set_policy_meter_class,
       (NoAction, {DEFAULT_ONLY : True})
    ],
    default_action = NoAction,
    api_name = "dash_meter",
    is_object = "true"
)

# MAX_METER_BUCKET = MAX_ENI(64) * NUM_BUCKETS_PER_ENI(4096)
MAX_METER_BUCKETS = 262144

meter_bucket_inbound  = byte_counter(MAX_METER_BUCKETS)
meter_bucket_outbound = byte_counter(MAX_METER_BUCKETS)

def meter_bucket_action(outbound_bytes_counter : Annotated[int, 64, {TYPE : "sai_uint64_t", ISREADONLY : "true"}],
                        inbound_bytes_counter  : Annotated[int, 64, {TYPE : "sai_uint64_t", ISREADONLY : "true"}],
                        meter_bucket_index     : Annotated[int, 32, {TYPE : "sai_uint32_t", SKIPATTR : "true"}]):
    # read only counters for SAI api generation only
    meta.meter_bucket_index = meter_bucket_index

meter_bucket = Table(
    key = {
        "meta.eni_id"      : EXACT,
        "meta.meter_class" : EXACT
    },
    actions = [
       meter_bucket_action,
       (NoAction, {DEFAULT_ONLY : True})
    ],
    default_action = NoAction,
    api_name = "dash_meter",
    is_object = "true"
)

def set_eni(eni_id: Annotated[int, 16]):
    meta.eni_id = eni_id

eni_ether_address_map = Table(
    key = {
        "meta.eni_addr" : (EXACT, {SAI_KEY_NAME : "address"})
    },
    actions = [
       set_eni,
       (deny, {DEFAULT_ONLY : True})
    ],
    default_action = deny,
    api_name="dash_eni"
)

def set_acl_group_attrs(ip_addr_family: Annotated[int, 32, {TYPE : "sai_ip_addr_family_t", ISRESOURCETYPE : "true"}]):
    if ip_addr_family == 0:
        if meta.is_overlay_ip_v6 == 1:
            meta.dropped = True
    else:
        if meta.is_overlay_ip_v6 == 0:
            meta.dropped = True

dash_acl_group = Table(
    key = {
        "meta.stage1_dash_acl_group_id" : (EXACT, {SAI_KEY_NAME : "dash_acl_group_id"})
    },
    actions = [
       set_acl_group_attrs
    ],
    api_name = "dash_acl"
)

def apply():

    if vip.apply()["hit"]:
        # Use the same VIP that was in packet's destination if it's
        # present in the VIP table
        meta.encap_data.underlay_sip = hdr.ipv4.dst_addr

    # If Outer VNI matches with a reserved VNI, then the direction is Outbound
    direction_lookup.apply()

    appliance.apply()

    # Outer header processing

    # Put VM's MAC in the direction agnostic metadata field
    if meta.direction == dash_direction_t.OUTBOUND:
         meta.eni_addr = hdr.inner_ethernet.src_addr
    else:
         meta.eni_addr = hdr.inner_ethernet.dst_addr

    eni_ether_address_map.apply()
    if meta.direction == dash_direction_t.OUTBOUND:
        vxlan_decap()
    elif meta.direction == dash_direction_t.INBOUND:
        if inbound_routing.apply()["action_run"] == vxlan_decap_pa_validate:
            pa_validation.apply()
            vxlan_decap()

    # At this point the processing is done on customer headers

    meta.is_overlay_ip_v6 = 0
    meta.ip_protocol = 0
    meta.dst_ip_addr = 0
    meta.src_ip_addr = 0
    if hdr.ipv6:
        meta.ip_protocol = hdr.ipv6.next_header
        meta.src_ip_addr = hdr.ipv6.src_addr
        meta.dst_ip_addr = hdr.ipv6.dst_addr
        meta.is_overlay_ip_v6 = 1
    elif hdr.ipv4:
        meta.ip_protocol = hdr.ipv4.protocol
        meta.src_ip_addr = hdr.ipv4.src_addr
        meta.dst_ip_addr = hdr.ipv4.dst_addr

    if hdr.tcp:
        meta.src_l4_port = hdr.tcp.src_port
        meta.dst_l4_port = hdr.tcp.dst_port
    elif hdr.udp:
        meta.src_l4_port = hdr.udp.src_port
        meta.dst_l4_port = hdr.udp.dst_port

    eni.apply()
    if meta.eni_data.admin_state == 0:
        deny()
    dash_acl_group.apply()

    if meta.direction == dash_direction_t.OUTBOUND:
        outbound_apply()
    elif meta.direction == dash_direction_t.INBOUND:
        inbound_apply()

    # Underlay routing
    meta.dst_ip_addr = hdr.ipv4.dst_addr
    underlay_apply()

    if meta.meter_policy_en == 1:
        meter_policy.apply()
        meter_rule.apply()

    if meta.meter_policy_en == 1:
        meta.meter_class = meta.policy_meter_class
    else:
        meta.meter_class = meta.route_meter_class

    if (meta.meter_class == 0) or (meta.mapping_meter_class_override == 1):
        meta.meter_class = meta.mapping_meter_class


    meter_bucket.apply()
    if meta.direction == dash_direction_t.OUTBOUND:
        meter_bucket_outbound.count(meta.meter_bucket_index)
    elif meta.direction == dash_direction_t.INBOUND:
        meter_bucket_inbound.count(meta.meter_bucket_index)

    if meta.dropped:
        drop_action()

