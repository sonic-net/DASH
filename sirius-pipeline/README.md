# Sirius Pipeline

## Build the environment
```
make docker
```

## Build pipeline
```
make clean
bmv2/sirius_pipeline.bmv2/sirius_pipeline.json
```

## Run software switch
```
make run_switch
```

## Control plane
```
docker exec -it bmv2 simple_switch_CLI
```

## Configuration example
```
table_add direction_lookup set_direction 60 => 1
table_add direction_lookup set_direction 70 => 2
table_add eni_lookup_from_vm outbound.set_eni cc:cc:cc:cc:cc:cc => 7
table_add eni_lookup_to_vm sirius_ingress.set_eni c:cc:cc:cc:cc:cc => 7
table_add eni_to_vni set_vni 7 => 9
table_add routing route_vnet 7 0x01010100/24 => 14
table_add ca_to_pa set_tunnel_mapping 14 0x01010102 => 0x02020202 88:88:88:88:88:88 1
table_add ca_to_pa set_tunnel_mapping 14 0x01010103 => 0x02020202 88:88:88:88:88:88 0
table_add appliance set_appliance 0&&&0 => 77:77:77:77:77:77 66:66:66:66:66:66 0x02020201 0
```

## Simulation TODO
* Connection tracking - not supported by BMv2 at the moment
* List match types - should be added to the target architecture
* ACL stages - depend on items above
* SAI API implementation for BMv2
