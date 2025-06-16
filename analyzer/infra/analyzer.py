import json

from analyzer.infra.prompts import prompt_infra_analysis
from bedrock.llm import llm
from core.logger import logger

def analyze_infra() -> str:
    try:
        logger.info("[Infra] Starting analysis")

        chain = prompt_infra_analysis | llm
        response = chain.invoke()

        logger.info("[Infra] LLM response received")

        parsed = json.loads(response.content)
        result = json.dumps(parsed)

        logger.info("[Infra] LLM response parsed successfully")
        return result

    except Exception as e:
        logger.error(f"[Infra] analysis failed: {e}")
        raise