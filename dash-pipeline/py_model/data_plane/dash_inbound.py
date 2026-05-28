from py_model.libs.__utils import *
from py_model.libs.__table import *

from py_model.data_plane.dash_tunnel import do_tunnel_encap
from py_model.data_plane.dash_acl import *
from py_model.data_plane.dash_conntrack import *
from py_model.data_plane.stages.inbound_routing import *
from py_model.data_plane.stages.outbound_mapping import *

class inbound:
    @classmethod
    def apply(cls):
        if STATEFUL_P4:
            ConntrackIn.apply()
        if PNA_CONNTRACK:
            ConntrackIn.apply()
            if meta.overlay_data.sip != 0:
                do_action_nat64.apply()

        # ACL
        if not meta.conntrack_data.allow_in:
            acl.apply(cls.__name__)

        if STATEFUL_P4:
            ConntrackOut.apply()
        elif PNA_CONNTRACK:
            ConntrackOut.apply()

        inbound_routing_stage.apply()

        meta.routing_actions = dash_routing_actions_t.ENCAP_U0

        do_tunnel_encap(
            meta.u0_encap_data.underlay_dmac,
            meta.u0_encap_data.underlay_smac,
            meta.u0_encap_data.underlay_dip,
            meta.u0_encap_data.underlay_sip,
            dash_encapsulation_t.VXLAN,
            meta.u0_encap_data.vni
        )
