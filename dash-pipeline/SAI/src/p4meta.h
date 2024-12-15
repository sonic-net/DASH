#pragma once

#include <string>
#include <vector>
#include <map>
#include <PI/pi.h>

extern "C" {
#include "saimetadata.h"
}

#include "utils.h"

using namespace dash::utils;

namespace dash
{
    struct P4MetaKey {
        sai_attr_id_t attr_id;
        std::string name;
        uint32_t id;
        std::string match_type;
        std::string field;
        uint32_t bitwidth;
        uint32_t ip_is_v6_field_id;
    };

    struct P4MetaActionParam {
        sai_attr_id_t attr_id;
        std::string name;
        uint32_t id;
        std::string field;
        uint32_t bitwidth;
        uint32_t ip_is_v6_field_id;
    };

    struct P4MetaAction {
        std::string name;
        uint32_t id;
        std::vector<P4MetaActionParam> params;
    };

    struct P4MetaTable {
        uint32_t id;
        std::vector<P4MetaKey> keys;
        std::map<uint32_t, P4MetaAction> actions;

        P4MetaTable(
                uint32_t table_id,
                std::initializer_list<P4MetaKey> init_keys,
                std::initializer_list<std::map<uint32_t, P4MetaAction>::value_type> init_actions
                ) : id(table_id), keys(init_keys), actions(init_actions)

        {}

        const P4MetaKey* get_meta_key(
                _In_ sai_attr_id_t attr_id) const
        {
            for (auto i=0u; i<keys.size(); i++) {
                if (attr_id == keys[i].attr_id) {
                    return &keys[i];
                }
            }

            return nullptr;
        }

        const P4MetaKey* get_meta_key(
                _In_ const std::string &key_name) const
        {
            for (auto i=0u; i<keys.size(); i++) {
                if (key_name == keys[i].name) {
                    return &keys[i];
                }
            }

            return nullptr;
        }

        const P4MetaActionParam* get_meta_action_param(
                _In_ uint32_t action_id,
                _In_ sai_attr_id_t attr_id) const
        {
            auto itr = actions.find(action_id);
            if (itr != actions.end()) {
                auto params = itr->second.params;
                for (auto i=0u; i<params.size(); i++) {
                    if (attr_id == params[i].attr_id) {
                        return &params[i];
                    }
                }
            }

            return nullptr;
        }
    };

    inline bool has_suffix(const std::string &str, const std::string &suffix)
    {
        if (str.length() < suffix.length())
            return false;

        return !str.compare(str.length() - suffix.length(), suffix.length(), suffix);
    }

