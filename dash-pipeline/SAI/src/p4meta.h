#pragma once

#include <string>
#include <vector>
#include <map>
#include <PI/pi.h>

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

    template<typename T, typename V>
    void  set_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const V &value,
            _Inout_ T &t);

    template<typename V>
    void  set_mask(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const V &value,
            _Inout_ p4::v1::FieldMatch_Ternary *t);

    template<typename V>
    void set_key_value(
            _In_ const P4MetaKey &key,
            _In_ const V &value,
            _Inout_ p4::v1::FieldMatch *mf);

    // only for value.ipaddr.addr_family
    template<typename T>
    void get_ipaddr_family(
            _In_ const T &t,
            _Out_ sai_attribute_value_t &value);

    template<typename T>
    void get_value(
            _In_ const std::string &field,
            _In_ uint32_t bitwidth,
            _In_ const T &t,
            _Out_ sai_attribute_value_t &value);

    std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*> get_key(
            _In_ const P4MetaKey *meta_key,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry);

    std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*> get_action_param(
            _In_ const P4MetaActionParam *meta_param,
            _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry);
}
