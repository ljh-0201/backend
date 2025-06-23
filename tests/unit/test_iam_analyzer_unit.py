# tests/unit/test_iam_analyzer_unit.py

import json
import pytest
from analyzer.iam.analyzer import analyze_iam_usage, analyze_iam

def test_analyze_iam_usage_unit(mocker):
    mock_managed = {"policy1": "Allow *"}
    mock_inline = {"inline1": "Deny *"}
    mock_event = {"eventName": "s3:PutObject"}
    mock_days = 30

    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value.content = json.dumps({"result": "usage_ok"})

    mocker.patch("analyzer.iam.analyzer.prompt_policy_log_analysis", new=mocker.Mock())
    mocker.patch("analyzer.iam.analyzer.llm", new=mock_chain)
    mocker.patch("analyzer.iam.analyzer.logger")

    result = analyze_iam_usage(mock_managed, mock_inline, mock_event, mock_days)
    assert json.loads(result) == {"result": "usage_ok"}

def test_analyze_iam_unit(mocker):
    mock_usage = '{"user1": "ec2:StartInstances"}'
    mock_days = 30

    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value.content = json.dumps({"result": "iam_ok"})

    mocker.patch("analyzer.iam.analyzer.prompt_least_privilege_review", new=mocker.Mock())
    mocker.patch("analyzer.iam.analyzer.llm", new=mock_chain)
    mocker.patch("analyzer.iam.analyzer.logger")

    result = analyze_iam(mock_usage, mock_days)
    assert json.loads(result) == {"result": "iam_ok"}
