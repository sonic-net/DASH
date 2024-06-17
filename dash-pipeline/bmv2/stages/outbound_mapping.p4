#ifndef _DASH_STAGE_OUTBOUND_MAPPING_P4_
#define _DASH_STAGE_OUTBOUND_MAPPING_P4_

#include "../dash_routing_types.p4"

control outbound_mapping_stage(inout headers_t hdr,
                      inout metadata_t meta)
{
    DEFINE_TABLE_COUNTER(ca_to_pa_counter)

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
        size = 8388608;
        const default_action = drop(meta);

        ATTACH_TABLE_COUNTER(ca_to_pa_counter)
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
        if (meta.target_stage != dash_pipeline_stage_t.OUTBOUND_MAPPING) {
            return;
        }
        
        switch (ca_to_pa.apply().action_run) {
            set_tunnel_mapping: {
                vnet.apply();
            }
            drop: {
                UPDATE_ENI_COUNTER(outbound_ca_pa_entry_miss_drop);
            }
        }
    }
}

#endif /* _DASH_STAGE_OUTBOUND_MAPPING_P4_ */
