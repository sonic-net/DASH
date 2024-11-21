
#include <arpa/inet.h>

#include <dash/dash.h>
#include <dash/flow.h>

#define DASH_FLOW_NUM (1 << 12) /* 4K */
#define DASH_FLOW_NUM_BUCKETS (DASH_FLOW_NUM / BIHASH_KVP_PER_PAGE)
#define DASH_FLOW_MEMORY_SIZE (DASH_FLOW_NUM * 32)

static dash_flow_table_t dash_flow_table;

dash_flow_table_t*
dash_flow_table_get (void)
{
  return &dash_flow_table;
}

dash_flow_entry_t*
dash_flow_alloc()
{
    dash_flow_entry_t *flow;
    dash_flow_table_t *flow_table = dash_flow_table_get();

    pool_get (flow_table->flow_pool, flow);
    clib_memset (flow, 0, sizeof (*flow));
    flow->index = flow - flow_table->flow_pool;
    flow->timeout = DASH_FLOW_TIMEOUT;
    flow->access_time = (u64)unix_time_now();
    return flow;
}

void
dash_flow_free(dash_flow_entry_t *flow)
{
    dash_flow_table_t *flow_table = dash_flow_table_get();

    if (flow != NULL)
        pool_put(flow_table->flow_pool, flow);
}

dash_flow_entry_t*
dash_flow_get_by_index (u32 index)
{
    dash_flow_table_t *flow_table = dash_flow_table_get();
    dash_flow_entry_t *flow = pool_elt_at_index(flow_table->flow_pool, index);

    return flow;
}

static int
dash_flow_create (dash_flow_table_t *flow_table, const dash_header_t *dh)
{
    int r;
    sai_status_t status;

    ASSERT(flow_table && dh);

    u16 length = ntohs(dh->packet_meta.length);
    ASSERT_MSG(length >= offsetof(dash_header_t, flow_overlay_data), "dash header not enough");

    dash_flow_entry_t* flow = dash_flow_alloc();

    clib_memcpy_fast(&flow->key, &dh->flow_key, sizeof(dh->flow_key));

    clib_memcpy_fast(&flow->flow_data, &dh->flow_data, sizeof(dh->flow_data));

    /* FIXME
     * Assume overlay_data, u0_encap_data, u1_encap_data in order if exists
     * Need to add their offset in generic.
     */
    if (flow->flow_data.actions != 0) {
        ASSERT_MSG(length >= offsetof(dash_header_t, flow_u0_encap_data),
                "dash header not enough");
        clib_memcpy_fast(&flow->flow_overlay_data, &dh->flow_overlay_data, sizeof(dh->flow_overlay_data));
    }

    if (flow->flow_data.actions & htonl(SAI_DASH_FLOW_ACTION_ENCAP_U0)) {
        ASSERT_MSG(length >= offsetof(dash_header_t, flow_u1_encap_data),
                "dash header not enough");
        clib_memcpy_fast(&flow->flow_u0_encap_data, &dh->flow_u0_encap_data, sizeof(dh->flow_u0_encap_data));
    }

    if (flow->flow_data.actions & htonl(SAI_DASH_FLOW_ACTION_ENCAP_U1)) {
        ASSERT_MSG((u8*)(&dh->flow_u1_encap_data + 1) <= (u8*)dh + length,
                "dash header not enough");
        clib_memcpy_fast(&flow->flow_u1_encap_data, &dh->flow_u1_encap_data, sizeof(dh->flow_u1_encap_data));
    }

    r = dash_flow_table_add_entry (flow_table, flow);
    if (r != 0) goto table_add_entry_fail;

    status = dash_sai_create_flow_entry(flow);
    if (status != SAI_STATUS_SUCCESS) goto sai_create_flow_fail;

    flow_table->flow_stats.create_ok++;
    flow->timer_handle = TW (tw_timer_start) (&flow_table->flow_tw, flow->index, 0, flow->timeout);
    return 0;

sai_create_flow_fail:
    flow_table->flow_stats.create_fail++;
    dash_flow_table_delete_entry (flow_table, flow);
    dash_flow_free(flow);
    return -1;

table_add_entry_fail:
    dash_flow_free(flow);
    return r;
}

static int
dash_flow_update (dash_flow_table_t *flow_table, const dash_header_t *dh)
{
    return -1; /* TODO later */
}

static int
dash_flow_remove (dash_flow_table_t *flow_table, const dash_header_t *dh)
{
    int r = -1;
    sai_status_t status;
    dash_flow_hash_key_t flow_hash_key;
    dash_flow_entry_t* flow;

    ASSERT(flow_table && dh);

    u16 length = ntohs(dh->packet_meta.length);
    ASSERT(length >= offsetof(dash_header_t, flow_key));

    bzero(&flow_hash_key, sizeof(flow_hash_key));
    clib_memcpy_fast(&flow_hash_key, &dh->flow_key, sizeof(dh->flow_key));

    flow = dash_flow_table_lookup_entry(flow_table, &flow_hash_key.key);
    if (!flow) goto flow_not_found;

    status = dash_sai_remove_flow_entry(flow);
    if (status != SAI_STATUS_SUCCESS) goto sai_remove_flow_fail;

    TW (tw_timer_stop) (&flow_table->flow_tw, flow->timer_handle);

    r = dash_flow_table_delete_entry (flow_table, flow);
    ASSERT(r == 0);
    dash_flow_free(flow);

    flow_table->flow_stats.remove_ok++;
    return 0;

sai_remove_flow_fail:
    flow_table->flow_stats.remove_fail++;

flow_not_found:
    return -1;
}

