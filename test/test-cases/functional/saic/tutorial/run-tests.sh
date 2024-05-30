#!/bin/bash
# Execute Pytest scripts in this directory
# Usage: [SETUP=<path>] ./run_tests.sh [Pytest options...]
#
[ X$SETUP == "X" ] && export SETUP=../sai_dpu_client_server_snappi.json
echo "==> PYTHONPATH=.. pytest -sv --setup $SETUP $@"
PYTHONPATH=.. pytest -sv --setup $SETUP $@
