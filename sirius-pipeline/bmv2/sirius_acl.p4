#ifndef _SIRIUS_ACL_P4_
#define _SIRIUS_ACL_P4_

#include "sirius_headers.p4"

match_kind {
    /* list of ternary values
       A/A_len,B/_B-len,...
       if empty, then don't care
     */
    list,
    /* Also possibly range_list - a-b,c-d,... */
    range_list
}

#define ACL_STAGE(table_name) \
    direct_counter(CounterType.packets_and_bytes) ## table_name ##_counter; \
    table table_name { \
        key = { \
            meta.eni : exact @name("meta.eni:eni"); \
            hdr.ipv4.dst_addr : list @name("hdr.ipv4.dst_addr:dip"); \
            hdr.ipv4.src_addr : list @name("hdr.ipv4.src_addr:sip"); \
            hdr.ipv4.protocol : list @name("hdr.ipv4.src_addr:protocol"); \
            hdr.tcp.src_port : range_list @name("hdr.tcp.src_port:sport"); \
            hdr.tcp.dst_port : range_list @name("hdr.tcp.dst_port:dport"); \
        } \
        actions = { \
            permit; \
            permit_and_continue; \
            deny; \
            deny_and_continue; \
        } \
        default_action = deny; \
        counters = ## table_name ##_counter; \
    }

#define ACL_STAGE_APPLY(table_name) \
        switch (table_name.apply().action_run) { \
            permit: {return;} \
            deny: {return;} \
        }

/* 
 * This control results in a new set of tables every time
 * it is applied, i. e. inbound ACL tables are different
 * from outbound, and API will be generated for each of them
 */
control acl(inout headers_t hdr,
            inout metadata_t meta,
            inout standard_metadata_t standard_metadata)
{
    action permit() {}
    action permit_and_continue() {}
    action deny() {meta.dropped = true;}
    action deny_and_continue() {meta.dropped = true;}

ACL_STAGE(stage1)
ACL_STAGE(stage2)
ACL_STAGE(stage3)

    apply {
ACL_STAGE_APPLY(stage1)
ACL_STAGE_APPLY(stage2)
ACL_STAGE_APPLY(stage3)
    }
}
#endif /* _SIRIUS_ACL_P4_ */
