#include "utils.h"

#include <algorithm>

const sai_attribute_t* dash::utils::getMaskAttr(sai_attr_id_t id, uint32_t attr_count, const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();

    for (uint32_t i = 0; i < attr_count; i++)
    {
        if (attr_list[i].id == id)
        {
            return &attr_list[i];
        }
    }

    return nullptr;
}

void dash::utils::correctIpPrefix(void *ip, const void *mask, size_t length)
{
    DASH_LOG_ENTER();

    auto _ip = reinterpret_cast<uint8_t *>(ip);
    auto _mask = reinterpret_cast<const uint8_t *>(mask);

    for (size_t i = 0; i < length; i++)
    {
        _ip[i] = _ip[i] & _mask[i];
    }
}

int dash::utils::leadingNonZeroBits(const uint32_t ipv4)
{
    DASH_LOG_ENTER();

    auto firstSetBit = __builtin_ffs(ipv4);

    if (0==firstSetBit)
    {
        return 0;
    }

    return 33 - firstSetBit;
}

int dash::utils::leadingNonZeroBits(const sai_ip6_t& ipv6)
{
    DASH_LOG_ENTER();

    int trailingZeros = 0;

    for (int i = 0; i < 16; i+=4)
    {
        auto num = static_cast<uint32_t>(ipv6[i]) +
            (static_cast<uint32_t>(ipv6[i+1]) << 8) +
            (static_cast<uint32_t>(ipv6[i+2]) << 16) +
            (static_cast<uint32_t>(ipv6[i+3]) << 24);

        auto firstSetBit = leadingNonZeroBits(num);

        if (firstSetBit > 0)
        {
            return 129-trailingZeros-(33-firstSetBit);
        }

        trailingZeros += 32;
    }

    return 0;
}


int dash::utils::getPrefixLength(const sai_ip_prefix_t &value)
{
    switch(value.addr_family)
    {
        case SAI_IP_ADDR_FAMILY_IPV4:
            // LPM entry match field prefix length calculation needs to be fixed to accomodate 128 bit size.
            // So the 96 is added to the prefix length.
            return leadingNonZeroBits(htonl(value.mask.ip4)) + 96;
        case SAI_IP_ADDR_FAMILY_IPV6:
            sai_ip6_t mask;
            memcpy(mask, value.mask.ip6, sizeof(mask));
            std::reverse(std::begin(mask), std::end(mask));
            return leadingNonZeroBits(mask);
        default:
            assert(0 && "unrecognzed value.ipaddr.addr_family");
    }
    return 0;
}

int dash::utils::getPrefixLength(const sai_attribute_value_t &value)
{
    return getPrefixLength(value.ipprefix);
}
