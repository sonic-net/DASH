# Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`

# Tutorial Files

| File | Description |
| ---- | ----------- |
| [run_tests.sh](run_tests.sh) | Execute all PyTests |
| [test_sai_vnet_vips_config_gen.py](test_sai_vnet_vips_config_gen.py)| Create/Remove VIP entries using a custom SAI record generator. As an executable, generates JSON for create/remove a config.
| [test_sai_vnet_vips_config_list_comprehension.py](test_sai_vnet_vips_list_comprehension.py)| Create/Remove VIP entries using a list-comprehension expression.  As an executable, generates JSON for create/remove a config.|
| [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) | Create a small-sized outbound vnet configuration using the `dpugen` generator fed with high-level scale parameters.  As an executable, generates JSON for create/remove a config.
| [sai_vnet_outbound_small_scale_config_create_gen.json](sai_vnet_outbound_small_scale_config_create_gen.json) <br> [sai_vnet_outbound_small_scale_config_remove_gen.json](sai_vnet_outbound_small_scale_config_remove_gen.json) | JSON files produced by [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen.py) and consumed by [test_sai_vnet_outbound_small_scale_config_file.py](test_sai_vnet_outbound_small_scale_config_file.py)


# Generated JSON files for select test-cases
Some of the examples use DUT configuration files containing SAI records in JSON format, which are loaded and applied to the device via a  SAI-Challenger DUT API driver, e.g. SAI-thrift. Some of these JSON files were themselves generated  using one of the example `.py` files, some of which are dual-purpose Pytest scripts:
* They can be executed by the Pytest framework using either bespoke code or [dpugen](https://pypi.org/project/dpugen/)  to generate scaled configurations, and apply them to the device.
* They can be run in command-line mode to emit the generated configurations as JSON text which, which we saved to the example `.json` files.

For example, we use the [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) test-case in command-line mode to generate two JSON files:
* `sai_vnet_outbound_small_scale_config_create_gen.json`
* `sai_vnet_outbound_small_scale_config_remove_gen.json`

## Using a Pytest in command-line mode to generate JSON
Some of the Pytest scripts have a command-line mode. (Check the files for a `__main__` section.) THIs is useful to create persistent copies of generated configurations, or simply to examine the configuration and make adjustments during development. Each file has a `-h` option to show usage and available options.

To generate JSON containing SAI records to **create** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -c > sai_vnet_outbound_small_scale_config_create_gen.json
```
This generates JSON containing SAI records to **remove** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -r > sai_vnet_outbound_small_scale_config_remove_gen.json
```