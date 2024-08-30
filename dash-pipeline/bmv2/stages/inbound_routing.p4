#ifndef _DASH_STAGE_INBOUND_ROUTING_P4_
#define _DASH_STAGE_INBOUND_ROUTING_P4_

#include "../dash_routing_types.p4"

control inbound_routing_stage(inout headers_t hdr,
                              inout metadata_t meta)
{
    action permit() {}

    @SaiTable[name = "pa_validation", api = "dash_pa_validation"]
    table pa_validation {
        key = {
            meta.vnet_id: exact @SaiVal[type="sai_object_id_t"];
            meta.rx_encap.underlay_sip : exact @SaiVal[name = "sip", type="sai_ip_address_t"];
        }

        actions = {
            permit;
            @defaultonly drop(meta);
        }

        const default_action = drop(meta);
    }

    action vxlan_decap() {}
    action vxlan_decap_pa_validate() {}

    action tunnel_decap(inout headers_t hdr,
                        inout metadata_t meta,
                        bit<32> meter_class_or,
                        @SaiVal[default_value="4294967295"] bit<32> meter_class_and) {
        set_meter_attrs(meta, meter_class_or, meter_class_and);
    }

    action tunnel_decap_pa_validate(inout headers_t hdr,
                                    inout metadata_t meta,
                                    @SaiVal[type="sai_object_id_t"] bit<16> src_vnet_id,
                                    bit<32> meter_class_or,
                                    @SaiVal[default_value="4294967295"] bit<32> meter_class_and) {
        meta.vnet_id = src_vnet_id;
        set_meter_attrs(meta, meter_class_or, meter_class_and);
    }

    @SaiTable[name = "inbound_routing", api = "dash_inbound_routing"]
    table inbound_routing {
        key = {
            meta.eni_id: exact @SaiVal[type="sai_object_id_t"];
            meta.rx_encap.vni : exact @SaiVal[name = "VNI"];
            meta.rx_encap.underlay_sip : ternary @SaiVal[name = "sip", type="sai_ip_address_t"];
        }
        actions = {
            tunnel_decap(hdr, meta);
            tunnel_decap_pa_validate(hdr, meta);
            vxlan_decap;                // Deprecated, but cannot be removed until SWSS is updated.
            vxlan_decap_pa_validate;    // Deprecated, but cannot be removed until SWSS is updated.
            @defaultonly drop(meta);
        }

        const default_action = drop(meta);
    }

    apply {
        if (meta.target_stage != dash_pipeline_stage_t.INBOUND_ROUTING) {
            return;
        }

        switch (inbound_routing.apply().action_run) {
            tunnel_decap_pa_validate: {
                pa_validation.apply();
            }
            drop: {
                UPDATE_ENI_COUNTER(inbound_routing_entry_miss_drop);
            }
        }
    }
}

#endif /* _DASH_STAGE_INBOUND_ROUTING_P4_ */