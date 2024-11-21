#ifndef __included_dash_h__
#define __included_dash_h__

#include <vnet/vnet.h>
#include <vnet/ip/ip.h>
#include <vnet/ethernet/ethernet.h>

#include <vppinfra/hash.h>
#include <vppinfra/error.h>
#include <vppinfra/elog.h>

#include <dash/flow.h>

#include <sai.h>
#include <saiextensions.h>

typedef struct {
    /* API message ID base */
    u16 msg_id_base;

    /* convenience */
    vnet_main_t * vnet_main;

    /* dash pipeline arc index */
    u8 feature_arc_index;
} dash_main_t;

extern dash_main_t dash_main;

extern vlib_node_registration_t dash_node;

extern vlib_log_class_registration_t dash_log;

#define dash_log_err(fmt, ...)	\
  vlib_log_err (dash_log.class, fmt, ##__VA_ARGS__)

#define dash_log_warn(fmt, ...)	\
  vlib_log_warn (dash_log.class, fmt, ##__VA_ARGS__)

#define dash_log_notice(fmt, ...)	\
  vlib_log_notice (dash_log.class, fmt, ##__VA_ARGS__)

#define dash_log_info(fmt, ...)	\
  vlib_log_info (dash_log.class, fmt, ##__VA_ARGS__)

#define dash_log_debug(fmt, ...)	\
  vlib_log_debug (dash_log.class, fmt, ##__VA_ARGS__)


#define ASSERT_MSG(expr, message) \
    do { \
        if (!(expr)) { \
            dash_log_err("Assertion failed: (%s), %s:%d %s", \
                         #expr, __FILE__, __LINE__, message);\
            abort(); \
        } \
    } while (0)

void dash_sai_init ();
sai_status_t dash_sai_create_flow_entry (const dash_flow_entry_t *flow);
sai_status_t dash_sai_remove_flow_entry (const dash_flow_entry_t *flow);

#define DASH_PLUGIN_BUILD_VER "1.0"

#endif /* __included_dash_h__ */
