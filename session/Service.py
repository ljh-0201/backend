from core.logger import logger
from typing import Dict
from session.AWSConfig import AWSConfig
from session.BaseAWSManager import BaseAWSManager

class Service:
    def __init__(self):
        self._user_sessions: Dict[str, BaseAWSManager] = {}

    def register_user(self, access_key: str, secret_key: str, region: str = "ap-northeast-2", instance_id: str = None, gitlab_token: str = None) -> None:
        config = AWSConfig(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            instance_id=instance_id,
            gitlab_token=gitlab_token
        )
        manager = BaseAWSManager(config)
        self._user_sessions[access_key] = manager
        logger.info(f"[{access_key}] user registration and session initialization complete")

    def get_user_manager(self, access_key: str) -> BaseAWSManager:
        if access_key not in self._user_sessions:
            raise ValueError(f"unregistered user access_key: {access_key}")
        return self._user_sessions[access_key]
