#ifndef _DASH_STAGE_PRE_PIPELINE_P4_
#define _DASH_STAGE_PRE_PIPELINE_P4_

control pre_pipeline_stage(inout headers_t hdr,
                           inout metadata_t meta)
{
    action accept() {}

    action set_appliance(bit<8> local_region_id) {
        meta.local_region_id = local_region_id;
    }

    @SaiTable[name = "dash_appliance", api = "dash_appliance", order = 0, isobject="true"]
    table appliance {
        key = {
            meta.appliance_id : exact @SaiVal[type="sai_object_id_t"];
        }

        actions = {
            set_appliance;
            @defaultonly accept;
        }
        const default_action = accept;
    }

    action set_underlay_mac(EthernetAddress neighbor_mac,
                            EthernetAddress mac) {
        meta.encap_data.underlay_dmac = neighbor_mac;
        meta.encap_data.underlay_smac = mac;
    }

    /* This table API should be implemented manually using underlay SAI */
    @SaiTable[ignored = "true"]
    table underlay_mac {
        key = {
            meta.appliance_id : ternary;
        }

        actions = {
            set_underlay_mac;
        }
    }

    @SaiTable[name = "vip", api = "dash_vip"]
    table vip {
        key = {
            meta.rx_encap.underlay_dip : exact @SaiVal[name = "VIP", type="sai_ip_address_t"];
        }

        actions = {
            accept;
            @defaultonly drop(meta);
        }

        const default_action = drop(meta);
    }

    apply {
        // Normalize the outer headers.
        // This helps us handling multiple encaps and different type of encaps in the future and simplify the later packet processing.
        meta.rx_encap.underlay_smac = hdr.u0_ethernet.src_addr;
        meta.rx_encap.underlay_dmac = hdr.u0_ethernet.dst_addr;

        if (hdr.u0_ipv4.isValid()) {
            meta.rx_encap.underlay_sip = hdr.u0_ipv4.src_addr;
            meta.rx_encap.underlay_dip = hdr.u0_ipv4.dst_addr;
        }
        // IPv6 encap on received packet is not supported yet.
        // else if ((hdr.u0_ipv6.isValid()) {
        //     meta.rx_encap.underlay_sip = hdr.u0_ipv6.src_addr;
        //     meta.rx_encap.underlay_dip = hdr.u0_ipv6.dst_addr;
        // }

        meta.rx_encap.dash_encapsulation = dash_encapsulation_t.VXLAN;
        meta.rx_encap.vni = hdr.u0_vxlan.vni;

        // Save the original DSCP value
        meta.eni_data.dscp_mode = dash_tunnel_dscp_mode_t.PRESERVE_MODEL;
        meta.eni_data.dscp = (bit<6>)hdr.u0_ipv4.diffserv;

        // Normalize the customer headers for later lookups.
        meta.is_overlay_ip_v6 = 0;
        meta.ip_protocol = 0;
        meta.dst_ip_addr = 0;
        meta.src_ip_addr = 0;
        if (hdr.customer_ipv6.isValid()) {
            meta.ip_protocol = hdr.customer_ipv6.next_header;
            meta.src_ip_addr = hdr.customer_ipv6.src_addr;
            meta.dst_ip_addr = hdr.customer_ipv6.dst_addr;
            meta.is_overlay_ip_v6 = 1;
        } else if (hdr.customer_ipv4.isValid()) {
            meta.ip_protocol = hdr.customer_ipv4.protocol;
            meta.src_ip_addr = (bit<128>)hdr.customer_ipv4.src_addr;
            meta.dst_ip_addr = (bit<128>)hdr.customer_ipv4.dst_addr;
        }

        if (hdr.customer_tcp.isValid()) {
            meta.src_l4_port = hdr.customer_tcp.src_port;
            meta.dst_l4_port = hdr.customer_tcp.dst_port;
        } else if (hdr.customer_udp.isValid()) {
            meta.src_l4_port = hdr.customer_udp.src_port;
            meta.dst_l4_port = hdr.customer_udp.dst_port;
        }

        // The pipeline starts from here and we can use the normalized headers for processing.
        if (meta.is_fast_path_icmp_flow_redirection_packet) {
            UPDATE_COUNTER(port_lb_fast_path_icmp_in, 0);
        }

        if (vip.apply().hit) {
            /* Use the same VIP that was in packet's destination if it's present in the VIP table */
            meta.encap_data.underlay_sip = meta.rx_encap.underlay_dip;
        } else {
            UPDATE_COUNTER(vip_miss_drop, 0);

            if (meta.is_fast_path_icmp_flow_redirection_packet) {
            }
        }

        appliance.apply();
        underlay_mac.apply();
    }
}

#endif // _DASH_STAGE_PRE_PIPELINE_P4_
