# Sirius Pipeline P4 Behavior Models
**TODO**

TCP AND UDP

Fragmentation
NATs write-up in documentation

Sequence # tracking for FIN and final ACK (already started) FIN/ACK ACK
Tracking the ACKs, close down xns more quickly?
Do we need to track the sequence # to ensure it is tracking for the FIN?  - add to doc
Are we garbage-collecting re: how long to wait?  (look for stale or temporal xns) - add to doc
Absolute timer?  For most cases we will get the close. Timers are expensive; expands flow table, esp at high xn rates?
If flow cache is behaving correctly (aging out, etc...) s/not have active xns.  
3 variables:  rate, working set of flows, backup.
Background tasks removing temporal flows?  Advantage here vs. sequence # tracking?  
Expense of timer vs. sequence #.  Timer = less expensive.

Enforce xn rate limit?


