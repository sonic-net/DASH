#ifndef _SIRIUS_ACL_P4_
#define _SIRIUS_ACL_P4_

#include "dash_headers.p4"

match_kind {
    /* list of ternary values
       A/A_len,B/_B-len,...
       if empty, then don't care
     */
    list,
    /* Also possibly range_list - a-b,c-d,... */
    range_list
}

#ifdef DASH_MATCH
#define LIST_MATCH list
#define RANGE_LIST_MATCH range_list
#else
#define LIST_MATCH optional
#define RANGE_LIST_MATCH optional
#endif

#define str(name) #name

#define ACL_STAGE(table_name) \
    direct_counter(CounterType.packets_and_bytes) ## table_name ##_counter; \
    @name(str(table_name##:dash_acl_rule|dash_acl)) \
    table table_name { \
        key = { \
            meta. ## table_name ##_dash_acl_group_id : exact @name("meta.dash_acl_group_id:dash_acl_group_id"); \
            meta.dst_ip_addr : LIST_MATCH @name("meta.dst_ip_addr:dip"); \
            meta.src_ip_addr : LIST_MATCH @name("meta.src_ip_addr:sip"); \
            meta.ip_protocol : LIST_MATCH @name("meta.ip_protocol:protocol"); \
            hdr.tcp.src_port : RANGE_LIST_MATCH @name("hdr.tcp.src_port:src_port"); \
            hdr.tcp.dst_port : RANGE_LIST_MATCH @name("hdr.tcp.dst_port:dst_port"); \
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
        if ( meta. ## table_name ##_dash_acl_group_id  != 0) { \
        switch (table_name.apply().action_run) { \
            permit: {return;} \
            deny: {return;} \
        } \
        } \

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
