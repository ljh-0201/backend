# tests/integration/test_iam_analyzer_integration.py

import json
from analyzer.iam.analyzer import analyze_iam_usage, analyze_iam

def test_analyze_iam_usage_integration():
    result = analyze_iam_usage(
        managed_policy={"AmazonS3FullAccess": "*"},
        inline_policy={"MyPolicy": "Allow"},
        event={"eventName": "s3:GetObject"},
        days=30
    )
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert "recommendations" in parsed or "result" in parsed

def test_analyze_iam_integration():
    result = analyze_iam(
        usage='{"user": "s3:PutObject"}',
        days=30
    )
    parsed = json.loads(result)
    assert isinstance(parsed, dict)
    assert "recommendations" in parsed or "result" in parsed
