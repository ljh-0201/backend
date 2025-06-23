# tests/unit/test_infra_prompts_unit.py

from analyzer.infra.prompts import prompt_infra_analysis

def test_prompt_infra_analysis_inputs():
    assert prompt_infra_analysis.input_variables == []

def test_prompt_infra_analysis_template_contains_outputs():
    template = prompt_infra_analysis.template

    assert "Result Report" in template
    assert "Action Report" in template
    assert "data1" in template
    assert "data2" in template
    assert "JSON Only" in template
    assert "출력 규칙" in template
