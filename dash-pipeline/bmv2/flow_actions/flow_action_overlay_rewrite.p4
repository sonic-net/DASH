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
        hdr.customer_ipv4.dst_addr = (IPv4Address)((IPv6Address)meta.overlay_data.dip & meta.overlay_data.dip_mask);
        hdr.customer_ipv4.src_addr = (IPv4Address)((IPv6Address)meta.overlay_data.sip & meta.overlay_data.sip_mask);
        hdr.customer_ethernet.dst_addr = meta.overlay_data.dmac;
        hdr.customer_ethernet.ether_type = IPV4_ETHTYPE;
    }
}

#endif /* _DASH_FLOW_ACTION_OVERLAY_REWRITE_P4_ */