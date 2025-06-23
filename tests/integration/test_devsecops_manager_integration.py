# tests/integration/test_devsecops_manager_integration.py

import pytest
from session.manager.DevSecOpsManager import DevSecOpsManager

@pytest.fixture
def real_config():
    from session.AWSConfig import AWSConfig
    return AWSConfig(
        access_key="real-access-key",
        secret_key="real-secret-key",
        instance_id="i-actual-ec2",
        gitlab_token="real-gitlab-token"
    )

def test_integration_get_projects(real_config):
    manager = DevSecOpsManager(real_config)
    result = manager.get_gitlab_projects()
    assert isinstance(result, dict)
    assert "data" in result or "message" in result
