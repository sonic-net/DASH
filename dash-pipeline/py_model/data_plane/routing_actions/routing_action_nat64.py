from py_model.libs.__utils import *
def push_action_nat64(src: Annotated[int, IPv4Address_size],
                      dst: Annotated[int, IPv4Address_size]):
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.NAT64
    meta.overlay_data.is_ipv6 = 0
    meta.overlay_data.sip = src
    meta.overlay_data.dip = dst

class do_action_nat64:    
    @classmethod
    def apply(cls):
        if (meta.routing_actions & dash_routing_actions_t.NAT64 == 0):
            return
        
        assert(meta.overlay_data.is_ipv6 == 0)
        
        hdr.u0_ipv4 = ipv4_t()
        hdr.u0_ipv4.version = 4
        hdr.u0_ipv4.ihl = 5
        hdr.u0_ipv4.diffserv = 0
        hdr.u0_ipv4.total_len = hdr.u0_ipv6.payload_length + IPV4_HDR_SIZE
        hdr.u0_ipv4.identification = 1
        hdr.u0_ipv4.flags = 0
        hdr.u0_ipv4.frag_offset = 0
        hdr.u0_ipv4.protocol = hdr.u0_ipv6.next_header
        hdr.u0_ipv4.ttl = hdr.u0_ipv6.hop_limit
        hdr.u0_ipv4.hdr_checksum = 0
        hdr.u0_ipv4.dst_addr = meta.overlay_data.dip
        hdr.u0_ipv4.src_addr = meta.overlay_data.sip
        
        hdr.u0_ipv6 = None
        hdr.u0_ethernet.ether_type = IPV4_ETHTYPE