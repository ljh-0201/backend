# tests/integration/test_main_integration.py

from fastapi.testclient import TestClient
from main import server

client = TestClient(server)

def test_healthcheck_like_endpoint():
    # 간단한 POST endpoint 존재 여부 테스트
    response = client.post("/iam/session", json={
        "access_key": "ak",
        "secret_key": "sk"
    })
    assert response.status_code in (200, 400)  # 입력이 적절치 않아도 라우팅만 성공하면 통과
