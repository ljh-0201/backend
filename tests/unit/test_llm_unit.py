# tests/unit/test_llm_unit.py

import pytest
from bedrock import llm as bedrock_llm
from botocore.config import Config

def test_timeout_config_values():
    config = bedrock_llm.timeout_config
    assert isinstance(config, Config)
    assert config.connect_timeout == 10
    assert config.read_timeout == 600
    assert config.retries['max_attempts'] == 3

def test_bedrock_runtime_client_is_boto3(mocker):
    mock_boto = mocker.patch("bedrock.llm.boto3.client")
    from importlib import reload
    reload(bedrock_llm)  # re-import to trigger boto3.client again
    mock_boto.assert_called_with(
        "bedrock-runtime",
        region_name="us-east-1",
        config=bedrock_llm.timeout_config
    )

def test_llm_model_config():
    llm = bedrock_llm.llm
    assert llm.model_id.startswith("anthropic.claude")
    assert llm.model_kwargs["temperature"] == 0.1
    assert llm.model_kwargs["max_tokens"] == 4096
