"""
测试配置模块。
"""
import os
import pytest
from app.config.env import env_settings, EnvSettings
from app.config.settings import settings, GlobalSettings


def test_env_settings_defaults():
    """测试环境变量默认值。"""
    assert env_settings.ENV == "development"
    assert env_settings.SERVICE_NAME == "cyber-union-ai"
    assert env_settings.PORT == 8000
    assert env_settings.DEFAULT_MODEL == "gpt-4"
    assert env_settings.SQLITE_URL == "sqlite+aiosqlite:///./cyber_union.db"


def test_env_settings_from_env(monkeypatch):
    """测试从环境变量覆盖配置。"""
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    
    from app.config.env import get_env_settings
    get_env_settings.cache_clear()
    new_settings = get_env_settings()
    
    assert new_settings.ENV == "production"
    assert new_settings.PORT == 9000
    assert new_settings.OPENAI_API_KEY == "test-key"


def test_global_settings():
    """测试全局配置对象。"""
    assert settings.service_name == env_settings.SERVICE_NAME
    assert settings.env == env_settings.ENV
    assert settings.sqlite_url == env_settings.SQLITE_URL
    assert settings.log_level == env_settings.LOG_LEVEL