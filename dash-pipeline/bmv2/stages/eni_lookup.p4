#ifndef _DASH_STAGE_ENI_LOOKUP_P4_
#define _DASH_STAGE_ENI_LOOKUP_P4_

control eni_lookup_stage(
    inout headers_t hdr,
    inout metadata_t meta)
{
    DEFINE_COUNTER(port_lb_fast_path_eni_miss_counter, 1, name="lb_fast_path_eni_miss", attr_type="stats")

    action set_eni(@SaiVal[type="sai_object_id_t"] bit<16> eni_id) {
        meta.eni_id = eni_id;
    }

    action deny() {
        meta.dropped = true;
    }
    
    @SaiTable[name = "eni_ether_address_map", api = "dash_eni", order=0]
    table eni_ether_address_map {
        key = {
            meta.eni_addr : exact @SaiVal[name = "address", type = "sai_mac_t"];
        }

        actions = {
            set_eni;
            @defaultonly deny;
        }
        const default_action = deny;
    }

    apply {
        /* Put VM's MAC in the direction agnostic metadata field */
        meta.eni_addr = meta.direction == dash_direction_t.OUTBOUND  ?
                                          hdr.customer_ethernet.src_addr :
                                          hdr.customer_ethernet.dst_addr;
                                          
        if (!eni_ether_address_map.apply().hit) {
            if (meta.is_fast_path_icmp_flow_redirection_packet) {
                UPDATE_COUNTER(port_lb_fast_path_eni_miss_counter, 0);
            }
        }
    }
}

#endif /* _DASH_STAGE_ENI_LOOKUP_P4_ */