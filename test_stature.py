import unittest
import json
import mock

from docker import Client
from cachet import Cachet

from stature import main

class TestOneShotMode(unittest.TestCase):
    containerz = json.load(open("fixtures/containers.json"))
    settings = {'cachet': {'api_key': 'afancyapikey', 'url': 'http://localhost/api/v1'}, 'containers': {'cachetdocker_cachet_1': 1}}
    
    @mock.patch('cachet.Cachet.postComponents')
    def test_registers_containers(self, cachet_mock):
        # containers_mock.side_effect = self.containerz
        cli_mock = mock.Mock(spec=Client)
        cli_mock.containers = mock.Mock()
        cli_mock.containers.side_effect = [self.containerz]
        cachet = mock.Mock(spec=Cachet)
        cachet.putComponentsByID=mock.Mock()

        main(cli_mock,cachet,self.settings)
        cli_mock.containers.assert_called_once()
        cachet.putComponentsByID.assert_called()
        # cachet_mock.assert_called()

    @mock.patch("stature.logging.error")
    @mock.patch("sys.exit")
    def test_no_containers(self,patched_exit,patched_error):
        cli_mock = mock.Mock(spec=Client)
        cli_mock.containers = mock.Mock()
        cli_mock.containers.side_effect = [{}]
        cachet = mock.Mock(spec=Cachet)
        main(cli_mock,cachet,self.settings)
        patched_exit.assert_called_with(4)
        patched_error.assert_called_with("No containers running!")

    def test_exited_container(self):
        pass

    def test_tag_annotations(self):
        pass
