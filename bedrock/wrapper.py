from bedrock.client import get_bedrock_client

def call_bedrock_model(prompt: str) -> str:
    client = get_bedrock_client()
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body={
            "prompt": prompt,
            "max_tokens_to_sample": 4096
        }
    )
    return response['body'].read().decode()
