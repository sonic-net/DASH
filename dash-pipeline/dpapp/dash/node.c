#include <arpa/inet.h>

#include <vlib/vlib.h>
#include <vnet/vnet.h>
#include <vnet/pg/pg.h>
#include <vnet/ethernet/ethernet.h>
#include <vppinfra/error.h>
#include <dash/dash.h>


extern vlib_node_registration_t dash_node;

#define foreach_dash_error \
_(OK, "packets process OK") \
_(FAILED, "packets process FAILED")

typedef enum
{
#define _(sym,str) DASH_ERROR_##sym,
    foreach_dash_error
#undef _
    DASH_N_ERROR,
} dash_error_t;

static char *dash_error_strings[] = {
#define _(sym,string) string,
    foreach_dash_error
#undef _
};

typedef struct
{
    u32 next_index;
    dash_error_t error;
} dash_trace_t;


/* packet trace format function */
static u8 *
format_dash_trace (u8 * s, va_list * args)
{
    CLIB_UNUSED (vlib_main_t * vm) = va_arg (*args, vlib_main_t *);
    CLIB_UNUSED (vlib_node_t * node) = va_arg (*args, vlib_node_t *);
    dash_trace_t *t = va_arg (*args, dash_trace_t *);

    s = format (s, "DASH: next index %d, error %d\n",
                t->next_index, t->error);

    return s;
}

typedef enum
{
    DASH_NEXT_INTERFACE_OUTPUT,
    DASH_NEXT_DROP,
    DASH_N_NEXT,
} dash_next_t;

static inline void swap_ether_mac(ethernet_header_t *ether)
{
    u8 tmp[6];

    clib_memcpy_fast (tmp, ether->src_address, sizeof (tmp));
    clib_memcpy_fast (ether->src_address, ether->dst_address, sizeof (tmp));
    clib_memcpy_fast (ether->dst_address, tmp, sizeof (tmp));
}

static inline dash_error_t process_one_buffer(vlib_buffer_t *buffer)
{
    u32 if_index;
    ethernet_header_t *ether;
    dash_header_t *dh = vlib_buffer_get_current (buffer);

    if (dash_flow_process(dash_flow_table_get(), dh) != 0) {
        return DASH_ERROR_FAILED;
    }

    /* Update dash header */
    dh->packet_meta.packet_source = DPAPP;
    if (dh->packet_meta.packet_subtype != FLOW_DELETE) {
        /* Only keep packet_meta and flow_key in dash_header_t */
        u16 length0 = ntohs(dh->packet_meta.length);
        dh->packet_meta.length = htons(offsetof(dash_header_t, flow_data));
        /* Move customer packet after dash header */
        clib_memmove((u8*)&dh->flow_data, (u8*)dh + length0,
                     vlib_buffer_get_tail(buffer) - (u8*)dh - length0);
        buffer->current_length -= length0 - offsetof(dash_header_t, flow_data);
    }

    vlib_buffer_reset (buffer);

    /* Update ethernet header via swap src and dst mac */
    ether = vlib_buffer_get_current (buffer);
    swap_ether_mac(ether);

    /* Send pkt back out the RX interface */
    if_index = vnet_buffer (buffer)->sw_if_index[VLIB_RX];
    vnet_buffer (buffer)->sw_if_index[VLIB_TX] = if_index;

    return DASH_ERROR_OK;
}

VLIB_NODE_FN (dash_node) (vlib_main_t * vm, vlib_node_runtime_t * node,
                          vlib_frame_t * frame)
{
    u32 n_left_from, *from, *to_next;
    dash_next_t next_index;
    dash_error_t error;
    u32 pkts_counter[DASH_N_ERROR] = { 0 };

    from = vlib_frame_vector_args (frame);
    n_left_from = frame->n_vectors;
    next_index = node->cached_next_index;

    while (n_left_from > 0)
    {
        u32 n_left_to_next;

        vlib_get_next_frame (vm, node, next_index, to_next, n_left_to_next);

        while (n_left_from > 0 && n_left_to_next > 0)
        {
            u32 bi0;
            vlib_buffer_t *b0;
            u32 next0 = DASH_NEXT_INTERFACE_OUTPUT;

            /* speculatively enqueue buffer to the current next frame */
            bi0 = from[0];
            to_next[0] = bi0;
            from += 1;
            to_next += 1;
            n_left_from -= 1;
            n_left_to_next -= 1;

            b0 = vlib_get_buffer (vm, bi0);
            error = process_one_buffer (b0);
            if (error != DASH_ERROR_OK) {
                next0 = DASH_NEXT_DROP;
            }

            pkts_counter[error] += 1;

            if (PREDICT_FALSE ((node->flags & VLIB_NODE_FLAG_TRACE) &&
                               (b0->flags & VLIB_BUFFER_IS_TRACED)))
            {
                dash_trace_t *t = vlib_add_trace (vm, node, b0, sizeof (*t));
                t->next_index = next0;
                t->error = error;
            }

            /* verify speculative enqueue, maybe switch current next frame */
            vlib_validate_buffer_enqueue_x1 (vm, node, next_index,
                                             to_next, n_left_to_next,
                                             bi0, next0);
        }

        vlib_put_next_frame (vm, node, next_index, n_left_to_next);
    }

    for (error = 0; error < DASH_N_ERROR; error++) {
        vlib_node_increment_counter (vm, dash_node.index,
                                     error, pkts_counter[error]);
    }
    return frame->n_vectors;
}

/* *INDENT-OFF* */
VLIB_REGISTER_NODE (dash_node) =
{
    .name = "dash-pipeline-input",
    .vector_size = sizeof (u32),
    .format_trace = format_dash_trace,
    .type = VLIB_NODE_TYPE_INTERNAL,

    .n_errors = ARRAY_LEN(dash_error_strings),
    .error_strings = dash_error_strings,

    .n_next_nodes = DASH_N_NEXT,

    /* edit / add dispositions here */
    .next_nodes = {
        [DASH_NEXT_INTERFACE_OUTPUT] = "interface-output",
        [DASH_NEXT_DROP] = "error-drop"
    },
};
/* *INDENT-ON* */

/*
 * fd.io coding-style-patch-verification: ON
 *
 * Local Variables:
 * eval: (c-set-style "gnu")
 * End:
 */
