# tests/unit/test_logger_unit.py

from core.logger import logger

def test_logger_level():
    assert logger.level == 20  # logging.INFO == 20

def test_logger_name():
    assert logger.name == "core.logger"

def test_logger_can_log_info(caplog):
    with caplog.at_level("INFO"):
        logger.info("Test info message")
    assert "Test info message" in caplog.text
