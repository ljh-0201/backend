# tests/integration/test_infra_router_integration.py

from fastapi.testclient import TestClient
from main import app  # FastAPI 전체 앱 정의한 곳

client = TestClient(app)

def test_infra_scan_flow():
    # 세션 등록
    session_data = {
        "access_key": "real-ak",
        "secret_key": "real-sk"
    }
    res = client.post("/infra/session", json=session_data)
    assert res.status_code == 200

    # 인프라 분석
    res = client.post("/infra/analyzer", json={"access_key": session_data["access_key"]})
    assert res.status_code == 200
    assert isinstance(res.json(), dict)
    assert "Result Report" in res.text or "infra" in res.text or "recommendations" in res.text
