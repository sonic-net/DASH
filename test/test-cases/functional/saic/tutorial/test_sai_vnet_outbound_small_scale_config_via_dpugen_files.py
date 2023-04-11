#!/usr/bin/python3
#
# Pytest case which loads JSON files containing SAI records, to demonstrate this technique.
#
# PyTest:
# =======
# 
# Note, not all tests involve sending traffic, for example setup/teardown of DUT configurations,
# so PTF or snappi may not be relevant. Such cases are often marked for both dataplanes.
#
# run snappi-enabled tests using snappi dataplane (e.g. ixia-c pktgen):
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_snappi.json -m snappi <this-filename> 
# run PTF-enabled tests using snappi test fixture (e.g. ixia-c pktgen)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_snappi.json -m ptf <this-filename>
# run PTF-enabled tests using PTF dataplane (e.g. scapy)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_ptf.json -m ptf <this-filename>
#   
# NOT SUPPORTED: run snappi-capable tests using PTF dataplane (PTF can't support snappi at this writing)
#   PYTHONPATH=. pytest -sv --setup sai_dpu_client_server_ptf.json -m snappi <this-filename>

import json
from pathlib import Path
from pprint import pprint

import pytest

current_file_dir = Path(__file__).parent

def test_sai_vnet_outbound_small_scale_config_create_file(dpu):

    with (current_file_dir / f'test_sai_vnet_outbound_small_scale_config_via_dpugen_create.json').open(mode='r') as config_file:
        setup_commands = json.load(config_file)
        result = [*dpu.process_commands(setup_commands)]
        pprint(result)

def test_sai_vnet_outbound_small_scale_config_remove_file(dpu):

    with (current_file_dir / f'test_sai_vnet_outbound_small_scale_config_via_dpugen_remove.json').open(mode='r') as config_file:
        teardown_commands = json.load(config_file)
        results = [*dpu.process_commands(teardown_commands)]
        print("\n======= SAI commands RETURN values =======")
        print(results)
