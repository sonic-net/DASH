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
#ifdef BMV2_V1MODEL
#define LIST_MATCH optional
#define RANGE_LIST_MATCH optional
#endif // BMV2_V1MODEL
#ifdef DPDK_PNA
#define LIST_MATCH ternary
#define RANGE_LIST_MATCH range
#endif // DPDK_PNA
#endif

#define str(name) #name

#ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
// See the #ifdef with same preprocessor symbol in dash_pipeline.p4

#define ACL_STAGE(table_name) \
    DirectCounter<bit<64>>(PNA_CounterType_t.PACKETS_AND_BYTES) ## table_name ##_counter; \
    @name(str(table_name##:dash_acl_rule|dash_acl)) \
    table table_name { \
        key = { \
            meta. ## table_name ##_dash_acl_group_id : exact @name("meta.dash_acl_group_id:dash_acl_group_id"); \
            meta.dst_ip_addr : LIST_MATCH @name("meta.dst_ip_addr:dip"); \
            meta.src_ip_addr : LIST_MATCH @name("meta.src_ip_addr:sip"); \
            meta.ip_protocol : LIST_MATCH @name("meta.ip_protocol:protocol"); \
            meta.src_l4_port : RANGE_LIST_MATCH @name("meta.src_l4_port:src_port"); \
            meta.dst_l4_port : RANGE_LIST_MATCH @name("meta.dst_l4_port:dst_port"); \
        } \
        actions = { \
            permit; \
            permit_and_continue; \
            deny; \
            deny_and_continue; \
        } \
        default_action = deny; \
        DIRECT_COUNTER_TABLE_PROPERTY = ## table_name ##_counter; \
    }

#else   // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE

#define ACL_STAGE(table_name) \
    @name(str(table_name##:dash_acl_rule|dash_acl)) \
    table table_name { \
        key = { \
            meta. ## table_name ##_dash_acl_group_id : exact @name("meta.dash_acl_group_id:dash_acl_group_id"); \
            meta.dst_ip_addr : LIST_MATCH @name("meta.dst_ip_addr:dip"); \
            meta.src_ip_addr : LIST_MATCH @name("meta.src_ip_addr:sip"); \
            meta.ip_protocol : LIST_MATCH @name("meta.ip_protocol:protocol"); \
            meta.src_l4_port : RANGE_LIST_MATCH @name("meta.src_l4_port:src_port"); \
            meta.dst_l4_port : RANGE_LIST_MATCH @name("meta.dst_l4_port:dst_port"); \
        } \
        actions = { \
            permit; \
            permit_and_continue; \
            deny; \
            deny_and_continue; \
        } \
        default_action = deny; \
    }

#endif  // DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE

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
control acl(
      inout headers_t hdr
    , inout metadata_t meta
#ifdef BMV2_V1MODEL
    , inout standard_metadata_t standard_metadata
#endif // BMV2_V1MODEL
    )
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
