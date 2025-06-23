# tests/unit/test_prompts_unit.py

from analyzer.devsecops.prompts import prompt_devsecops_analysis

def test_prompt_input_variables():
    assert isinstance(prompt_devsecops_analysis.input_variables, list)
    assert "data" in prompt_devsecops_analysis.input_variables

def test_prompt_template_structure():
    template_text = prompt_devsecops_analysis.template

    assert isinstance(template_text, str)
    assert "standard" in template_text
    assert "status" in template_text
    assert "evidence" in template_text
    assert "출력은 **한국어로" in template_text
