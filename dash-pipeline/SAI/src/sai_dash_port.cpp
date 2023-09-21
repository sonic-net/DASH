#include "saiimpl.h"

DASH_GENERIC_QUAD(PORT,port);

sai_port_api_t dash_sai_port_api_impl = {

    DASH_GENERIC_QUAD_API(port)

    .get_port_stats = 0,
    .get_port_stats_ext = 0,
    .clear_port_stats = 0,
    .clear_port_all_stats = 0,
    .create_port_pool = 0,
    .remove_port_pool = 0,
    .set_port_pool_attribute = 0,
    .get_port_pool_attribute = 0,
    .get_port_pool_stats = 0,
    .get_port_pool_stats_ext = 0,
    .clear_port_pool_stats = 0,
    .create_port_connector = 0,
    .remove_port_connector = 0,
    .set_port_connector_attribute = 0,
    .get_port_connector_attribute = 0,
    .create_port_serdes = 0,
    .remove_port_serdes = 0,
    .set_port_serdes_attribute = 0,
    .get_port_serdes_attribute = 0,
    .create_ports = 0,
    .remove_ports = 0,
    .set_ports_attribute = 0,
    .get_ports_attribute = 0,
    .create_port_serdess = 0,
    .remove_port_serdess = 0,
    .set_port_serdess_attribute = 0,
    .get_port_serdess_attribute = 0,
};
