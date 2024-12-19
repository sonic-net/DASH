extern "C" {
#include "saimetadata.h"
}

#include "utils.h"
#include "p4meta.h"

using namespace dash;
using namespace dash::utils;

namespace dash
{
    const P4MetaKey* P4MetaTable::get_meta_key(
            _In_ sai_attr_id_t attr_id) const
    {
        for (auto i=0u; i<keys.size(); i++) {
            if (attr_id == keys[i].attr_id) {
                return &keys[i];
            }
        }

        return nullptr;
    }

    const P4MetaKey* P4MetaTable::get_meta_key(
            _In_ const std::string &key_name) const
    {
        for (auto i=0u; i<keys.size(); i++) {
            if (key_name == keys[i].name) {
                return &keys[i];
            }
        }

        return nullptr;
    }

    const P4MetaKey* P4MetaTable::get_meta_object_key() const
    {
        for (auto i=0u; i<keys.size(); i++) {
            if (string_has_suffix(keys[i].name, "_OBJECT_KEY")) {
                return &keys[i];
            }
        }

        return nullptr;
    }

    const P4MetaActionParam* P4MetaTable::get_meta_action_param(
            _In_ uint32_t action_id,
            _In_ sai_attr_id_t attr_id) const
    {
        auto itr = actions.find(action_id);
        if (itr != actions.end()) {
            auto &params = itr->second.params;
            for (auto i=0u; i<params.size(); i++) {
                if (attr_id == params[i].attr_id) {
                    return &params[i];
                }
            }
        }

        return nullptr;
    }

    pi_p4_id_t P4MetaTable::find_action_id(
            _In_ uint32_t attr_count,
            _In_ const sai_attribute_t *attr_list) const
    {
        if (actions.size() == 1) {
            return actions.begin()->first;
        }

        auto itr = extra_fields.find("ACTION");
        assert(itr != extra_fields.end());

        for (uint32_t i = 0; i < attr_count; i++) {
            if (attr_list[i].id == itr->second) {
                uint32_t action_enum_id = attr_list[i].value.u32;
                for (auto &action: actions) {
                    if (action.second.enum_id == action_enum_id) {
                        return action.first;
                    }
                }
                break;
            }
        }

        return 0; // invalid p4 action id
    }

    //
    // helper functions, set/get attr to/from p4 match|action
    //

