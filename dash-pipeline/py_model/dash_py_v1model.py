import struct
import socket

from py_model.libs.__utils import *
from py_model.libs.__obj_classes import *

from py_model.data_plane.dash_parser import *
from py_model.data_plane.dash_headers import *
from py_model.data_plane.dash_metadata import *
from py_model.data_plane.dash_pipeline import *

def dash_verify_checksum():
    pass

def DASH_COMPUTE_CHECKSUM_DEF(underlay_id):
    def compute_checksum():
        ipv4 = getattr(hdr, f"{underlay_id}_ipv4", None)
        if ipv4 is None:
            return None

        # First 16 bits: version (4b) + IHL (4b) + DiffServ/DSCP (8b)
        ver_ihl = (ipv4.version << 12) | (ipv4.ihl << 8) | ipv4.diffserv

        # Flags (3b) + Fragment offset (13b)
        flags_frag = (ipv4.flags << 13) | ipv4.frag_offset

        # Convert IP addresses to 32-bit integers
        src = struct.unpack("!I", socket.inet_aton(str(ipv4.src_addr)))[0]
        dst = struct.unpack("!I", socket.inet_aton(str(ipv4.dst_addr)))[0]

        # Pack the header fields (checksum = 0 while computing)
        header = struct.pack(
            "!HHHHBBHII",
            ver_ihl,               # Version + IHL + DiffServ
            ipv4.total_len,        # Total length
            ipv4.identification,   # Identification
            flags_frag,            # Flags + Fragment offset
            ipv4.ttl,              # TTL
            ipv4.protocol,         # Protocol
            0,                     # Placeholder checksum
            src,                   # Source address
            dst                    # Destination address
        )

        # Compute Internet checksum (RFC 791)
        total = 0
        for i in range(0, len(header), 2):
            word = (header[i] << 8) + header[i+1]
            total += word
            total = (total & 0xFFFF) + (total >> 16)

        checksum = ~total & 0xFFFF

        # Update the field directly
        ipv4.hdr_checksum = checksum

    compute_checksum.__name__ = f"compute_checksum_{underlay_id}"
    return compute_checksum

compute_checksum_u0 = DASH_COMPUTE_CHECKSUM_DEF("u0")
compute_checksum_u1 = DASH_COMPUTE_CHECKSUM_DEF("u1")


def dash_compute_checksum():
    if hdr.u1_ipv4:
        compute_checksum_u1()
    compute_checksum_u0()


def dash_py_model(pkt_bytes):
    hdr.__init__()
    meta.__init__()
    pkt_in.__init__()
    pkt_out.__init__()
    standard_metadata.__init__()

    pkt_in.set_data(pkt_bytes)

    state = dash_parser(pkt_in)
    if state == State.reject:
        py_log("info", "Parser rejected the packet")

    dash_verify_checksum()

    dash_ingress.apply()
 
    py_log("info", f"Egress port is: {standard_metadata.egress_spec}")
    if is_dropped(standard_metadata):
        py_log("info", "Pipeline dropped the packet\n")
    else:
        dash_compute_checksum()

        dash_deparser(pkt_out)

        final_pkt = pkt_out.data + pkt_in.get_unparsed_slice()
        return final_pkt.tobytes()
