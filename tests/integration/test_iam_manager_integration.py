# tests/integration/test_iam_manager_integration.py

from session.manager.IAMManager import IAMManager

def test_integration_get_users():
    from session.AWSConfig import AWSConfig
    config = AWSConfig(access_key="real-ak", secret_key="real-sk", region="ap-northeast-2")
    manager = IAMManager(config)
    users = manager.get_iam_users()
    assert isinstance(users, dict)
    assert "data" in users

def test_integration_get_cloudtrail_events():
    from session.AWSConfig import AWSConfig
    config = AWSConfig(access_key="real-ak", secret_key="real-sk", region="ap-northeast-2")
    manager = IAMManager(config)
    result = manager.get_cloudtrail_events("valid-username", 1)
    assert isinstance(result, list)
