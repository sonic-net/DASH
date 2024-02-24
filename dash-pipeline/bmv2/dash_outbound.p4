#ifndef _SIRIUS_OUTBOUND_P4_
#define _SIRIUS_OUTBOUND_P4_

#include "dash_headers.p4"
#include "dash_acl.p4"
#include "dash_routing_types.p4"
#include "dash_conntrack.p4"

control outbound(inout headers_t hdr,
                 inout metadata_t meta)
{
#ifdef TARGET_BMV2_V1MODEL
    direct_counter(CounterType.packets_and_bytes) routing_counter;
#elif TARGET_DPDK_PNA   // TARGET_BMV2_V1MODEL
#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
    // See the #ifdef with same preprocessor symbol in dash_pipeline.p4
    DirectCounter<bit<64>>(PNA_CounterType_t.PACKETS_AND_BYTES) routing_counter;
#endif  // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
#endif  // TARGET_DPDK_PNA

    @SaiTable[name = "outbound_routing", api = "dash_outbound_routing"]
    table routing {
        key = {
            meta.eni_id : exact @SaiVal[type="sai_object_id_t"];
            meta.is_overlay_ip_v6 : exact @SaiVal[name = "destination_is_v6"];
            meta.dst_ip_addr : lpm @SaiVal[name = "destination"];
        }

        actions = {
            route_vnet(hdr, meta); /* for expressroute - ecmp of overlay */
            route_vnet_direct(hdr, meta);
            route_direct(hdr, meta);
            route_service_tunnel(hdr, meta);
            drop(meta);
        }
        const default_action = drop(meta);

#ifdef TARGET_BMV2_V1MODEL
        counters = routing_counter;
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
        pna_direct_counter = routing_counter;
#endif // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
#endif // TARGET_DPDK_PNA
    }

#ifdef TARGET_BMV2_V1MODEL
    direct_counter(CounterType.packets_and_bytes) ca_to_pa_counter;
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
    DirectCounter<bit<64>>(PNA_CounterType_t.PACKETS_AND_BYTES) ca_to_pa_counter;
#endif  // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
#endif  // TARGET_DPDK_PNA

    @SaiTable[name = "outbound_ca_to_pa", api = "dash_outbound_ca_to_pa"]
    table ca_to_pa {
        key = {
            /* Flow for express route */
            meta.dst_vnet_id: exact @SaiVal[type="sai_object_id_t"];
            meta.is_lkup_dst_ip_v6 : exact @SaiVal[name = "dip_is_v6"];
            meta.lkup_dst_ip_addr : exact @SaiVal[name = "dip"];
        }

        actions = {
            set_tunnel_mapping(hdr, meta);
            set_private_link_mapping(hdr, meta);
            @defaultonly drop(meta);
        }
        const default_action = drop(meta);

#ifdef TARGET_BMV2_V1MODEL
        counters = ca_to_pa_counter;
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
        pna_direct_counter = ca_to_pa_counter;
#endif // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
#endif // TARGET_DPDK_PNA
    }

    action set_vnet_attrs(bit<24> vni) {
        meta.encap_data.vni = vni;
    }

    @SaiTable[name = "vnet", api = "dash_vnet", isobject="true"]
    table vnet {
        key = {
            meta.vnet_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_vnet_attrs;
        }
    }

    apply {
#ifdef STATEFUL_P4
           ConntrackOut.apply(0);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackOut.apply(hdr, meta);
#endif // PNA_CONNTRACK

        /* ACL */
        if (!meta.conntrack_data.allow_out) {
            acl.apply(hdr, meta);
        }

#ifdef STATEFUL_P4
            ConntrackIn.apply(1);
#endif /* STATEFUL_P4 */

#ifdef PNA_CONNTRACK
        ConntrackIn.apply(hdr, meta);
#endif // PNA_CONNTRACK

        meta.lkup_dst_ip_addr = meta.dst_ip_addr;
        meta.is_lkup_dst_ip_v6 = meta.is_overlay_ip_v6;

        switch (routing.apply().action_run) {
            route_vnet_direct:
            route_vnet: {
                switch (ca_to_pa.apply().action_run) {
                    set_tunnel_mapping: {
                        vnet.apply();
                    }
                }

                tunnel_encap(hdr,
                             meta,
                             meta.encap_data.overlay_dmac,
                             meta.encap_data.underlay_dmac,
                             meta.encap_data.underlay_smac,
                             meta.encap_data.underlay_dip,
                             meta.encap_data.underlay_sip,
                             meta.encap_data.dash_encapsulation,
                             meta.encap_data.vni);
             }
           route_service_tunnel: {
                tunnel_encap(hdr,
                             meta,
                             meta.encap_data.overlay_dmac,
                             meta.encap_data.underlay_dmac,
                             meta.encap_data.underlay_smac,
                             meta.encap_data.underlay_dip,
                             meta.encap_data.underlay_sip,
                             meta.encap_data.dash_encapsulation,
                             meta.encap_data.vni);
             }
         }
    }
}

#endif /* _SIRIUS_OUTBOUND_P4_ */
