# tests/integration/test_devsecops_router_integration.py

import pytest
from fastapi.testclient import TestClient
from main import app  # FastAPI 전체 앱 import (예: main.py에 정의된 FastAPI(app))

client = TestClient(app)

def test_full_scan_flow():
    # NOTE: 실제 유효한 access_key와 token, gitlab 연결 필요
    session_data = {
        "access_key": "real-ak",
        "secret_key": "real-sk",
        "gitlab_token": "real-token",
        "region": "ap-northeast-2"
    }
    response = client.post("/devsecops/session", json=session_data)
    assert response.status_code == 200

    response = client.post("/devsecops/projects", json={"access_key": session_data["access_key"]})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    project_id = response.json()[0]  # 첫 프로젝트 ID 사용
    response = client.post("/devsecops/projects/analyzer", json={
        "access_key": session_data["access_key"],
        "project_id": project_id
    })
    assert response.status_code == 200
    assert "recommendations" in response.text or "result" in response.text
