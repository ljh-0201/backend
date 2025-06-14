from .prompts import build_prompt
from .model import analyze_with_bedrock

def analyze_iam_policy(policy_data: dict) -> str:
    prompt = build_prompt(policy_data)
    return analyze_with_bedrock(prompt)
