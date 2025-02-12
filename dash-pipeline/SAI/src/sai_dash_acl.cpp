#include "saiimpl.h"

DASH_GENERIC_QUAD(ACL_TABLE,acl_table);

sai_acl_api_t dash_sai_acl_api_impl = {

    DASH_GENERIC_QUAD_API(acl_table)

    .create_acl_entry = 0,
    .remove_acl_entry = 0,
    .set_acl_entry_attribute = 0,
    .get_acl_entry_attribute = 0,

    .create_acl_counter = 0,
    .remove_acl_counter = 0,
    .set_acl_counter_attribute = 0,
    .get_acl_counter_attribute = 0,

    .create_acl_range = 0,
    .remove_acl_range = 0,
    .set_acl_range_attribute = 0,
    .get_acl_range_attribute = 0,

    .create_acl_table_group = 0,
    .remove_acl_table_group = 0,
    .set_acl_table_group_attribute = 0,
    .get_acl_table_group_attribute = 0,

    .create_acl_table_group_member = 0,
    .remove_acl_table_group_member = 0,
    .set_acl_table_group_member_attribute = 0,
    .get_acl_table_group_member_attribute = 0,

    .create_acl_table_chain_group = 0,
    .remove_acl_table_chain_group = 0,
    .set_acl_table_chain_group_attribute = 0,
    .get_acl_table_chain_group_attribute = 0,
};
