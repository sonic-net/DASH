# Sirius Pipeline

## Build the environment
```
make docker
```

## Build pipeline
```
make clean
make bmv2/sirius_pipeline.bmv2/sirius_pipeline.json
```

## Run software switch
```
make run-switch
```

## Control plane
```
docker exec -it <bmv2-Container-ID> simple_switch_CLI
```

## Configuration example
```
table_add direction_lookup set_direction 60 => 1
table_add direction_lookup set_direction 70 => 2
table_add eni_lookup_from_vm outbound.set_eni cc:cc:cc:cc:cc:cc => 7
table_add eni_lookup_to_vm inbound.set_eni c:cc:cc:cc:cc:cc => 7
table_add eni_to_vni set_vni 7 => 9
table_add routing route_vnet 7 0x01010100/24 => 14
table_add ca_to_pa set_tunnel_mapping 14 0x01010102 => 0x02020202 88:88:88:88:88:88 1
table_add ca_to_pa set_tunnel_mapping 14 0x01010103 => 0x02020202 88:88:88:88:88:88 0
table_add appliance set_appliance 0&&&0 => 77:77:77:77:77:77 66:66:66:66:66:66 0x02020201 0
table_add ca_to_pa set_tunnel_mapping 14 0x01010104 => 0x02020202 88:88:88:88:88:88 1
table_add ca_to_pa set_tunnel_mapping 14 0x01010105 => 0x02020202 88:88:88:88:88:88 0
```

# Sirius Pipeline P4 Behavior Models
**TODO**

TCP AND UDP

Fragmentation

NACK write-up in documentation

Sequence # tracking for FIN and final ACK (already started) FIN/ACK ACK - Reshma/Anjali to write into PR

Tracking the ACKs, close down xns more quickly?

Do we need to track the sequence # to ensure it is tracking for the FIN?  - add to doc

Are we garbage-collecting re: how long to wait?  (look for stale or temporal xns) - add to doc

Absolute timer?  For most cases we will get the close. Timers are expensive; expands flow table, esp at high xn rates?

If flow cache is behaving correctly (aging out, etc...) s/not have active xns.  

3 variables:  rate, working set of flows, backup.

Background tasks removing temporal flows?  Advantage here vs. sequence # tracking?  

Expense of timer vs. sequence #.  Timer = less expensive.

Enforce xn rate limit?
