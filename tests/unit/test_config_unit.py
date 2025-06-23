# tests/unit/test_config_unit.py

from core.config import server_config

def test_server_config_structure():
    assert isinstance(server_config, dict)
    assert "backend" in server_config
    assert isinstance(server_config["backend"], dict)

def test_server_config_values():
    backend = server_config["backend"]
    assert backend["host"] == "0.0.0.0"
    assert backend["port"] == 5001
