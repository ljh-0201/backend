from langchain_aws import ChatBedrock
from botocore.config import Config
import boto3

timeout_config = Config(
    connect_timeout=10,
    read_timeout=600,
    retries={
        'max_attempts': 3,
        'mode': 'standard'
    }
)

bedrock_runtime_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    config=timeout_config
)

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock_runtime_client,
    model_kwargs={
        "temperature": 0.1,
        "max_tokens": 4096
    }
)