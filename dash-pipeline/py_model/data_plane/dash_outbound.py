from py_model.libs.__utils import *
from py_model.libs.__table import *

from py_model.data_plane.dash_acl import *
from py_model.data_plane.dash_conntrack import *
from py_model.data_plane.stages.outbound_mapping import *
from py_model.data_plane.stages.outbound_routing import *
from py_model.data_plane.stages.outbound_pre_routing_action_apply import *

class outbound:
    @classmethod
    def apply(cls):
        if STATEFUL_P4:
            ConntrackOut.apply()
        if PNA_CONNTRACK:
            ConntrackOut.apply()

        # ACL
        if not meta.conntrack_data.allow_out:
            acl.apply(cls.__name__)

        if STATEFUL_P4:
            ConntrackIn.apply()
        if PNA_CONNTRACK:
            ConntrackIn.apply()

        meta.lkup_dst_ip_addr = meta.dst_ip_addr
        meta.is_lkup_dst_ip_v6 = meta.is_overlay_ip_v6

        outbound_routing_stage.apply()
        outbound_mapping_stage.apply()
        outbound_pre_routing_action_apply_stage.apply()

