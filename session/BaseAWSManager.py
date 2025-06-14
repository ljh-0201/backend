from core.logger import logger
import boto3
from .AWSConfig import AWSConfig


class BaseAWSManager:
    def __init__(self, config: AWSConfig):
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> boto3.Session:
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            logger.info("공통 AWS 세션 초기화 완료")
            return session
        except Exception as e:
            logger.error(f"AWS 세션 초기화 실패: {e}")
            raise RuntimeError(f"AWS 세션 초기화 실패: {e}")