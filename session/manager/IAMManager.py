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
        logger.info("[IAM] IAMManager initialization complete")

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
            logger.info(f"[IAM] completed extracting allowed actions from policy. total {len(result.get('allowed_actions', []))}")
            return result

        except Exception as e:
            logger.error(f"[IAM] policy parsing failed: {e}")
            raise

    def get_iam_users(self) -> Dict[str, Any]:
        try:
            logger.info("[IAM] start querying the list of IAM users")
            user_names = []
            paginator = self.iam_client.get_paginator('list_users')
            for page in paginator.paginate():
                user_names.extend([user['UserName'] for user in page['Users']])
            logger.info(f"[IAM] completed query of {len(user_names)} IAM users")
            return {"data": user_names}
        except ClientError as e:
            logger.error(f"[IAM] failed to retrieve user list: {e}")
            raise

    def get_managed_policies(self, user_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"[IAM] start managed policy lookup for user '{user_name}'")
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

            logger.info(f"[IAM] total {len(managed_policies)} managed policies search completed")
            return self._extract_allowed_actions(managed_policies)

        except ClientError as e:
            logger.error(f"[IAM] managed policy lookup failed: {e}")
            raise

    def get_inline_policies(self, user_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"[IAM] start inline policy lookup for user '{user_name}'")
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

            logger.info(f"[IAM] total {len(inline_policies)} inline policies search completed")
            return self._extract_allowed_actions(inline_policies)

        except ClientError as e:
            logger.error(f"[IAM] inline policy lookup failed: {e}")
            raise

    def get_cloudtrail_events(self, user_name: str, analysis_days: int) -> Dict[str, Any]:
        try:
            logger.info(f"[CloudTrail] start viewing events for the last {analysis_days} days for user '{user_name}'")
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

            logger.info(f"[CloudTrail] total {len(result)} events search completed")
            return result

        except ClientError as e:
            logger.error(f"[CloudTrail] event collection failed: {e}")
            raise
