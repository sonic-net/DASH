#pragma once

#include <string>
#include <vector>
#include <map>
#include <PI/pi.h>

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
        uint32_t id;
        std::string field;
        uint32_t bitwidth;
        uint32_t ip_is_v6_field_id;
    };

    struct P4MetaAction {
        uint32_t enum_id;
        std::vector<P4MetaActionParam> params;
    };

    struct P4MetaTable {
        uint32_t id;
        std::vector<P4MetaKey> keys;
        std::map<uint32_t, P4MetaAction> actions;
        std::map<std::string, sai_attr_id_t> extra_fields;

        P4MetaTable(
                uint32_t table_id,
                std::initializer_list<P4MetaKey> init_keys,
                std::initializer_list<std::map<uint32_t, P4MetaAction>::value_type> init_actions,
                std::initializer_list<std::map<std::string, sai_attr_id_t>::value_type> extras
                ) : id(table_id), keys(init_keys), actions(init_actions), extra_fields(extras)

        {}

        const P4MetaKey* get_meta_key(
                _In_ sai_attr_id_t attr_id) const;

        const P4MetaKey* get_meta_key(
                _In_ const std::string &key_name) const;

		const P4MetaKey* get_meta_object_key() const;

		const P4MetaActionParam* get_meta_action_param(
				_In_ uint32_t action_id,
				_In_ sai_attr_id_t attr_id) const;

		pi_p4_id_t find_action_id(
				_In_ uint32_t attr_count,
				_In_ const sai_attribute_t *attr_list) const;
    };


    template<typename T>
    static inline
    void  set_attr_value_to_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const sai_attribute_value_t &value,
            _Inout_ T *p4_key_or_param)
    {
        if (field == "booldata")
            return booldataSetVal(value, p4_key_or_param, bitwidth);
        if (field == "u8")
            return u8SetVal(value, p4_key_or_param, bitwidth);
        if (field == "u16")
            return u16SetVal(value, p4_key_or_param, bitwidth);
        if (field == "u32")
            return u32SetVal(value, p4_key_or_param, bitwidth);
        if (field == "u64")
            return u64SetVal(value, p4_key_or_param, bitwidth);
        if (field == "ipaddr")
            return ipaddrSetVal(value, p4_key_or_param, bitwidth);
        if (field == "mac")
            return macSetVal(value, p4_key_or_param, bitwidth);
        if (field == "u8list")
            return u8listSetVal(value, p4_key_or_param, bitwidth);

        assert(0);
    }

    void  set_attr_value_to_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch_LPM *mf_lpm);

    template<typename T>
    static inline
    void get_attr_value_from_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const T *p4_key_or_param,
            _Out_ sai_attribute_value_t &value)
    {
        const char *v = p4_key_or_param->value().c_str();

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
            memcpy(value.u8list.list, v, p4_key_or_param->value().size());
        }
        else {
            assert(0);
        }
    }

    void get_attr_value_from_p4(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_LPM *mf_lpm,
            _Out_ sai_attribute_value_t &value);

    // set/get only for value.ipaddr.addr_family
    template<typename T>
    static inline
    void set_attr_ipaddr_family_to_p4(
            _In_ const sai_attribute_value_t &value,
            _Out_ T *t)
    {
        booldataSetVal(value.ipaddr.addr_family == SAI_IP_ADDR_FAMILY_IPV4 ? 0 : 1, t, 1);
    }

    template<typename T>
    static inline
    void get_attr_ipaddr_family_from_p4(
            _In_ const T *t,
            _Out_ sai_attribute_value_t &value)
    {
        const char *v = t->value().c_str();

        if (*(const bool*)v) // is_ipv6
            value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
        else
            value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
    }

    void set_attr_value_mask_to_p4_ternary(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch_Ternary *mf_ternary);

    void get_attr_value_mask_from_p4_ternary(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const p4::v1::FieldMatch_Ternary *mf_ternary,
            _Out_ sai_attribute_value_t &value);

    void set_attr_value_to_p4_match(
            _In_ const P4MetaKey &key,
            _In_ const sai_attribute_value_t &value,
            _Inout_ p4::v1::FieldMatch *mf);

    void get_attr_value_from_p4_match(
            _In_ const P4MetaKey &key,
            _In_ p4::v1::FieldMatch *mf,
            _Out_ sai_attribute_value_t &value);

    void  set_attr_to_p4_match(
            _In_ const P4MetaKey *meta_key,
            _In_ const sai_attribute_t *attr,
            _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry);

    void  set_attr_to_p4_action(
            _In_ const P4MetaActionParam *meta_param,
            _In_ const sai_attribute_t *attr,
            _Out_ p4::v1::Action *action);

    std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*> get_match_pair_from_p4_table_entry(
            _In_ const P4MetaKey *meta_key,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry);

    std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*> get_action_param_pair_from_p4_table_entry(
            _In_ const P4MetaActionParam *meta_param,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry);

    bool string_has_suffix(const std::string &str, const std::string &suffix);
}
