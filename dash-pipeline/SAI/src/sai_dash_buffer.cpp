#include "saiimpl.h"

DASH_GENERIC_QUAD(BUFFER_POOL,buffer_pool);
DASH_GENERIC_QUAD(INGRESS_PRIORITY_GROUP,ingress_priority_group);
DASH_GENERIC_QUAD(BUFFER_PROFILE,buffer_profile);

sai_buffer_api_t dash_sai_buffer_api_impl = {

    DASH_GENERIC_QUAD_API(buffer_pool)

    .get_buffer_pool_stats = 0,
    .get_buffer_pool_stats_ext = 0,
    .clear_buffer_pool_stats = 0,

    DASH_GENERIC_QUAD_API(ingress_priority_group)

    .get_ingress_priority_group_stats = 0,
    .get_ingress_priority_group_stats_ext = 0,
    .clear_ingress_priority_group_stats = 0,

    DASH_GENERIC_QUAD_API(buffer_profile)
};
