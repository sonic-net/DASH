
control dash_verify_checksum(inout headers_t hdr,
                         inout metadata_t meta)
{
    apply { }
}

#define UPDATE_IPV4_CHECKSUM(IPHDR) \
    update_checksum( \
        IPHDR.isValid(), \
        { \
            IPHDR.version, \
            IPHDR.ihl, \
            IPHDR.diffserv, \
            IPHDR.total_len, \
            IPHDR.identification, \
            IPHDR.frag_offset, \
            IPHDR.flags, \
            IPHDR.ttl, \
            IPHDR.protocol, \
            IPHDR.src_addr, \
            IPHDR.dst_addr \
        }, \
        IPHDR.hdr_checksum, \
        HashAlgorithm.csum16)

control dash_compute_checksum(inout headers_t hdr,
                          inout metadata_t meta)
{
    apply {
#ifdef TARGET_BMV2_V1MODEL
        UPDATE_IPV4_CHECKSUM(hdr.u0_ipv4);
        UPDATE_IPV4_CHECKSUM(hdr.u1_ipv4);
#endif // TARGET_BMV2_V1MODEL
    }
}

control dash_egress(inout headers_t hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata)
{
    apply { }
}

V1Switch(dash_parser(),
         dash_verify_checksum(),
         dash_ingress(),
         dash_egress(),
         dash_compute_checksum(),
         dash_deparser()) main;
