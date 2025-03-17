#pragma once

#if __APPLE__
#include <net/ethernet.h>
#else
#include <netinet/ether.h>
#include <netinet/in.h>
#endif

#include <PI/pi.h>
#include <grpcpp/grpcpp.h>
#include <p4/v1/p4runtime.grpc.pb.h>
#include <google/protobuf/text_format.h>
#include <google/rpc/code.pb.h>

extern "C"
{
#include "sai.h"
#include "saiextensions.h"
}

#include "logger.h"

#include <mutex>
#include <unordered_map>
#include <atomic>
#include <limits>
#include <fstream>
#include <memory>

namespace dash
{
    namespace utils
    {
        template<typename T>
            void booldataSetVal(const sai_attribute_value_t &value, T &t, int bits = 8)
            {
                assert(bits <= 8);

                t->set_value(const_cast<bool*>(&value.booldata), 1);
            }

        template<typename T>
            void booldataSetVal(const bool &value, T &t, int bits = 8)
            {
                assert(bits <= 8);

                t->set_value(const_cast<bool*>(&value), 1);
            }

        template<typename T>
            void u8SetVal(const sai_attribute_value_t &value, T &t, int bits = 8)
            {
                assert(bits <= 8);

                t->set_value(const_cast<uint8_t*>(&value.u8), 1);
            }

        template<typename T>
            void u8SetVal(const sai_uint8_t &value, T &t, int bits = 8)
            {
                assert(bits <= 8);

                t->set_value(const_cast<uint8_t*>(&value), 1);
            }

        template<typename T>
            void u16SetVal(const sai_attribute_value_t &value, T &t, int bits = 16)
            {
                assert(bits <= 16);

                uint16_t val = value.u16;

                val = htons(val);

                t->set_value(&val, 2);
            }

        template<typename T>
            void u16SetVal(const sai_uint16_t &value, T &t, int bits = 16)
            {
                assert(bits <= 16);

                uint16_t val = value;

                val = htons(val);

                t->set_value(&val, 2);
            }

        template<typename T>
            void u32SetVal(const sai_attribute_value_t &value, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val = value.u32;

                val = htonl(val);
                val = val >> (32 - bits);

                int bytes = (bits + 7) / 8;

                t->set_value(&val, bytes);
            }

        template<typename T>
            void s32SetVal(const sai_attribute_value_t &value, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val = value.u32;

                val = htonl(val);
                val = val >> (32 - bits);

                int bytes = (bits + 7) / 8;

                t->set_value(&val, bytes);
            }

        template<typename T>
            void u32SetVal(const sai_uint32_t &value, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val = value;

                val = htonl(val);
                val = val >> (32 - bits);

                int bytes = (bits + 7) / 8;

                t->set_value(&val, bytes);
            }

        template<typename T>
            void u64SetVal(const sai_uint64_t &value, T &t, int bits = 64)
            {
                assert(bits <= 64);

                uint64_t val = value;

                if (*reinterpret_cast<const char*>("\0\x01") == 0) // Little Endian
                {
                    const uint32_t high_part = htonl(static_cast<uint32_t>(val >> 32));
                    const uint32_t low_part = htonl(static_cast<uint32_t>(val & 0xFFFFFFFFLL));

                    val = (static_cast<uint64_t>(low_part) << 32) | high_part;
                    val = val >> (64 - bits);
                }

                int bytes = (bits + 7) / 8;

                t->set_value(&val, bytes);
            }

        template<typename T>
            void u64SetVal(const sai_attribute_value_t &value, T &t, int bits = 64)
            {
                u64SetVal(value.u64, t, bits);
            }

        template<typename T>
            void ipaddrSetVal(const sai_ip_address_t &value, T &t, int bits = -1)
            {
                switch(value.addr_family)
                {
                    case SAI_IP_ADDR_FAMILY_IPV4:
                        {
                            uint32_t val = value.addr.ip4;

                            t->set_value(&val, 4);
                        }
                        break;

                    case SAI_IP_ADDR_FAMILY_IPV6:
                        {
                            t->set_value(const_cast<uint8_t*>(&value.addr.ip6[0]), 16);
                        }
                        break;

                    default:
                        assert(0 && "unrecognzed value.ipaddr.addr_family");
                }
            }

        template<typename T>
            void ipaddrSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                ipaddrSetVal(value.ipaddr, t);
            }

        template<typename T>
            void ipaddrSetMask(const sai_ip_address_t &value, T &t, int bits = -1)
            {
                switch(value.addr_family)
                {
                    case SAI_IP_ADDR_FAMILY_IPV4:
                        {
                            uint32_t mask = value.addr.ip4;

                            t->set_mask(&mask, 4);
                        }
                        break;

                    case SAI_IP_ADDR_FAMILY_IPV6:
                        {
                            t->set_mask(const_cast<uint8_t*>(&value.addr.ip6[0]), 16);
                        }
                        break;

                    default:
                        assert(0 && "unrecognzed value.ipaddr.addr_family");
                }
            }

