#ifndef _SIRIUS_CONNTRACK_P4_
#define _SIRIUS_CONNTRACK_P4_

#include "sirius_headers.p4"

#ifdef STATEFUL_P4

state_context ConntrackCtx {
}

state_graph ConnGraphOut(inout state_context flow_ctx,
                             in headers_t headers,
                             in standard_metadata_t standard_metadata)
{
    state START {
        /* Only for new connections */
        if (!headers.tcp.isValid() || headers.tcp.flags != 0x2 /* SYN */) {
            return;
        }

        if (meta.direction == INBOUND) {
            transition ALLOW;
        }
    }

    state ALLOW {
        meta.conntrack_data.allow_out = true;

        /* Remove connection based on TCP flags */
        if (headers.tcp.flags & 0x101 /* FIN/RST */) {
            transition START;
        }
    }
}

state_graph ConnGraphIn(inout state_context flow_ctx,
                             in headers_t headers,
                             in standard_metadata_t standard_metadata)
{
    state START {
        /* Only for new connections */
        if (!headers.tcp.isValid() || headers.tcp.flags != 0x2 /* SYN */) {
            return;
        }

        if (meta.direction == OUTBOUND) {
            transition ALLOW;
        }
    }

    state ALLOW {
        meta.conntrack_data.allow_in = true;

        /* Remove connection based on TCP flags */
        if (headers.tcp.flags & 0x101 /* FIN/RST */) {
            transition START;
        }
    }
}

state_table ConntrackOut
{
    flow_key[0] = {hdr.ipv4.src, hdr.ipv4.dst , hdr.ipv4.proto, hdr.l4.src_port, hdr.l4.dst_port, meta.eni};
    flow_key[1] = {hdr.ipv4.dst, hdr.ipv4.src , hdr.ipv4.proto, hdr.l4.dst_port, hdr.l4.src_port, meta.eni};
    eviction_policy = LRU;
    context = ConntrackCtx;
    graph = ConnGraphOut(ConntrackCtx, hdr, standard_metadata);
}

state_table ConntrackIn
{
    flow_key[0] = {hdr.ipv4.src, hdr.ipv4.dst , hdr.ipv4.proto, hdr.l4.src_port, hdr.l4.dst_port, meta.eni};
    flow_key[1] = {hdr.ipv4.dst, hdr.ipv4.src , hdr.ipv4.proto, hdr.l4.dst_port, hdr.l4.src_port, meta.eni};
    eviction_policy = LRU;
    context = ConntrackCtx;
    graph = ConnGraphIn(ConntrackCtx, hdr, standard_metadata);
}

#endif /* STATEFUL_P4 */

#endif /* _SIRIUS_CONNTRACK_P4_ */
