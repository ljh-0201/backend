import json

from analyzer.devsecops.prompts import prompt_devsecops_analysis
from bedrock.llm import llm

def analyze_devsecops(gitlab_ci: dict) -> str:
    chain = prompt_devsecops_analysis | llm

    response = chain.invoke({
        "data": gitlab_ci
    })

    parsed_json = json.loads(response.content)
    result = json.dumps(parsed_json, indent=4, ensure_ascii=False)

    print(result)

    return result