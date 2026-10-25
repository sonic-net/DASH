extern "C" {
#include <sai.h>
#include <saiextensions.h>
#include <saiexperimentaldashvip.h>
}
#include <cstdio>

int main() {
    void *methods = nullptr;
    if (sai_api_query(SAI_API_SWITCH, &methods) != SAI_STATUS_SUCCESS || !methods)
        return 1;
    methods = nullptr;
    if (sai_api_query(static_cast<sai_api_t>(SAI_API_DASH_VIP), &methods) != SAI_STATUS_SUCCESS || !methods)
        return 2;
    const auto *vip = static_cast<const sai_dash_vip_api_t *>(methods);
    if (!vip->create_vip_entry || !vip->remove_vip_entry ||
        !vip->set_vip_entry_attribute || !vip->get_vip_entry_attribute ||
        !vip->create_vip_entries || !vip->remove_vip_entries)
        return 3;
    std::puts("DASH installed SDK API query passed");
    return 0;
}
