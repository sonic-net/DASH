#ifndef _DASH_ROUTING_ACTION_SET_MAC_P4_
#define _DASH_ROUTING_ACTION_SET_MAC_P4_

action push_action_set_smac(
    in headers_t hdr,
    inout metadata_t meta,
    in EthernetAddress overlay_dmac)
{
    // not used by now
}

action push_action_set_dmac(
    in headers_t hdr,
    inout metadata_t meta,
    in EthernetAddress overlay_dmac)
{
    meta.routing_actions = meta.routing_actions | dash_routing_actions_t.SET_DMAC;
    meta.overlay_data.dmac = overlay_dmac;
}

control do_action_set_smac(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        // not used by now
    }
}

control do_action_set_dmac(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        if (meta.routing_actions & dash_routing_actions_t.SET_DMAC == 0) {
            return;
        }

        hdr.customer_ethernet.dst_addr = meta.overlay_data.dmac;
    }
}

#endif /* _DASH_ROUTING_ACTION_SET_MAC_P4_ */
