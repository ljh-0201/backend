# tests/integration/test_iam_router_integration.py

from fastapi.testclient import TestClient
from main import app  # FastAPI 전체 앱 import 필요

client = TestClient(app)

def test_full_iam_flow():
    session_data = {
        "access_key": "real-ak",
        "secret_key": "real-sk"
    }

    # 세션 생성
    res = client.post("/iam/session", json=session_data)
    assert res.status_code == 200

    # 사용자 목록 조회
    res = client.post("/iam/users", json={"access_key": session_data["access_key"]})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 분석 호출
    user_name = res.json()[0]
    res = client.post("/iam/users/analyzer", json={
        "access_key": session_data["access_key"],
        "user_name": user_name,
        "days": 30
    })
    assert res.status_code == 200
    assert isinstance(res.json(), dict)
    assert "recommendations" in res.text or "result" in res.text
