from dash_headers import *
from dash_parser import *
from scapy.all import *


pkt=Ether(dst="ab:cd:ef:12:34:56", src="12:12:12:12:12:12")
/IP(src="127.0.0.1", dst="192.168.1.1")
/UDP(sport=80, dport=53)
/Raw(load=('32ff00'))



packet = packet_in(bytes(pkt))
headers = headers_t()



print(dash_parser(packet, headers))



"""
packets = [
        # HTTP Packet
        Ether(src="ab:ab:ab:ab:ab:ab", dst="12:12:12:12:12:12")
        / IP(src="127.0.0.1", dst="192.168.1.1")
        / TCP(sport=12345, dport=80)
        / HTTP()
        / HTTPRequest(Method="GET", Path="/foo", Host="https://google.com"),
        # DNS Packet
        Ether(src="ab:ab:ab:ab:ab:ab", dst="12:12:12:12:12:12")
        / IP(src="127.0.0.1", dst="192.168.1.1")
        / UDP(sport=80, dport=53)
        / DNS(rd=1, qd=DNSQR(qtype="A", qname="google.com"), an=DNSRR(rdata="123.0.0.1")),
        # TCP Packet
        Ether(src="ab:ab:ab:ab:ab:ab", dst="12:12:12:12:12:12")
        / IP(src="127.0.0.1", dst="192.168.1.1")
        / TCP(sport=80, dport=5355),
    ]
"""
