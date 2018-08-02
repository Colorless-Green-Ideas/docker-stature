import unittest
import json
import random
try:
    import unittest.mock as mock
except ImportError:
    import mock

import docker
import attr
from cachet import Cachet

from stature import main


@attr.s
class FakeContainer(object):
    name = attr.ib()
    labels = attr.ib()
    status = attr.ib()


def container_mock():
    "make a fake docker.Container"
    name = "foo_{}".format(random.randint(0, 25))
    cont = FakeContainer(name=name, labels={}, status=u"running")
    return cont


class TestOneShotMode(unittest.TestCase):
    # containerz = json.load(open("fixtures/containers.json")
    settings = {
        "cachet": {"api_key": "afancyapikey", "url": "http://localhost/api/v1"},
        "containers": {"cachetdocker_cachet_1": 1},
    }

    @mock.patch("cachet.Cachet.postComponents")
    def test_registers_containers(self, cachet_mock):
        # containers_mock.side_effect = self.containerz
        cli_mock = mock.Mock()
        cli_mock.containers.list.return_value = [container_mock()]
        cachet = mock.Mock()
        # cachet.putComponentsByID = mock.Mock()

        main(cli_mock, cachet, self.settings)
        # cli_mock.containers.assert_called()
        cachet.putComponentsByID.assert_called_once()
        # cachet_mock.assert_called()

    @mock.patch("stature.logging.error")
    @mock.patch("sys.exit")
    def test_no_containers(self, patched_exit, patched_error):
        cli_mock = mock.Mock()
        cli_mock.containers.list.return_value = []
        cachet = mock.Mock(spec=Cachet)
        main(cli_mock, cachet, self.settings)
        patched_exit.assert_called_with(4)
        patched_error.assert_called_with("No containers running!")

    @mock.patch("stature.logging.error")
    def test_no_containers_section(self, patched_error):
        cli_mock = mock.MagicMock()
        cachet_mock = mock.Mock()
        lsettings = {"cachet": {"api_key": "fjdjkfhsdfh", "url": "http://localhost/api/v1"},}
        main(cli_mock, cachet_mock, lsettings)
        patched_error.assert_called_with("Write out your toml file! Try an empty containers section.")

    def test_exited_container(self):
        pass

    def test_tag_annotations(self):
        pass

class IntegrationHCTest(unittest.TestCase):
    settings = {
        "cachet": {"api_key": "afancyapikey", "url": "http://localhost/api/v1"},
        "containers": {}
    }

    def setUp(self):
        self.client = docker.from_env()

    def tearDown(self):
        self.client.close()
        
    @mock.patch("cachet.Cachet.postComponents")
    def test_with_healthceck(self, fake_cachet):
        labels = {"org.cachet.name": "Python Test Container", "org.cachet.link": "localhost:1337", "org.cachet.description": "This tests the cachet integrations!"}
        container = self.client.containers.run("python:2", "python -m SimpleHTTPServer 1337", detach=True, healthcheck={"test": ["CMD", "curl", "localhost:1337"]}, labels=labels)
        main(self.client, fake_cachet, self.settings)
        print(fake_cachet.calls)
        container.kill()
        container.remove()

