from .prompts import build_prompt
from .model import analyze_with_bedrock

def analyze_devsecops_pipeline(gitlab_ci_file: dict) -> str:
    prompt = build_prompt(gitlab_ci_file)
    return analyze_with_bedrock(prompt)
