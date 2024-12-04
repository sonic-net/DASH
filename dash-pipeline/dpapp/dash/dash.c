/**
 * @file
 * @brief Dash Plugin, plugin API / trace / CLI handling.
 */

#include <vnet/vnet.h>
#include <vnet/plugin/plugin.h>
#include <dash/dash.h>

#include <vlibapi/api.h>
#include <vlibmemory/api.h>

#include <dash/dash.api_enum.h>
#include <dash/dash.api_types.h>

#define REPLY_MSG_ID_BASE sm->msg_id_base
#include <vlibapi/api_helper_macros.h>

/* *INDENT-OFF* */
VLIB_PLUGIN_REGISTER () = {
    .version = DASH_PLUGIN_BUILD_VER,
    .description = "Dash of VPP Plugin",
};
/* *INDENT-ON* */

VLIB_REGISTER_LOG_CLASS (dash_log) = {
  .class_name = "dash",
};

dash_main_t dash_main;

/**
 * @brief Enable/disable the dash plugin.
 *
 * Action function shared between message handler and debug CLI.
 */

int dash_enable_disable (dash_main_t * sm, u32 sw_if_index,
                         int enable_disable)
{
  vnet_sw_interface_t * sw;
  int rv = 0;

  /* Utterly wrong? */
  if (pool_is_free_index (sm->vnet_main->interface_main.sw_interfaces,
                          sw_if_index))
    return VNET_API_ERROR_INVALID_SW_IF_INDEX;

  /* Not a physical port? */
  sw = vnet_get_sw_interface (sm->vnet_main, sw_if_index);
  if (sw->type != VNET_SW_INTERFACE_TYPE_HARDWARE)
    return VNET_API_ERROR_INVALID_SW_IF_INDEX;

  vnet_feature_enable_disable ("dash-pipeline", "dash-pipeline-input",
                               sw_if_index, enable_disable, 0, 0);

  return rv;
}

static clib_error_t *
dash_cmd_set_enable_disable_fn (vlib_main_t * vm,
                                unformat_input_t * input,
                                vlib_cli_command_t * cmd)
{
  dash_main_t * sm = &dash_main;
  u32 sw_if_index = ~0;
  int enable_disable = 1;
  int rv;

  while (unformat_check_input (input) != UNFORMAT_END_OF_INPUT) {
    if (unformat (input, "disable"))
      enable_disable = 0;
    else if (unformat (input, "%U", unformat_vnet_sw_interface,
                       sm->vnet_main, &sw_if_index))
      ;
    else
      break;
  }

  if (sw_if_index == ~0)
    return clib_error_return (0, "Please specify an interface...");

  rv = dash_enable_disable (sm, sw_if_index, enable_disable);

  switch(rv) {
  case 0:
    break;

  case VNET_API_ERROR_INVALID_SW_IF_INDEX:
    return clib_error_return
      (0, "Invalid interface, only works on physical ports");
    break;

  case VNET_API_ERROR_UNIMPLEMENTED:
    return clib_error_return (0, "Device driver doesn't support redirection");
    break;

  default:
    return clib_error_return (0, "dash_enable_disable returned %d",
                              rv);
  }
  return 0;
}

/**
 * @brief CLI command to enable/disable the dash plugin.
 */
VLIB_CLI_COMMAND (dash_set_command, static) = {
    .path = "set dash",
    .short_help =
    "set dash <interface-name> [disable]",
    .function = dash_cmd_set_enable_disable_fn,
};

/**
 * @brief Plugin API message handler.
 */
static void vl_api_dash_enable_disable_t_handler
(vl_api_dash_enable_disable_t * mp)
{
  vl_api_dash_enable_disable_reply_t * rmp;
  dash_main_t * sm = &dash_main;
  int rv;

  rv = dash_enable_disable (sm, ntohl(mp->sw_if_index),
                            (int) (mp->enable_disable));

  REPLY_MACRO(VL_API_DASH_ENABLE_DISABLE_REPLY);
}

/* API definitions */
#include <dash/dash.api.c>

/**
 * @brief Initialize the dash plugin.
 */
static clib_error_t * dash_init (vlib_main_t * vm)
{
  dash_main_t * sm = &dash_main;

  sm->vnet_main =  vnet_get_main ();

  /* Add our API messages to the global name_crc hash table */
  sm->msg_id_base = setup_message_id_table ();

  /* Reuse SECURE_DATA (0x876D) for dash metadata */
  ethernet_register_input_type (vm, ETHERNET_TYPE_SECURE_DATA, dash_node.index);

  dash_flow_table_init(dash_flow_table_get());

  dash_sai_init();

  return 0;
}

VLIB_INIT_FUNCTION (dash_init);

/**
 * @brief Hook the dash plugin into the VPP graph hierarchy.
 */
VNET_FEATURE_ARC_INIT (dash_pipeline, static) =
{
  .arc_name = "dash-pipeline",
  .start_nodes = VNET_FEATURES ("dash-pipeline-input"),
  .last_in_arc = "error-drop",
  .arc_index_ptr = &dash_main.feature_arc_index,
};

static uword
dash_timer_process (vlib_main_t * vm, vlib_node_runtime_t * rt, vlib_frame_t * f)
{
  f64 sleep_duration = 1.0;

  while (1)
  {
      /*
       * Notify the first worker thread to scan flow table
       */
      vlib_node_set_interrupt_pending (vlib_get_main_by_index(1),
        dash_flow_scan_node.index);

      vlib_process_suspend (vm, sleep_duration);
  }
  return 0;
}

/* *INDENT-OFF* */
VLIB_REGISTER_NODE (dash_timer_node,static) = {
  .function = dash_timer_process,
  .name = "dash-timer-process",
  .type = VLIB_NODE_TYPE_PROCESS,
};
/* *INDENT-ON* */