typedef int (*dash_flow_cmd_handler) (dash_flow_table_t *flow_table, const dash_header_t *dh);

static dash_flow_cmd_handler  flow_cmd_funs[] = {
    [FLOW_CREATE] = dash_flow_create,
    [FLOW_UPDATE] = dash_flow_update,
    [FLOW_DELETE] = dash_flow_remove,
};


int
dash_flow_process (dash_flow_table_t *flow_table, const dash_header_t *dh)
{
    ASSERT(dh->packet_meta.packet_type == REGULAR);
    ASSERT(dh->packet_meta.packet_subtype >= FLOW_CREATE);
    ASSERT(dh->packet_meta.packet_subtype <= FLOW_DELETE);

    return flow_cmd_funs[dh->packet_meta.packet_subtype](flow_table, dh);
}

static void
dash_flow_expired_timer_callback (u32 * expired_timers)
{
  int i;
  u32 index;
  sai_status_t status;
  dash_flow_table_t *flow_table = dash_flow_table_get();

  for (i = 0; i < vec_len (expired_timers); i++)
    {
      index = expired_timers[i] & 0x7FFFFFFF;
      dash_flow_entry_t *flow = dash_flow_get_by_index(index);
      status = dash_sai_remove_flow_entry(flow);
      if (status != SAI_STATUS_SUCCESS) {
        dash_log_err("dash_sai_remove_flow_entry fail: %d", status);
        continue;
      }

      if (dash_flow_table_delete_entry (flow_table, flow) == 0) {
        dash_flow_free(flow);
      } else {
        ASSERT(0);
      }
    }
}

void
dash_flow_table_init (dash_flow_table_t *flow_table)
{
    BV(clib_bihash_init) (&flow_table->hash_table, "flow hash table",
        DASH_FLOW_NUM_BUCKETS, DASH_FLOW_MEMORY_SIZE);

    pool_init_fixed (flow_table->flow_pool, DASH_FLOW_NUM);

    bzero(&flow_table->flow_stats, sizeof(flow_table->flow_stats));

    TW (tw_timer_wheel_init) (&flow_table->flow_tw,
                              dash_flow_expired_timer_callback,
                              1.0 /* timer interval */, 1024);
}

int
dash_flow_table_add_entry (dash_flow_table_t *flow_table, dash_flow_entry_t *flow)
{
    BVT (clib_bihash_kv) kv;

    clib_memcpy_fast (kv.key, &flow->key, sizeof(kv.key));
    kv.value = (u64)(uintptr_t)&flow->flow_data;
    return BV (clib_bihash_add_del) (&flow_table->hash_table, &kv, 1 /* is_add */ );
}

int
dash_flow_table_delete_entry (dash_flow_table_t *flow_table, dash_flow_entry_t *flow)
{
    BVT (clib_bihash_kv) kv;

    clib_memcpy_fast (kv.key, &flow->key, sizeof(kv.key));
    return BV (clib_bihash_add_del) (&flow_table->hash_table, &kv, 0 /* is_del */ );
}

dash_flow_entry_t*
dash_flow_table_lookup_entry (dash_flow_table_t *flow_table, flow_key_t *flow_key)
{
    BVT (clib_bihash_kv) kv;
    flow_data_t *flow_data;

    clib_memcpy_fast (kv.key, flow_key, sizeof(kv.key));
    if (BV (clib_bihash_search) (&flow_table->hash_table, &kv, &kv))
        return NULL;

    flow_data = (flow_data_t *)(uintptr_t)kv.value;
    return (dash_flow_entry_t*)((u8*)flow_data - offsetof(dash_flow_entry_t, flow_data));
}

static uword
dash_flow_scan (vlib_main_t * vm, vlib_node_runtime_t * rt, vlib_frame_t * f)
{
    dash_flow_table_t *flow_table = dash_flow_table_get();
    TW (tw_timer_expire_timers) (&flow_table->flow_tw, vlib_time_now(vm));
    return 0;
}

/* *INDENT-OFF* */
VLIB_REGISTER_NODE (dash_flow_scan_node) = {
  .function = dash_flow_scan,
  .name = "dash-flow-scan",
  .type = VLIB_NODE_TYPE_INPUT,
  .state = VLIB_NODE_STATE_INTERRUPT,
};
/* *INDENT-ON* */

