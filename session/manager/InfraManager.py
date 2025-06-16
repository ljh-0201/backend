from core.logger import logger
from session.BaseAWSManager import BaseAWSManager


class InfraManager(BaseAWSManager):
    def __init__(self, config):
        super().__init__(config)
        logger.info("[Infra] InfraManager initialization complete")
