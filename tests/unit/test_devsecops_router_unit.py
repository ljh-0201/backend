# tests/unit/test_devsecops_router_unit.py

import pytest
from fastapi.testclient import TestClient
from api.routers import devsecops
from session.Service import Service

app = devsecops.router
client = TestClient(app)

def test_create_session_success(mocker):
    mock_register = mocker.patch.object(Service, "register_user")
    response = client.post("/devsecops/session", json={
        "access_key": "abc",
        "secret_key": "xyz"
    })
    assert response.status_code == 200
    assert response.json() == "abc"
    mock_register.assert_called_once()

def test_get_gitlab_projects_success(mocker):
    mock_manager = mocker.Mock()
    mock_manager.get_gitlab_projects.return_value = ["project1", "project2"]

    mocker.patch("api.routers.devsecops.DevSecOpsManager", return_value=mock_manager)
    mocker.patch("api.routers.devsecops.service.get_user_manager", return_value=mocker.Mock(config="dummy"))

    response = client.post("/devsecops/projects", json={"access_key": "abc"})
    assert response.status_code == 200
    assert response.json() == ["project1", "project2"]

def test_scan_gitlab_ci_success(mocker):
    mock_manager = mocker.Mock()
    mock_manager.get_gitlab_ci_file.return_value = {"stages": ["test"]}
    mocker.patch("api.routers.devsecops.DevSecOpsManager", return_value=mock_manager)
    mocker.patch("api.routers.devsecops.service.get_user_manager", return_value=mocker.Mock(config="dummy"))
    mocker.patch("api.routers.devsecops.analyzer.analyze_devsecops", return_value={"result": "ok"})

    response = client.post("/devsecops/projects/analyzer", json={
        "access_key": "abc",
        "project_id": "123"
    })
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}
