from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from session.Service import Service

router = APIRouter(prefix="/infra", tags=["Infra"])
service = Service()

class Session(BaseModel):
    access_key: str
    secret_key: str
    region: str = "ap-northeast-2"

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