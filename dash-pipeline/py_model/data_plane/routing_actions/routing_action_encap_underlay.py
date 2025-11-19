from py_model.libs.__utils import *
from py_model.data_plane.dash_tunnel import *

def push_action_encap_u0(dash_encapsulation : dash_encapsulation_t = dash_encapsulation_t.VXLAN,
                         vni                : Annotated[int, 24] = 0,
                         underlay_sip       : Annotated[int, IPv4Address_size] = 0,
                         underlay_dip       : Annotated[int, IPv4Address_size] = 0,
                         underlay_smac      : Annotated[int, EthernetAddress_size] = 0,
                         underlay_dmac      : Annotated[int, EthernetAddress_size] = 0):
    
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.ENCAP_U0

    meta.u0_encap_data.dash_encapsulation = dash_encapsulation

    meta.u0_encap_data.vni = meta.u0_encap_data.vni if vni == 0 else vni
    meta.u0_encap_data.underlay_smac = meta.u0_encap_data.underlay_smac if underlay_smac == 0 else underlay_smac
    meta.u0_encap_data.underlay_dmac = meta.u0_encap_data.underlay_dmac if underlay_dmac == 0 else underlay_dmac
    meta.u0_encap_data.underlay_sip = meta.u0_encap_data.underlay_sip if underlay_sip == 0 else underlay_sip
    meta.u0_encap_data.underlay_dip = meta.u0_encap_data.underlay_dip if underlay_dip == 0 else underlay_dip

def push_action_encap_u1(dash_encapsulation : dash_encapsulation_t = dash_encapsulation_t.VXLAN,
                         vni                : Annotated[int, 24] = 0,
                         underlay_sip       : Annotated[int, IPv4Address_size] = 0,
                         underlay_dip       : Annotated[int, IPv4Address_size] = 0,
                         underlay_smac      : Annotated[int, EthernetAddress_size] = 0,
                         underlay_dmac      : Annotated[int, EthernetAddress_size] = 0):
    
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.ENCAP_U1

    meta.u0_encap_data.dash_encapsulation = dash_encapsulation
    meta.u1_encap_data.vni = meta.u1_encap_data.vni if vni == 0 else vni

    meta.u1_encap_data.underlay_smac = meta.u1_encap_data.underlay_smac if underlay_smac == 0 else underlay_smac
    meta.u1_encap_data.underlay_dmac = meta.u1_encap_data.underlay_dmac if underlay_dmac == 0 else underlay_dmac
    meta.u1_encap_data.underlay_sip = meta.u1_encap_data.underlay_sip if underlay_sip == 0 else underlay_sip
    meta.u1_encap_data.underlay_dip = meta.u1_encap_data.underlay_dip if underlay_dip == 0 else underlay_dip

class do_action_encap_u0:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0) == 0:
            return
        
        if meta.u0_encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN:
            push_vxlan_tunnel_u0(meta.u0_encap_data.underlay_dmac,
                                 meta.u0_encap_data.underlay_smac,
                                 meta.u0_encap_data.underlay_dip,
                                 meta.u0_encap_data.underlay_sip,
                                 meta.u0_encap_data.vni)

        elif meta.u0_encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE:
            push_nvgre_tunnel_u0(meta.u0_encap_data.underlay_dmac,
                                 meta.u0_encap_data.underlay_smac,
                                 meta.u0_encap_data.underlay_dip,
                                 meta.u0_encap_data.underlay_sip,
                                 meta.u0_encap_data.vni)

class do_action_encap_u1:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U1) == 0:
            return
        if meta.u1_encap_data.dash_encapsulation == dash_encapsulation_t.VXLAN:
            push_vxlan_tunnel_u1(meta.u1_encap_data.underlay_dmac,
                                 meta.u1_encap_data.underlay_smac,
                                 meta.u1_encap_data.underlay_dip,
                                 meta.u1_encap_data.underlay_sip,
                                 meta.u1_encap_data.vni)

        elif meta.u1_encap_data.dash_encapsulation == dash_encapsulation_t.NVGRE:
            push_nvgre_tunnel_u1(meta.u1_encap_data.underlay_dmac,
                                 meta.u1_encap_data.underlay_smac,
                                 meta.u1_encap_data.underlay_dip,
                                 meta.u1_encap_data.underlay_sip,
                                 meta.u1_encap_data.vni)
