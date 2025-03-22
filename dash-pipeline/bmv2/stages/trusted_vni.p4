#ifndef _DASH_STAGE_TRUSTED_VNI_P4_
#define _DASH_STAGE_TRUSTED_VNI_P4_

control trusted_vni_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    action permit() {}

    action deny() {
        meta.dropped = true;
    }

    @SaiTable[single_match_priority = "true", api = "dash_trusted_vni"]
    table trusted_vni {
        key = {
            meta.eni_id : exact @SaiVal[type="sai_object_id_t"];
            meta.rx_encap.vni: range @SaiVal[name = "vni_range"];
        }

        actions = {
            permit;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    apply {
        trusted_vni.apply();
    }
}

#endif /* _DASH_STAGE_TRUSTED_VNI_P4_ */
