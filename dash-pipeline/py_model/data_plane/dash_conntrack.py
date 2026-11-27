from py_model.libs.__utils import *
from py_model.libs.__table import *

if PNA_CONNTRACK:
    EXPIRE_TIME_PROFILE_NOW  = 0  # Expire immediately
    EXPIRE_TIME_PROFILE_LONG = 2  # Expire after a long period

    # Helpers to neutralize direction for IP address and port
    def directionNeutralAddr(direction: dash_direction_t,
                            outbound_address: Annotated[int, IPv4Address_size],
                            inbound_address: Annotated[int, IPv4Address_size]):
        if direction == dash_direction_t.OUTBOUND:
            return outbound_address
        else:
            return inbound_address

    def directionNeutralPort(direction: dash_direction_t,
                            outbound_port: Annotated[int, 16],
                            inbound_port: Annotated[int, 16]):
        if direction == dash_direction_t.OUTBOUND:
            return outbound_port
        else:
            return inbound_port


    class ConntrackIn:
        @staticmethod
        def conntrackIn_allow(original_overlay_sip: Annotated[int, IPv4Address_size],
                            original_overlay_dip: Annotated[int, IPv4Address_size]):
            # Invalidate entry based on TCP flags
            # If FIN is 1 (0b000001), or if RST is 1 (0b000100):
            if (hdr.customer_tcp is not None and hdr.customer_tcp.flags & 0b000101) != 0:  # FIN/RST
                # set_entry_expire_time(EXPIRE_TIME_PROFILE_NOW)  # New PNA extern
                # # set entry to be purged
                pass

            # restart_expire_timer()  # reset expiration timer for entry
            meta.conntrack_data.allow_in = True
            meta.overlay_data.is_ipv6 = 0
            meta.overlay_data.sip = original_overlay_sip
            meta.overlay_data.dip = original_overlay_dip

        @staticmethod
        def conntrackIn_miss():
            # TODO: Should this be ((hdr.tcp.flags & 0x2) != 0) instead?
            if hdr.customer_tcp is not None and hdr.customer_tcp.flags == 0x2:  # SYN
                if meta.direction == dash_direction_t.OUTBOUND:
                    if (meta.routing_actions & dash_routing_actions_t.NAT46) != 0:
                        # # New PNA extern: add new entry to table
                        # add_entry(
                        #     "conntrackIn_allow",
                        #     [IPv4Address_size(meta.src_ip_addr), IPv4Address_size(meta.dst_ip_addr)],
                        #     EXPIRE_TIME_PROFILE_LONG
                        # )
                        pass
                    # TODO: Add failure handling


        conntrackIn = Table(
            key = {
                "ipv4_addr1"                  :  EXACT,
                "ipv4_addr2"                  :  EXACT,
                "hdr.customer_ipv4.protocol"  :  EXACT,
                "tcp_port1"                   :  EXACT,
                "tcp_port2"                   :  EXACT,
                "meta.eni_id"                 :  EXACT
            },
            actions = [
                conntrackIn_allow,
                conntrackIn_miss
            ],
            const_default_action = conntrackIn_miss,
            tname=f"{__qualname__}.conntrackIn",
        )

        @classmethod
        def apply(cls):
            py_log("info", "Applying table Table: 'conntrackIn'")
            cls.conntrackIn.apply()

    class ConntrackOut:
        @staticmethod
        def conntrackOut_allow():
            # Invalidate entry based on TCP flags
            # If FIN is 1 (0b000001), or if RST is 1 (0b000100):
            if (hdr.customer_tcp is not None and hdr.customer_tcp.flags & 0b000101) != 0:  # FIN/RST
                # set_entry_expire_time(EXPIRE_TIME_PROFILE_NOW)  # New PNA extern
                pass
                # # set entry to be purged

            # restart_expire_timer()  # reset expiration timer for entry
            meta.conntrack_data.allow_out = True

        # Handle miss (SYN packet cases)
        @staticmethod
        def conntrackOut_miss():
            # TODO: Should this be ((hdr.tcp.flags & 0x2) != 0) instead?
            if hdr.customer_tcp is not None and hdr.customer_tcp.flags == 0x2:  # SYN
                if meta.direction == dash_direction_t.INBOUND:
                    # # New PNA extern: add new entry to table
                    # add_entry("conntrackOut_allow", {}, EXPIRE_TIME_PROFILE_LONG)
                    # # TODO: Add failure handling
                    pass


        conntrackOut = Table(
            key = {
                "ipv4_addr1"                : (EXACT, {}),
                "ipv4_addr2"                : (EXACT, {}),
                "hdr.customer_ipv4.protocol": (EXACT, {}),
                "tcp_port1"                 : (EXACT, {}),
                "tcp_port2"                 : (EXACT, {}),
                "meta.eni_id"               : (EXACT, {})
            },
            actions = [
                conntrackOut_allow,
                conntrackOut_miss
            ],
            const_default_action = conntrackOut_miss,
            tname=f"{__qualname__}.conntrackOut",
        )

        @classmethod
        def apply(cls):
            py_log("info", "Applying table Table: 'conntrackOut'")
            cls.conntrackOut.apply()


if STATEFUL_P4:
    # related to state_graph
    pass