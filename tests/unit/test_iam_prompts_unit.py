# tests/unit/test_iam_prompts_unit.py

from analyzer.iam.prompts import prompt_policy_log_analysis, prompt_least_privilege_review

def test_prompt_policy_log_analysis_inputs():
    assert sorted(prompt_policy_log_analysis.input_variables) == sorted(
        ["days", "managed_policies", "inline_policies", "event_log"]
    )

    template = prompt_policy_log_analysis.template
    assert "{managed_policies}" in template
    assert "permissions_usage" in template
    assert "CloudTrail" in template

def test_prompt_least_privilege_review_inputs():
    assert sorted(prompt_least_privilege_review.input_variables) == sorted(["data", "days"])

    template = prompt_least_privilege_review.template
    assert "deletion_recommend" in template
    assert "conversion_decision" in template
    assert "와일드카드 권한" in template
    assert "출력 형식" in template
