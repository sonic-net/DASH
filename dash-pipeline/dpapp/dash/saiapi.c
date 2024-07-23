
#include <arpa/inet.h>

#include <dash/dash.h>
#include <dash/flow.h>

#include <sai.h>
#include <saiextensions.h>

static sai_object_id_t dash_switch_id = SAI_NULL_OBJECT_ID;
static sai_dash_flow_api_t *dash_flow_api = NULL;

void
dash_sai_init ()
{
    sai_status_t status;

    status = sai_api_initialize(0, NULL);
    ASSERT_MSG(status == SAI_STATUS_SUCCESS, "Failed to initialize SAI api");

    sai_switch_api_t *switch_api;
    status = sai_api_query((sai_api_t)SAI_API_SWITCH, (void**)&switch_api);
    ASSERT_MSG(status == SAI_STATUS_SUCCESS, "Failed to query SAI_API_SWITCH");

    status = switch_api->create_switch(&dash_switch_id, 0, NULL);
    ASSERT_MSG(status == SAI_STATUS_SUCCESS, "Failed to create switch");

    status = sai_api_query((sai_api_t)SAI_API_DASH_FLOW, (void**)&dash_flow_api);
    ASSERT_MSG(status == SAI_STATUS_SUCCESS, "Failed to query SAI_API_DASH_FLOW");

    dash_log_info("Succeeded to init dash sai api");
}

