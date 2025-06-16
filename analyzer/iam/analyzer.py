import json

from analyzer.iam.prompts import prompt_policy_log_analysis, prompt_least_privilege_review
from bedrock.llm import llm

def analyze_iam(managed_policy: dict, inline_policy: dict, event: dict, days: int) -> str:
    chain = prompt_policy_log_analysis | llm

    response = chain.invoke({
        "days": days,
        "managed_policies": managed_policy,
        "inline_policies": inline_policy,
        "event_log": event
    })

    parsed_json = json.loads(response.content)
    result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

    chain = prompt_least_privilege_review | llm
    response = chain.invoke({
        "data": result
    })

    parsed_json = json.loads(response.content)
    result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

    return result