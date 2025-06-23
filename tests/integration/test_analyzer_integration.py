# tests/integration/test_analyzer_integration.py

import json
from analyzer.devsecops.analyzer import analyze_devsecops

def test_analyze_devsecops_with_real_llm():
    # 실제로 LLM을 호출하는 테스트입니다
    test_input = {
        "stages": ["build", "deploy"],
        "deploy-job": {
            "stage": "deploy",
            "script": ["echo Deploying..."]
        }
    }

    result = analyze_devsecops(test_input)
    parsed = json.loads(result)

    assert isinstance(parsed, dict)
    assert "recommendations" in parsed or "result" in parsed  # 예상되는 필드 기준으로 조정
