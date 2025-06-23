# tests/unit/test_infra_router_unit.py

import pytest
from fastapi.testclient import TestClient
from api.routers import infra
from session.Service import Service

app = infra.router
client = TestClient(app)

def test_create_session_unit(mocker):
    mocker.patch.object(Service, "register_user")
    response = client.post("/infra/session", json={
        "access_key": "abc",
        "secret_key": "xyz"
    })
    assert response.status_code == 200
    assert response.json() == "abc"

def test_scan_gitlab_ci_unit(mocker):
    # mock InfraManager and analyzer
    mocker.patch("api.routers.infra.InfraManager", return_value=mocker.Mock())
    mocker.patch("api.routers.infra.service.get_user_manager", return_value=mocker.Mock(config="dummy"))
    mocker.patch("api.routers.infra.analyzer.analyze_infra", return_value={"result": "infra-ok"})

    response = client.post("/infra/analyzer", json={"access_key": "abc"})
    assert response.status_code == 200
    assert response.json() == {"result": "infra-ok"}