    void  set_attr_value_to_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch_LPM *mf_lpm)
    {
        assert (field == "ipPrefix");
        return ipPrefixSetVal(value, mf_lpm, bitwidth);
    }

    void get_attr_value_from_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_LPM *mf_lpm,
            _Out_ sai_attribute_value_t &value)
    {
        assert (field == "ipPrefix");
        const char *v = mf_lpm->value().c_str();
        auto prefix_len = mf_lpm->prefix_len();

        if (value.ipprefix.addr_family == SAI_IP_ADDR_FAMILY_IPV4) {
            uint32_t val = *(const uint32_t*)v;
            prefix_len -= 96;
            assert (prefix_len <= 32);
            value.ipprefix.addr.ip4 = val;
            value.ipprefix.mask.ip4 = 0xffffffff << (32 - prefix_len);
        }
        else {
            assert (prefix_len <= 128);
            uint8_t netmask[16] = { 0 };
            int i;

            for (i = 0; i < prefix_len/8; i++)
                netmask[i] = 0xff;
            if (prefix_len % 8 != 0)
                netmask[i] = (uint8_t)(0xff << (8 - prefix_len%8));
            memcpy(value.ipprefix.mask.ip6, netmask, 16);
        }
    }


    void set_attr_value_mask_to_p4_ternary(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch_Ternary *mf_ternary)
    {
        if (field == "ipaddr")
            return ipaddrSetMask(value, mf_ternary, bitwidth);
        if (field == "u32")
            return u32SetMask(value, mf_ternary, bitwidth);
        if (field == "u64")
            return u64SetMask(value, mf_ternary, bitwidth);

        assert(0);
    }

    void get_attr_value_mask_from_p4_ternary(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_Ternary *mf_ternary,
            _Out_ sai_attribute_value_t &value)

    {
        const char *v = mf_ternary->mask().c_str();

        if (field == "ipaddr") {
            if (value.ipaddr.addr_family == SAI_IP_ADDR_FAMILY_IPV4) {
                uint32_t val = *(const uint32_t*)v;
                value.ipaddr.addr.ip4 = val;
            }
            else {
                memcpy(value.ipaddr.addr.ip6, v, 16);
            }
        }
        else if (field == "u32") {
           uint32_t val = *(const uint32_t*)v;
           value.u32 = ntohl(val) >> (32 - bitwidth);
        }
        else if (field == "u64") {
           uint64_t val = *(const uint64_t*)v;
           if (*reinterpret_cast<const char*>("\0\x01") == 0) { // Little Endian
               value.u64 = be64toh(val) >> (64 - bitwidth);
           }
           else {
               value.u64 = val & ((1ul<<bitwidth) - 1);
           }
        }
        else {
            assert(0);
        }
    }


    void set_attr_value_to_p4_match(
            _In_ const P4MetaKey &key,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch *mf)
    {
        if (key.match_type == "exact") {
            auto mf_exact = mf->mutable_exact();
            set_attr_value_to_p4(key.field, key.bitwidth, value, mf_exact);
        }
        else if (key.match_type == "lpm") {
            auto mf_lpm = mf->mutable_lpm();
            if (getPrefixLength(value) == 0)
            {
                // https://github.com/p4lang/PI/blob/24e0a3c08c964e36d235973556b90e0ae922b894/proto/frontend/src/device_mgr.cpp#L2242-L2246
                DASH_LOG_WARN("Invalid reprsentation of 'don't care' LPM match, omit match field instead of using a prefix length of 0");
                return;
            }
            set_attr_value_to_p4(key.field, key.bitwidth, value, mf_lpm);
        }
        else if (key.match_type == "ternary") {
            auto mf_ternary = mf->mutable_ternary();
            set_attr_value_to_p4(key.field, key.bitwidth, value, mf_ternary);
        }
        else if (key.match_type == "optional") {
            auto mf_optional = mf->mutable_optional();
            set_attr_value_to_p4(key.field, key.bitwidth, value, mf_optional);
        }
        else if (key.match_type == "list") {
            // BMv2 doesn't support "list" match type, and we are using "optional" match in v1model as our implementation.
            // Hence, here we only take the first item from the list and program it as optional match.
            auto mf_optional = mf->mutable_optional();
            if (key.field == "ipprefixlist") {
                sai_attribute_value_t val;
                val.ipaddr.addr_family = value.ipprefixlist.list[0].addr_family;
                val.ipaddr.addr = value.ipprefixlist.list[0].addr;
                set_attr_value_to_p4("ipaddr", key.bitwidth, val, mf_optional);
            }
            else {
                set_attr_value_to_p4(key.field, key.bitwidth, value, mf_optional);
            }
        }
        else if (key.match_type == "range_list") {
            // BMv2 doesn't support "range_list" match type, and we are using "optional" match in v1model as our implementation.
            // Hence, here we only take the first item from the list and program the range start as optional match.
            auto mf_optional = mf->mutable_optional();
            // FIXME only u16rangelist in sai_attribute_value_t
            u16SetVal(value.u16rangelist.list[0].min, mf_optional, key.bitwidth);
        }
        else {
            assert(0);
        }
    }

    void get_attr_value_from_p4_match(
            _In_ const P4MetaKey &key,
            _In_ p4::v1::FieldMatch *mf,
            _Out_ sai_attribute_value_t &value)
    {
        if (key.match_type == "exact") {
            auto mf_exact = mf->mutable_exact();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_exact, value);
        }
        else if (key.match_type == "lpm") {
            auto mf_lpm = mf->mutable_lpm();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_lpm, value);
        }
        else if (key.match_type == "ternary") {
            auto mf_ternary = mf->mutable_ternary();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_ternary, value);
        }
        else if (key.match_type == "optional") {
            auto mf_optional = mf->mutable_optional();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_optional, value);
        }
        else if (key.match_type == "list") {
            auto mf_optional = mf->mutable_optional();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_optional, value);
        }
        else if (key.match_type == "range_list") {
            auto mf_optional = mf->mutable_optional();
            get_attr_value_from_p4(key.field, key.bitwidth, mf_optional, value);
        }
        else {
            assert(0);
        }
    }

    void  set_attr_to_p4_match(
            _In_ const P4MetaKey *meta_key,
            _In_ const sai_attribute_t *attr,
            _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry)
    {
        if (meta_key->ip_is_v6_field_id) {
            auto mf = matchActionEntry->add_match();
            mf->set_field_id(meta_key->ip_is_v6_field_id);
            set_attr_ipaddr_family_to_p4(attr->value, mf->mutable_exact());
        }

        auto mf = matchActionEntry->add_match();
        mf->set_field_id(meta_key->id);
        if (meta_key->match_type == "ternary" && string_has_suffix(meta_key->name, "_MASK")) {
            set_attr_value_mask_to_p4_ternary(meta_key->field, meta_key->bitwidth, attr->value,
                     mf->mutable_ternary());
        }
        else {
            set_attr_value_to_p4_match(*meta_key, attr->value, mf);
        }
    }

    void  set_attr_to_p4_action(
            _In_ const P4MetaActionParam *meta_param,
            _In_ const sai_attribute_t *attr,
            _Out_ p4::v1::Action *action)
    {
        if (meta_param->ip_is_v6_field_id) {
            auto param = action->add_params();
            param->set_param_id(meta_param->ip_is_v6_field_id);
            set_attr_ipaddr_family_to_p4(attr->value, param);
        }

        auto param = action->add_params();
        param->set_param_id(meta_param->id);
        set_attr_value_to_p4(meta_param->field, meta_param->bitwidth, attr->value, param);
    }

    std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*> get_match_pair_from_p4_table_entry(
            _In_ const P4MetaKey *meta_key,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry)
    {
        std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*> pair_key = {nullptr, nullptr};

        for (int i = 0; i < matchActionEntry->match_size(); i++) {
            auto mf = matchActionEntry->mutable_match(i);
            if (mf->field_id() == meta_key->id) {
                pair_key.first = mf;
            }
            else if (mf->field_id() == meta_key->ip_is_v6_field_id) {
                pair_key.second = mf;
            }
        }

        return pair_key;
    }

    std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*> get_action_param_pair_from_p4_table_entry(
            _In_ const P4MetaActionParam *meta_param,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry)
    {
        auto action = matchActionEntry->mutable_action()->mutable_action();
        std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*> pair_param = {nullptr, nullptr};

        for (int i = 0; i < action->params_size(); i++) {
            auto param = action->mutable_params(i);
            if (param->param_id() == meta_param->id) {
                pair_param.first = param;
            }
            else if (param->param_id() == meta_param->ip_is_v6_field_id) {
                pair_param.second = param;
            }
        }

        return pair_param;
    }

    bool string_has_suffix(const std::string &str, const std::string &suffix)
    {
        if (str.length() < suffix.length())
            return false;

        return !str.compare(str.length() - suffix.length(), suffix.length(), suffix);
    }
}

