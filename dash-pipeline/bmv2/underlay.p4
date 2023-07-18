#include <core.p4>
#include "dash_headers.p4"
#include "dash_metadata.p4"

control underlay(
      inout headers_t hdr
    , inout metadata_t meta
#ifdef TARGET_BMV2_V1MODEL
    , inout standard_metadata_t standard_metadata
#endif // TARGET_BMV2_V1MODEL
#ifdef TARGET_DPDK_PNA
    , in    pna_main_input_metadata_t  istd
#endif // TARGET_DPDK_PNA  
    ) 
{
    action set_nhop(bit<9> next_hop_id) {
#ifdef TARGET_BMV2_V1MODEL
        standard_metadata.egress_spec = next_hop_id;
#endif // TARGET_BMV2_V1MODEL

#ifdef TARGET_DPDK_PNA
#ifdef DPDK_PNA_SEND_TO_PORT_FIX_MERGED
        // As of 2023-Jan-26, the version of the pna.p4 header file
        // included with p4c defines send_to_port with a parameter
        // that has no 'in' direction.  The following commit in the
        // public pna repo fixes this, but this fix has not yet been
        // copied into the p4c repo.
        // https://github.com/p4lang/pna/commit/b9fdfb888e5385472c34ff773914c72b78b63058
        // Until p4c is updated with this fix, the following line will
        // give a compile-time error.
        istd.input_port = next_hop_id;
        send_to_port(istd.input_port);
#endif  // DPDK_PNA_SEND_TO_PORT_FIX_MERGED
#endif // TARGET_DPDK_PNA  
    }

    action def_act() {
#ifdef TARGET_BMV2_V1MODEL
        standard_metadata.egress_spec = standard_metadata.ingress_port;
#endif // TARGET_BMV2_V1MODEL

#ifdef TARGET_DPDK_PNA
#ifdef DPDK_PNA_SEND_TO_PORT_FIX_MERGED
        // As of 2023-Jan-26, the version of the pna.p4 header file
        // included with p4c defines send_to_port with a parameter
        // that has no 'in' direction.  The following commit in the
        // public pna repo fixes this, but this fix has not yet been
        // copied into the p4c repo.
        // https://github.com/p4lang/pna/commit/b9fdfb888e5385472c34ff773914c72b78b63058
        // Until p4c is updated with this fix, the following line will
        // give a compile-time error.
        send_to_port(istd.input_port);
#endif  // DPDK_PNA_SEND_TO_PORT_FIX_MERGED
#endif // TARGET_DPDK_PNA
    }

    @name("route|route")
    // TODO: To add structural annotations (example: @Sai[skipHeaderGen=true])
    table underlay_routing {
        key = {
            meta.dst_ip_addr : lpm @name("meta.dst_ip_addr:destination");
        }

        actions = {
            /* Send packet on different/same port it arrived based on routing */
            set_nhop;

            /* Send packet on same port it arrived (echo) by default */
            @defaultonly def_act;
        }
    }

    apply {
        underlay_routing.apply();
    }
}
