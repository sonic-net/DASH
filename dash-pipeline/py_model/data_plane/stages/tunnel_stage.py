from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.data_plane.routing_actions.routing_action_encap_underlay import *


class tunnel_stage:
    if TARGET == TARGET_DPDK_PNA:
        tunnel_data = meta_encap_data_t()
    else:
        tunnel_data = encap_data_t()

    @staticmethod
    def set_tunnel_attrs(dash_encapsulation : Annotated[dash_encapsulation_t, {"type" : "sai_dash_encapsulation_t", "default_value" : "SAI_DASH_ENCAPSULATION_VXLAN", "create_only" : "true"}],
                         tunnel_key         : Annotated[int, 24, {"create_only" : "true"}],
                         max_member_size    : Annotated[int, 32, {"default_value" : "1", "create_only" : "true"}],
                         dip                : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}],
                         sip                : Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}]
                         ):

        meta.dash_tunnel_max_member_size = max_member_size

        tunnel_stage.tunnel_data.dash_encapsulation = dash_encapsulation
        tunnel_stage.tunnel_data.vni = tunnel_key
        tunnel_stage.tunnel_data.underlay_sip = sip if sip != 0 else hdr.u0_ipv4.src_addr
        tunnel_stage.tunnel_data.underlay_dip = dip

    @staticmethod
    def select_tunnel_member(dash_tunnel_member_id: Annotated[int, 16]):
        meta.dash_tunnel_member_id = dash_tunnel_member_id

    @staticmethod
    def set_tunnel_member_attrs(dash_tunnel_id          : Annotated[int, 16, {"type" : "sai_object_id_t", "mandatory" : "true", "create_only" : "true"}],
                                dash_tunnel_next_hop_id : Annotated[int, 16, {"type" : "sai_object_id_t", "mandatory" : "true"}]):
        # dash_tunnel_id in tunnel member must match the metadata
        assert meta.dash_tunnel_id == dash_tunnel_id
        meta.dash_tunnel_next_hop_id = dash_tunnel_next_hop_id

    @staticmethod
    def set_tunnel_next_hop_attrs(dip: Annotated[int, IPv4Address_size, {"type" : "sai_ip_address_t"}]):
        assert dip != 0
        tunnel_stage.tunnel_data.underlay_dip = dip


    tunnel = Table(
        key = {
            "meta.dash_tunnel_id": (EXACT, {"type": "sai_object_id_t"})
        },
        actions=[
            set_tunnel_attrs,
        ],
        tname=f"{__qualname__}.tunnel",
        sai_table=SaiTable(name="dash_tunnel", api="dash_tunnel", order=0, isobject="true",),
    )

    # This table is a helper table that used to select the tunnel member based on the index.
    # The entry of this table is created by DASH data plane app, when the tunnel member is created.
    tunnel_member_select = Table(
        key = {
            "meta.dash_tunnel_member_index" : (EXACT, {"type" : "sai_object_id_t", "is_object_key": "true"}),
            "meta.dash_tunnel_id"           : (EXACT, {"type" : "sai_object_id_t"})
        },
        actions=[
            select_tunnel_member,
        ],
        tname=f"{__qualname__}.tunnel_member_select",
        sai_table=SaiTable(ignored="true",),
    )

    tunnel_member = Table(
        key = {
            "meta.dash_tunnel_member_id": (EXACT, {"type" : "sai_object_id_t", "is_object_key": "true"})
        },
        actions=[
            set_tunnel_member_attrs,
        ],
        tname=f"{__qualname__}.tunnel_member",
        sai_table=SaiTable(name="dash_tunnel_member", api="dash_tunnel", order=1, isobject="true",),
    )

    tunnel_next_hop = Table(
        key = {
            "meta.dash_tunnel_next_hop_id": (EXACT, {"type": "sai_object_id_t"})
        },
        actions=[
            set_tunnel_next_hop_attrs,
        ],
        tname=f"{__qualname__}.tunnel_next_hop",
        sai_table=SaiTable(name="dash_tunnel_next_hop", api="dash_tunnel", order=2,isobject="true",),
    )

    @classmethod
    def apply(cls):
        if meta.dash_tunnel_id == 0:
            return

        py_log("info", "Applying table 'tunnel'")
        cls.tunnel.apply()

        # If max member size is greater than 1, the tunnel is programmed with multiple members.
        if meta.dash_tunnel_max_member_size > 1:
            if TARGET == TARGET_PYTHON_V1MODEL:
                # Select tunnel member based on the hash of the packet tuples.
                meta.dash_tunnel_member_index = (
                    hash((meta.dst_ip_addr, meta.src_ip_addr,
                        meta.src_l4_port, meta.dst_l4_port))
                    % meta.dash_tunnel_max_member_size
                )
            else:
                meta.dash_tunnel_member_index = 0

            py_log("info", "Applying table 'tunnel_member_select'")
            cls.tunnel_member_select.apply()
            py_log("info", "Applying table 'tunnel_member'")
            cls.tunnel_member.apply()
            py_log("info", "Applying table 'tunnel_next_hop'")
            py_log("info", "Applying table 'tunnel_next_hop'")
            cls.tunnel_next_hop.apply()

        # Encapsulation push
        if (meta.routing_actions & dash_routing_actions_t.ENCAP_U0) == 0:
            meta.tunnel_pointer = 0
            push_action_encap_u0(
                encap=tunnel_stage.tunnel_data.dash_encapsulation,
                vni=tunnel_stage.tunnel_data.vni,
                underlay_sip=tunnel_stage.tunnel_data.underlay_sip,
                underlay_dip=tunnel_stage.tunnel_data.underlay_dip
            )
        else:
            meta.tunnel_pointer = 1
            push_action_encap_u1(
                encap=tunnel_stage.tunnel_data.dash_encapsulation,
                vni=tunnel_stage.tunnel_data.vni,
                underlay_sip=tunnel_stage.tunnel_data.underlay_sip,
                underlay_dip=tunnel_stage.tunnel_data.underlay_dip
            )
