import json

from analyzer.iam.prompts import prompt_policy_log_analysis, prompt_least_privilege_review
from bedrock.llm import llm
from core.logger import logger

def analyze_iam(managed_policy: dict, inline_policy: dict, event: dict, days: int) -> str:
    try:
        logger.info("[IAM] starting first analysis")
        chain = prompt_policy_log_analysis | llm
        response = chain.invoke({
            "days": days,
            "managed_policies": managed_policy,
            "inline_policies": inline_policy,
            "event_log": event
        })

        logger.info("[IAM] LLM first response received")
        parsed_json = json.loads(response.content)
        result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

        logger.info("[IAM] starting second analysis")
        chain = prompt_least_privilege_review | llm
        response = chain.invoke({
            "data": result
        })

        logger.info("[IAM] LLM second response received")
        parsed_json = json.loads(response.content)
        result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

        logger.info("[IAM] LLM response parsed successfully")
        return result

    except Exception as e:
        logger.error(f"[Infra] analysis failed: {e}")
        raise