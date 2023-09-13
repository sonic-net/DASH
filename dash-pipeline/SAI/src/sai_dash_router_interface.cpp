#include "saiimpl.h"

DASH_GENERIC_QUAD(ROUTER_INTERFACE,router_interface);

sai_router_interface_api_t dash_sai_router_interface_api_impl = {

    DASH_GENERIC_QUAD_API(router_interface)
    DASH_GENERIC_STATS_API(router_interface)
};
