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

    def _validate_ssm_instance(self) -> None:
        logger.info("SSM 인스턴스 유효성 검증 시작...")
        response = self.ssm_client.describe_instance_information()
        valid_instances = {info['InstanceId'] for info in response['InstanceInformationList']}

        if self.config.instance_id not in valid_instances:
            msg = f"인스턴스 {self.config.instance_id}는 SSM에서 관리되지 않거나 접근할 수 없습니다."
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"SSM 접근 가능 인스턴스 확인됨: {self.config.instance_id}")

    def _fetch_accessible_ip(self) -> None:
        logger.info(f"EC2 접근 가능한 IP 조회 중... 인스턴스: {self.config.instance_id}")
        response = self.ec2_client.describe_instances(InstanceIds=[self.config.instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        public_ip = instance.get('PublicIpAddress')
        private_ip = instance.get('PrivateIpAddress')

        if public_ip:
            self.config.accessible_ip = public_ip
            logger.info(f"퍼블릭 IP 사용: {public_ip}")
        elif private_ip:
            self.config.accessible_ip = private_ip
            logger.info(f"프라이빗 IP 사용: {private_ip}")
        else:
            msg = "퍼블릭/프라이빗 IP가 모두 존재하지 않습니다."
            logger.error(msg)
            raise RuntimeError(msg)

    def _execute_ssm_command(self, command: str, comment: str) -> Dict[str, Any]:
        logger.info(f"SSM 명령 실행 시작: {comment}")
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
                    logger.info(f"SSM 명령 실행 완료. 상태: {output['Status']}")
                    return output
            except ClientError as e:
                if 'InvocationDoesNotExist' in str(e):
                    continue
                raise
        raise TimeoutError("SSM 명령 실행 시간 초과")

    def get_gitlab_projects(self) -> Dict[str, Any]:
        command = (
            f"curl -s --header 'PRIVATE-TOKEN: {self.config.gitlab_token}' "
            f"http://{self.config.accessible_ip}/api/v4/projects"
        )
        logger.info("GitLab 프로젝트 목록 조회 시작...")
        output = self._execute_ssm_command(command, "Get GitLab projects")

        if output.get('Status') != 'Success':
            msg = f"GitLab 프로젝트 명령 실행 실패: {output.get('StatusDetails', '상세정보 없음')}"
            logger.error(msg)
            return {"message": msg}

        try:
            result = json.loads(output['StandardOutputContent'])
        except json.JSONDecodeError:
            logger.error("GitLab 프로젝트 응답 파싱 실패")
            return {"message": "GitLab 프로젝트 응답 파싱 실패"}

        if isinstance(result, dict) and 'message' in result:
            logger.error(f"GitLab API 에러 메시지: {result['message']}")
            return {"message": f"GitLab API 에러: {result['message']}"}

        logger.info("GitLab 프로젝트 목록 파싱 완료")
        return {"data": result}

    def get_gitlab_ci_file(self, project_id: str) -> Dict[str, Any]:
        command = (
            f"curl -s --header 'PRIVATE-TOKEN: {self.config.gitlab_token}' "
            f"http://{self.config.accessible_ip}/api/v4/projects/{project_id}/repository/files/"
            f".gitlab-ci.yml/raw?ref=main"
        )
        logger.info(f"GitLab CI 조회 중... 프로젝트: {project_id}")
        output = self._execute_ssm_command(command, "Get GitLab .gitlab-ci.yml")

        if output.get('Status') == 'Success':
            logger.info(".gitlab-ci.yml 조회 성공")
            return {"data": output.get('StandardOutputContent', '')}
        else:
            msg = f".gitlab-ci.yml 조회 실패: {output.get('StatusDetails', '상세정보 없음')}"
            logger.error(msg)
            return {"message": msg}
