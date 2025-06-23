# tests/integration/test_service_integration.py

from session.Service import Service

def test_register_and_retrieve_user_integration():
    from session.AWSConfig import AWSConfig

    service = Service()
    service.register_user(
        access_key="real-ak",
        secret_key="real-sk",
        region="ap-northeast-2",
        instance_id="i-ec2",
        gitlab_token="gl-token"
    )

    manager = service.get_user_manager("real-ak")
    assert hasattr(manager, "session")
    assert hasattr(manager, "config")
    assert manager.config.gitlab_token == "gl-token"
