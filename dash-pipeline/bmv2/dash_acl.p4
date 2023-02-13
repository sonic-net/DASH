#ifndef _SIRIUS_ACL_P4_
#define _SIRIUS_ACL_P4_

#include "dash_headers.p4"
#include "dash_metadata.p4"

match_kind {
    /* list of ternary values
       A/A_len,B/_B-len,...
       if empty, then don't care
     */
    list,
    /* Also possibly range_list - a-b,c-d,... */
    range_list
}

// #define DASH_MATCH
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
            meta.dst_tag_map : ternary @name("meta.dst_tag_map:dst_tag"); \
            meta.src_tag_map : ternary @name("meta.src_tag_map:src_tag"); \
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

    action set_src_tag(tag_map_t tag_map) {
        meta.src_tag_map = tag_map;
    }

    @name("acl_src_tag|dash_acl")
    table acl_src_tag {
        key = {
            meta.src_ip_addr : lpm @name("meta.src_ip_addr:sip");
        }
        actions = {
            set_src_tag;
        }
    }

    action set_dst_tag(tag_map_t tag_map) {
        meta.dst_tag_map = tag_map;
    }

    @name("acl_dst_tag|dash_acl")
    table acl_dst_tag {
        key = {
            meta.dst_ip_addr : lpm @name("meta.dst_ip_addr:dip");
        }
        actions = {
            set_dst_tag;
        }
    }

ACL_STAGE(stage1)
ACL_STAGE(stage2)
ACL_STAGE(stage3)

    apply {

    acl_src_tag.apply();
    acl_dst_tag.apply();

ACL_STAGE_APPLY(stage1)
ACL_STAGE_APPLY(stage2)
ACL_STAGE_APPLY(stage3)
    }
}
#endif /* _SIRIUS_ACL_P4_ */
