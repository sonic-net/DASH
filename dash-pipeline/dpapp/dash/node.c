/*
 * Copyright (c) 2015 Cisco and/or its affiliates.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <arpa/inet.h>

#include <vlib/vlib.h>
#include <vnet/vnet.h>
#include <vnet/pg/pg.h>
#include <vnet/ethernet/ethernet.h>
#include <vppinfra/error.h>
#include <dash/dash.h>

typedef struct
{
  u32 next_index;
  u32 sw_if_index;
  u8 new_src_mac[6];
  u8 new_dst_mac[6];
} dash_trace_t;


/* packet trace format function */
static u8 *
format_dash_trace (u8 * s, va_list * args)
{
  CLIB_UNUSED (vlib_main_t * vm) = va_arg (*args, vlib_main_t *);
  CLIB_UNUSED (vlib_node_t * node) = va_arg (*args, vlib_node_t *);
  dash_trace_t *t = va_arg (*args, dash_trace_t *);

  s = format (s, "DASH: sw_if_index %d, next index %d\n",
	      t->sw_if_index, t->next_index);
  s = format (s, "  new src %U -> new dst %U",
	      format_mac_address, t->new_src_mac,
	      format_mac_address, t->new_dst_mac);

  return s;
}

extern vlib_node_registration_t dash_node;

#define foreach_dash_error \
_(SWAPPED, "Mac swap packets processed")

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

typedef enum
{
  DASH_NEXT_INTERFACE_OUTPUT,
  DASH_N_NEXT,
} dash_next_t;

#define foreach_mac_address_offset              \
_(0)                                            \
_(1)                                            \
_(2)                                            \
_(3)                                            \
_(4)                                            \
_(5)

