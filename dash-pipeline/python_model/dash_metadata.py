from dash_headers import *
from typing import *
from __dash_enum import *

class encap_data_t:
    vni                   :  Annotated[int, 24]
    dest_vnet_vni         :  Annotated[int, 24]
    underlay_sip          :  Annotated[int, IPv4Address_size]
    underlay_dip          :  Annotated[int, IPv4Address_size]
    underlay_smac         :  Annotated[int, EthernetAddress_size]
    underlay_dmac         :  Annotated[int, EthernetAddress_size]
    overlay_dmac          :  Annotated[int, EthernetAddress_size]
    dash_encapsulation    :  Annotated[int, 16]
    service_tunnel_key    :  Annotated[int, 24]
    original_overlay_sip  :  Annotated[int, IPv4Address_size]
    original_overlay_dip  :  Annotated[int, IPv4Address_size]

class dash_direction_t(dash_enum):
    INVALID   =  0
    OUTBOUND  =  1
    INBOUND   =  2

class conntrack_data_t:
    allow_in  : bool
    allow_out : bool

class eni_data_t:
    cps          :  Annotated[int, 32]
    pps          :  Annotated[int, 32]
    flows        :  Annotated[int, 32]
    admin_state  :  Annotated[int, 1]

class metadata_t:
    dropped                      :  bool
    direction                    :  Annotated[int, 16]
    encap_data                   :  encap_data_t
    eni_addr                     :  Annotated[int, EthernetAddress_size]
    vnet_id                      :  Annotated[int, 16]
    dst_vnet_id                  :  Annotated[int, 16]
    eni_id                       :  Annotated[int, 16]
    eni_data                     :  eni_data_t
    inbound_vm_id                :  Annotated[int, 16]
    appliance_id                 :  Annotated[int, 8]
    is_overlay_ip_v6             :  Annotated[int, 1]
    is_lkup_dst_ip_v6            :  Annotated[int, 1]
    ip_protocol                  :  Annotated[int, 8]
    dst_ip_addr                  :  Annotated[int, IPv4ORv6Address_size]
    src_ip_addr                  :  Annotated[int, IPv4ORv6Address_size]
    lkup_dst_ip_addr             :  Annotated[int, IPv4ORv6Address_size]
    conntrack_data               :  conntrack_data_t
    src_l4_port                  :  Annotated[int, 16]
    dst_l4_port                  :  Annotated[int, 16]
    dash_acl_group_id            :  Annotated[int, 16]
    acl_outcome_allow            :  Annotated[int, 1]
    acl_outcome_terminate        :  Annotated[int, 1]
    stage1_dash_acl_group_id     :  Annotated[int, 16]
    stage2_dash_acl_group_id     :  Annotated[int, 16]
    stage3_dash_acl_group_id     :  Annotated[int, 16]
    stage4_dash_acl_group_id     :  Annotated[int, 16]
    stage5_dash_acl_group_id     :  Annotated[int, 16]
    meter_policy_en              :  Annotated[int, 1]
    mapping_meter_class_override :  Annotated[int, 1]
    meter_policy_id              :  Annotated[int, 16]
    policy_meter_class           :  Annotated[int, 16]
    route_meter_class            :  Annotated[int, 16]
    mapping_meter_class          :  Annotated[int, 16]
    meter_class                  :  Annotated[int, 16]
    meter_bucket_index           :  Annotated[int, 32]

    def __init__(self):
        self.encap_data     = encap_data_t()
        self.eni_data       = eni_data_t()
        self.conntrack_data = conntrack_data_t()
