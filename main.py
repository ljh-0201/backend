import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import iam, infra, devsecops
from core.config import server_config


def create_app() -> FastAPI:
    app = FastAPI()

    origins = [
        "http://localhost:3000",
        f"http://{server_config['frontend']['host']}:{server_config['frontend']['port']}"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(iam.router)
    app.include_router(infra.router)
    app.include_router(devsecops.router)

    return app


server = create_app()

if __name__ == "__main__":
    uvicorn.run(
        server,
        host=server_config["backend"]["host"],
        port=server_config["backend"]["port"],
        access_log=False
    )
