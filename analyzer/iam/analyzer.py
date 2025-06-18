import json

from analyzer.iam.prompts import prompt_policy_log_analysis, prompt_least_privilege_review
from bedrock.llm import llm
from core.logger import logger

def analyze_iam_usage(managed_policy: dict, inline_policy: dict, event: dict, days: int) -> str:
    try:
        logger.info("[IAM] starting usage analysis")
        chain = prompt_policy_log_analysis | llm
        response = chain.invoke({
            "managed_policies": managed_policy,
            "inline_policies": inline_policy,
            "event_log": event,
            "days": days
        })

        logger.info("[IAM] LLM response received")
        parsed_json = json.loads(response.content)
        result = json.dumps(parsed_json, ensure_ascii=False)

        logger.info("[IAM] LLM response parsed successfully")
        return result

    except Exception as e:
        logger.error(f"[IAM] analysis failed: {e}")
        raise

def analyze_iam(usage: str, days: int) -> str:
    try:
        logger.info("[IAM] starting iam analysis")
        chain = prompt_least_privilege_review | llm
        response = chain.invoke({
            "data": usage,
            "days": days
        })

        logger.info("[IAM] LLM response received")
        parsed_json = json.loads(response.content)
        result = json.dumps(parsed_json, ensure_ascii=False)

        logger.info("[IAM] LLM response parsed successfully")
        return result

    except Exception as e:
        logger.error(f"[IAM] analysis failed: {e}")
        raise