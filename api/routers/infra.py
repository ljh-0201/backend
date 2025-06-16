from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from session.Service import Service
from session.manager.InfraManager import InfraManager
from analyzer.infra import analyzer

router = APIRouter(prefix="/infra", tags=["Infra"])
service = Service()

class Session(BaseModel):
    access_key: str
    secret_key: str
    region: str = "ap-northeast-2"

class Analyzer(BaseModel):
    access_key: str

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

@router.post("/analyzer")
def scan_gitlab_ci(data: Analyzer):
    try:
        InfraManager(service.get_user_manager(data.access_key).config)
        result = analyzer.analyze_infra()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))