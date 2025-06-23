# tests/unit/test_service_unit.py

import pytest
from session.Service import Service

def test_service_init_creates_empty_session():
    service = Service()
    assert isinstance(service._user_sessions, dict)
    assert len(service._user_sessions) == 0

def test_register_user_stores_manager(mocker):
    mock_manager = mocker.Mock()
    mock_base = mocker.patch("session.Service.BaseAWSManager", return_value=mock_manager)
    mock_logger = mocker.patch("session.Service.logger")

    service = Service()
    service.register_user("ak", "sk", region="us-east-1", instance_id="i-abc", gitlab_token="token")

    assert "ak" in service._user_sessions
    assert service._user_sessions["ak"] == mock_manager
    mock_logger.info.assert_called_once()
    mock_base.assert_called_once()

def test_get_user_manager_returns_existing():
    service = Service()
    fake_manager = "dummy"
    service._user_sessions["ak"] = fake_manager

    result = service.get_user_manager("ak")
    assert result == "dummy"

def test_get_user_manager_raises_on_invalid_key():
    service = Service()
    with pytest.raises(ValueError, match="unregistered user access_key"):
        service.get_user_manager("nonexistent")
