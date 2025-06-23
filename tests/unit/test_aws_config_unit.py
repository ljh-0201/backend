# tests/unit/test_aws_config_unit.py

import pytest
from session.AWSConfig import AWSConfig

def test_aws_config_basic_fields():
    cfg = AWSConfig(access_key="ak", secret_key="sk")
    assert cfg.access_key == "ak"
    assert cfg.secret_key == "sk"
    assert cfg.region == "ap-northeast-2"
    assert cfg.instance_id is None
    assert cfg.accessible_ip is None
    assert cfg.gitlab_token is None

def test_aws_config_all_fields():
    cfg = AWSConfig(
        access_key="ak",
        secret_key="sk",
        region="us-west-1",
        instance_id="i-abc",
        accessible_ip="1.2.3.4",
        gitlab_token="token"
    )
    assert cfg.region == "us-west-1"
    assert cfg.instance_id == "i-abc"
    assert cfg.accessible_ip == "1.2.3.4"
    assert cfg.gitlab_token == "token"
