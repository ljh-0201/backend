import datetime
import jmespath

from core.logger import logger
from botocore.exceptions import ClientError
from typing import Any, Dict, List
from session.BaseAWSManager import BaseAWSManager


class IAMManager(BaseAWSManager):
    def __init__(self, config):
        super().__init__(config)
        self.iam_client = self.session.client('iam')
        self.cloudtrail_client = self.session.client('cloudtrail')
        logger.info("[IAM] IAMManager 초기화 완료")

    @staticmethod
    def _extract_allowed_actions(policies: List[Dict]) -> Dict[str, Any]:
        try:
            allowed_actions = set()

            for policy in policies:
                statements = policy.get("Statement", [])
                if isinstance(statements, dict):
                    statements = [statements]

                for stmt in statements:
                    if stmt.get("Effect") != "Allow":
                        continue

                    actions = stmt.get("Action", [])
                    if isinstance(actions, str):
                        allowed_actions.add(actions)
                    elif isinstance(actions, list):
                        allowed_actions.update(actions)

            result = {"allowed_actions": sorted(list(allowed_actions))} if allowed_actions else {}
            logger.info(f"[IAM] 정책에서 허용된 액션 추출 완료. 총 {len(result.get('allowed_actions', []))}개")
            return result

        except Exception as e:
            logger.error(f"[IAM] 정책 파싱 실패: {e}")
            raise

    def get_iam_users(self) -> Dict[str, Any]:
        try:
            logger.info("[IAM] IAM 사용자 목록 조회 시작")
            user_names = []
            paginator = self.iam_client.get_paginator('list_users')
            for page in paginator.paginate():
                user_names.extend([user['UserName'] for user in page['Users']])
            logger.info(f"[IAM] 총 {len(user_names)}명의 IAM 사용자 조회 완료")
            return {"data": user_names}
        except ClientError as e:
            logger.error(f"[IAM] 사용자 목록 조회 실패: {e}")
            raise

    def get_managed_policies(self, user_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"[IAM] 사용자 '{user_name}'에 연결된 관리형 정책 조회 시작")
            managed_policies = []
            attached_policies = self.iam_client.list_attached_user_policies(UserName=user_name)

            for policy in attached_policies['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_info = self.iam_client.get_policy(PolicyArn=policy_arn)['Policy']
                policy_version = self.iam_client.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=policy_info['DefaultVersionId']
                )

                managed_policies.append({
                    "PolicyArn": policy_arn,
                    "VersionId": policy_info['DefaultVersionId'],
                    "Statement": policy_version['PolicyVersion']['Document']['Statement']
                })

            logger.info(f"[IAM] 총 {len(managed_policies)}개의 관리형 정책 조회 완료")
            return self._extract_allowed_actions(managed_policies)

        except ClientError as e:
            logger.error(f"[IAM] 관리형 정책 조회 실패: {e}")
            raise

    def get_inline_policies(self, user_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"[IAM] 사용자 '{user_name}'의 인라인 정책 조회 시작")
            inline_policies = []
            policy_names = self.iam_client.list_user_policies(UserName=user_name)['PolicyNames']

            for policy_name in policy_names:
                policy_doc = self.iam_client.get_user_policy(
                    UserName=user_name,
                    PolicyName=policy_name
                )

                inline_policies.append({
                    "PolicyName": policy_name,
                    "Statement": policy_doc['PolicyDocument']['Statement']
                })

            logger.info(f"[IAM] 총 {len(inline_policies)}개의 인라인 정책 조회 완료")
            return self._extract_allowed_actions(inline_policies)

        except ClientError as e:
            logger.error(f"[IAM] 인라인 정책 조회 실패: {e}")
            raise

    def get_cloudtrail_events(self, user_name: str, analysis_days: int) -> Dict[str, Any]:
        try:
            logger.info(f"[CloudTrail] 사용자 '{user_name}'의 최근 {analysis_days}일간 이벤트 조회 시작")
            events = []
            next_token = None

            start_time = datetime.datetime.utcnow() - datetime.timedelta(days=analysis_days)
            end_time = datetime.datetime.utcnow()

            while True:
                if next_token:
                    response = self.cloudtrail_client.lookup_events(
                        LookupAttributes=[{
                            'AttributeKey': 'Username',
                            'AttributeValue': user_name
                        }],
                        StartTime=start_time,
                        EndTime=end_time,
                        MaxResults=50,
                        NextToken=next_token
                    )
                else:
                    response = self.cloudtrail_client.lookup_events(
                        LookupAttributes=[{
                            'AttributeKey': 'Username',
                            'AttributeValue': user_name
                        }],
                        StartTime=start_time,
                        EndTime=end_time,
                        MaxResults=50
                    )

                events.extend(response.get("Events", []))
                next_token = response.get("NextToken")
                if not next_token:
                    break

            result = jmespath.search(
                '[?Resources && Resources[?ResourceName]].{time: EventTime, action: EventName, resource: Resources[].ResourceName}',
                events
            ) or []

            logger.info(f"[CloudTrail] 총 {len(result)}건의 이벤트 수집 완료")
            return result

        except ClientError as e:
            logger.error(f"[CloudTrail] 이벤트 수집 실패: {e}")
            raise
