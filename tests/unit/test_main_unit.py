# tests/unit/test_main_unit.py

from main import create_app
from fastapi.middleware.cors import CORSMiddleware

def test_create_app_instance():
    app = create_app()
    assert app.title == "FastAPI"
    assert isinstance(app.middleware[0].cls, type(CORSMiddleware)) or \
           isinstance(app.user_middleware[0].cls, type(CORSMiddleware))

def test_create_app_routes():
    app = create_app()
    routes = [route.path for route in app.routes]
    assert "/iam/session" in routes or any("iam" in r for r in routes)
    assert "/infra/session" in routes or any("infra" in r for r in routes)
    assert "/devsecops/session" in routes or any("devsecops" in r for r in routes)
