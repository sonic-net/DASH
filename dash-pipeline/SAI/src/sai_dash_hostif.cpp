#include "saiimpl.h"

DASH_GENERIC_QUAD(HOSTIF,hostif);
DASH_GENERIC_QUAD(HOSTIF_TABLE_ENTRY,hostif_table_entry);
DASH_GENERIC_QUAD(HOSTIF_TRAP_GROUP,hostif_trap_group);
DASH_GENERIC_QUAD(HOSTIF_TRAP,hostif_trap);
DASH_GENERIC_QUAD(HOSTIF_USER_DEFINED_TRAP,hostif_user_defined_trap);

sai_hostif_api_t dash_sai_hostif_api_impl = {

    DASH_GENERIC_QUAD_API(hostif)
    DASH_GENERIC_QUAD_API(hostif_table_entry)
    DASH_GENERIC_QUAD_API(hostif_trap_group)
    DASH_GENERIC_QUAD_API(hostif_trap)
    DASH_GENERIC_QUAD_API(hostif_user_defined_trap)

    .recv_hostif_packet = 0,
    .send_hostif_packet = 0,
    .allocate_hostif_packet = 0,
    .free_hostif_packet = 0,
};
