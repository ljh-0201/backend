# tests/integration/test_infra_manager_integration.py

from session.manager.InfraManager import InfraManager
from session.AWSConfig import AWSConfig

def test_infra_manager_integration():
    config = AWSConfig(access_key="real-ak", secret_key="real-sk", region="ap-northeast-2")
    manager = InfraManager(config)
    assert manager.session is not None
