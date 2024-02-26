#include "saiimpl.h"

DASH_GENERIC_QUAD(DTEL,dtel);
DASH_GENERIC_QUAD(DTEL_QUEUE_REPORT,dtel_queue_report);
DASH_GENERIC_QUAD(DTEL_INT_SESSION,dtel_int_session);
DASH_GENERIC_QUAD(DTEL_REPORT_SESSION,dtel_report_session);
DASH_GENERIC_QUAD(DTEL_EVENT,dtel_event);

sai_dtel_api_t dash_sai_dtel_api = {

    DASH_GENERIC_QUAD_API(dtel)
    DASH_GENERIC_QUAD_API(dtel_queue_report)
    DASH_GENERIC_QUAD_API(dtel_int_session)
    DASH_GENERIC_QUAD_API(dtel_report_session)
    DASH_GENERIC_QUAD_API(dtel_event)
};