VLIB_NODE_FN (dash_node) (vlib_main_t * vm, vlib_node_runtime_t * node,
			    vlib_frame_t * frame)
{
  u32 n_left_from, *from, *to_next;
  dash_next_t next_index;
  u32 pkts_swapped = 0;

  from = vlib_frame_vector_args (frame);
  n_left_from = frame->n_vectors;
  next_index = node->cached_next_index;

  while (n_left_from > 0)
    {
      u32 n_left_to_next;

      vlib_get_next_frame (vm, node, next_index, to_next, n_left_to_next);

      while (n_left_from >= 4 && n_left_to_next >= 2)
	{
	  u32 next0 = DASH_NEXT_INTERFACE_OUTPUT;
	  u32 next1 = DASH_NEXT_INTERFACE_OUTPUT;
	  u32 sw_if_index0, sw_if_index1;
	  u8 tmp0[6], tmp1[6];
	  ethernet_header_t *en0, *en1;
	  dash_header_t *dh0, *dh1;
	  u32 bi0, bi1;
	  vlib_buffer_t *b0, *b1;

	  /* Prefetch next iteration. */
	  {
	    vlib_buffer_t *p2, *p3;

	    p2 = vlib_get_buffer (vm, from[2]);
	    p3 = vlib_get_buffer (vm, from[3]);

	    vlib_prefetch_buffer_header (p2, LOAD);
	    vlib_prefetch_buffer_header (p3, LOAD);

	    clib_prefetch_store (p2->data);
	    clib_prefetch_store (p3->data);
	  }

	  /* speculatively enqueue b0 and b1 to the current next frame */
	  to_next[0] = bi0 = from[0];
	  to_next[1] = bi1 = from[1];
	  from += 2;
	  to_next += 2;
	  n_left_from -= 2;
	  n_left_to_next -= 2;

	  b0 = vlib_get_buffer (vm, bi0);
	  b1 = vlib_get_buffer (vm, bi1);

	  dh0 = vlib_buffer_get_current (b0);
	  dh1 = vlib_buffer_get_current (b1);
	  dash_flow_table_t *flow_table = dash_flow_table_get();
	  if (dash_flow_process(flow_table, dh0) != 0) {
	      /* FIXME */
	  }
	  if (dash_flow_process(flow_table, dh1) != 0) {
	      /* FIXME */
	  }

	  /*
	   * Build new packet
	   */

	  /* Update ethernet header via swap src and dst mac */
	  en0 = (ethernet_header_t*)dh0 - 1;
#define _(a) tmp0[a] = en0->src_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en0->src_address[a] = en0->dst_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en0->dst_address[a] = tmp0[a];
	  foreach_mac_address_offset;
#undef _

	  en1 = (ethernet_header_t*)dh1 - 1;
#define _(a) tmp1[a] = en1->src_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en1->src_address[a] = en1->dst_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en1->dst_address[a] = tmp1[a];
	  foreach_mac_address_offset;
#undef _

	  /* Update dash header */

	  dh0->packet_meta.packet_source = DPAPP;
	  if (dh0->packet_meta.packet_subtype != FLOW_DELETE) {
	    /* Only keep packet_meta and flow_key in dash_header_t */
	    u16 length0 = ntohs(dh0->packet_meta.length);
	    dh0->packet_meta.length = htons(offsetof(dash_header_t, flow_data));
	    /* Move customer packet after dash header */
	    clib_memmove((u8*)&dh0->flow_data, (u8*)dh0 + length0, vlib_buffer_get_tail(b0) - (u8*)dh0 - length0);
	    b0->current_length -= length0 - offsetof(dash_header_t, flow_data);
	  }

	  dh1->packet_meta.packet_source = DPAPP;
	  if (dh1->packet_meta.packet_subtype != FLOW_DELETE) {
	    /* Only keep packet_meta and flow_key in dash_header_t */
	    u16 length1 = ntohs(dh1->packet_meta.length);
	    dh1->packet_meta.length = htons(offsetof(dash_header_t, flow_data));
	    /* Move customer packet after dash header */
	    clib_memmove((u8*)&dh1->flow_data, (u8*)dh1 + length1, vlib_buffer_get_tail(b1) - (u8*)dh1 - length1);
	    b1->current_length -= length1 - offsetof(dash_header_t, flow_data);
	  }

	  vlib_buffer_reset (b0);
	  vlib_buffer_reset (b1);


	  sw_if_index0 = vnet_buffer (b0)->sw_if_index[VLIB_RX];
	  sw_if_index1 = vnet_buffer (b1)->sw_if_index[VLIB_RX];

	  /* Send pkt back out the RX interface */
	  vnet_buffer (b0)->sw_if_index[VLIB_TX] = sw_if_index0;
	  vnet_buffer (b1)->sw_if_index[VLIB_TX] = sw_if_index1;

	  pkts_swapped += 2;

	  if (PREDICT_FALSE ((node->flags & VLIB_NODE_FLAG_TRACE)))
	    {
	      if (b0->flags & VLIB_BUFFER_IS_TRACED)
		{
		  dash_trace_t *t =
		    vlib_add_trace (vm, node, b0, sizeof (*t));
		  t->sw_if_index = sw_if_index0;
		  t->next_index = next0;
		  clib_memcpy_fast (t->new_src_mac, en0->src_address,
				    sizeof (t->new_src_mac));
		  clib_memcpy_fast (t->new_dst_mac, en0->dst_address,
				    sizeof (t->new_dst_mac));

		}
	      if (b1->flags & VLIB_BUFFER_IS_TRACED)
		{
		  dash_trace_t *t =
		    vlib_add_trace (vm, node, b1, sizeof (*t));
		  t->sw_if_index = sw_if_index1;
		  t->next_index = next1;
		  clib_memcpy_fast (t->new_src_mac, en1->src_address,
				    sizeof (t->new_src_mac));
		  clib_memcpy_fast (t->new_dst_mac, en1->dst_address,
				    sizeof (t->new_dst_mac));
		}
	    }

	  /* verify speculative enqueues, maybe switch current next frame */
	  vlib_validate_buffer_enqueue_x2 (vm, node, next_index,
					   to_next, n_left_to_next,
					   bi0, bi1, next0, next1);
	}

      while (n_left_from > 0 && n_left_to_next > 0)
	{
	  u32 bi0;
	  vlib_buffer_t *b0;
	  u32 next0 = DASH_NEXT_INTERFACE_OUTPUT;
	  u32 sw_if_index0;
	  u8 tmp0[6];
	  ethernet_header_t *en0;
	  dash_header_t *dh0;

	  /* speculatively enqueue b0 to the current next frame */
	  bi0 = from[0];
	  to_next[0] = bi0;
	  from += 1;
	  to_next += 1;
	  n_left_from -= 1;
	  n_left_to_next -= 1;

	  b0 = vlib_get_buffer (vm, bi0);
	  dh0 = vlib_buffer_get_current (b0);
	  dash_flow_table_t *flow_table = dash_flow_table_get();
	  if (dash_flow_process(flow_table, dh0) != 0) {
	      /* FIXME */
	  }

	  /*
	   * Build new packet
	   */

	  /* Update ethernet header via swap src and dst mac */
	  en0 = (ethernet_header_t*)dh0 - 1;
#define _(a) tmp0[a] = en0->src_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en0->src_address[a] = en0->dst_address[a];
	  foreach_mac_address_offset;
#undef _
#define _(a) en0->dst_address[a] = tmp0[a];
	  foreach_mac_address_offset;
#undef _

	  /* Update dash header */
	  dh0->packet_meta.packet_source = DPAPP;
	  if (dh0->packet_meta.packet_subtype != FLOW_DELETE) {
	    /* Only keep packet_meta and flow_key in dash_header_t */
	    u16 length0 = ntohs(dh0->packet_meta.length);
	    dh0->packet_meta.length = htons(offsetof(dash_header_t, flow_data));
	    /* Move customer packet after dash header */
	    clib_memmove((u8*)&dh0->flow_data, (u8*)dh0 + length0, vlib_buffer_get_tail(b0) - (u8*)dh0 - length0);
	    b0->current_length -= length0 - offsetof(dash_header_t, flow_data);
	  }

	  vlib_buffer_reset (b0);

	  sw_if_index0 = vnet_buffer (b0)->sw_if_index[VLIB_RX];

	  /* Send pkt back out the RX interface */
	  vnet_buffer (b0)->sw_if_index[VLIB_TX] = sw_if_index0;

	  if (PREDICT_FALSE ((node->flags & VLIB_NODE_FLAG_TRACE)
			     && (b0->flags & VLIB_BUFFER_IS_TRACED)))
	    {
	      dash_trace_t *t = vlib_add_trace (vm, node, b0, sizeof (*t));
	      t->sw_if_index = sw_if_index0;
	      t->next_index = next0;
	      clib_memcpy_fast (t->new_src_mac, en0->src_address,
				sizeof (t->new_src_mac));
	      clib_memcpy_fast (t->new_dst_mac, en0->dst_address,
				sizeof (t->new_dst_mac));
	    }

	  pkts_swapped += 1;

	  /* verify speculative enqueue, maybe switch current next frame */
	  vlib_validate_buffer_enqueue_x1 (vm, node, next_index,
					   to_next, n_left_to_next,
					   bi0, next0);
	}

      vlib_put_next_frame (vm, node, next_index, n_left_to_next);
    }

  vlib_node_increment_counter (vm, dash_node.index,
			       DASH_ERROR_SWAPPED, pkts_swapped);
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
