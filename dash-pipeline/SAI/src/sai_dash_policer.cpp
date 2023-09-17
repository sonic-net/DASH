#include "saiimpl.h"

DASH_GENERIC_QUAD(POLICER,policer);

sai_policer_api_t dash_sai_policer_api_impl = {

    DASH_GENERIC_QUAD_API(policer)
    DASH_GENERIC_STATS_API(policer)
};
