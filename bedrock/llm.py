from langchain_aws import ChatBedrock
from botocore.config import Config
import boto3

timeout_config = Config(
    connect_timeout=10,   # 연결 시도 제한 시간
    read_timeout=300,     # 응답 대기 시간 (5분)
    retries={
        'max_attempts': 3,    # 재시도 횟수
        'mode': 'standard'    # 기본 재시도 모드
    }
)

bedrock_runtime_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",  # 사용 중인 리전 명시
    config=timeout_config
)

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock_runtime_client,  # 커스텀 클라이언트 주입
    model_kwargs={
        "temperature": 0.1,
        "max_tokens": 4096
    }
)