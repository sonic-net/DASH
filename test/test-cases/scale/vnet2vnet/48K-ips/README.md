The intention of the 48K-IPs test is to evaluate a DPUs performance with an objective of maintaining 6M parallel flows.
 - After a Ramp-up period the best CPS is measured.
 - Using constraints set to 6M will push the DPU to its limits returning a Max CPS.



*sample output of the 48K-IPs CPS test*
```
+-------------------------+-------------------------+-------------------------+
|   Connect Time min (us) |   Connect Time max (us) |   Connect Time avg (us) |
|-------------------------+-------------------------+-------------------------|
|                      80 |                     500 |                     350 |
+-------------------------+-------------------------+-------------------------+

+------+----------------+------------------------+---------------+-----------------+-----------------+
|   It |   Obtained CPS |   HTTP Requests Failed |   TCP Retries |   TCP Resets TX |   TCP Resets RX |
|------+----------------+------------------------+---------------+-----------------+-----------------|
|    1 |        100000  |                      0 |            10 |               0 |               0 |
+------+----------------+------------------------+---------------+-----------------+-----------------+
```
