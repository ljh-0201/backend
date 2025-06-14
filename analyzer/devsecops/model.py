from bedrock.wrapper import call_bedrock_model

def analyze_with_bedrock(prompt: str) -> str:
    return call_bedrock_model(prompt)
