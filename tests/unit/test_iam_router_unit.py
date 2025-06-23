# tests/unit/test_iam_router_unit.py

import pytest
from fastapi.testclient import TestClient
from api.routers import iam
from session.Service import Service

app = iam.router
client = TestClient(app)

def test_create_session_unit(mocker):
    mocker.patch.object(Service, "register_user")
    response = client.post("/iam/session", json={
        "access_key": "abc",
        "secret_key": "xyz"
    })
    assert response.status_code == 200
    assert response.json() == "abc"

def test_get_iam_users_unit(mocker):
    mock_manager = mocker.Mock()
    mock_manager.get_iam_users.return_value = ["user1", "user2"]
    mocker.patch("api.routers.iam.IAMManager", return_value=mock_manager)
    mocker.patch("api.routers.iam.service.get_user_manager", return_value=mocker.Mock(config="dummy"))

    response = client.post("/iam/users", json={"access_key": "abc"})
    assert response.status_code == 200
    assert response.json() == ["user1", "user2"]

def test_scan_gitlab_ci_unit(mocker):
    mock_manager = mocker.Mock()
    mock_manager.get_managed_policies.return_value = {"policy": "value"}
    mock_manager.get_inline_policies.return_value = {"inline": "value"}
    mock_manager.get_cloudtrail_events.return_value = {"event": "value"}

    mocker.patch("api.routers.iam.IAMManager", return_value=mock_manager)
    mocker.patch("api.routers.iam.service.get_user_manager", return_value=mocker.Mock(config="dummy"))
    mocker.patch("api.routers.iam.analyzer.analyze_iam_usage", return_value="usage")
    mocker.patch("api.routers.iam.analyzer.analyze_iam", return_value={"result": "ok"})

    data = {"access_key": "abc", "user_name": "tester", "days": 45}
    response = client.post("/iam/users/analyzer", json=data)
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}

def test_scan_gitlab_ci_v2_unit(mocker):
    # same as above but return list
    mock_manager = mocker.Mock()
    mock_manager.get_managed_policies.return_value = {"policy": "value"}
    mock_manager.get_inline_policies.return_value = {"inline": "value"}
    mock_manager.get_cloudtrail_events.return_value = {"event": "value"}

    mocker.patch("api.routers.iam.IAMManager", return_value=mock_manager)
    mocker.patch("api.routers.iam.service.get_user_manager", return_value=mocker.Mock(config="dummy"))
    mocker.patch("api.routers.iam.analyzer.analyze_iam_usage", return_value="usage")
    mocker.patch("api.routers.iam.analyzer.analyze_iam", return_value={"result": "ok"})

    data = {"access_key": "abc", "user_name": "tester", "days": 45}
    response = client.post("/iam/users/analyzer/2", json=data)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0] == "usage"
    assert response.json()[1] == {"result": "ok"}
