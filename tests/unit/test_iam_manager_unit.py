# tests/unit/test_iam_manager_unit.py

import pytest
from session.manager.IAMManager import IAMManager

@pytest.fixture
def mock_config():
    class Config:
        access_key = "ak"
        secret_key = "sk"
        region = "ap-northeast-2"
    return Config()

def test_extract_allowed_actions_single_and_list():
    data = [
        {
            "Statement": [
                {"Effect": "Allow", "Action": "s3:GetObject"},
                {"Effect": "Allow", "Action": ["ec2:StartInstances", "ec2:StopInstances"]},
                {"Effect": "Deny", "Action": "iam:DeleteUser"}
            ]
        }
    ]
    result = IAMManager._extract_allowed_actions(data)
    assert sorted(result["allowed_actions"]) == sorted(["s3:GetObject", "ec2:StartInstances", "ec2:StopInstances"])

def test_get_iam_users_unit(mocker, mock_config):
    mocker.patch("session.manager.IAMManager.BaseAWSManager.__init__", return_value=None)
    manager = IAMManager(mock_config)
    paginator = mocker.Mock()
    paginator.paginate.return_value = [{"Users": [{"UserName": "user1"}, {"UserName": "user2"}]}]
    manager.iam_client = mocker.Mock()
    manager.iam_client.get_paginator.return_value = paginator

    result = manager.get_iam_users()
    assert result == {"data": ["user1", "user2"]}

def test_get_managed_policies_unit(mocker, mock_config):
    mocker.patch("session.manager.IAMManager.BaseAWSManager.__init__", return_value=None)
    manager = IAMManager(mock_config)
    iam_mock = mocker.Mock()

    iam_mock.list_attached_user_policies.return_value = {
        "AttachedPolicies": [{"PolicyArn": "arn:aws:iam::123456:policy/test"}]
    }
    iam_mock.get_policy.return_value = {"Policy": {"DefaultVersionId": "v1"}}
    iam_mock.get_policy_version.return_value = {
        "PolicyVersion": {
            "Document": {
                "Statement": [{"Effect": "Allow", "Action": "ec2:StartInstances"}]
            }
        }
    }

    manager.iam_client = iam_mock
    result = manager.get_managed_policies("user1")
    assert "allowed_actions" in result
    assert "ec2:StartInstances" in result["allowed_actions"]

def test_get_inline_policies_unit(mocker, mock_config):
    mocker.patch("session.manager.IAMManager.BaseAWSManager.__init__", return_value=None)
    manager = IAMManager(mock_config)
    iam_mock = mocker.Mock()

    iam_mock.list_user_policies.return_value = {"PolicyNames": ["policy1"]}
    iam_mock.get_user_policy.return_value = {
        "PolicyDocument": {
            "Statement": [{"Effect": "Allow", "Action": "s3:PutObject"}]
        }
    }

    manager.iam_client = iam_mock
    result = manager.get_inline_policies("user1")
    assert "allowed_actions" in result
    assert "s3:PutObject" in result["allowed_actions"]

def test_get_cloudtrail_events_unit(mocker, mock_config):
    mocker.patch("session.manager.IAMManager.BaseAWSManager.__init__", return_value=None)
    manager = IAMManager(mock_config)
    cloudtrail_mock = mocker.Mock()

    cloudtrail_mock.lookup_events.return_value = {
        "Events": [
            {
                "EventTime": "2024-01-01T12:00:00Z",
                "EventName": "RunInstances",
                "Resources": [{"ResourceName": "ec2-instance"}]
            }
        ]
    }

    manager.cloudtrail_client = cloudtrail_mock
    result = manager.get_cloudtrail_events("user1", 1)
    assert isinstance(result, list)
    assert result[0]["action"] == "RunInstances"
