# Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`

# Tutorial Files

| File | Description |
| ---- | ----------- |
| [run_tests.sh](run_tests.sh) | Execute all PyTests |
| [test_sai_vnet_vips_config_gen.py](test_sai_vnet_vips_config_gen.py)| Create/Remove VIP entries using a custom SAI record generator. As an executable, generates JSON for create/remove a config.
| [test_sai_vnet_vips_config_list_comprehension.py](test_sai_vnet_vips_list_comprehension.py)| Create/Remove VIP entries using a list-comprehension expression.  As an executable, generates JSON for create/remove a config.|
| [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) | Create a small-sized outbound vnet configuration using the `dpugen` generator fed with high-level scale parameters.  As an executable, generates JSON for create/remove a config.
| [sai_vnet_outbound_small_scale_config_create_gen.json](sai_vnet_outbound_small_scale_config_create_gen.json) <br> [sai_vnet_outbound_small_scale_config_remove_gen.json](sai_vnet_outbound_small_scale_config_remove_gen.json) | JSON files produced by [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen.py) and consumed by [test_sai_vnet_outbound_small_scale_config_file.py](test_sai_vnet_outbound_small_scale_config_file.py)


## vnet_outbound_scale_config - JSON files
To create JSON files for the examples which load scaled VNET configurations from files, we actually use the test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) test-case in comand-line mode to generate the JSON as follows:

This generates JSON containing SAI records to create the vnet config:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -c > sai_vnet_outbound_small_scale_config_create_gen.json
```
This generates JSON containing SAI records to remove the vnet config:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -r > sai_vnet_outbound_small_scale_config_remove_gen.json
```