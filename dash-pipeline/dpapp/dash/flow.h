#ifndef __included_flow_h__
#define __included_flow_h__

#include <asm/byteorder.h>

#include <vppinfra/bihash_48_8.h>
#include <vppinfra/pool.h>
#include <vnet/ip/ip.h>

#include <vppinfra/tw_timer_2t_1w_2048sl.h>

/* Default timeout in seconds */
#define DASH_FLOW_TIMEOUT   30
/* Max timeout in seconds */
#define DASH_FLOW_MAX_TIMEOUT   1800

typedef enum _dash_packet_source_t {
    EXTERNAL = 0,           // Packets from external sources.
    PIPELINE = 1,           // Packets from P4 pipeline.
    DPAPP = 2,              // Packets from data plane app.
    PEER = 3                // Packets from the paired DPU.
} dash_packet_source_t;

typedef enum _dash_packet_type_t {
    REGULAR = 0,            // Regular packets from external sources.
    FLOW_SYNC_REQ = 1,      // Flow sync request packet.
    FLOW_SYNC_ACK = 2,      // Flow sync ack packet.
    DP_PROBE_REQ = 3,       // Data plane probe packet.
    DP_PROBE_ACK = 4        // Data plane probe ack packet.
} dash_packet_type_t;

typedef enum _dash_packet_subtype_t {
    NONE = 0,        // no op
    FLOW_CREATE = 1, // New flow creation.
    FLOW_UPDATE = 2, // Flow resimulation or any other reason causing existing flow to be updated.
    FLOW_DELETE = 3  // Flow deletion.
} dash_packet_subtype_t;

typedef struct dash_packet_meta {
    u8 packet_source;
#if defined(__LITTLE_ENDIAN_BITFIELD)
    u8 packet_subtype :4;
    u8 packet_type :4;
#elif defined (__BIG_ENDIAN_BITFIELD)
    u8 packet_type :4;
    u8 packet_subtype :4;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
    u16 length;
} __clib_packed  dash_packet_meta_t;

/*
 * If sizeof flow_key_t > 48, update the use of bihash_xx
 */
typedef struct flow_key {
    u8 eni_mac[6];
    u16 vnet_id;
    ip46_address_t src_ip;
    ip46_address_t dst_ip;
    u16 src_port;
    u16 dst_port;
    u8  ip_proto;
#if defined(__LITTLE_ENDIAN_BITFIELD)
    u8  is_ip_v6 :1;
    u8  reserved :7;
#elif defined (__BIG_ENDIAN_BITFIELD)
    u8  reserved :7;
    u8  is_ip_v6 :1;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
} __clib_packed  flow_key_t;

typedef union {
    flow_key_t key;
    u64 bihash_key[6]; /* bihash_48_8 */
} dash_flow_hash_key_t;

typedef struct flow_data {
#if defined(__LITTLE_ENDIAN_BITFIELD)
    u8  is_unidirectional :1;
    u8  reserved :7;
#elif defined (__BIG_ENDIAN_BITFIELD)
    u8  reserved :7;
    u8  is_unidirectional :1;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
    u16 direction;
    u32 version;
    u32 actions;
    u32 meter_class;
    u32 idle_timeout_in_ms;
} __clib_packed flow_data_t;

typedef struct encap_data {
    u16 vni_high;
    u8  vni_low;
    u8  reserved;
    ip4_address_t underlay_sip;
    ip4_address_t underlay_dip;
    u8 underlay_smac[6];
    u8 underlay_dmac[6];
    u16 dash_encapsulation;
} __clib_packed encap_data_t;

typedef struct overlay_rewrite_data {
    u8 dmac[6];
    ip46_address_t sip;
    ip46_address_t dip;
    ip6_address_t  sip_mask;
    ip6_address_t  dip_mask;
    u16 sport;
    u16 dport;
#if defined(__LITTLE_ENDIAN_BITFIELD)
    u8  is_ipv6  :1;
    u8  reserved :7;
#elif defined (__BIG_ENDIAN_BITFIELD)
    u8  reserved :7;
    u8  is_ipv6  :1;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
} __clib_packed overlay_rewrite_data_t;


typedef struct dash_header {
    dash_packet_meta_t    packet_meta;
    union {
        struct {
            flow_key_t   flow_key;
            flow_data_t  flow_data; // flow common data
            overlay_rewrite_data_t flow_overlay_data;
            encap_data_t flow_u0_encap_data;
            encap_data_t flow_u1_encap_data;
        };
        u8 data[0];
    };
}
__clib_packed  dash_header_t;


typedef struct dash_flow_entry {
    union {
        flow_key_t key;
        u64 bihash_key[6]; /* bihash_48_8 */
    };

    struct {
        flow_data_t            flow_data;
        overlay_rewrite_data_t flow_overlay_data;
        encap_data_t           flow_u0_encap_data;
        encap_data_t           flow_u1_encap_data;
    };

    u32 index;

    /* timers */
    u32 timer_handle; /* index in the timer pool */
    u32 timeout;      /* in seconds */
    u64 access_time;  /* in seconds */
} dash_flow_entry_t;

typedef struct dash_flow_stats {
    u32 create_ok;
    u32 create_fail;

    u32 remove_ok;
    u32 remove_fail;
} dash_flow_stats_t;

typedef struct dash_flow_table {
    /* hashtable */
    BVT(clib_bihash) hash_table;

    dash_flow_entry_t *flow_pool;
    dash_flow_stats_t  flow_stats;

    TWT (tw_timer_wheel) flow_tw;
} dash_flow_table_t;

dash_flow_table_t* dash_flow_table_get (void);
dash_flow_entry_t* dash_flow_alloc();
void dash_flow_free(dash_flow_entry_t *flow);
dash_flow_entry_t* dash_flow_get_by_index (u32 index);

void dash_flow_table_init (dash_flow_table_t *flow_table);
int dash_flow_table_add_entry (dash_flow_table_t *flow_table, dash_flow_entry_t *flow);
int dash_flow_table_delete_entry (dash_flow_table_t *flow_table, dash_flow_entry_t *flow);
dash_flow_entry_t* dash_flow_table_lookup_entry (dash_flow_table_t *flow_table, flow_key_t *flow_key);


int dash_flow_process (dash_flow_table_t *flow_table, const dash_header_t *dh);

extern vlib_node_registration_t dash_flow_scan_node;

#endif /* __included_flow_h__ */