sai_status_t
dash_sai_create_flow_entry (const dash_flow_entry_t *flow)
{
    sai_flow_entry_t flow_entry;
    u32 count = 0;
    sai_attribute_t attrs[SAI_FLOW_ENTRY_ATTR_END];
    const flow_key_t *flow_key = &flow->key;
    const flow_data_t *flow_data = &flow->flow_data;
    const overlay_rewrite_data_t *flow_overlay_data = &flow->flow_overlay_data;
    const encap_data_t *flow_u0_encap_data = &flow->flow_u0_encap_data;
    const encap_data_t *flow_u1_encap_data = &flow->flow_u1_encap_data;

    /*
     * Fill sai_flow_entry_t, sai_attribute_t, whose values need host order
     * ip4/6 address in network order
     */
    flow_entry.switch_id = dash_switch_id;
    clib_memcpy_fast(flow_entry.eni_mac, flow_key->eni_mac, sizeof(flow_entry.eni_mac));
    flow_entry.vnet_id = ntohs(flow_key->vnet_id);
    if (flow_key->is_ip_v6) {
        flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(flow_entry.src_ip.addr.ip6, &flow_key->src_ip.ip6, sizeof(sai_ip6_t));
        flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(flow_entry.dst_ip.addr.ip6, &flow_key->dst_ip.ip6, sizeof(sai_ip6_t));
    } else {
        flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        flow_entry.src_ip.addr.ip4 = flow_key->src_ip.ip4.as_u32;
        flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        flow_entry.dst_ip.addr.ip4 = flow_key->dst_ip.ip4.as_u32;
    }
    flow_entry.src_port = ntohs(flow_key->src_port);
    flow_entry.dst_port = ntohs(flow_key->dst_port);
    flow_entry.ip_proto = flow_key->ip_proto;

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_ACTION;
    attrs[count++].value.u32 = SAI_FLOW_ENTRY_ACTION_SET_FLOW_ENTRY_ATTR;

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_VERSION;
    attrs[count++].value.u32 = ntohl(flow_data->version);

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_DASH_DIRECTION;
    attrs[count++].value.u16 = ntohs(flow_data->direction);

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_DASH_FLOW_ACTION;
    attrs[count++].value.u32 = ntohl(flow_data->actions);

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_METER_CLASS;
    attrs[count++].value.u32 = ntohl(flow_data->meter_class);

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_IS_UNIDIRECTIONAL_FLOW;
    attrs[count++].value.booldata = flow_data->is_unidirectional;

    attrs[count].id = SAI_FLOW_ENTRY_ATTR_DASH_FLOW_SYNC_STATE;
    attrs[count++].value.u8 = SAI_DASH_FLOW_SYNC_STATE_FLOW_CREATED;

    /* FIXME: Attrs for reverse flow key */
    {
        u8 mac[6] = {0};
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_REVERSE_FLOW_ENI_MAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;
    }

    /* Attrs for overlay rewrite data */
    if (flow_data->actions != 0) {
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_DST_MAC;
        clib_memcpy_fast(attrs[count].value.mac, flow_overlay_data->dmac, sizeof(ethernet_header_t));
        count++;

        if (flow_overlay_data->is_ipv6) {
            attrs[count].id = SAI_FLOW_ENTRY_ATTR_SIP;
            attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
            clib_memcpy_fast(attrs[count].value.ipaddr.addr.ip6,
                             &flow_overlay_data->sip.ip6, sizeof(sai_ip6_t));
            count++;

            attrs[count].id = SAI_FLOW_ENTRY_ATTR_DIP;
            attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
            clib_memcpy_fast(attrs[count].value.ipaddr.addr.ip6,
                             &flow_overlay_data->dip.ip6, sizeof(sai_ip6_t));
            count++;
        } else {
            attrs[count].id = SAI_FLOW_ENTRY_ATTR_SIP;
            attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
            attrs[count++].value.ipaddr.addr.ip4 = flow_overlay_data->sip.ip4.as_u32;

            attrs[count].id = SAI_FLOW_ENTRY_ATTR_DIP;
            attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
            attrs[count++].value.ipaddr.addr.ip4 = flow_overlay_data->dip.ip4.as_u32;
        }

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_SIP_MASK;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(attrs[count].value.ipaddr.addr.ip6,
                         &flow_overlay_data->sip_mask, sizeof(sai_ip6_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_DIP_MASK;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(attrs[count].value.ipaddr.addr.ip6,
                         &flow_overlay_data->dip_mask, sizeof(sai_ip6_t));
        count++;
    } else {
        u8 mac[6] = {0};
        /* set default value for bmv2 table */
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_DST_MAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;
    }

    /* Attrs for encap data of underlay 0 */
    if (flow_data->actions & htonl(SAI_DASH_FLOW_ACTION_ENCAP_U0)) {
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_VNET_ID;
        attrs[count++].value.u32 = ntohs(flow_u0_encap_data->vni_high) << 8 | flow_u0_encap_data->vni_low;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_SIP;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        attrs[count++].value.ipaddr.addr.ip4 = flow_u0_encap_data->underlay_sip.as_u32;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DIP;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        attrs[count++].value.ipaddr.addr.ip4 = flow_u0_encap_data->underlay_dip.as_u32;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_SMAC;
        clib_memcpy_fast(attrs[count].value.mac, flow_u0_encap_data->underlay_smac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DMAC;
        clib_memcpy_fast(attrs[count].value.mac, flow_u0_encap_data->underlay_dmac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DASH_ENCAPSULATION;
        attrs[count++].value.s32 = ntohs(flow_u0_encap_data->dash_encapsulation);
    } else {
        u8 mac[6] = {0};
        /* set default value for bmv2 table */
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_SMAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY0_DMAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;
    }

    /* Attrs for encap data of underlay 1 */
    if (flow_data->actions & htonl(SAI_DASH_FLOW_ACTION_ENCAP_U1)) {
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_VNET_ID;
        attrs[count++].value.u32 = ntohs(flow_u1_encap_data->vni_high) << 8 | flow_u1_encap_data->vni_low;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SIP;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        attrs[count++].value.ipaddr.addr.ip4 = flow_u1_encap_data->underlay_sip.as_u32;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DIP;
        attrs[count].value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        attrs[count++].value.ipaddr.addr.ip4 = flow_u1_encap_data->underlay_dip.as_u32;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SMAC;
        clib_memcpy_fast(attrs[count].value.mac, flow_u1_encap_data->underlay_smac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DMAC;
        clib_memcpy_fast(attrs[count].value.mac, flow_u1_encap_data->underlay_dmac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DASH_ENCAPSULATION;
        attrs[count++].value.s32 = ntohs(flow_u1_encap_data->dash_encapsulation);
    } else {
        u8 mac[6] = {0};
        /* set default value for bmv2 table */
        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_SMAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;

        attrs[count].id = SAI_FLOW_ENTRY_ATTR_UNDERLAY1_DMAC;
        clib_memcpy_fast(attrs[count].value.mac, mac, sizeof(ethernet_header_t));
        count++;
    }

    return dash_flow_api->create_flow_entry(&flow_entry, count, attrs);
}

sai_status_t
dash_sai_remove_flow_entry (const dash_flow_entry_t *flow)
{
    sai_flow_entry_t flow_entry;
    const flow_key_t *flow_key = &flow->key;

    flow_entry.switch_id = dash_switch_id;
    clib_memcpy_fast(flow_entry.eni_mac, flow_key->eni_mac, sizeof(flow_entry.eni_mac));
    flow_entry.vnet_id = ntohs(flow_key->vnet_id);

    if (flow_key->is_ip_v6) {
        flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(flow_entry.src_ip.addr.ip6, &flow_key->src_ip.ip6, sizeof(sai_ip6_t));
        flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        clib_memcpy_fast(flow_entry.dst_ip.addr.ip6, &flow_key->dst_ip.ip6, sizeof(sai_ip6_t));
    } else {
        flow_entry.src_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        flow_entry.src_ip.addr.ip4 = flow_key->src_ip.ip4.as_u32;
        flow_entry.dst_ip.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
        flow_entry.dst_ip.addr.ip4 = flow_key->dst_ip.ip4.as_u32;
    }

    flow_entry.src_port = ntohs(flow_key->src_port);
    flow_entry.dst_port = ntohs(flow_key->dst_port);
    flow_entry.ip_proto = flow_key->ip_proto;

    return dash_flow_api->remove_flow_entry(&flow_entry);
}

