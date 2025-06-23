# tests/unit/test_devsecops_manager_unit.py

import pytest
from session.manager.DevSecOpsManager import DevSecOpsManager

@pytest.fixture
def mock_config():
    class Config:
        instance_id = "i-123456"
        gitlab_token = "fake-token"
        accessible_ip = "127.0.0.1"
    return Config()

def test_init_calls_validate_and_fetch(mocker, mock_config):
    mock_session = mocker.Mock()
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    mocker.patch("session.manager.DevSecOpsManager.DevSecOpsManager._validate_ssm_instance")
    mocker.patch("session.manager.DevSecOpsManager.DevSecOpsManager._fetch_accessible_ip")

    manager = DevSecOpsManager(mock_config)
    manager.session = mock_session
    assert isinstance(manager, DevSecOpsManager)

def test_validate_ssm_instance_success(mocker, mock_config):
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    manager = DevSecOpsManager(mock_config)
    manager.ssm_client = mocker.Mock()
    manager.ssm_client.describe_instance_information.return_value = {
        'InstanceInformationList': [{'InstanceId': mock_config.instance_id}]
    }
    manager._validate_ssm_instance()  # Should not raise

def test_fetch_accessible_ip_public(mocker, mock_config):
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    manager = DevSecOpsManager(mock_config)
    manager.ec2_client = mocker.Mock()
    manager.ec2_client.describe_instances.return_value = {
        'Reservations': [{
            'Instances': [{
                'PublicIpAddress': '1.2.3.4',
                'PrivateIpAddress': '10.0.0.1'
            }]
        }]
    }
    manager._fetch_accessible_ip()
    assert mock_config.accessible_ip == '1.2.3.4'

def test_execute_ssm_command_success(mocker, mock_config):
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    manager = DevSecOpsManager(mock_config)
    mock_send = mocker.Mock(return_value={'Command': {'CommandId': 'abc'}})
    mock_get = mocker.Mock(return_value={'Status': 'Success'})
    manager.ssm_client = mocker.Mock()
    manager.ssm_client.send_command = mock_send
    manager.ssm_client.get_command_invocation = mock_get

    result = manager._execute_ssm_command("echo ok", "test")
    assert result["Status"] == "Success"

def test_get_gitlab_projects_json_error(mocker, mock_config):
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    manager = DevSecOpsManager(mock_config)
    manager._execute_ssm_command = mocker.Mock(return_value={
        "Status": "Success",
        "StandardOutputContent": "not json"
    })
    result = manager.get_gitlab_projects()
    assert "failed to parse" in result["message"]

def test_get_gitlab_ci_file_success(mocker, mock_config):
    mocker.patch("session.manager.DevSecOpsManager.BaseAWSManager.__init__", return_value=None)
    manager = DevSecOpsManager(mock_config)
    manager._execute_ssm_command = mocker.Mock(return_value={
        "Status": "Success",
        "StandardOutputContent": "yml content"
    })
    result = manager.get_gitlab_ci_file("123")
    assert "data" in result
    assert result["data"] == "yml content"
