#ifndef _DASH_ROUTING_ACTION_NAT_PORT_P4_
#define _DASH_ROUTING_ACTION_NAT_PORT_P4_

action push_action_snat_port(
    in headers_t hdr,
    inout metadata_t meta,
    in bit<16> sport)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.SNAT_PORT;
    meta.overlay_data.sport = sport;
}

action push_action_dnat_port(
    in headers_t hdr,
    inout metadata_t meta,
    in bit<16> dport)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.DNAT_PORT;
    meta.overlay_data.dport = dport;
}

control do_action_snat_port(
    inout headers_t hdr,
    in metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.SNAT_PORT == 0) {
            return;
        }

        if (hdr.customer_tcp.isValid()) {
            hdr.customer_tcp.src_port = meta.overlay_data.sport;
        } else if (hdr.customer_udp.isValid()) {
            hdr.customer_udp.src_port = meta.overlay_data.sport;
        }
    }
}

control do_action_dnat_port(
    inout headers_t hdr,
    in metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.DNAT_PORT == 0) {
            return;
        }

        if (hdr.customer_tcp.isValid()) {
            hdr.customer_tcp.dst_port = meta.overlay_data.dport;
        } else if (hdr.customer_udp.isValid()) {
            hdr.customer_udp.dst_port = meta.overlay_data.dport;
        }
    }
}

#endif /* _DASH_ROUTING_ACTION_NAT_PORT_P4_ */
