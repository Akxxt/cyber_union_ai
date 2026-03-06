"""
测试日志系统。
"""
import os
import tempfile
from pathlib import Path
import pytest
from loguru import logger

from app.audit.logger import Logger, get_logger
from app.config.settings import settings


def test_logger_configuration():
    """测试日志配置是否应用。"""
    log = Logger()
    log.configure()
    assert log._configured is True


def test_logger_write(tmp_path):
    """测试日志写入文件。"""
    original_path = settings.log_path
    settings.log_path = str(tmp_path)
    
    log = Logger()
    log.configure()
    
    log.info("Test info message", task_id="123", agent_role="PRESIDENT", module="test")
    log.error("Test error message", task_id="456", exc_info=False)
    
    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) > 0
    
    settings.log_path = original_path


def test_logger_bind_context():
    """测试上下文绑定。"""
    log = Logger()
    log.debug("debug", task_id="t1")
    log.info("info", agent_role="CONGRESS")
    log.warning("warn", module="test")
    log.error("error")
    log.critical("critical")
    log.exception("exception")
    assert True