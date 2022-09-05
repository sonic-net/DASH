import logging

import pytest

import sys
sys.path.insert(0, '/sai-challenger/common')  # Needed for correct load_module
from sai_dpu import SaiDpu
from sai_environment import init_setup


def pytest_addoption(parser):
    parser.addoption("--traffic", action="store_true", default=False, help="run tests with traffic")
    parser.addoption("--loglevel", action="store", default='NOTICE', help="syncd logging level")
    parser.addoption("--setup", action="store", default=None, help="Setup description (Path to the json file).")


@pytest.fixture(scope="session")
def exec_params(request):
    config_param = {}
    config_param["setup"] = init_setup(request.config)
    config_param["traffic"] = request.config.getoption("--traffic")
    config_param["loglevel"] = request.config.getoption("--loglevel")
    logging.getLogger().setLevel(getattr(logging, config_param["loglevel"].upper(), "INFO"))
    return config_param

@pytest.fixture(scope="session")
def dpu(exec_params) -> SaiDpu:
    dpu = exec_params["setup"]["DPU"][0]
    if dpu is not None:
        dpu.reset()
    return dpu

@pytest.fixture(scope="session")
def dataplane_session(exec_params):
    dataplane = exec_params["setup"]["DATAPLANE"][0]
    # Set up the dataplane
    dataplane.init()
    yield dataplane
    # Shutdown the dataplane
    dataplane.remove()


@pytest.fixture(scope="function")
def dataplane(dataplane_session):
    dataplane_session.setUp()
    yield dataplane_session
    dataplane_session.tearDown()
