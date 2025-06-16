import json

from analyzer.infra.prompts import prompt_infra_analysis
from bedrock import llm

def analyze_infra() -> str:
    chain = prompt_infra_analysis | llm

    response = chain.invoke()

    parsed_json = json.loads(response.content)
    result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

    print(result)

    return result