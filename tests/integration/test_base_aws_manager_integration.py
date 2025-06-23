# tests/integration/test_base_aws_manager_integration.py

from session.BaseAWSManager import BaseAWSManager
from session.AWSConfig import AWSConfig

def test_create_real_aws_session():
    config = AWSConfig(
        access_key="real-ak",
        secret_key="real-sk",
        region="ap-northeast-2"
    )
    manager = BaseAWSManager(config)
    session = manager.session
    assert session is not None
    assert hasattr(session, "client")
