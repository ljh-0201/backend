def build_prompt(managed_policy: dict, inline_policy: dict, event: dict, days: int) -> str:
    return f"""
다음은 IAM 정책 목록입니다. 최소 권한 원칙에 따라 문제를 진단하고 개선안을 제시하세요:

{managed_policy}
{inline_policy}
{event}
{days}
"""
