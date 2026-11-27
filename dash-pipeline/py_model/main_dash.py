import sys
import signal
import threading
from scapy.all import sniff, sendp, Ether
from py_model.dash_py_v1model import dash_py_model
from py_model.control_plane.grpc_server import serve
from py_model.libs.__utils import py_log, standard_metadata

iface_list = []

def sniff_packet() -> None:
    """Capture packets on configured interfaces and process them."""
    def process_packet(pkt: Ether) -> None:
        raw_bytes = bytes(pkt)
        py_log("info", f"Processing packet received on {pkt.sniffed_on}")

        result = dash_py_model(raw_bytes)
        if not result:
            return

        ether_frame = Ether(result)

        egress_idx = standard_metadata.egress_spec
        if egress_idx < len(iface_list):
            egress_port = iface_list[egress_idx]
            py_log("info", f"Transmitting {len(ether_frame)} bytes out of port {egress_port}\n")
            sendp(ether_frame, iface=egress_port, verbose=False)
        else:
            py_log("warn", f"Egress port index {egress_idx} out of range — dropping packet.")

    sniff(iface=iface_list, prn=process_packet, store=False, filter="inbound")


def setup_interfaces(args: list[str]) -> None:
    """Parse command-line arguments and populate iface_list."""
    if len(args) < 3:
        py_log(None, "\nUsage: python3 -m py_model.main_dash '<IFACE0>' '<IFACE1>' ['<IFACE2>']")
        sys.exit(1)

    iface_list.extend(args[1:4])  # add 2 or 3 interfaces
    py_log(None, "")  # blank line for readability

    for idx, iface in enumerate(iface_list):
        role = "(DPAPP)" if idx == 2 else ""
        py_log(None, f"Adding interface {iface} as port {idx} {role}")
    py_log(None, "")


def main() -> None:
    """Main entry point for running the DASH Python model."""
    setup_interfaces(sys.argv)

    # Start gRPC server
    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()

    # Start packet sniffer
    sniff_thread = threading.Thread(target=sniff_packet, daemon=True)
    sniff_thread.start()

    # Graceful shutdown handler
    def handle_exit(signum, frame):
        py_log(None, "\nStopping Python DASH model...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Keep threads alive
    server_thread.join()
    sniff_thread.join()


if __name__ == "__main__":
    main()
