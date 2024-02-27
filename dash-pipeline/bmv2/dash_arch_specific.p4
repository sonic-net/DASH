#ifndef __DASH_TARGET_SPECIFIC__
#define __DASH_TARGET_SPECIFIC__

#ifdef TARGET_BMV2_V1MODEL

#include <v1model.p4>
#define DIRECT_COUNTER_TABLE_PROPERTY counters

// DBC (Design By Contract) macros
#define REQUIRES(cond) assert(cond)

#endif // TARGET_BMV2_V1MODEL

#ifdef TARGET_DPDK_PNA

#include <pna.p4>
#define DIRECT_COUNTER_TABLE_PROPERTY pna_direct_counter

// DBC (Design By Contract) macros
// NOTE: PNA doesn't support assert, hence all macros are defined as empty
#define REQUIRES(cond)

#endif // TARGET_DPDK_PNA

#endif // __DASH_TARGET_SPECIFIC__
