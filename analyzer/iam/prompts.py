from langchain_core.prompts import PromptTemplate

prompt_policy_log_analysis = PromptTemplate(
    input_variables=["days", "managed_policies", "inline_policies", "event_log"],
    template=r"""
    당신은 AWS IAM · CloudTrail 전문가입니다.  
    전달받은 **IAM 정책**(관리형·인라인)과 **CloudTrail 이벤트 로그**를 바탕으로, 지정된 기간({days}일) 동안 실제 사용된 권한을 다음 순서로 분석하십시오.

    1. 정책 문서에서 각 **권한 문자열**(예: `"s3:GetObject"`, `"ec2:*"`)을 추출한다.  
    2. CloudTrail 이벤트 로그에서 각 권한이 **호출된 횟수**(`frequency`)와 **가장 최근 호출 시각**(`last_usage`, ISO‑8601)을 계산한다.  
    3. 권한 문자열에 와일드카드(`*`)가 포함된 경우, 이벤트 로그를 이용해 **실제로 호출된 세부 작업 목록**을 `actual_use_policy`(배열) 필드에 추가한다.
    4. 권한 문자열에 와일드카드(`*`)가 포함된 경우, **호출된 횟수**(`frequency`)는 `actual_use_policy`(배열)의 `frequency`의 총 합과 같아야 한다.
    5. 정책에 정의돼 있지만 로그에 **전혀 등장하지 않은** 권한은 `frequency` `0`, `last_usage` `null` 로 기록한다.

    ---
    ### 입력(모두 JSON 문서)
    - **관리형 정책**: {managed_policies}  
    - **인라인 정책**: {inline_policies}  
    - **CloudTrail 로그**: {event_log}  
    ---

    ### 출력 형식(단 하나의 JSON 객체만 허용)
    {{
        "permissions_usage": [
        {{
            "permission": "string",
            "frequency": integer,
            "last_usage": "YYYY-MM-DDTHH:MM:SSZ or null",
            "actual_use_policy": [
                {{
                    "permission": "string",
                    "frequency": integer,
                    "last_usage": "YYYY-MM-DDTHH:MM:SSZ or null",
                }}, ...
            ]   // 와일드카드일 때만 포함
        }},
        ...
        ]
    }}

    출력 규칙
    - 반드시 위 구조를 그대로 따를 것
    - permissions_usage는 배열이며, 각 요소가 한 권한의 사용 내역을 담는다.
    - 문자열은 모두 큰따옴표로 감싼다.
    - JSON 이외의 텍스트(설명, 주석, 추가 구문)를 절대 포함하지 않는다.
    - 날짜·시간은 항상 UTC ISO‑8601 형식 사용.

    단계별로 사고하되, 최종 응답에는 오직 JSON만 남겨라.
    """
)

prompt_least_privilege_review = PromptTemplate(
    input_variables=["data", "days"],
    template="""
    당신은 AWS 환경에서 보안 점검을 수행하는 IAM 권한 최적화 전문가입니다.
    다음 IAM 권한 데이터를 분석하여 각 권한을 **삭제, 역할 전환, 유지** 중 하나로 분류하고, 그 이유를 명확하고 **누구나 이해할 수 있도록 쉽게 설명**하세요.

    ---
    ## 판단 기준 및 우선순위
    **1순위: 사용 횟수(`frequency`) 기준으로 먼저 판단**  
    **2순위: 마지막 사용 날짜(`last_usage`)는 보조 기준으로만 사용**
    ---
    ### [삭제 권장 대상 - deletion]
    - 해당 권한이 **기간 내 한 번도 사용되지 않은 경우** (`frequency == 0`), 무조건 삭제 대상입니다.

    ### [역할 전환 권장 대상 - conversion]
    - 권한이 사용되었으며(즉, `frequency != 0`이면서), **전체 권한의 평균 사용 횟수 이하**인 경우 (평균값 포함)
    - 또는, 마지막 사용 날짜(`last_usage`)가 현재일 기준 **⌊{days}/2⌋일 이상** 경과한 경우  
    - (예: days=30이면 15일, days=15이면 7일)

    ### [유지 권장 대상 - retention]
    - 사용 횟수(`frequency`)가 전체 평균보다 높은 경우  
    - 또는 마지막 사용 날짜(`last_usage`)가 **최근 7일 이내**인 경우
    ---
    ## 특수 조건: 와일드카드 권한 (`*`) 처리
    - `"s3:*"` 또는 `"ec2:*"`처럼 와일드카드가 포함된 권한은 반드시 `삭제` 또는 `역할 전환` 중 하나로 분류합니다. `유지` 대상이 될 수 없습니다.
    - `actual_use_policy` 필드가 존재하는 경우, 실제로 사용된 구체적인 작업(API 이름)을 나열하고, 과도한 권한 범위인지 여부를 명확히 설명합니다.
    - 예: `"ec2:StartInstances", "ec2:StopInstances"` 등 구체적 명칭 사용 필수 (모호한 표현 금지)
    ---
    ## 입력 데이터 (String)
    {data}
    ---

    ## 출력 형식 (JSON Only)
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

    출력 규칙
    - 출력은 반드시 유효한 JSON만 포함해야 합니다 (절대 주석, 설명 추가 금지)
    - 문자열은 모두 **큰따옴표(")**로 감쌀 것
    - 각 항목은 **빈 문자열 없이** 구체적인 내용을 포함할 것
    - 각 이유(`*_decision`)는 **한국어로 자연스럽고 이해하기 쉽게** 작성할 것
    - 사용된 기술 용어는 반드시 한국어 해석 포함 (예: `"사용 횟수(frequency)"`, `"마지막 사용 날짜(last_usage)"`)
    - 각 권한은 초보자도 쉽게 이해할 수 있도록 설명

    심호흡을 하고 아래 항목들을 단계적으로 점검하십시오:
    1. 사용 기록이 전혀 없는 권한(즉, `frequency` == 0인 권한) → 삭제로 우선 분류
    2. 사용 횟수가 평균 이하인 권한 또는 오래된 권한 → 역할 전환 분류
    3. 사용 횟수가 평균보다 큰 권한 또는 최근 사용된 권한 → 유지 분류
    4. 와일드카드 권한 여부 판단 및 구체적 사용 기록 분석 포함
    5. 모든 판단 근거를 명확하고 직관적으로 설명
    """
)