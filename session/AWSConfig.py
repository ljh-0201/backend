from dataclasses import dataclass
from typing import Optional

@dataclass
class AWSConfig:
    access_key: str
    secret_key: str
    region: str = "ap-northeast-2"
    instance_id: Optional[str] = None
    accessible_ip: Optional[str] = None
    gitlab_token: Optional[str] = None