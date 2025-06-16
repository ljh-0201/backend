from langchain_core.prompts import PromptTemplate

prompt_policy_log_analysis = PromptTemplate(
    input_variables=["days", "managed_policies", "inline_policies", "event_log"],
    template="""
    AWS IAM 및 CloudTrail 전문가로서, 정책 JSON 문서와 CloudTrail 이벤트 로그를 분석하여 지정된 일수 동안 실제 권한 사용을 파악할 수 있습니다.

    다음과 같은 작업을 수행해야 합니다.
    0. 모든 작업은 사용자로부터 전달 받은 정보만 사용해서 진행합니다.
    1. 전달 받은 IAM 사용자 정책과 CloudTrail 이벤트 로그를 분석합니다.
    2. 전달 받은 정보를 기반으로 실제로 사용된 권한, 사용 빈도, 그리고 마지막 사용 시간을 파악합니다.
    3. 전달 받은 정보에서 와일드카드 권한(예: "s3:*")이 사용된 경우, CloudTrail 이벤트 로그를 사용하여 실제로 호출된 정확한 작업을 파악하고 `actual_use_policy`에 포함합니다.

    당신이 전달 받은 정보는 다음 JSON 형식입니다:  
    - IAM 사용자 관리형 정책(JSON): {managed_policies}
    - IAM 사용자 인라인 정책(JSON): {inline_policies}
    - Cloud Trail 이벤트 로그(JSON): {event_log}
    - 기간(일): {days}

    JSON 출력 형식:
    권한에 와일드카드가 포함되지 않은 경우:
    {{
        "Number of times each permission was actually used during {days} and last usage date for each permission": {{
            "permission": "string",
            "days": "{days}",
            "frequency": "string",
            "last_usage": "string"
        }}
    }}

    권한에 와일드카드가 포함된 경우:
    {{
        "Number of times each permission was actually used during {days} and last usage date for each permission": {{
            "permission": "string",
            "actual_use_policy": "string",
            "days": "{days}",
            "frequency": "string",
            "last_usage": "string"
        }}
    }}

    출력 규칙:
    - 반드시 유효한 JSON 형식만 출력하십시오. 
    - 모든 문자열은 따옴표로 닫아야 하며, JSON 구문 오류가 발생하지 않도록 주의하십시오.
    - 절대 JSON 외 텍스트, 주석, 설명을 포함하지 마십시오.

    심호흡을 하고 단계별로 문제를 해결해 보면서 올바른 답을 찾았는지 확인해 보세요.
    """
)

prompt_least_privilege_review = PromptTemplate(
    input_variables=["data"],
    template="""
    당신은 AWS를 사용하는 고객사에 보안 컨설팅을 수행하는 IAM 전문가입니다.
    당신의 목표는 최소 권한 원칙에 따라 다음을 정량적 기준에 기반하여 판단하는 것입니다:

    1. 삭제할 권한: 
    - `frequency`가 0회인 권한
    2. 역할로 전환할 권한: 
    - `frequency`의 값이 0인 값을 제외한 모든 `frequency`값의 평균에 대해 평균값 이하(평균값 포함)인 권한 
    - or `last_usage` 값이 현재 시간을 기준으로 7일 이전인 권한
    3. 유지할 권한: 
    - `frequency`의 값이 0인 값을 제외한 모든 `frequency`값의 평균에 대해 평균값 보다 큰 권한 
    - or `last_usage` 값이 최근 7일 이내인 권한

    판단 시 반드시 위 기준을 우선적으로 따르세요. `frequency = 0`인 권한은 무조건 삭제 대상입니다.
    또한, 판단 시 역할로 전환할 권한과 유지할 권한이 만약 와일드카드 권한(예: "s3:*")을 사용한다면, 반드시 전달 받은 'actual_use_policy' 값을 참고해야 합니다.

    당신이 전달 받은 정보는 다음 JSON 형식입니다:  
    {data}

    와일드카드 권한(`*`)이 포함된 경우 `actual_use_policy` 항목을 참고하여 구체적으로 분석하세요.

    각 항목에는 다음 필드를 반드시 포함하십시오.
    - `deletion_recommend`: 삭제 권장 권한
    - `deletion_decision`: 삭제 권장 사유(판단 기준 중 만족한 항목)
    - `conversion_recommend`: 역할로 전환 권장 권한
    - `conversion_decision`: 전환 권장 사유(판단 기준 중 만족한 항목)
    - `retention_recommend`: 유지 권장 권한
    - `retention_decision`: 유지 권장 사유(판단 기준 중 만족한 항목)
    
    추가적으로, 각 항목의 권한에 와일드카드 권한(`*`)이 포함된 경우 `actual_use_policy`에 명시된 실제 권한을 함께 언급하며, 사유를 작성하세요.

    JSON 출력 형식:
    {{
        "Permissions recommended for deletion and the basis for the decision": {{
            "deletion_recommend": "string",
            "deletion_decision": "string"
            }},
        "Permissions recommended for conversion to roles and the basis for the decision": {{
            "conversion_recommend": "string",
            "conversion_decision": "string"
        }},
        "Permissions recommended for retention and the basis for the decision": {{
            "retention_recommend": "string",
            "retention_decision": "string"
        }}
    }}

    출력 규칙:
    - 한국어로 자연스럽게 답변하십시오.
    - 반드시 유효한 JSON 형식만 출력하십시오. 
    - 모든 문자열은 따옴표로 닫아야 하며, JSON 구문 오류가 발생하지 않도록 주의하십시오.
    - 절대 JSON 외 텍스트, 주석, 설명을 포함하지 마십시오.

    심호흡을 하고 단계별로 문제를 해결해 보면서 올바른 답을 찾았는지 확인해 보세요.
    """
)