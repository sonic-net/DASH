from py_model.libs.__utils import *
from py_model.libs.__table import *
from py_model.data_plane.dash_counters import *
from py_model.data_plane.dash_routing_types import *


class pre_pipeline_stage:
    @staticmethod
    def accept():
        pass

    @staticmethod
    def set_appliance(local_region_id: Annotated[int, 8, {"create_only":"true"}]):
        meta.local_region_id = local_region_id

    @staticmethod
    def set_internal_config(neighbor_mac: Annotated[int, EthernetAddress_size],
                            mac         : Annotated[int, EthernetAddress_size],
                            cpu_mac     : Annotated[int, EthernetAddress_size],
                            flow_enabled: Annotated[int, 1]):
        meta.u0_encap_data.underlay_dmac = neighbor_mac
        meta.u0_encap_data.underlay_smac = mac
        meta.cpu_mac = cpu_mac
        meta.flow_enabled = flow_enabled

    appliance = Table(
        key = {
            "meta.appliance_id" : (EXACT, {"type": "sai_object_id_t"})
        },
        actions=[
            set_appliance,
            (accept, {"annotations": "@defaultonly"})
        ],
        const_default_action=accept,
        tname=f"{__qualname__}.appliance",
        sai_table=SaiTable(name="dash_appliance", api="dash_appliance", order=0, isobject="true",),
    )

    internal_config = Table(
        key = {
            "meta.appliance_id" : TERNARY
        },
        actions = [
            set_internal_config
        ],
        tname=f"{__qualname__}.internal_config",
        sai_table=SaiTable(ignored="true",),
    )

    vip = Table(
        key = {
            "meta.rx_encap.underlay_dip": (EXACT, {"name": "VIP", "type": "sai_ip_address_t"})
        },
        actions=[
            accept,
            (drop, {"annotations": "@defaultonly"})
        ],
        const_default_action=drop,
        tname=f"{__qualname__}.vip",
        sai_table=SaiTable(name="vip", api="dash_vip",),
    )

    @classmethod
    def apply(cls):
            #  Normalize the outer headers.
            #  This helps us handling multiple encaps and different type of encaps in the future and simplify the later packet processing.
            meta.rx_encap.underlay_smac = hdr.u0_ethernet.src_addr
            meta.rx_encap.underlay_dmac = hdr.u0_ethernet.dst_addr

            if hdr.u0_ipv4 is not None:
                meta.rx_encap.underlay_sip = hdr.u0_ipv4.src_addr
                meta.rx_encap.underlay_dip = hdr.u0_ipv4.dst_addr
            #  IPv6 encap on received packet is not supported yet.
            #  elif (hdr.u0_ipv6 is not None):
                #  meta.rx_encap.underlay_sip = hdr.u0_ipv6.src_addr
                #  meta.rx_encap.underlay_dip = hdr.u0_ipv6.dst_addr
            #  
            meta.rx_encap.dash_encapsulation = dash_encapsulation_t.VXLAN
            meta.rx_encap.vni = hdr.u0_vxlan.vni

            #  Save the original DSCP value
            meta.eni_data.dscp_mode = dash_tunnel_dscp_mode_t.PRESERVE_MODEL
            meta.eni_data.dscp = hdr.u0_ipv4.diffserv

            #  Normalize the customer headers for later lookups.
            meta.is_overlay_ip_v6 = 0
            meta.ip_protocol = 0
            meta.dst_ip_addr = 0
            meta.src_ip_addr = 0
            if (hdr.customer_ipv6 is not None):
                meta.ip_protocol = hdr.customer_ipv6.next_header
                meta.src_ip_addr = hdr.customer_ipv6.src_addr
                meta.dst_ip_addr = hdr.customer_ipv6.dst_addr
                meta.is_overlay_ip_v6 = 1
            elif (hdr.customer_ipv4 is not None):
                meta.ip_protocol = hdr.customer_ipv4.protocol
                meta.src_ip_addr = hdr.customer_ipv4.src_addr
                meta.dst_ip_addr = hdr.customer_ipv4.dst_addr

            if (hdr.customer_tcp is not None):
                meta.src_l4_port = hdr.customer_tcp.src_port
                meta.dst_l4_port = hdr.customer_tcp.dst_port
            elif (hdr.customer_udp is not None):
                meta.src_l4_port = hdr.customer_udp.src_port
                meta.dst_l4_port = hdr.customer_udp.dst_port

            #  The pipeline starts from here and we can use the normalized headers for processing.
            if (meta.is_fast_path_icmp_flow_redirection_packet):
                UPDATE_COUNTER("port_lb_fast_path_icmp_in", 0)
                pass

            py_log("info", "Applying table 'vip'")
            if cls.vip.apply()["hit"]:
                #  Use the same VIP that was in packet's destination if it's present in the VIP table
                meta.u0_encap_data.underlay_sip = meta.rx_encap.underlay_dip
            else:
                UPDATE_COUNTER("vip_miss_drop", 0)

                if (meta.is_fast_path_icmp_flow_redirection_packet):
                    pass # Do Nothing
    
            py_log("info", "Applying table 'appliance'")
            cls.appliance.apply()

            py_log("info", "Applying table 'internal_config'")
            cls.internal_config.apply()
