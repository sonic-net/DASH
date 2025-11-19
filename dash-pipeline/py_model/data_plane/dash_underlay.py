from py_model.libs.__utils import *
from py_model.libs.__table import *

# The values in this context have been sourced from the 'saiswitch.h' file and 
# have been manually designated to maintain alignment with enum values specified in the SAI commit <d8d40b4>.
SAI_PACKET_ACTION_DROP = 0
SAI_PACKET_ACTION_FORWARD = 1

class underlay:
    # Send packet on different/same port it arrived based on routing
    @staticmethod
    def set_nhop(next_hop_id : Annotated[int, 9]):
        if TARGET == TARGET_PYTHON_V1MODEL:
            standard_metadata.egress_spec = next_hop_id
        if TARGET == TARGET_DPDK_PNA:
            pass

    @staticmethod
    def pkt_act(packet_action: Annotated[int, 9], next_hop_id: Annotated[int, 9]):
        if packet_action == SAI_PACKET_ACTION_DROP:
            # Drops the packet
            meta.dropped = True
        elif packet_action == SAI_PACKET_ACTION_FORWARD:
            # Forwards the packet on different/same port it arrived based on routing
            underlay.set_nhop(next_hop_id)

    @staticmethod
    def def_act():
        if TARGET == TARGET_PYTHON_V1MODEL:
            # if hdr.packet_meta.packet_source == dash_packet_source_t.DPAPP:
            if hdr.packet_meta and (hdr.packet_meta.packet_source == dash_packet_source_t.DPAPP):
                standard_metadata.egress_spec = 0; # FIXME
            else:
                standard_metadata.egress_spec = standard_metadata.ingress_port

        if TARGET == TARGET_DPDK_PNA:
            pass

    underlay_routing = Table(
        key = {
            "meta.dst_ip_addr": (LPM, {"name" : "destination"})
        },
        actions = [
            # Processes a packet based on the specified packet action.
            # Depending on the packet action, it either drops the packet or forwards it to the specified next-hop. 
            pkt_act,
            (def_act, {"annotations": "@defaultonly"}),
        ],
        # Send packet on same port it arrived (echo) by default
        const_default_action=def_act,
        tname=f"{__qualname__}.underlay_routing",
        sai_table=SaiTable(name="route", api="route", api_type="underlay",),
    )

    @classmethod
    def apply(cls):
        py_log("info", "Applying table 'underlay_routing'")
        cls.underlay_routing.apply()
