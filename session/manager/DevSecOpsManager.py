import json
import time
from core.logger import logger
from botocore.exceptions import ClientError
from typing import Any, Dict
from session.BaseAWSManager import BaseAWSManager

class DevSecOpsManager(BaseAWSManager):
    def __init__(self, config):
        super().__init__(config)
        self.ssm_client = self.session.client('ssm')
        self.ec2_client = self.session.client('ec2')
        self._validate_ssm_instance()
        self._fetch_accessible_ip()
        logger.info("[DevSecOps] DevSecOpsManager initialization complete")

    def _validate_ssm_instance(self) -> None:
        logger.info("start SSM instance validation...")
        response = self.ssm_client.describe_instance_information()
        valid_instances = {info['InstanceId'] for info in response['InstanceInformationList']}

        if self.config.instance_id not in valid_instances:
            msg = f"instance {self.config.instance_id} is not managed by SSM or is inaccessible."
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"SSM accessible instances verified: {self.config.instance_id}")

    def _fetch_accessible_ip(self) -> None:
        logger.info(f"EC2 accessible IP lookup... instance: {self.config.instance_id}")
        response = self.ec2_client.describe_instances(InstanceIds=[self.config.instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        public_ip = instance.get('PublicIpAddress')
        private_ip = instance.get('PrivateIpAddress')

        if public_ip:
            self.config.accessible_ip = public_ip
            logger.info(f"use public IP: {public_ip}")
        elif private_ip:
            self.config.accessible_ip = private_ip
            logger.info(f"use private IP: {private_ip}")
        else:
            msg = "neither public nor private IPs exist."
            logger.error(msg)
            raise RuntimeError(msg)

    def _execute_ssm_command(self, command: str, comment: str) -> Dict[str, Any]:
        logger.info(f"start executing SSM commands: {comment}")
        response = self.ssm_client.send_command(
            InstanceIds=[self.config.instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [command]},
            Comment=comment
        )
        command_id = response['Command']['CommandId']

        max_attempts = 20
        for _ in range(max_attempts):
            time.sleep(3)
            try:
                output = self.ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=self.config.instance_id
                )
                if output['Status'] in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                    logger.info(f"SSM command execution completed. status: {output['Status']}")
                    return output
            except ClientError as e:
                if 'InvocationDoesNotExist' in str(e):
                    continue
                raise
        raise TimeoutError("SSM command execution timeout")

    def get_gitlab_projects(self) -> Dict[str, Any]:
        command = (
            f"curl -s --header 'PRIVATE-TOKEN: {self.config.gitlab_token}' "
            f"http://{self.config.accessible_ip}/api/v4/projects"
        )
        logger.info("start viewing the list of GitLab projects...")
        output = self._execute_ssm_command(command, "Get GitLab projects")

        if output.get('Status') != 'Success':
            msg = f"failed to execute GitLab project command: {output.get('StatusDetails', 'No details')}"
            logger.error(msg)
            return {"message": msg}

        try:
            result = json.loads(output['StandardOutputContent'])
        except json.JSONDecodeError:
            logger.error("failed to parse GitLab project response")
            return {"message": "failed to parse GitLab project response"}

        if isinstance(result, dict) and 'message' in result:
            logger.error(f"GitLab API error messages: {result['message']}")
            return {"message": f"GitLab API error: {result['message']}"}

        logger.info("completed parsing GitLab project list")
        return {"data": result}

    def get_gitlab_ci_file(self, project_id: str) -> Dict[str, Any]:
        command = (
            f"curl -s --header 'PRIVATE-TOKEN: {self.config.gitlab_token}' "
            f"http://{self.config.accessible_ip}/api/v4/projects/{project_id}/repository/files/"
            f".gitlab-ci.yml/raw?ref=main"
        )
        logger.info(f"retrieving GitLab CI... project: {project_id}")
        output = self._execute_ssm_command(command, "Get GitLab .gitlab-ci.yml")

        if output.get('Status') == 'Success':
            logger.info(".gitlab-ci.yml lookup successful")
            return {"data": output.get('StandardOutputContent', '')}
        else:
            msg = f".gitlab-ci.yml lookup failed: {output.get('StatusDetails', 'No details')}"
            logger.error(msg)
            return {"message": msg}
