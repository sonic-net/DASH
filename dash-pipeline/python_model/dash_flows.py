from __table import *
from threading import *

def flow_action_inbound(timer, original_overlay_sip, original_overlay_dip):
    meta.encap_data.original_overlay_sip = original_overlay_sip
    meta.encap_data.original_overlay_dip = original_overlay_dip
    timer.restart()

def flow_action_outbound(timer):
    timer.restart()

flows = Table(
    key = {
        "meta.eni_id"   : EXACT,
        "meta.sip"      : EXACT,
        "meta.dip"      : EXACT,
        "meta.protocol" : EXACT,
        "meta.src_port" : EXACT,
        "meta.dst_port" : EXACT
    },
    actions = [
        flow_action_inbound,
        flow_action_outbound
    ]
)

def _flow_timer_callback(forward_flow, reverse_flow):
    flows.delete(forward_flow)
    flows.delete(reverse_flow)

class flow_timer:
    def __init__(self, interval, forward_flow, reverse_flow):
        self.interval = interval
        self.forward_flow = forward_flow
        self.reverse_flow = reverse_flow
        self.timer = Timer(self.interval, _flow_timer_callback, [self.forward_flow, self.reverse_flow])

    def start(self):
        self.timer.start()

    def restart(self):
        self.timer.cancel()
        self.timer = Timer(self.interval, _flow_timer_callback, [self.forward_flow, self.reverse_flow])
        self.timer.start()
