#include "saiimpl.h"

DASH_GENERIC_QUAD(SWITCH,switch);

static sai_status_t dash_create_switch_uniq(
        _Out_ sai_object_id_t *switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();

    return dash_create_switch(
            switch_id,
            SAI_NULL_OBJECT_ID, // no switch id since we create switch
            attr_count,
            attr_list);
}

sai_switch_api_t dash_sai_switch_api_impl = {
    .create_switch = dash_create_switch_uniq,
    .remove_switch = dash_remove_switch,
    .set_switch_attribute = dash_set_switch_attribute,
    .get_switch_attribute = dash_get_switch_attribute,
    .get_switch_stats = 0,
    .get_switch_stats_ext = 0,
    .clear_switch_stats = 0,
    .switch_mdio_read = 0,
    .switch_mdio_write = 0,
    .create_switch_tunnel = 0,
    .remove_switch_tunnel = 0,
    .set_switch_tunnel_attribute = 0,
    .get_switch_tunnel_attribute = 0,
    .switch_mdio_cl22_read = 0,
    .switch_mdio_cl22_write = 0,
};
