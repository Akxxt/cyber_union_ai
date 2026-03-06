"""
全局配置管理模块（最终版）。
基于pydantic BaseSettings实现，提供全局统一的配置对象，支持热更新。
"""
import os
import json
from typing import Optional, List, Dict
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from app.config.env import env_settings


class Settings(BaseSettings):
    """
    全局配置类，继承自env_settings，可扩展更多运行时配置，支持热更新。
    """
    # 服务基础
    service_name: str = Field(default_factory=lambda: env_settings.SERVICE_NAME)
    version: str = Field(default_factory=lambda: env_settings.VERSION)
    env: str = Field(default_factory=lambda: env_settings.ENV)
    host: str = Field(default_factory=lambda: env_settings.HOST)
    port: int = Field(default_factory=lambda: env_settings.PORT)
    cors_origins: List[str] = Field(default_factory=lambda: env_settings.CORS_ORIGINS)

    # 大模型
    openai_api_key: Optional[str] = Field(default_factory=lambda: env_settings.OPENAI_API_KEY)
    openai_base_url: Optional[str] = Field(default_factory=lambda: env_settings.OPENAI_BASE_URL)
    default_model: str = Field(default_factory=lambda: env_settings.DEFAULT_MODEL)
    model_timeout: int = Field(default_factory=lambda: env_settings.MODEL_TIMEOUT)
    model_max_retries: int = Field(default_factory=lambda: env_settings.MODEL_MAX_RETRIES)

    # 数据库
    sqlite_url: str = Field(default_factory=lambda: env_settings.SQLITE_URL)
    redis_host: str = Field(default_factory=lambda: env_settings.REDIS_HOST)
    redis_port: int = Field(default_factory=lambda: env_settings.REDIS_PORT)
    redis_password: Optional[str] = Field(default_factory=lambda: env_settings.REDIS_PASSWORD)
    redis_db: int = Field(default_factory=lambda: env_settings.REDIS_DB)

    # 任务
    task_max_concurrent: int = Field(default_factory=lambda: env_settings.TASK_MAX_CONCURRENT)
    task_max_execution_seconds: int = Field(default_factory=lambda: env_settings.TASK_MAX_EXECUTION_SECONDS)
    default_token_budget: int = Field(default_factory=lambda: env_settings.DEFAULT_TOKEN_BUDGET)
    single_step_max_retries: int = Field(default_factory=lambda: env_settings.SINGLE_STEP_MAX_RETRIES)

    # 日志
    log_path: str = Field(default_factory=lambda: env_settings.LOG_PATH)
    log_level: str = Field(default_factory=lambda: env_settings.LOG_LEVEL)
    log_file_max_size: str = Field(default_factory=lambda: env_settings.LOG_FILE_MAX_SIZE)
    log_backup_count: int = Field(default_factory=lambda: env_settings.LOG_BACKUP_COUNT)

    # 安全
    compliance_switch: bool = Field(default_factory=lambda: env_settings.COMPLIANCE_SWITCH)
    sensitive_detect_switch: bool = Field(default_factory=lambda: env_settings.SENSITIVE_DETECT_SWITCH)
    api_secret_key: Optional[str] = Field(default_factory=lambda: env_settings.API_SECRET_KEY)

    # 模型提供商
    deepseek_api_key: Optional[str] = Field(default_factory=lambda: env_settings.DEEPSEEK_API_KEY)
    deepseek_base_url: Optional[str] = Field(default_factory=lambda: env_settings.DEEPSEEK_BASE_URL)
    claude_api_key: Optional[str] = Field(default_factory=lambda: env_settings.CLAUDE_API_KEY)
    claude_base_url: Optional[str] = Field(default_factory=lambda: env_settings.CLAUDE_BASE_URL)
    doubao_api_key: Optional[str] = Field(default_factory=lambda: env_settings.DOUBAO_API_KEY)
    doubao_base_url: Optional[str] = Field(default_factory=lambda: env_settings.DOUBAO_BASE_URL)

    # 角色模型映射
    role_model_mapping: Dict[str, str] = Field(default_factory=lambda: env_settings.ROLE_MODEL_MAPPING)

    # 函数调用
    function_calling_enabled: bool = Field(default_factory=lambda: env_settings.FUNCTION_CALLING_ENABLED)
    function_sandbox: bool = Field(default_factory=lambda: env_settings.FUNCTION_SANDBOX)

    # 插件
    plugin_dir: str = Field(default_factory=lambda: env_settings.PLUGIN_DIR)
    plugin_timeout: int = Field(default_factory=lambda: env_settings.PLUGIN_TIMEOUT)
    max_concurrent_plugins: int = Field(default_factory=lambda: env_settings.MAX_CONCURRENT_PLUGINS)
    http_domain_whitelist: List[str] = Field(default_factory=lambda: env_settings.HTTP_DOMAIN_WHITELIST)
    file_plugin_work_dir: str = Field(default_factory=lambda: env_settings.FILE_PLUGIN_WORK_DIR)
    role_permission_levels: Dict[str, int] = Field(default_factory=lambda: env_settings.ROLE_PERMISSION_LEVELS)

    # 行政分支
    executive_config_path: str = Field(default_factory=lambda: env_settings.EXECUTIVE_CONFIG_PATH)
    budget_warning_threshold: float = Field(default_factory=lambda: env_settings.BUDGET_WARNING_THRESHOLD)

    # 内阁
    cabinet_parallel_max_workers: int = Field(default_factory=lambda: env_settings.CABINET_PARALLEL_MAX_WORKERS)
    cabinet_execution_timeout: int = Field(default_factory=lambda: env_settings.CABINET_EXECUTION_TIMEOUT)
    cabinet_retry_max_times: int = Field(default_factory=lambda: env_settings.CABINET_RETRY_MAX_TIMES)

    # 热更新相关
    _config_path: str = "config.json"
    _observer = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_json_config()
        self._start_watcher()

    def _load_json_config(self):
        """从JSON文件加载额外配置（覆盖环境变量）。"""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            except Exception as e:
                print(f"加载配置文件失败: {e}")

    def _start_watcher(self):
        """启动配置文件监听（需安装watchdog）。"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class ConfigFileHandler(FileSystemEventHandler):
                def __init__(self, settings_obj):
                    self.settings_obj = settings_obj

                def on_modified(self, event):
                    if event.src_path.endswith(self.settings_obj._config_path):
                        self.settings_obj._load_json_config()
                        print("配置已热更新")

            self._observer = Observer()
            self._observer.schedule(ConfigFileHandler(self), path=".", recursive=False)
            self._observer.start()
        except ImportError:
            print("watchdog未安装，热更新功能不可用")

    def reload_settings(self):
        """手动触发配置重载。"""
        self._load_json_config()

    def stop_watcher(self):
        """停止监听。"""
        if self._observer:
            self._observer.stop()
            self._observer.join()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()