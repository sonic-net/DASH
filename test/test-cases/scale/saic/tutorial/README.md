<h1>Contents</h1>

- [Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`](#tutorial---writing-dash-pytests-using-sai-challenger-and-dpugen)
- [Tutorial Files](#tutorial-files)
- [Device Configuration Tutorials](#device-configuration-tutorials)
  - [Device Config using SAI Challenger -  Overview](#device-config-using-sai-challenger----overview)
  - [Generated JSON files for select test-cases](#generated-json-files-for-select-test-cases)
    - [Using a Pytest in command-line mode to generate JSON](#using-a-pytest-in-command-line-mode-to-generate-json)

# Tutorial - Writing DASH Pytests using SAI Challenger and `dpugen`
This document takes you through several aspects of writing  using the [SAI Challenger](https://github.com/opencomputeproject/SAI-Challenger) test framework. This framework and its DASH enhancements are described [here](../../../../docs/dash-saichallenger-testbed.md)

# Tutorial Files

| File | Description |
| ---- | ----------- |
| [run_tests.sh](run_tests.sh) | Execute all PyTests |
| [test_sai_vnet_vips_config_gen.py](test_sai_vnet_vips_config_gen.py)| Create/Remove VIP entries using a custom SAI record generator. As an executable, generates JSON for create/remove a config.
| [test_sai_vnet_vips_config_list_comprehension.py](test_sai_vnet_vips_list_comprehension.py)| Create/Remove VIP entries using a list-comprehension expression.  As an executable, generates JSON for create/remove a config.|
| [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) | Create a small-sized outbound vnet configuration using the `dpugen` generator fed with high-level scale parameters.  As an executable, generates JSON for create/remove a config.
| [sai_vnet_outbound_small_scale_config_create_gen.json](sai_vnet_outbound_small_scale_config_create_gen.json) <br> [sai_vnet_outbound_small_scale_config_remove_gen.json](sai_vnet_outbound_small_scale_config_remove_gen.json) | JSON files produced by [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen.py) and consumed by [test_sai_vnet_outbound_small_scale_config_file.py](test_sai_vnet_outbound_small_scale_config_file.py)


# Device Configuration Tutorials
## Device Config using SAI Challenger -  Overview
## Generated JSON files for select test-cases
Some of the examples use DUT configuration files containing SAI records in JSON format, which are loaded and applied to the device via a  SAI-Challenger DUT API driver, e.g. SAI-thrift. Some of these JSON files were themselves generated  using one of the example `.py` files, some of which are dual-purpose Pytest scripts:
* They can be executed by the Pytest framework using either bespoke code or [dpugen](https://pypi.org/project/dpugen/)  to generate scaled configurations, and apply them to the device.
* They can be run in command-line mode to emit the generated configurations as JSON text which, which we saved to the example `.json` files.

For example, we use the [test_sai_vnet_outbound_small_scale_config_gen.py](test_sai_vnet_outbound_small_scale_config_gen) test-case in command-line mode to generate two JSON files:
* `sai_vnet_outbound_small_scale_config_create_gen.json`
* `sai_vnet_outbound_small_scale_config_remove_gen.json`

### Using a Pytest in command-line mode to generate JSON
Some of the Pytest scripts have a command-line mode. (Check the files for a `__main__` section.) This is useful to create persistent copies of generated configurations, or simply to examine the configuration and make adjustments during development. Each file has a `-h` option to show usage and available options.

To generate JSON containing SAI records to **create** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -c > sai_vnet_outbound_small_scale_config_create_gen.json
```
To generate JSON containing SAI records to **remove** the vnet config and redirect to a file:
```
PYTHONPATH=.. test_sai_vnet_outbound_small_scale_config_gen.py -r > sai_vnet_outbound_small_scale_config_remove_gen.json
```