# SAI-Challenger Test Workflows
# Relevant make targets:
**`docker-saichallenger-client`**: Build SAI-Challenger docker image and docker image based on SAI-Challenger client docker image with sai_thrift, saigen and DASH files.

**`run-saichallenger-client`**: Start Ixia-C and docker container `dash-saichallenger-client-$(USER)` from image built in `docker-saichallenger-client` target.

**`kill-saichallenger-client`**: Stop `dash-saichallenger-client-$(USER)` container.

**`run-saichallenger-tests`**: Run test manually. This target may be triggered with passing parameters, or with default parameters:

Defaults:
* Setup file: `sai_dpu_client_server_snappi.json`
* Test folder: `DASH/test/test-cases/scale/saic`

Run SAI Challenger tests using defaults listed above:
```
make run-saichallenger-tests
```

Run with setup parameter and default test parameter (All tests):
```
make run-saichallenger-tests <setup_file>
```

Run with setup parameter and test parameter:
```
make run-saichallenger-tests <setup_file> <test_file-or-directory>
```
Run SAI Challenger tutorial test cases. See also [SAI Challenger Tutorials](../test-cases/scale/saic/tutorial/README.md).
```
make run-saichallenger-tutorials
```

# How to start

## Environment
Install dependencies listed [**here**](../../dash-pipeline/README.md#prerequisites).

## Install and build
```
git clone https://github.com/sonic-net/DASH.git
cd DASH/dash-pipeline
make clean
make all

pwd
```

## Start environment
Run in the 3 separate windows/tabs.
- take the output of `pwd` from previous step and do `cd <that location from pwd>` in each window
- window 1: `make run-switch`
- window 2: `make run-saithrift-server`
- window 3: will be used to run the test as per instructions below<br>
Stop all daemons: `make kill-all` (from Window 3)

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
>**NOTE:** Feel free to use other Pytest flags. In particular, `-k <filter expression>` and `-m <mark expression>` can select tests based on a string pattern expression to filter by test-case name or `@pytest.mark` annotations, respectively. Refer to [Pytest documentation](https://docs.pytest.org/en/7.2.x/contents.html) for more info. Use `pytest -h` for help.
