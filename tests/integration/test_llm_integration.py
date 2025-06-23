# tests/integration/test_llm_integration.py

import pytest
from bedrock.llm import llm

def test_llm_invoke_response():
    # 실제 AWS Bedrock LLM 호출이 일어남 (요금 발생 가능)
    response = llm.invoke({"data": "hello"})
    assert hasattr(response, "content")
    assert isinstance(response.content, str)
    assert len(response.content) > 0
