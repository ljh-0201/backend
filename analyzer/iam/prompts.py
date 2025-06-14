def build_prompt(policy_data: dict) -> str:
    return f"""
다음은 IAM 정책 목록입니다. 최소 권한 원칙에 따라 문제를 진단하고 개선안을 제시하세요:

{policy_data}
"""
