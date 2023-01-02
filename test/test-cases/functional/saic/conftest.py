import os
import pytest


curdir = os.path.dirname(os.path.realpath(__file__))

from saichallenger.common.sai_dpu import SaiDpu
from saichallenger.common.sai_testbed import SaiTestbed

def pytest_addoption(parser):
    parser.addoption("--traffic", action="store_true", default=False, help="run tests with traffic")
    parser.addoption("--setup", action="store", default=None, help="Setup description (Path to the json file).")


@pytest.fixture(scope="session")
def exec_params(request):
    config_param = {
        # Generic parameters
        "traffic": request.config.getoption("--traffic"),
        "testbed": request.config.getoption("--setup"),
    }
    return config_param


@pytest.fixture(scope="session")
def testbed_instance(exec_params):
    testbed_json = exec_params.get("testbed", None)
    if testbed_json is None:
        yield None
    else:
        testbed = SaiTestbed(f"{curdir}/../..", testbed_json, exec_params["traffic"])
        testbed.init()
        yield testbed
        testbed.deinit()


@pytest.fixture(scope="function")
def testbed(testbed_instance):
    if testbed_instance:
        testbed_instance.setup()
        yield testbed_instance
        testbed_instance.teardown()
    else:
        yield None


@pytest.fixture(scope="session")
def dpu(exec_params, testbed_instance) -> SaiDpu:
    if len(testbed_instance.dpu) == 1:
        return testbed_instance.dpu[0]
    return None


@pytest.fixture(scope="session")
def dataplane_instance(testbed_instance):
    if len(testbed_instance.dataplane) == 1:
        yield testbed_instance.dataplane[0]
    else:
        yield None


@pytest.fixture(scope="session")
def confgen():
    return dpugen.sai.SaiConfig()


@pytest.fixture(scope="function")
def dataplane(dataplane_instance):
    if dataplane_instance:
        dataplane_instance.setup()
        yield dataplane_instance
        dataplane_instance.teardown()
    else:
        yield None
