
control dash_verify_checksum(inout headers_t hdr,
                         inout metadata_t meta)
{
    apply { }
}

control dash_compute_checksum(inout headers_t hdr,
                          inout metadata_t meta)
{
    apply {
#ifdef TARGET_BMV2_V1MODEL
        update_checksum(
         hdr.u0_ipv4.isValid(),
         {
             hdr.u0_ipv4.version,
             hdr.u0_ipv4.ihl,
             hdr.u0_ipv4.diffserv,
             hdr.u0_ipv4.total_len,
             hdr.u0_ipv4.identification,
             hdr.u0_ipv4.frag_offset,
             hdr.u0_ipv4.flags,
             hdr.u0_ipv4.ttl,
             hdr.u0_ipv4.protocol,
             hdr.u0_ipv4.src_addr,
             hdr.u0_ipv4.dst_addr
         },
         hdr.u0_ipv4.hdr_checksum,
         HashAlgorithm.csum16);
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
