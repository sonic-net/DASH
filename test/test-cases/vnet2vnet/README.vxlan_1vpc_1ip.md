The purpose of this test case is to obtain the best performance numbers the hardware can achieve
Combined with the worst case scenario cases (TBD) we will be able to determine the range of performance within the hardware can operate.

![vxlan_1vpc_1ip](../../images/test_vxlan_1vpc_1ip.svg)

1. Configure VxLAN with 1 VPC and 1 VNI.
2. Configure BGP to achieve conectivity between the loopback interfaces.
3. Configure VMs behind VTEPs.
4. Verify that the control plane is up.
5. Find the Max PPS supported using stateless UDP bidirectional traffic
	start rate of 10 Million pps
	increase the rate as long as there are 0 dropped packets
	provide result in millions of pps


- sample output for pps test:
```
Final Possible Boundry is  3000000
+--------+-------------+-------------+----------------+----------+
| PPS    |   Tx Frames |   Rx Frames |   Frames Delta |   Loss % |
|--------+-------------+-------------+----------------+----------|
| 1.00M  |       10000 |       10000 |              0 |    0     |
| 4.00M  |       40000 |       39387 |            613 |   15.34  |
| 2.00M  |       20000 |       20000 |              0 |    0     |
| 3.00M  |       30000 |       30000 |              0 |    0     |
+--------+-------------+-------------+----------------+----------+
```



- sample output for cps test:
```
HTTP Transactions -> 445
HTTP Connections -> 445
TCP Connections Established -> 445
TCP Connection Requests Failed -> 0
```