    template<typename T, typename V>
    static inline
    void  set_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const V &value,
            _Inout_ T *t)
    {
        if (field == "booldata")
            return booldataSetVal(value, t, bitwidth);
        if (field == "u8")
            return u8SetVal(value, t, bitwidth);
        if (field == "u16")
            return u16SetVal(value, t, bitwidth);
        if (field == "u32")
            return u32SetVal(value, t, bitwidth);
        if (field == "u64")
            return u64SetVal(value, t, bitwidth);
        if (field == "ipaddr")
            return ipaddrSetVal(value, t, bitwidth);
        if (field == "mac")
            return macSetVal(value, t, bitwidth);
        if (field == "u8list")
            return u8listSetVal(value, t, bitwidth);

        assert(0);
    }

    template<typename V>
    static inline
    void  set_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const V &value,
            _Inout_ p4::v1::FieldMatch_LPM *t)
    {
        assert (field == "ipPrefix");
        return ipPrefixSetVal(value, t, bitwidth);
    }

    template<typename T>
    static inline
    void get_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const T *t,
            _Out_ sai_attribute_value_t &value)
    {
        const char *v = t->value().c_str();

        if (field == "booldata") {
           value.booldata = *(const bool*)v;
        }
        else if (field == "u8") {
           value.u8 = *(const uint8_t*)v;
        }
        else if (field == "u16") {
           uint16_t val = *(const uint16_t*)v;
           value.u16 = ntohs(val);
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
        else if (field == "ipaddr") {
            if (value.ipaddr.addr_family == SAI_IP_ADDR_FAMILY_IPV4) {
                uint32_t val = *(const uint32_t*)v;
                value.ipaddr.addr.ip4 = val;
            }
            else {
                memcpy(value.ipaddr.addr.ip6, v, 16);
            }
        }
        else if (field == "mac") {
            memcpy(value.mac, v, 6);
        }
        else if (field == "u8list") {
            memcpy(value.u8list.list, v, t->value().size());
        }
        else {
            assert(0);
        }
    }

    static inline
    void get_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_LPM *t,
            _Out_ sai_attribute_value_t &value)
    {
        assert (field == "ipPrefix");
        const char *v = t->value().c_str();
        auto prefix_len = t->prefix_len();

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

    template<typename V>
    static inline
    void set_mask(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const V &value,
            _Inout_ p4::v1::FieldMatch_Ternary *t)
    {
        if (field == "ipaddr")
            return ipaddrSetMask(value, t, bitwidth);
        if (field == "u32")
            return u32SetMask(value, t, bitwidth);
        if (field == "u64")
            return u64SetMask(value, t, bitwidth);

        assert(0);
    }

    static inline
    void get_mask(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_Ternary *t,
            _Out_ sai_attribute_value_t &value)

    {
        const char *v = t->mask().c_str();

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

    static inline
    void set_key_value(
            _In_ const P4MetaKey &key,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch *mf)
    {
        if (key.match_type == "exact") {
            auto mf_exact = mf->mutable_exact();
            set_value(key.field, key.bitwidth, value, mf_exact);
        }
        else if (key.match_type == "lpm") {
            auto mf_lpm = mf->mutable_lpm();
            if (getPrefixLength(value) == 0)
            {
                // https://github.com/p4lang/PI/blob/24e0a3c08c964e36d235973556b90e0ae922b894/proto/frontend/src/device_mgr.cpp#L2242-L2246
                DASH_LOG_WARN("Invalid reprsentation of 'don't care' LPM match, omit match field instead of using a prefix length of 0");
                return;
            }
            set_value(key.field, key.bitwidth, value, mf_lpm);
        }
        else if (key.match_type == "ternary") {
            auto mf_ternary = mf->mutable_ternary();
            set_value(key.field, key.bitwidth, value, mf_ternary);
        }
        else if (key.match_type == "optional") {
            auto mf_optional = mf->mutable_optional();
            set_value(key.field, key.bitwidth, value, mf_optional);
        }
        else if (key.match_type == "list") {
            // BMv2 doesn't support "list" match type, and we are using "optional" match in v1model as our implementation.
            // Hence, here we only take the first item from the list and program it as optional match.
            auto mf_optional = mf->mutable_optional();
            if (key.field == "ipprefixlist") {
                sai_attribute_value_t val;
                val.ipaddr.addr_family = value.ipprefixlist.list[0].addr_family;
                val.ipaddr.addr = value.ipprefixlist.list[0].addr;
                set_value("ipaddr", key.bitwidth, val, mf_optional);
            }
            else {
                set_value(key.field, key.bitwidth, value, mf_optional);
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

    static inline
    void get_key_value(
            _In_ const P4MetaKey &key,
            _In_ p4::v1::FieldMatch *mf,
            _Out_ sai_attribute_value_t &value)
    {
        if (key.match_type == "exact") {
            auto mf_exact = mf->mutable_exact();
            get_value(key.field, key.bitwidth, mf_exact, value);
        }
        else if (key.match_type == "lpm") {
            auto mf_lpm = mf->mutable_lpm();
            get_value(key.field, key.bitwidth, mf_lpm, value);
        }
        else if (key.match_type == "ternary") {
            auto mf_ternary = mf->mutable_ternary();
            get_value(key.field, key.bitwidth, mf_ternary, value);
        }
        else if (key.match_type == "optional") {
            auto mf_optional = mf->mutable_optional();
            get_value(key.field, key.bitwidth, mf_optional, value);
        }
        else if (key.match_type == "list") {
            auto mf_optional = mf->mutable_optional();
            get_value(key.field, key.bitwidth, mf_optional, value);
        }
        else if (key.match_type == "range_list") {
            auto mf_optional = mf->mutable_optional();
            get_value(key.field, key.bitwidth, mf_optional, value);
        }
        else {
            assert(0);
        }
    }

    // set/get only for value.ipaddr.addr_family
    template<typename T>
    static inline
    void set_ipaddr_family(
            _In_ const sai_attribute_value_t &value,
            _Out_ T *t)
    {
        booldataSetVal(value.ipaddr.addr_family == SAI_IP_ADDR_FAMILY_IPV4 ? 0 : 1, t, 1);
    }

    template<typename T>
    static inline
    void get_ipaddr_family(
            _In_ const T *t,
            _Out_ sai_attribute_value_t &value)
    {
        const char *v = t->value().c_str();

        if (*(const bool*)v) // is_ipv6
            value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        else
            value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
    }


    static inline
    std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*> get_key(
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

    static inline
    std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*> get_action_param(
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
}
