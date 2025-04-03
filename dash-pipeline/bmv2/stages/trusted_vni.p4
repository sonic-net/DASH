#ifndef _DASH_STAGE_TRUSTED_VNI_P4_
#define _DASH_STAGE_TRUSTED_VNI_P4_

control trusted_vni_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action permit() {}

    @SaiTable[single_match_priority = "true", api = "dash_trusted_vni", order=0, isobject="false"]
    table global_trusted_vni {
        key = {
            meta.rx_encap.vni: range @SaiVal[name = "vni_range"];
        }

        actions = {
            permit;
        }
    }

    @SaiTable[single_match_priority = "true", api = "dash_trusted_vni", order=1]
    table eni_trusted_vni {
        key = {
            meta.eni_id : exact @SaiVal[type="sai_object_id_t"];
            meta.rx_encap.vni: range @SaiVal[name = "vni_range"];
        }

        actions = {
            permit;
            @defaultonly deny(meta);
        }
        const default_action = deny(meta);
    }

    apply {
        if (global_trusted_vni.apply().hit) {
            return;
        }

        if (!eni_trusted_vni.apply().hit) {
            UPDATE_ENI_COUNTER(eni_trusted_vni_entry_miss_drop);
        }
    }
}

#endif /* _DASH_STAGE_TRUSTED_VNI_P4_ */
