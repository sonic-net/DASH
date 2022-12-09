#!/bin/bash
# Execute Pytest scripts in this directory
PYTHONPATH=.. pytest -sv --setup ../sai_dpu_client_server_snappi.json .
