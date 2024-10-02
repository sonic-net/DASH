#ifndef __DASH_TARGET_SPECIFIC__
#define __DASH_TARGET_SPECIFIC__

//
// P4 arch/target includes
//
#if defined(TARGET_BMV2_V1MODEL)
    #include <v1model.p4>
#elif defined(TARGET_DPDK_PNA)  // TARGET_BMV2_V1MODEL
    #include <pna.p4>
#endif // TARGET_DPDK_PNA

//
// Counters
// - The counters are defined differently for different arch.
//
#if defined(TARGET_BMV2_V1MODEL)
    
    #define DEFINE_COUNTER(name, count, ...) \
        @SaiCounter[__VA_ARGS__] \
        counter(count, CounterType.packets_and_bytes) name;

    #define DEFINE_PACKET_COUNTER(name, count, ...) \
        @SaiCounter[__VA_ARGS__] \
        counter(count, CounterType.packets) name;

    #define DEFINE_BYTE_COUNTER(name, count, ...) \
        @SaiCounter[__VA_ARGS__] \
        counter(count, CounterType.bytes) name;

    #define DEFINE_HIT_COUNTER(name, count, ...) \
        @SaiCounter[no_suffix="true", __VA_ARGS__] \
        counter(count, CounterType.packets) name;

    #define UPDATE_COUNTER(name, index) \
        name.count((bit<32>)index)
    
    #define DEFINE_TABLE_COUNTER(counter_name) direct_counter(CounterType.packets_and_bytes) counter_name;
    #define ATTACH_TABLE_COUNTER(counter_name) counters = counter_name;
    
#elif defined(TARGET_DPDK_PNA)  // TARGET_BMV2_V1MODEL
    
    // Counters are not supported yet for PNA arch in DASH
    #define DEFINE_COUNTER(name, count, ...)
    #define DEFINE_PACKET_COUNTER(name, count, ...)
    #define DEFINE_BYTE_COUNTER(name, count, ...)
    #define DEFINE_HIT_COUNTER(name, count, ...)
    #define UPDATE_COUNTER(name, index)

    #ifdef DPDK_SUPPORTS_DIRECT_COUNTER_ON_WILDCARD_KEY_TABLE
        // Omit all direct counters for tables with ternary match keys,
        // because the latest version of p4c-dpdk as of 2023-Jan-26 does
        // not support this combination of features.  If you try to
        // compile it with this code enabled, the error message looks like
        // this:
        //
        // [--Werror=target-error] error: Direct counters and direct meters are unsupported for wildcard match table outbound_acl_stage1:dash_acl_rule|dash_acl
        //
        // This p4c issue is tracking this feature gap in p4c-dpdk:
        // https://github.com/p4lang/p4c/issues/3868
        #define DEFINE_TABLE_COUNTER(counter_name) DirectCounter<bit<64>>(PNA_CounterType_t.PACKETS_AND_BYTES) counter_name;
        #define ATTACH_TABLE_COUNTER(counter_name) pna_direct_counter = counter_name;
    #else
        #define DEFINE_TABLE_COUNTER(counter_name)
        #define ATTACH_TABLE_COUNTER(counter_name)
    #endif

#endif // TARGET_DPDK_PNA

//
// DBC (Design By Contract) macros
// - These macros will be used as a replacement for asserts, which makes the precondition and postcondition checks more explicit.
//
#if defined(TARGET_BMV2_V1MODEL)
    
    #define REQUIRES(cond) assert(cond)
    
#elif defined(TARGET_DPDK_PNA)  // TARGET_BMV2_V1MODEL
    
    // NOTE: PNA doesn't support assert, hence all macros are defined as empty
    #define REQUIRES(cond)
    
#endif // TARGET_DPDK_PNA

//
// Utility macros
//

// The second macro will have the value of x expanded before stringification.
#define PP_STR_RAW(x) #x
#define PP_STR(x) PP_STR_RAW(x)

#endif // __DASH_TARGET_SPECIFIC__
