#ifndef _SIRIUS_CONNTRACK_P4_
#define _SIRIUS_CONNTRACK_P4_

#include "sirius_headers.p4"

#ifdef PNA_CONNTRACK

#include pna.p4

const ExpireTimeProfileId_t EXPIRE_TIME_PROFILE_NOW    = (ExpireTimeProfileId_t) 0;
const ExpireTimeProfileId_t EXPIRE_TIME_PROFILE_LONG   = (ExpireTimeProfileId_t) 2;


action conntrackIn_allow () {
/* Invalidate entry based on TCP flags */
        if (headers.tcp.flags & 0x101 /* FIN/RST */) {
          set_entry_expire_time(EXPIRE_TIME_PROFILE_NOW); // New PNA extern
          /* set entry to be purged */
        }
        restart_expire_timer(); // reset expiration timer for entry
        meta.conntrack_data.allow_in = true;
}

action conntrackIn_miss() {
        if (headers.tcp.flags == 0x2 /* SYN */) {
          if (meta.direction == OUTBOUND) {
             add_entry("conntrackIn_allow"); // New PNA Extern
             //adding failiure to be eventually handled
             set_entry_expire_time(EXPIRE_TIME_PROFILE_LONG);
          }
        }
}

table contrackIn {
    key = {
        directionNeutralAddr(meta.direction, hdr.ipv4.srcAddr, hdr.ipv4.dstAddr):
            exact;
        directionNeutralAddr(meta.direction, hdr.ipv4.dstAddr, hdr.ipv4.srcAddr):
            exact;
        hdr.ipv4.protocol : exact;
        directionNeutralPort(meta.direction, hdr.tcp.srcPort, hdr.tcp.dstPort):
            exact;
        directionNeutralPort(meta.direction, hdr.tcp.dstPort, hdr.tcp.srcPort):
            exact;
    }
    actions = {
        conntrackIn_allow;
        conntrackIn_miss;
    }

    add_on_miss = true; //New PNA property

    idle_timeout_with_auto_delete = true; // New PNA property
    const default_action = conntrackIn_miss; //New PNA property
}

action conntrackOut_allow () {
/* Invalidate entry based on TCP flags */
        if (headers.tcp.flags & 0x101 /* FIN/RST */) {
          set_entry_expire_time(EXPIRE_TIME_PROFILE_NOW); // New PNA extern
          /* set entry to be purged */
        }
        restart_expire_timer(); // reset expiration timer for entry
        meta.conntrack_data.allow_out = true;
}

action conntrackOut_miss() {
        if (headers.tcp.flags == 0x2 /* SYN */) {
          if (meta.direction == INBOUND) {
             add_entry("ConntrackOut_allow"); // New PNA Extern
             //adding failiure to be eventually handled
             set_entry_expire_time(EXPIRE_TIME_PROFILE_LONG);
          }
        }
}

table ConntrackOut {
    key = {
        directionNeutralAddr(meta.direction, hdr.ipv4.srcAddr, hdr.ipv4.dstAddr):
            exact;
        directionNeutralAddr(meta.direction, hdr.ipv4.dstAddr, hdr.ipv4.srcAddr):
            exact;
        hdr.ipv4.protocol : exact;
        directionNeutralPort(meta.direction, hdr.tcp.srcPort, hdr.tcp.dstPort):
            exact;
        directionNeutralPort(meta.direction, hdr.tcp.dstPort, hdr.tcp.srcPort):
            exact;
        meta.eni : exact;
    }
    actions = {
        conntrackOut_allow;
        conntrackOut_miss;
    }

    add_on_miss = true; //New PNA property

    idle_timeout_with_auto_delete = true; // New PNA property
    const default_action = conntrackIn_miss; //New PNA property
}


#endif // PNA_CONNTRACK


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
