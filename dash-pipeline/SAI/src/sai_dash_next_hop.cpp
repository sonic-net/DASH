#include "saiimpl.h"

DASH_GENERIC_QUAD(NEXT_HOP,next_hop);

sai_next_hop_api_t dash_sai_next_hop_api_impl = {

    DASH_GENERIC_QUAD_API(next_hop)

    .create_next_hops = 0,
    .remove_next_hops = 0,
    .set_next_hops_attribute = 0,
    .get_next_hops_attribute = 0,
};
