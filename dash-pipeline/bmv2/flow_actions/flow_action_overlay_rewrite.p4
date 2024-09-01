#ifndef _DASH_FLOW_ACTION_OVERLAY_REWRITE_P4_
#define _DASH_FLOW_ACTION_OVERLAY_REWRITE_P4_

control do_action_overlay_rewrite(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.conntrack_data.flow_data.actions & dash_flow_action_t.OVERLAY_REWRITE == 0) {
            return;
        }

        REQUIRES(meta.overlay_data.is_ipv6 == false);

        hdr.customer_ipv4.setValid();
        hdr.customer_ipv4.version = 4;
        hdr.customer_ipv4.ihl = 5;
        hdr.customer_ipv4.diffserv = 0;
        hdr.customer_ipv4.total_len = hdr.customer_ipv6.payload_length + IPV4_HDR_SIZE;
        hdr.customer_ipv4.identification = 1;
        hdr.customer_ipv4.flags = 0;
        hdr.customer_ipv4.frag_offset = 0;
        hdr.customer_ipv4.protocol = hdr.customer_ipv6.next_header;
        hdr.customer_ipv4.ttl = hdr.customer_ipv6.hop_limit;
        hdr.customer_ipv4.hdr_checksum = 0;
        hdr.customer_ipv4.dst_addr = (IPv4Address)((IPv6Address)meta.overlay_data.dip & meta.overlay_data.dip_mask);
        hdr.customer_ipv4.src_addr = (IPv4Address)((IPv6Address)meta.overlay_data.sip & meta.overlay_data.sip_mask);
        
        hdr.customer_ipv6.setInvalid();
        hdr.customer_ethernet.dst_addr = meta.overlay_data.dmac;
        hdr.customer_ethernet.ether_type = IPV4_ETHTYPE;
    }
}

#endif /* _DASH_FLOW_ACTION_OVERLAY_REWRITE_P4_ */