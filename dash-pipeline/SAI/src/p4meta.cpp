extern "C" {
#include "saimetadata.h"
}

#include "utils.h"
#include "p4meta.h"

using namespace dash;
using namespace dash::utils;

template<typename T, typename V>
void  dash::set_value(
        _In_ const std::string &field,
        _In_ uint32_t bitwidth,
        _In_ const V &value,
        _Inout_ T &t)
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
    if (field == "ipPrefix")
        return ipPrefixSetVal(value, t, bitwidth);
    if (field == "u8list")
        return u8listSetVal(value, t, bitwidth);
}

template<typename V>
void  dash::set_mask(
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

template<typename V>
void dash::set_key_value(
        _In_ const P4MetaKey &key,
        _In_ const V &value,
        _Inout_ p4::v1::FieldMatch *mf)
{
    if (key.match_type == "exact") {
        auto mf_exact = mf->mutable_exact();
        set_value(key.field, key.bitwidth, value, mf_exact);
    }
    else if (key.match_type == "lpm") {
        auto mf_lpm = mf->mutable_lpm();
        set_value(key.field, key.bitwidth, value, mf_lpm);
        // FIXME
        //set_mask(key.field, key.bitwidth, value, mf_lpm);
    }
    else if (key.match_type == "ternary") {
        auto mf_ternary = mf->mutable_ternary();
        set_value(key.field, key.bitwidth, value, mf_ternary);
        // FIXME
        //set_mask(key.field, key.bitwidth, value, mf_ternary);
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

template<typename T>
void dash::get_ipaddr_family(
        _In_ const T &t,
        _Out_ sai_attribute_value_t &value)
{
    const char *v = t->value().c_str();

    if (*const_cast<bool*>(v)) // is_ipv6
        value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV6;
    else
        value.ipaddr.addr_family = SAI_IP_ADDR_FAMILY_IPV4;
}

template<typename T>
void dash::get_value(
        _In_ const std::string &field,
        _In_ uint32_t bitwidth,
        _In_ const T &t,
        _Out_ sai_attribute_value_t &value)
{
    const char *v = t->value().c_str();

    if (field == "booldata") {
       value.booldata = *const_cast<bool*>(v);
    }
    else if (field == "u8") {
       value.u8 = *const_cast<uint8_t*>(v);
    }
    else if (field == "u16") {
       uint16_t val = *const_cast<uint16_t*>(v);
       value.u16 = ntohs(val);
    }
    else if (field == "u32") {
       uint32_t val = *const_cast<uint32_t*>(v);
       value.u32 = ntohl(val);
    }
    else if (field == "u64") {
       uint64_t val = *const_cast<uint64_t*>(v);
       if (*reinterpret_cast<const char*>("\0\x01") == 0) { // Little Endian
           value.u64 = be64toh(val);
       }
       else {
           value.u64 = val;
       }
    }
    else if (field == "ipaddr") {
        if (value.ipaddr.addr_family == SAI_IP_ADDR_FAMILY_IPV4) {
            uint32_t val = *const_cast<uint32_t*>(v);
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

std::pair<p4::v1::Action_Param*, p4::v1::Action_Param*>
dash::get_action_param(
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

std::pair<p4::v1::FieldMatch*, p4::v1::FieldMatch*>
dash::get_key(
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

