# tests/unit/test_base_aws_manager_unit.py

import pytest
from session.BaseAWSManager import BaseAWSManager

@pytest.fixture
def mock_config():
    class MockConfig:
        access_key = "fake-ak"
        secret_key = "fake-sk"
        region = "ap-northeast-2"
    return MockConfig()

def test_baseawsmanager_init_calls_create_session(mocker, mock_config):
    mock_create = mocker.patch("session.BaseAWSManager.BaseAWSManager._create_session", return_value="mock-session")
    manager = BaseAWSManager(mock_config)
    assert manager.config == mock_config
    assert manager.session == "mock-session"
    mock_create.assert_called_once()

def test_create_session_success(mocker, mock_config):
    mock_boto = mocker.patch("session.BaseAWSManager.boto3.Session", return_value="session-object")
    manager = BaseAWSManager(mock_config)
    session = manager._create_session()
    assert session == "session-object"
    mock_boto.assert_called_once_with(
        aws_access_key_id="fake-ak",
        aws_secret_access_key="fake-sk",
        region_name="ap-northeast-2"
    )
