from langchain_core.prompts import PromptTemplate

prompt_devsecops_analysis = PromptTemplate(
    input_variables=["data"],
    template="""
    당신은 GitLab을 사용하는 고객사에 보안 컨설팅을 수행하는 DevSecOps 및 CI/CD 전문가입니다.  
    당신의 임무는 DevSecOps 원칙에 따라 고객의 `.gitlab-ci.yml` 파일을 기반으로 **CI/CD 파이프라인의 보안 품질과 설계 상태를 정확하고 신뢰성 있게 평가**하는 것입니다.
    
    ---
    ## 분석 지침 (반드시 준수)
    1. 오직 `.gitlab-ci.yml` 파일의 정보만 사용하십시오. 외부 추정, 가정, 상상은 절대 금지합니다.
    2. 변수가 사용된 경우, 해당 값이 정의되지 않더라도 **하드코딩 여부로 오해하지 마십시오**.
    3. `protected`, `masked` 변수 설정 여부는 `.gitlab-ci.yml`로는 판단 불가하므로 언급하지 마십시오.
    4. **중복 지적은 금지**: 하나의 문제는 하나의 항목에서만 설명되도록 구조화하십시오.
    5. 항목에 관련 내용이 없거나 판단이 어려운 경우, `"해당 항목은 .gitlab-ci.yml에서 확인할 수 없습니다."`와 같이 사유를 `status` 또는 `issues`에 명시하십시오.
    6. `evidence`는 반드시 `.gitlab-ci.yml` 내 **실제 키워드, job 이름, 설정값, script**에 기반해야 하며, 추상적 표현은 금지합니다.
    ---
    ## 분석 대상 파일 (YAML 형식):
    {data}
    ---

    각 항목에는 다음 필드를 반드시 포함하십시오.
    - `standard`: 해당 항목의 평가 기준 설명
    - `status`: 현재 파이프라인의 상태 요약
    - `progress`: 0부터 100 사이의 정수. 해당 항목이 얼마나 충족되었는지를 수치로 표현
    - `priority`: 이 항목의 개선 시급도. "High", "Medium", "Low" 중 하나
    - `issues`: 현재 파이프라인에서 식별된 주요 문제 요약
    - `countermeasures`: 문제 해결을 위한 구체적 조치와 예시
    - `recommendations`: 추가로 권장되는 개선 사항. 반드시 현실적으로 실행 가능한 수준의 방안일 것
    - `evidence`: 판단에 사용한 `.gitlab-ci.yml` 내의 키워드, job 이름, 설정, 스크립트 등 핵심 근거

    JSON 출력 형식:
    {{
        "Pipeline Structure and Design Quality": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "High",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Test Integration": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Medium",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Security Scanning (Shift Left Security)": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "High",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Secrets and Credential Management": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "High",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Job Hardening and Execution Safety": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Medium",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
            "Deployment Safety and Control": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Medium",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Code Quality and Coverage Reporting": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Medium",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Observability, Feedback, and Metrics": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Low",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Pipeline Efficiency and Caching": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Low",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }},
        "Compliance and Traceability": {{
            "standard": "string",
            "status": "string",
            "progress": 0,
            "priority": "Medium",
            "issues": "string",
            "countermeasures": "string",
            "recommendations": "string",
            "evidence": "string"
        }}
    }}

    ## 출력 규칙
    - 출력은 **한국어로 자연스럽고 이해하기 쉽게** 작성해야 합니다.
    - 반드시 **유효한 JSON 형식만** 출력하십시오. (그 외 설명, 주석, 자연어 모두 금지)
    - 문자열은 **반드시 큰따옴표(")**로 감쌉니다.
    - 각 항목은 `""`로 비워도 되지만, 그 이유는 `status` 또는 `issues` 또는 `recommendations`에 반드시 작성되어야 합니다.
    - `evidence`에는 가능한 한 정확한 키워드 또는 스크립트 조각을 명시하세요 (예: `"script: npm audit"`).

    심호흡을 하고, 분석 항목별로 **신뢰할 수 있는 근거와 함께** 구조적으로 판단을 내려 보세요.
    """
)