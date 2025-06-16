from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from session.Service import Service
from session.manager.IAMManager import IAMManager
from analyzer.iam import analyzer

router = APIRouter(prefix="/iam", tags=["IAM"])
service = Service()

class Session(BaseModel):
    access_key: str
    secret_key: str
    region: str = "ap-northeast-2"

class Users(BaseModel):
    access_key: str

class Analyzer(BaseModel):
    access_key: str
    user_name: str
    days: int

@router.post("/session")
def create_session(data: Session):
    try:
        service.register_user(
            access_key=data.access_key,
            secret_key=data.secret_key,
        )
        return data.access_key
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users")
def get_iam_users(data: Users):
    try:
        manager = IAMManager(service.get_user_manager(data.access_key).config)
        users = manager.get_iam_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/analyzer")
def scan_gitlab_ci(data: Analyzer):
    try:
        manager = IAMManager(service.get_user_manager(data.access_key).config)
        managed_policy = manager.get_managed_policies(data.user_name)
        inline_policy = manager.get_inline_policies(data.user_name)
        event = manager.get_cloudtrail_events(data.user_name, data.days)
        result = analyzer.analyze_iam(managed_policy, inline_policy, event, data.days)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))