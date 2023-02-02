#ifndef __DASH_ARCH_SPECIFIC__
#define __DASH_ARCH_SPECIFIC__

#ifdef ARCH_BMV2_V1MODEL

#include <v1model.p4>
#define DIRECT_COUNTER_TABLE_PROPERTY counters

#endif // ARCH_BMV2_V1MODEL

#ifdef ARCH_DPDK_PNA

#include <pna.p4>
#define DIRECT_COUNTER_TABLE_PROPERTY pna_direct_counter

#endif // ARCH_DPDK_PNA

#endif // __DASH_ARCH_SPECIFIC__