        template<typename T>
            void ipaddrSetMask(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                ipaddrSetMask(value.ipaddr, t);
            }

        template<typename T>
            void macSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                t->set_value(const_cast<uint8_t*>(&value.mac[0]), 6);
            }

        template<typename T>
            void macSetVal(const sai_mac_t &value, T &t, int bits = -1)
            {
                t->set_value(const_cast<uint8_t*>(&value[0]), 6);
            }

        void correctIpPrefix(void *ip, const void *mask, size_t length);

        int leadingNonZeroBits(const uint32_t ipv4);

        int leadingNonZeroBits(const sai_ip6_t& ipv6);

        int getPrefixLength(const sai_ip_prefix_t &value);

        int getPrefixLength(const sai_attribute_value_t &value);

        template<typename T>
            void ipPrefixSetVal(const sai_ip_prefix_t &value, T &t, int bits = -1)
            {
                switch(value.addr_family)
                {
                    case SAI_IP_ADDR_FAMILY_IPV4:
                        {
                            uint32_t val = value.addr.ip4;

                            correctIpPrefix(&val, &value.mask.ip4, 4);

                            t->set_value(&val, 4);
                            t->set_prefix_len(getPrefixLength(value));
                        }
                        break;

                    case SAI_IP_ADDR_FAMILY_IPV6:
                        {
                            uint8_t ip[16];

                            std::copy(const_cast<uint8_t*>(&value.addr.ip6[0]), const_cast<uint8_t*>(&value.addr.ip6[0]) + 16, ip);

                            correctIpPrefix(ip, value.mask.ip6, 16);

                            t->set_value(ip, 16);
                            t->set_prefix_len(getPrefixLength(value));
                        }
                        break;

                    default:
                        assert(0 && "unrecognzed value.ipaddr.addr_family");
                }
            }

        template<typename T>
            void ipPrefixSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                ipPrefixSetVal(value.ipprefix, t);
            }

        template<typename T>
            void u32rangeSetVal(const sai_u32_range_t &range, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val;
                int bytes = (bits + 7) / 8;

                val = htonl(range.min);
                val = val >> (32 - bits);
                t->set_low(&val, bytes);

                val = htonl(range.max);
                val = val >> (32 - bits);
                t->set_high(&val, bytes);
            }

        template<typename T>
            void u32rangeSetVal(const sai_attribute_value_t &value, T &t, int bits = 32)
            {
                u32rangeSetVal(value.u32range, t, bits);
            }

        template<typename T>
            void u8listSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                t->set_value(value.u8list.list, value.u8list.count);
            }

        template<typename T>
            void u16listVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u32listSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u64listSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void ipaddrlistSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u8rangelistSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u16rangelistVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u32rangelistSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u64rangelistSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void ipaddrrangelistSetVal(const sai_attribute_value_t &value, T &t, int bits = -1)
            {
                assert (0 && "NYI");
            }

        template<typename T>
            void u32SetMask(const sai_attribute_value_t &value, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val = value.u32;

                val = htonl(val);
                val = val >> (32 - bits);

                int bytes = (bits + 7) / 8;

                t->set_mask(&val, bytes);
            }

        template<typename T>
            void u32SetMask(const sai_uint32_t &value, T &t, int bits = 32)
            {
                assert(bits <= 32);

                uint32_t val = value;

                val = htonl(val);
                val = val >> (32 - bits);

                int bytes = (bits + 7) / 8;

                t->set_mask(&val, bytes);
            }

        template<typename T>
            void u64SetMask(const sai_uint64_t &value, T &t, int bits = 64)
            {
                assert(bits <= 64);

                uint64_t val = value;

                if (*reinterpret_cast<const char*>("\0\x01") == 0) // Little Endian
                {
                    const uint32_t high_part = htonl(static_cast<uint32_t>(val >> 32));
                    const uint32_t low_part = htonl(static_cast<uint32_t>(val & 0xFFFFFFFFLL));

                    val = (static_cast<uint64_t>(low_part) << 32) | high_part;
                    val = val >> (64-bits);
                }

                int bytes = (bits + 7) / 8;

                t->set_mask(&val, bytes);
            }

        template<typename T>
            void u64SetMask(const sai_attribute_value_t &value, T &t, int bits = 64)
            {
                u64SetMask(value.u64, t, bits);
            }

        const sai_attribute_t* getMaskAttr(sai_attr_id_t id, uint32_t attr_count, const sai_attribute_t* attr_list);
    }
}