static u8 *
dash_flow_format (u8 * s, va_list * args)
{
  dash_flow_entry_t *flow = va_arg(*args, dash_flow_entry_t*);

  s = format (s, "eni %U, vnet_id %d, proto %d, ",
              format_mac_address, flow->key.eni_mac,
              clib_net_to_host_u16 (flow->key.vnet_id),
              flow->key.ip_proto);

  if (flow->key.is_ip_v6) {
      s = format (s, "%U %d -> %U %d\n",
                  format_ip6_address, &flow->key.src_ip.ip6,
                  clib_net_to_host_u16 (flow->key.src_port),
                  format_ip6_address, &flow->key.dst_ip.ip6,
                  clib_net_to_host_u16 (flow->key.dst_port));
  } else {
      s = format (s, "%U %d -> %U %d\n",
                  format_ip4_address, &flow->key.src_ip.ip4,
                  clib_net_to_host_u16 (flow->key.src_port),
                  format_ip4_address, &flow->key.dst_ip.ip4,
                  clib_net_to_host_u16 (flow->key.dst_port));
  }

  s = format (s, "        common data - version %u, direction %u, actions 0x%x",
              clib_net_to_host_u32 (flow->flow_data.version),
              clib_net_to_host_u16 (flow->flow_data.direction),
              clib_net_to_host_u32 (flow->flow_data.actions));
  s = format (s, ", timeout %lu\n",
              flow->access_time + flow->timeout - (u64)unix_time_now());

  return s;
}

typedef struct dash_flow_show_walk_ctx_t_
{
  u8 verbose;
  vlib_main_t *vm;
} dash_flow_show_walk_ctx_t;

static int
dash_flow_show_walk_cb (BVT (clib_bihash_kv) * kvp, void *arg)
{
  dash_flow_show_walk_ctx_t *ctx = arg;
  flow_data_t *flow_data = (flow_data_t *)(uintptr_t)kvp->value;
  dash_flow_entry_t *flow = (dash_flow_entry_t*)((u8*)flow_data -
          offsetof(dash_flow_entry_t, flow_data));

  vlib_cli_output (ctx->vm, "%6u: %U", flow->index, dash_flow_format, flow);

  return BIHASH_WALK_CONTINUE;
}

static clib_error_t *
dash_cmd_show_flow_fn (vlib_main_t * vm,
               unformat_input_t * input, vlib_cli_command_t * cmd)
{
  clib_error_t *error = 0;
  dash_flow_show_walk_ctx_t ctx = {
    .vm = vm,
  };
  dash_flow_table_t *flow_table = dash_flow_table_get();

  BV (clib_bihash_foreach_key_value_pair)
    (&flow_table->hash_table, dash_flow_show_walk_cb, &ctx);

  return error;
}

VLIB_CLI_COMMAND (dash_show_flow_command, static) = {
    .path = "show dash flow",
    .short_help = "show dash flow [src-addr IP]",
    .function = dash_cmd_show_flow_fn,
};

static clib_error_t *
dash_cmd_clear_flow_fn (vlib_main_t * vm,
               unformat_input_t * input, vlib_cli_command_t * cmd)
{
  clib_error_t *error = 0;
  dash_flow_table_t *flow_table = dash_flow_table_get();
  u32 index;

  if (!unformat (input, "%u", &index))
    {
      error = clib_error_return (0, "expected flow index");
      goto done;
    }


  dash_flow_entry_t *flow = dash_flow_get_by_index(index);
  sai_status_t status = dash_sai_remove_flow_entry(flow);
  if (status != SAI_STATUS_SUCCESS) {
    error = clib_error_return (0, "dash_sai_remove_flow_entry fail: %d", status);
  }

  TW (tw_timer_stop) (&flow_table->flow_tw, flow->timer_handle);

  if (dash_flow_table_delete_entry (flow_table, flow) == 0) {
    dash_flow_free(flow);
  } else {
    ASSERT(0);
  }

done:
  return error;
}

VLIB_CLI_COMMAND (dash_clear_flow_command, static) = {
    .path = "clear dash flow",
    .short_help = "clear dash flow <index>",
    .function = dash_cmd_clear_flow_fn,
};


static clib_error_t *
dash_cmd_show_flow_stats_fn (vlib_main_t * vm,
               unformat_input_t * input, vlib_cli_command_t * cmd)
{
  clib_error_t *error = 0;
  dash_flow_table_t *flow_table = dash_flow_table_get();

  vlib_cli_output (vm, "%12s: %u", "create_ok",
                   flow_table->flow_stats.create_ok);
  vlib_cli_output (vm, "%12s: %u", "create_fail",
                   flow_table->flow_stats.create_fail);
  vlib_cli_output (vm, "%12s: %u", "remove_ok",
                   flow_table->flow_stats.remove_ok);
  vlib_cli_output (vm, "%12s: %u", "remove_fail",
                   flow_table->flow_stats.remove_fail);

  return error;
}

VLIB_CLI_COMMAND (dash_show_flow_stats_command, static) = {
    .path = "show dash flow stats",
    .short_help = "show dash flow [src-addr IP]",
    .function = dash_cmd_show_flow_stats_fn,
};

