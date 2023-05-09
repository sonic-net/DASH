#include <iostream>
#include <vector>
#include <unordered_map>
#include <string.h>

#include <sai.h>


extern sai_status_t sai_create_direction_lookup_entry(
        _In_ const sai_direction_lookup_entry_t *direction_lookup_entry,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);
extern sai_status_t sai_remove_direction_lookup_entry(
        _In_ const sai_direction_lookup_entry_t *direction_lookup_entry);

extern sai_status_t sai_create_eni_ether_address_map_entry(
        _In_ const sai_eni_ether_address_map_entry_t *outbound_eni_lookup_from_vm_entry,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);
extern sai_status_t sai_remove_eni_ether_address_map_entry(
        _In_ const sai_eni_ether_address_map_entry_t *outbound_eni_lookup_from_vm_entry);

extern sai_status_t sai_create_vnet(
        _Out_ sai_object_id_t *vnet_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);
extern sai_status_t sai_remove_vnet(_In_ sai_object_id_t vnet_id);

extern sai_status_t sai_create_eni(
        _Out_ sai_object_id_t *eni_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);

extern sai_status_t sai_create_eni(
        _Out_ sai_object_id_t *eni_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);
extern sai_status_t sai_remove_eni(
        _In_ sai_object_id_t eni_id);

extern sai_status_t sai_create_dash_acl_group(
        _Out_ sai_object_id_t *acl_group_id,
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list);
extern sai_status_t sai_remove_dash_acl_group(
        _In_ sai_object_id_t eni_id);

