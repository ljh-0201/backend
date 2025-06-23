# tests/unit/test_infra_analyzer_unit.py

import json
import pytest
from analyzer.infra.analyzer import analyze_infra

def test_analyze_infra_unit(mocker):
    # Mock LLM Chain
    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value.content = json.dumps({"infra": "ok"})

    # Patch components
    mocker.patch("analyzer.infra.analyzer.prompt_infra_analysis", new=mocker.Mock())
    mocker.patch("analyzer.infra.analyzer.llm", new=mock_chain)
    mocker.patch("analyzer.infra.analyzer.logger")

    result = analyze_infra()
    assert json.loads(result) == {"infra": "ok"}
