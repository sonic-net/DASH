import importlib
import json
import os
import sys
from pprint import pprint as pp

import pytest
import utils as util
from ixload import IxLoadTestSettings as TestSettings
from ixload import IxLoadUtils as IxLoadUtils
from ixload import IxRestUtils as IxRestUtils
from ixnetwork_restpy import SessionAssistant
from ixnetwork_restpy.testplatform.testplatform import TestPlatform

targets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "targets"))
sys.path.insert(0, targets_dir)


@pytest.fixture(scope="session")
def tbinfo(request):
    """Create and return testbed information"""
    from credentials import CREDENTIALS as CR
    from testbed import TESTBED as TB
    TB["CR"] = CR
    return TB


@pytest.fixture(name="smartnics", scope="session")
def fixture_smartnics(tbinfo):
    test_type = tbinfo['novus'][0]['dpu'][0]['type']
    if test_type:
        modname = test_type.lower() + "." + test_type.lower()
    else:
        raise Exception('Fail to load module %s' % modname)
    try:
        imod = importlib.import_module(modname)
        cls = getattr(imod, test_type.title() + "Test")
        return cls(**tbinfo)
    except:
        raise Exception('Fail to load module %s' % modname)


@pytest.fixture(scope="session")
def utils():
    return util


@pytest.fixture
def create_ixload_session_url(tbinfo):
    ixload_settings = {}
    tg = {
        'chassis_list': tbinfo['cloudstorm'][0]['server'],
        'tgen': tbinfo['cloudstorm'][0]['tgen'],
        'vxlan': tbinfo['cloudstorm'][0]['tgen'],
        'dpu': tbinfo['cloudstorm'][0]
    }

    # Helper Functions
    def create_test_settings():
        # TEST CONFIG
        test_settings = TestSettings.IxLoadTestSettings()
        test_settings.gatewayServer = tbinfo['cloudstorm'][0]['server'][0]['addr']
        test_settings.apiVersion = "v0"
        test_settings.ixLoadVersion = "9.20.0.279"

        slot1 = tg['tgen'][0][1]
        port1 = tg['tgen'][0][2]
        slot2 = tg['tgen'][1][1]
        port2 = tg['tgen'][1][2]

        test_settings.portListPerCommunity = {
            # format: { community name : [ port list ] }
            "Traffic1@Network1": [(1, slot1, port1)],
            "Traffic2@Network2": [(1, slot2, port2)]
        }

        chassisList = tg['tgen'][0][0]
        test_settings.chassisList = [chassisList]

        #test_settings.chassisList = ["10.36.79.165"]

        return test_settings

    def create_session(test_settings):
        connection = IxRestUtils.getConnection(
            test_settings.gatewayServer,
            test_settings.gatewayPort,
            httpRedirect=test_settings.httpRedirect,
            version=test_settings.apiVersion
        )

        return connection

    test_settings = create_test_settings()
    connection = create_session(test_settings)
    connection.setApiKey(test_settings.apiKey)

    ixload_settings['connection'] = connection
    #ixload_settings['session_url'] = session_url
    ixload_settings['test_settings'] = test_settings

    yield ixload_settings


def getTestClass(*args, **kwargs):
    if test_type:
        modname = test_type.lower() + "." + test_type.lower()
    else:
        raise Exception('Fail to load module %s' % modname)
    try:
        imod = importlib.import_module(modname)
        cls = getattr(imod, test_type.title() + "Test")
        return cls(*args, **kwargs)
    except:
        raise Exception('Fail to load module %s' % modname)
