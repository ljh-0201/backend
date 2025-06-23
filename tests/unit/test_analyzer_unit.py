# tests/unit/test_analyzer_unit.py

import json
import pytest
from analyzer.devsecops.analyzer import analyze_devsecops

def test_analyze_devsecops_success(mocker):
    # Arrange
    mock_gitlab_ci = {"stages": ["build", "deploy"]}

    # Mock prompt + llm chain
    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value.content = json.dumps({"result": "ok"})

    mocker.patch("analyzer.devsecops.analyzer.prompt_devsecops_analysis", new=mocker.Mock())
    mocker.patch("analyzer.devsecops.analyzer.llm", new=mock_chain)
    mocker.patch("analyzer.devsecops.analyzer.logger")

    # Act
    result = analyze_devsecops(mock_gitlab_ci)

    # Assert
    assert json.loads(result) == {"result": "ok"}
