# tests/unit/test_infra_manager_unit.py

import pytest
from session.manager.InfraManager import InfraManager

@pytest.fixture
def mock_config():
    class Config:
        access_key = "ak"
        secret_key = "sk"
        region = "ap-northeast-2"
    return Config()

def test_infra_manager_init(mocker, mock_config):
    mocker.patch("session.manager.InfraManager.BaseAWSManager.__init__", return_value=None)
    mock_logger = mocker.patch("session.manager.InfraManager.logger")

    manager = InfraManager(mock_config)
    assert isinstance(manager, InfraManager)
    mock_logger.info.assert_called_with("[Infra] InfraManager initialization complete")
