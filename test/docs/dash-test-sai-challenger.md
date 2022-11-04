# General changes
* Added [SAI-Challenger](https://github.com/opencomputeproject/SAI-Challenger.OCP) submodule by path: `DASH/test/SAI-Challenger`.
* Added test cases for SAI-Challenger by path: `DASH/test/test-cases/scale/saic`

# New make targets:
**`docker-saichallenger-client`**: Build SAI-Challenger docker image and docker image based on SAI-Challenger client docker image with sai_thrift, saigen and DASH files.

**`run-saichallenger-client`**: Start Ixia-C and docker container `sc-client-thrift-run` from image built on `docker-saichallenger-client` target. To the original SAI-Challenger tests (`DASH/test/SAI-Challenger/tests`) folder a new folder `dash_tests` mounted from `DASH/test/test-cases/scale/saic` folder inside of container. Bound mount volume with DASH folder.

**`kill-saichallenger-client`**: Stop Ixia-C and `sc-client-thrift-run` container.

**`run-saichallenger-tests`**: Run test manually. This target may be triggered with passing parameters, or with default parameters.
Run with default parameters(Setup file: `sai_dpu_client_server_snappi.json`; Test: `test_sai_vnet_*.py`):
```
make run-saichallenger-tests
```

Run with setup parameter and default test parameter (All tests):
```
make run-saichallenger-tests <setup_file>
```

Run with setup parameter and test parameter:
```
make run-saichallenger-tests <setup_file> <test_name>
```

# How to start

## Environment
Install dependencies listed [**here**](../../dash-pipeline/README.md#prerequisites).

## Prepare repository
```
git clone https://github.com/PLVision/DASH.git
cd DASH && git checkout test-framework-extension
git submodule update --init --recursive
```

## Build environment
```
cd dash-pipeline
make clean ;# skip on a fresh setup as it will fail
make all

pwd
```

## Start environment
Run in the 3 separate windows/tabs.
- take the output of `pwd` from previous step and do `cd <that location from pwd>` in each window
- window 1: `make run-switch`
- window 2: `make run-saithrift-server`
- window 3: will be used to run the test as per instructions bellow

## Run tests manually

### Using make target
Run all available VNET tests:
```sh
make run-saichallenger-tests
```

Run tests in DASH configuration format with the custom options:
```sh
make run-saichallenger-tests sai_dpu_client_server_snappi.json test_sai_vnet_inbound.py
make run-saichallenger-tests sai_dpu_client_server_snappi.json test_sai_vnet_outbound.py
```

Run tests in SAI configuration format with custom options:
```sh
make run-saichallenger-tests sai_dpu_client_server_snappi.json test_vnet_inbound.py
make run-saichallenger-tests sai_dpu_client_server_snappi.json test_vnet_outbound.py
```

### Manually from the docker (developers mode)
Run the `dash-saichallenger-client-$USER` container.
```sh
make run-saichallenger-client-bash
```

And execute tests in DASH configuration format (inside the container):
```sh
pytest -sv --setup=sai_dpu_client_server_snappi.json test_sai_vnet_inbound.py
pytest -sv --setup=sai_dpu_client_server_snappi.json test_sai_vnet_outbound.py
```

Or in SAI configuration format:
```sh
pytest -sv --setup=sai_dpu_client_server_snappi.json test_vnet_inbound.py
pytest -sv --setup=sai_dpu_client_server_snappi.json test_vnet_outbound.py
```

# Known issues
