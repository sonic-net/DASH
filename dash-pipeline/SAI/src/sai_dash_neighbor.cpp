#include "saiimpl.h"

static sai_status_t dash_create_neighbor_entry(
        _In_ const sai_neighbor_entry_t *neighbor_entry,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();

    DASH_LOG_WARN("dummy create");

    return SAI_STATUS_SUCCESS;
}

static sai_status_t dash_remove_neighbor_entry(
        _In_ const sai_neighbor_entry_t *neighbor_entry)
{
    DASH_LOG_ENTER();

    DASH_LOG_WARN("dummy remove");

    return SAI_STATUS_SUCCESS;
}

static sai_status_t dash_set_neighbor_entry_attribute(
        _In_ const sai_neighbor_entry_t *neighbor_entry,
        _In_ const sai_attribute_t *attr)
{
    DASH_LOG_ENTER();

    DASH_LOG_WARN("dummy set");

    return SAI_STATUS_SUCCESS;
}

static sai_status_t dash_get_neighbor_entry_attribute(
        _In_ const sai_neighbor_entry_t *neighbor_entry,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();

    DASH_LOG_ERROR("not implemented");

    return SAI_STATUS_NOT_IMPLEMENTED;
}

sai_neighbor_api_t dash_sai_neighbor_api_impl = {

    DASH_GENERIC_QUAD_API(neighbor_entry)

    .remove_all_neighbor_entries = 0,

    .create_neighbor_entries = 0,
    .remove_neighbor_entries = 0,
    .set_neighbor_entries_attribute = 0,
    .get_neighbor_entries_attribute = 0,
};
