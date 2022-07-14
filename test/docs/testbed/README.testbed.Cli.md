
# run tests

```
docker run --network host -v $PWD:/dash --mount src=/etc/localtime,target=/etc/localtime,type=bind,readonly -it dash/keysight bash
cd /dash/test

# Only needed for Stateful tests to configure BGP and VLAN-to-VXLAN
python ./vnet2vnet2/bgp_stateful_config.py
python ./vnet2vnet2/vlan_to_vxlan_stateful_config.py

# To run all the test cases
pytest ./test-cases
```
