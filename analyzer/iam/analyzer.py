from .prompts import build_prompt
from .model import analyze_with_bedrock

def analyze_iam_policy(managed_policy: dict, inline_policy: dict, event: dict, days: int) -> str:
    prompt = build_prompt(managed_policy, inline_policy, event, days)
    return analyze_with_bedrock(prompt)
