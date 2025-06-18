import json
from analyzer.devsecops.prompts import prompt_devsecops_analysis
from bedrock.llm import llm
from core.logger import logger


def analyze_devsecops(gitlab_ci: dict) -> str:
    try:
        logger.info("[DevSecOps] Starting GitLab‑CI analysis")

        chain = prompt_devsecops_analysis | llm
        response = chain.invoke({"data": gitlab_ci})

        logger.info("[DevSecOps] LLM response received")

        parsed = json.loads(response.content)
        result = json.dumps(parsed, ensure_ascii=False)

        logger.info("[DevSecOps] LLM response parsed successfully")
        return result

    except Exception as e:
        logger.error(f"[DevSecOps] GitLab‑CI analysis failed: {e}")
        raise
