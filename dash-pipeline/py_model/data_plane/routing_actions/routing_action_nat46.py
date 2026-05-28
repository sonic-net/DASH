from py_model.libs.__utils import *

def push_action_nat46(sip:          Annotated[int, IPv6Address_size],
                      sip_mask:     Annotated[int, IPv6Address_size],
                      dip:          Annotated[int, IPv6Address_size],
                      dip_mask:     Annotated[int, IPv6Address_size]):
    
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.NAT46
    meta.overlay_data.is_ipv6 = 1
    meta.overlay_data.sip = sip
    meta.overlay_data.sip_mask = sip_mask
    meta.overlay_data.dip = dip
    meta.overlay_data.dip_mask = dip_mask
    
class do_action_nat46:
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.NAT46 == 0):
            return

        assert(meta.overlay_data.is_ipv6 == 1);            

        hdr.u0_ipv6 = ipv6_t()
        hdr.u0_ipv6.version = 6
        hdr.u0_ipv6.traffic_class = 0
        hdr.u0_ipv6.flow_label = 0
        hdr.u0_ipv6.payload_length = hdr.u0_ipv4.total_len - IPV4_HDR_SIZE
        hdr.u0_ipv6.next_header = hdr.u0_ipv4.protocol
        hdr.u0_ipv6.hop_limit = hdr.u0_ipv4.ttl

        # Python support arithmetic on 128-bit operands
        hdr.u0_ipv6.dst_addr = (hdr.u0_ipv4.dst_addr & ~meta.overlay_data.dip_mask) | (meta.overlay_data.dip & meta.overlay_data.dip_mask)
        hdr.u0_ipv6.src_addr = (hdr.u0_ipv4.src_addr & ~meta.overlay_data.sip_mask) | (meta.overlay_data.sip & meta.overlay_data.sip_mask)

        hdr.u0_ipv4 = None
        hdr.u0_ethernet.ether_type = IPV6_ETHTYPE