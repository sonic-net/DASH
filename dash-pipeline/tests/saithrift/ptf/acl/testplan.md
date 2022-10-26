# ACL Rule

1. Test priority
    Case 1.
        Rule(priority=1, action=deny, terminating=True, protocol=17, dst_addr="10.0.0.2", dst_port="1")
        Rule(priority=2, action=allow, terminating=True, protocol=17, dst_addr="10.0.0.2", dst_port="1")
        Rule(priority=3, action=allow, terminating=True, protocol=17, dst_addr="10.0.0.2", dst_port="2")
        Rule(priority=4, action=deny, terminating=True, protocol=17, dst_addr="10.0.0.2", dst_port="2")

        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="1"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="2"), EXPECT FOLLOW

2. Test action
    Case 2.
        Rule(priority=5, action=allow, terminating=False, protocol=17, dst_addr="10.0.0.2", dst_port="3")
        Rule(priority=6, action=deny, terminating=False, protocol=17, dst_addr="10.0.0.2", dst_port="3")

        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="3"), EXPECT DROP

3. Test protocol
    Case 3.
        Rule(priority=7, action=deny, terminating=False, protocol="17,18", dst_addr="10.0.0.2", dst_port="4")

        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="4"), EXPECT DROP
        packet(protocol=18, dst_addr="10.0.0.2", "dst_port"="4"), EXPECT DROP
        packet(protocol=19, dst_addr="10.0.0.2", "dst_port"="4"), EXPECT FOLLOW

4. Test src address
    Case 4.
        Rule(priority=7, action=deny, terminating=False, protocol="17", src_addr="10.0.0.0,10.0.0.1", dst_port="5")

        packet(protocol=17, src_addr="10.0.0.2", "dst_port"="5"), EXPECT DROP
        packet(protocol=17, src_addr="10.0.0.2", "dst_port"="5"), EXPECT DROP

5. Test dst address
    Case 5.
        Rule(priority=7, action=deny, terminating=False, protocol="17", dst_addr="10.0.0.2,10.0.0.3", dst_port="6")

        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="6"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.3", "dst_port"="6"), EXPECT DROP

6. Test src port
    Case 6.
        Rule(priority=7, action=deny, terminating=False, protocol="17", dst_addr="10.0.0.2", src_port="1-2,3")

        packet(protocol=17, dst_addr="10.0.0.2", "src_port"="1"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "src_port"="2"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "src_port"="3"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "src_port"="4"), EXPECT FOLLOW

7. Test dst port
    Case 7.
        Rule(priority=7, action=deny, terminating=False, protocol="17", dst_addr="10.0.0.2", dst_port="7-8,9")

        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="7"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="8"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="9"), EXPECT DROP
        packet(protocol=17, dst_addr="10.0.0.2", "dst_port"="10"), EXPECT FOLLOW

* All IPv4 address should be replaced by IPv6 for another round test
* Inbound/Outbound directions
