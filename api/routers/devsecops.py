from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from session.Service import Service
from session.manager.DevSecOpsManager import DevSecOpsManager
from analyzer.devsecops import analyzer

router = APIRouter(prefix="/devsecops", tags=["DevSecOps"])
service = Service()

class Session(BaseModel):
    access_key: str
    secret_key: str
    region: str = "ap-northeast-2"
    instance_id: str = None
    gitlab_token: str = None

class Projects(BaseModel):
    access_key: str

class Analyzer(BaseModel):
    access_key: str
    project_id: str

@router.post("/session")
def create_session(data: Session):
    try:
        service.register_user(
            access_key=data.access_key,
            secret_key=data.secret_key,
            instance_id=data.instance_id,
            gitlab_token=data.gitlab_token
        )
        return data.access_key
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/projects")
def get_gitlab_projects(data: Projects):
    try:
        manager = DevSecOpsManager(service.get_user_manager(data.access_key).config)
        projects = manager.get_gitlab_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/projects/analyzer")
def scan_gitlab_ci(data: Analyzer):
    try:
        manager = DevSecOpsManager(service.get_user_manager(data.access_key).config)
        gitlab_ci_file = manager.get_gitlab_ci_file(data.project_id)
        result = analyzer.analyze_devsecops(gitlab_ci_file)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))