int main(int argc, char **argv)
{
    sai_object_id_t switch_id = SAI_NULL_OBJECT_ID;
    sai_attribute_t attr;
    std::vector<sai_attribute_t> attrs;
    sai_object_id_t in_acl_group_id;
    sai_object_id_t out_acl_group_id;
    sai_object_id_t eni_id;
    sai_object_id_t vnet_id;

    sai_direction_lookup_entry_t dle = {};
    dle.switch_id = switch_id;
    dle.vni = 60;

    attr.id = SAI_DIRECTION_LOOKUP_ENTRY_ATTR_ACTION;
    attr.value.u32 = SAI_DIRECTION_LOOKUP_ENTRY_ACTION_SET_OUTBOUND_DIRECTION;
    attrs.push_back(attr);
    
    /* sai_status_t status = sai_dash_api_impl.create_direction_lookup_entry(&dle, attrs.size(), attrs.data()); */
    sai_status_t status = sai_create_direction_lookup_entry(&dle, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create Direction Lookup Entry" << std::endl;
        return 1;
    }

    attrs.clear();

    attr.id = SAI_DASH_ACL_GROUP_ATTR_IP_ADDR_FAMILY;
    attr.value.s32 = SAI_IP_ADDR_FAMILY_IPV4;
    attrs.push_back(attr);

    /* status = sai_dash_api_impl.create_dash_acl_group(&group_id, switch_id, attrs.size(), attrs.data()); */
    status = sai_create_dash_acl_group(&in_acl_group_id, switch_id, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create inbound Dash ACL group" << std::endl;
        return 1;
    }
    status = sai_create_dash_acl_group(&out_acl_group_id, switch_id, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create outbound Dash ACL group" << std::endl;
        return 1;
    }

    attrs.clear();

    attr.id = SAI_VNET_ATTR_VNI;
    attr.value.u32 = 9;
    attrs.push_back(attr);
    
    status = sai_create_vnet(&vnet_id, switch_id, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create VNET table entry" << std::endl;
        return 1;
    }

    attrs.clear();

    attr.id = SAI_ENI_ATTR_CPS;
    attr.value.u32 = 10000;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_PPS;
    attr.value.u32 = 100000;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_FLOWS;
    attr.value.u32 = 100000;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_ADMIN_STATE;
    attr.value.booldata = true;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_VM_UNDERLAY_DIP;
    sai_ip_addr_t u_dip_addr = {.ip4 = 0x010310ac};
    sai_ip_address_t u_dip = {.addr_family = SAI_IP_ADDR_FAMILY_IPV4,
                              .addr = u_dip_addr};
    attr.value.ipaddr = u_dip;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_VM_VNI;
    attr.value.u32 = 9;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_VNET_ID;
    attr.value.u32 = vnet_id;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_V4_METER_POLICY_ID;
    attr.value.oid = SAI_NULL_OBJECT_ID;
    attrs.push_back(attr);

    attr.id = SAI_ENI_ATTR_V6_METER_POLICY_ID;
    attr.value.oid = SAI_NULL_OBJECT_ID;
    attrs.push_back(attr);

    std::unordered_map<uint32_t, uint16_t> acl_group_ids = {
      {SAI_ENI_ATTR_INBOUND_V4_STAGE1_DASH_ACL_GROUP_ID, in_acl_group_id},
      {SAI_ENI_ATTR_INBOUND_V4_STAGE2_DASH_ACL_GROUP_ID, in_acl_group_id},
      {SAI_ENI_ATTR_INBOUND_V4_STAGE3_DASH_ACL_GROUP_ID, in_acl_group_id},
      {SAI_ENI_ATTR_INBOUND_V4_STAGE4_DASH_ACL_GROUP_ID, in_acl_group_id},
      {SAI_ENI_ATTR_INBOUND_V4_STAGE5_DASH_ACL_GROUP_ID, in_acl_group_id},
      {SAI_ENI_ATTR_OUTBOUND_V4_STAGE1_DASH_ACL_GROUP_ID, out_acl_group_id},
      {SAI_ENI_ATTR_OUTBOUND_V4_STAGE2_DASH_ACL_GROUP_ID, out_acl_group_id},
      {SAI_ENI_ATTR_OUTBOUND_V4_STAGE3_DASH_ACL_GROUP_ID, out_acl_group_id},
      {SAI_ENI_ATTR_OUTBOUND_V4_STAGE4_DASH_ACL_GROUP_ID, out_acl_group_id},
      {SAI_ENI_ATTR_OUTBOUND_V4_STAGE5_DASH_ACL_GROUP_ID, out_acl_group_id},
      {SAI_ENI_ATTR_INBOUND_V6_STAGE1_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_INBOUND_V6_STAGE2_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_INBOUND_V6_STAGE3_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_INBOUND_V6_STAGE4_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_INBOUND_V6_STAGE5_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_OUTBOUND_V6_STAGE1_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_OUTBOUND_V6_STAGE2_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_OUTBOUND_V6_STAGE3_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_OUTBOUND_V6_STAGE4_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
      {SAI_ENI_ATTR_OUTBOUND_V6_STAGE5_DASH_ACL_GROUP_ID, SAI_NULL_OBJECT_ID},
    };
    for (const auto& acl_grp_pair : acl_group_ids) {
        attr.id = acl_grp_pair.first;
        attr.value.oid = acl_grp_pair.second;
        attrs.push_back(attr);
    }

    status = sai_create_eni(&eni_id, switch_id, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create ENI object" << std::endl;
        return 1;
    }

    attrs.clear();

    sai_eni_ether_address_map_entry_t eam;
    eam.switch_id = switch_id;
    eam.address[0] = 0xaa;
    eam.address[1] = 0xcc;
    eam.address[2] = 0xcc;
    eam.address[3] = 0xcc;
    eam.address[4] = 0xcc;
    eam.address[5] = 0xcc;

    attr.id = SAI_ENI_ETHER_ADDRESS_MAP_ENTRY_ATTR_ENI_ID;
    attr.value.u16 = eni_id;
    attrs.push_back(attr);

    status = sai_create_eni_ether_address_map_entry(&eam, attrs.size(), attrs.data());
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to create ENI Lookup From VM" << std::endl;
        return 1;
    }

    // Delete everything in reverse order
    status = sai_remove_eni_ether_address_map_entry(&eam);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove ENI Lookup From VM" << std::endl;
        return 1;
    }

    status = sai_remove_eni(eni_id);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove ENI object " << eni_id << std::endl;
        return 1;
    }

    status = sai_remove_vnet(vnet_id);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove VNET table entry" << std::endl;
        return 1;
    }

    status = sai_remove_dash_acl_group(out_acl_group_id);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove Outbound ACL group object "
                  << out_acl_group_id << std::endl;
        return 1;
    }

    status = sai_remove_dash_acl_group(in_acl_group_id);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove Inbound ACL group object "
                  << in_acl_group_id << std::endl;
        return 1;
    }

    status = sai_remove_direction_lookup_entry(&dle);
    if (status != SAI_STATUS_SUCCESS)
    {
        std::cout << "Failed to remove Direction Lookup Entry" << std::endl;
        return 1;
    }

    std::cout << "Done." << std::endl;

    return 0;
}
