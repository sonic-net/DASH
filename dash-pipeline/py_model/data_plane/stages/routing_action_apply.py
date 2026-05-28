from py_model.libs.__utils import *
from py_model.data_plane.routing_actions.routing_actions import *
from py_model.data_plane.routing_actions.routing_action_encap_underlay import *
from py_model.data_plane.routing_actions.routing_action_nat46 import *
from py_model.data_plane.routing_actions.routing_action_nat64 import *
from py_model.data_plane.routing_actions.routing_action_nat_port import *
from py_model.data_plane.routing_actions.routing_action_set_mac import *

class routing_action_apply:
    @classmethod
    def apply(cls):
        py_log("info", "routing_action_apply")
        do_action_nat46.apply()
        do_action_nat64.apply()
        do_action_snat_port.apply()
        do_action_dnat_port.apply()
        do_action_set_dmac.apply()

        # Encaps needs to be added after all other transforms, from inner ones to outer ones,
        # because it requires the transforms on the inner packet to be finished in order to
        # get the correct inner packet size and other informations.
        do_action_encap_u0.apply()
        do_action_encap_u1.apply()
